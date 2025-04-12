import os
import time
import asyncio
from datetime import datetime
from celery import Celery
from pathlib import Path

# Configure Celery
# celery_app = Celery('goblin_forge',
#                     broker='redis://localhost:6379/0',
#                     backend='redis://localhost:6379/0')

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
    
    def __init__(self, results_dir="./results", retention_days=7):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.retention_days = retention_days
        self.minion_status = {}
        
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
        result_dir = self.create_result_directory(gadget.name.replace(" ", "_").lower(), mode)
        
        # Submit task to Celery
        task_id = f"{gadget.name}_{mode}_{int(time.time())}"
        self.minion_status[task_id] = self.STATUS_BUSY
        
        try:
            # Queue task in Celery
            result = execute_gadget_task.delay(
                gadget_module=gadget.__module__,
                gadget_class=gadget.__class__.__name__,
                mode=mode,
                params=params,
                result_dir=str(result_dir)
            )
            
            # Return task info
            return {
                "task_id": task_id,
                "status": self.STATUS_BUSY,
                "result_dir": str(result_dir),
                "celery_task_id": result.id
            }
        except Exception as e:
            self.minion_status[task_id] = self.STATUS_ERROR
            return {
                "task_id": task_id,
                "status": self.STATUS_ERROR,
                "error": str(e)
            }
    
    def get_task_status(self, task_id):
        """Get the status of a task"""
        return self.minion_status.get(task_id, self.STATUS_SLEEPING)
    
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

# Celery task for executing gadget
@celery_app.task
def execute_gadget_task(gadget_module, gadget_class, mode, params, result_dir):
    """Celery task to execute a gadget in a separate process"""
    try:
        # Dynamically import the gadget module and class
        # This is the problematic part - it needs to use absolute imports
        if not gadget_module.startswith('goblin_forge.'):
            gadget_module = f'goblin_forge.{gadget_module}'
            
        module = __import__(gadget_module, fromlist=[gadget_class])
        GadgetClass = getattr(module, gadget_class)
        gadget = GadgetClass()
        
        # Create event loop for async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Execute the gadget
        result = loop.run_until_complete(
            gadget.execute(mode, params, result_dir)
        )
        
        return {
            "status": "completed",
            "result": result,
            "result_dir": result_dir
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "result_dir": result_dir
        }