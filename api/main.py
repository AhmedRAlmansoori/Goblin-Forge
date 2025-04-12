from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio

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
    allow_origins=["http://localhost:3000"],  # Frontend URL
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
