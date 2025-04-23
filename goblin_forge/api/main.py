from fastapi import FastAPI, HTTPException , UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path
import time
import shutil

from goblin_forge.core.plugin_loader import PluginLoader
from goblin_forge.core.minion_manager import MinionManager

# Initialize app
app = FastAPI(
    title="Goblin Forge",
    description="A web application for executing CLI binaries through a menu-driven interface",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://frontend:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the plugin loader and minion manager
plugin_loader = PluginLoader()
minion_manager = MinionManager()

# Load plugins on startup
@app.on_event("startup")
async def startup_event():
    # Discover gadgets
    plugin_loader.discover_gadgets()
    # Clean up old results
    minion_manager.cleanup_old_results()

# Models for API requests and responses
class TaskSubmission(BaseModel):
    gadget_id: str
    modes: List[str]
    parameters: Dict[str, Dict[str, Any]]

class TaskResponse(BaseModel):
    task_ids: List[str]
    status: str
    result_dirs: List[str]

class GadgetInfo(BaseModel):
    id: str
    name: str
    description: str
    modes: List[Dict[str, Any]]

# API Endpoints
@app.get("/api/gadgets", response_model=List[GadgetInfo])
async def get_gadgets():
    """Get all available Goblin Gadgets"""
    gadgets = plugin_loader.discover_gadgets()
    print(f"API: Returning {len(gadgets)} gadgets")

    result = []
    
    for gadget_class in gadgets:
        gadget = gadget_class()
        modes_info = []
        
        for mode in gadget.get_modes():
            mode_id = mode["id"]
            modes_info.append({
                "id": mode_id,
                "name": mode["name"],
                "description": mode["description"],
                "form_schema": gadget.get_form_schema(mode_id)
            })
        
        result.append({
            "id": gadget.tab_id,
            "name": gadget.name,
            "description": gadget.description,
            "modes": modes_info
        })
    
    return result

@app.post("/api/submit_task", response_model=TaskResponse)
async def submit_task(task: TaskSubmission):
    """Submit tasks to be executed by Minions"""
    gadget_id = task.gadget_id
    gadget_class = plugin_loader.get_gadget(gadget_id)
    
    if not gadget_class:
        raise HTTPException(status_code=404, detail=f"Gadget {gadget_id} not found")
    
    gadget = gadget_class()
    task_ids = []
    result_dirs = []
    
    # Submit each selected mode as a separate task
    for mode in task.modes:
        params = task.parameters.get(mode, {})
        
        # Submit the task to the minion manager
        # When calling submit_task, make sure the gadget module is correctly specified
        gadget_module = gadget.__module__
        # If the module doesn't already start with goblin_forge, add it
        if not gadget_module.startswith('goblin_forge.'):
            gadget_module = f'goblin_forge.{gadget_module}'
            
        task_info = await minion_manager.submit_task(gadget, mode, params)
        task_ids.append(task_info["task_id"])
        result_dirs.append(task_info["result_dir"])
    
    return {
        "task_ids": task_ids,
        "status": "submitted",
        "result_dirs": result_dirs
    }

@app.get("/api/task_status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a submitted task"""
    status = minion_manager.get_task_status(task_id)
    return {"task_id": task_id, "status": status}

@app.get("/api/minion_status")
async def get_minion_status():
    """Get status of all Minions"""
    return {"minions": minion_manager.minion_status}

# Add an endpoint to force cleanup of old results
@app.post("/api/cleanup_results")
async def cleanup_results():
    """Manually trigger cleanup of old results"""
    minion_manager.cleanup_old_results()
    return {"status": "Cleanup completed"}



@app.get("/api/completed_tasks", response_model=List[dict])
async def get_completed_tasks(limit: int = 50):
    """Get recently completed tasks with their results"""
    return minion_manager.get_completed_tasks(limit)

@app.get("/api/pending_tasks", response_model=List[dict])
async def get_pending_tasks():
    """Get currently pending tasks"""
    return minion_manager.get_pending_tasks()

@app.get("/api/minion_metrics", response_model=dict)
async def get_minion_metrics():
    """Get system metrics for minions"""
    return minion_manager.get_minion_metrics()

@app.post("/api/cancel_task/{task_id}", response_model=dict)
async def cancel_task(task_id: str):
    """Cancel a running task"""
    return minion_manager.cancel_task(task_id)

@app.post("/api/retry_task/{task_id}", response_model=dict)
async def retry_task(task_id: str):
    """Retry a failed task"""
    return minion_manager.retry_task(task_id)

@app.post("/api/pause_minion/{minion_id}", response_model=dict)
async def pause_minion(minion_id: str):
    """Pause a minion to prevent it from taking new tasks"""
    return minion_manager.pause_minion(minion_id)

@app.post("/api/resume_minion/{minion_id}", response_model=dict)
async def resume_minion(minion_id: str):
    """Resume a paused minion"""
    return minion_manager.resume_minion(minion_id)

@app.get("/api/task_details/{task_id}", response_model=dict)
async def get_task_details(task_id: str):
    """Get detailed information about a task"""
    return minion_manager.get_task_details(task_id)

@app.post("/api/upload_file", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the task's result directory"""
    # Create a unique filename with timestamp
    timestamp = int(time.time())
    filename = f"{timestamp}_{file.filename}"
    
    # Create a temporary result directory for the upload
    temp_result_dir = Path("./results") / f"temp_upload_{timestamp}"
    temp_result_dir.mkdir(exist_ok=True, parents=True)
    
    # Save the uploaded file
    file_path = temp_result_dir / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "file_path": str(file_path),
        "original_filename": file.filename,
        "temp_filename": filename,
        "content_type": file.content_type,
        "upload_timestamp": timestamp,
        "temp_result_dir": str(temp_result_dir)
    }