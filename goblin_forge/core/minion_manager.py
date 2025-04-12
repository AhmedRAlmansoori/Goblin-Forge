# In core/minion_manager.py

from datetime import datetime, timedelta
import psutil  # For system resource monitoring
import json
import time
import asyncio
from celery import Celery
from pathlib import Path
import os

# Configure Celery
celery_app = Celery('goblin_forge',
                    broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
                    backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

# Configure task concurrency
celery_app.conf.update(
    worker_concurrency=5,  # Max 5 concurrent Minions
    task_time_limit=3600,  # 60 minute timeout
    task_soft_time_limit=3540  # Soft timeout 59 minutes
)

class MinionManager:
    """Manages worker processes (Minions) for executing Goblin Gadget tasks"""
    
    STATUS_IDLE = "Idle Goblin"
    STATUS_BUSY = "Busy Goblin"
    STATUS_ERROR = "Troubled Goblin"
    STATUS_SLEEPING = "Sleepy Goblin"
    STATUS_PAUSED = "Paused Goblin"  # New status for paused workers
    
    def __init__(self, results_dir="./results", retention_days=7):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.retention_days = retention_days
        self.minion_status = {}
        self.minion_details = {}  # Store detailed info about each minion
        self.completed_tasks = []  # Track completed tasks
        self.completed_tasks_max = 100  # Maximum number of completed tasks to store
        self.pending_tasks = []  # Track pending tasks
        self.paused_minions = set()  # Track paused minions
        
    def create_result_directory(self, gadget_name, mode):
        """Create a timestamped directory for results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"goblinforge_{timestamp}_{gadget_name}_{mode}"
        result_dir = self.results_dir / dir_name
        result_dir.mkdir(exist_ok=True)
        return result_dir
    
    async def submit_task(self, gadget, mode, params):
        """Submit a task to be executed by a Minion"""
        # Create results directory
        gadget_name = gadget.name.replace(" ", "_").lower()
        result_dir = self.create_result_directory(gadget_name, mode)
        
        # Submit task to Celery
        task_id = f"{gadget.name}_{mode}_{int(time.time())}"
        self.minion_status[task_id] = self.STATUS_BUSY
        
        # Store detailed info about the task
        task_info = {
            "task_id": task_id,
            "gadget_name": gadget.name,
            "mode": mode,
            "params": params,
            "result_dir": str(result_dir),
            "submit_time": datetime.now().isoformat(),
            "status": self.STATUS_BUSY,
        }
        
        self.minion_details[task_id] = task_info
        self.pending_tasks.append(task_info)
        
        try:
            # Queue task in Celery
            result = execute_gadget_task.delay(
                gadget_module=gadget.__module__,
                gadget_class=gadget.__class__.__name__,
                mode=mode,
                params=params,
                result_dir=str(result_dir),
                task_id=task_id  # Pass task_id to the Celery task
            )
            
            # Update task info with Celery task ID
            self.minion_details[task_id]["celery_task_id"] = result.id
            
            # Set up an async task to check for completion
            asyncio.create_task(self._monitor_task(task_id, result))

            # Return task info
            return {
                "task_id": task_id,
                "status": self.STATUS_BUSY,
                "result_dir": str(result_dir),
                "celery_task_id": result.id
            }
        except Exception as e:
            self.minion_status[task_id] = self.STATUS_ERROR
            self.minion_details[task_id]["status"] = self.STATUS_ERROR
            self.minion_details[task_id]["error"] = str(e)
            
            # Move from pending to completed
            self.pending_tasks = [t for t in self.pending_tasks if t["task_id"] != task_id]
            self.completed_tasks.insert(0, self.minion_details[task_id])
            
            return {
                "task_id": task_id,
                "status": self.STATUS_ERROR,
                "error": str(e)
            }
    async def _monitor_task(self, task_id, celery_task):
        """Monitor a Celery task for completion"""
        try:
            # Wait for task to complete
            task_result = await asyncio.to_thread(celery_task.get)
            
            print(f"Task {task_id} completed with result: {task_result}")
            
            # Update task status based on result
            if task_result.get("status") == "completed":
                self.update_task_status(task_id, self.STATUS_IDLE, task_result)
            else:
                self.update_task_status(task_id, self.STATUS_ERROR, task_result)
                
        except Exception as e:
            print(f"Error monitoring task {task_id}: {e}")
            self.update_task_status(task_id, self.STATUS_ERROR, {"error": str(e)})
            
    def update_task_status(self, task_id, status, result=None):
        """Update the status of a task and store results if completed"""
        print(f"Updating task {task_id} to status {status}")
        
        self.minion_status[task_id] = status
        
        if task_id in self.minion_details:
            self.minion_details[task_id]["status"] = status
            
            if result:
                print(f"Task {task_id} has result: {result}")
                self.minion_details[task_id]["result"] = result
                self.minion_details[task_id]["completion_time"] = datetime.now().isoformat()
                
                # Calculate execution time
                if "submit_time" in self.minion_details[task_id]:
                    submit_time = datetime.fromisoformat(self.minion_details[task_id]["submit_time"])
                    completion_time = datetime.fromisoformat(self.minion_details[task_id]["completion_time"])
                    execution_time = (completion_time - submit_time).total_seconds()
                    self.minion_details[task_id]["execution_time_seconds"] = execution_time
            
            if status in [self.STATUS_IDLE, self.STATUS_ERROR]:
                print(f"Moving task {task_id} from pending to completed")
                # Move task from pending to completed
                self.pending_tasks = [t for t in self.pending_tasks if t["task_id"] != task_id]
                self.completed_tasks.insert(0, self.minion_details[task_id])
                
                # Trim completed tasks list if needed
                if len(self.completed_tasks) > self.completed_tasks_max:
                    self.completed_tasks = self.completed_tasks[:self.completed_tasks_max]
                    
                # Remove from active minions list
                if task_id in self.minion_status:
                    print(f"Removing task {task_id} from minion_status")
                    del self.minion_status[task_id]

    def get_task_status(self, task_id):
        """Get the status of a task"""
        return self.minion_status.get(task_id, self.STATUS_SLEEPING)
    
    def get_task_details(self, task_id):
        """Get detailed information about a task"""
        return self.minion_details.get(task_id, {"error": "Task not found"})
    
    def get_completed_tasks(self, limit=50):
        """Get recently completed tasks with their results"""
        return self.completed_tasks[:limit]
    
    def get_pending_tasks(self):
        """Get currently pending tasks"""
        return self.pending_tasks
    
    def cancel_task(self, task_id):
        """Cancel a running task"""
        if task_id in self.minion_details and "celery_task_id" in self.minion_details[task_id]:
            celery_task_id = self.minion_details[task_id]["celery_task_id"]
            try:
                # Try to revoke the Celery task
                celery_app.control.revoke(celery_task_id, terminate=True)
                self.update_task_status(task_id, self.STATUS_ERROR, {"error": "Task cancelled by user"})
                return {"status": "success", "message": f"Task {task_id} cancelled"}
            except Exception as e:
                return {"status": "error", "message": f"Failed to cancel task: {str(e)}"}
        return {"status": "error", "message": "Task not found or already completed"}
    
    def pause_minion(self, minion_id):
        """Pause a minion to prevent it from taking new tasks"""
        if minion_id not in self.paused_minions:
            self.paused_minions.add(minion_id)
            return {"status": "success", "message": f"Minion {minion_id} paused"}
        return {"status": "error", "message": "Minion already paused"}
    
    def resume_minion(self, minion_id):
        """Resume a paused minion"""
        if minion_id in self.paused_minions:
            self.paused_minions.remove(minion_id)
            return {"status": "success", "message": f"Minion {minion_id} resumed"}
        return {"status": "error", "message": "Minion not paused"}
    
    def get_minion_metrics(self):
        """Get system metrics for minions"""
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "active_tasks": len([s for s in self.minion_status.values() if s == self.STATUS_BUSY]),
            "total_completed": len(self.completed_tasks),
            "error_rate": sum(1 for t in self.completed_tasks if t["status"] == self.STATUS_ERROR) / 
                         max(1, len(self.completed_tasks)) * 100,
            "pending_tasks": len(self.pending_tasks),
        }
        return metrics
    
    def cleanup_old_results(self):
        """Clean up results older than retention period"""
        current_time = time.time()
        for path in self.results_dir.glob("goblinforge_*"):
            if path.is_dir():
                # Check if folder is older than retention period
                folder_time = path.stat().st_mtime
                age_days = (current_time - folder_time) / (60 * 60 * 24)
                
                if age_days > self.retention_days:
                    # Delete folder and contents
                    try:
                        for file in path.glob("*"):
                            file.unlink()
                        path.rmdir()
                    except Exception as e:
                        print(f"Error cleaning up {path}: {e}")
    
    def retry_task(self, task_id):
        """Retry a failed task"""
        if task_id in self.minion_details and self.minion_details[task_id]["status"] == self.STATUS_ERROR:
            task_info = self.minion_details[task_id]
            
            # Create a new task with the same parameters
            new_task_id = f"{task_info['gadget_name']}_{task_info['mode']}_{int(time.time())}"
            self.minion_status[new_task_id] = self.STATUS_BUSY
            
            # Copy task info and update
            new_task_info = task_info.copy()
            new_task_info["task_id"] = new_task_id
            new_task_info["submit_time"] = datetime.now().isoformat()
            new_task_info["status"] = self.STATUS_BUSY
            new_task_info["is_retry"] = True
            new_task_info["original_task_id"] = task_id
            
            self.minion_details[new_task_id] = new_task_info
            self.pending_tasks.append(new_task_info)
            
            # Queue the task
            result = execute_gadget_task.delay(
                gadget_module=task_info.get("gadget_module"),
                gadget_class=task_info.get("gadget_class"),
                mode=task_info.get("mode"),
                params=task_info.get("params"),
                result_dir=task_info.get("result_dir"),
                task_id=new_task_id
            )
            
            self.minion_details[new_task_id]["celery_task_id"] = result.id
            
            return {
                "status": "success", 
                "message": f"Task {task_id} requeued as {new_task_id}",
                "new_task_id": new_task_id
            }
        
        return {"status": "error", "message": "Task not found or not in error state"}

# Celery task for executing gadget
@celery_app.task
def execute_gadget_task(gadget_module, gadget_class, mode, params, result_dir, task_id=None):
    """Celery task to execute a gadget in a separate process"""
    try:
        # Ensure gadget_module has the full path
        if not gadget_module.startswith('goblin_forge.'):
            gadget_module = f'goblin_forge.{gadget_module}'
            
        # Dynamically import the gadget module and class
        module = __import__(gadget_module, fromlist=[gadget_class])
        GadgetClass = getattr(module, gadget_class)
        gadget = GadgetClass()
        
        # Start time for performance tracking
        start_time = time.time()
        
        # Create event loop for async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Execute the gadget
        gadget_result = loop.run_until_complete(
            gadget.execute(mode, params, result_dir)
        )
        
        # End time for performance tracking
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Extract result file and preview if available
        result_file = gadget_result.get('result_file')
        result_preview = gadget_result.get('result_preview')
        
        # If result_preview doesn't exist, try to create one from the result file
        if result_file and not result_preview and os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    content = f.read(1000)  # Read first 1000 chars
                    result_preview = content + ('...' if len(content) >= 1000 else '')
            except Exception as e:
                print(f"Error creating result preview: {e}")
        
        # Add more metadata to the result
        output = {
            "status": "completed",
            "gadget_name": getattr(gadget, 'name', 'Unknown'),
            "gadget_module": gadget_module,
            "gadget_class": gadget_class,
            "mode": mode,
            "params": params,
            "result": gadget_result,  # Include original gadget result
            "result_file": result_file,  # Also include direct references to important fields
            "result_preview": result_preview,
            "result_dir": result_dir,
            "execution_time": execution_time,
            "execution_timestamp": datetime.now().isoformat(),
        }
        
        print(f"Task executed successfully. Result: {output}")
        return output
    except Exception as e:
        error_msg = f"Error executing task: {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "result_dir": result_dir,
            "gadget_name": "Unknown",
            "gadget_module": gadget_module,
            "gadget_class": gadget_class,
            "mode": mode
        }