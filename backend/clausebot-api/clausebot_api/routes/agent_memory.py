"""
Beads-inspired Agent Memory API Routes for ClauseBot
Provides JSON-first agent memory, ready work detection, and dependency tracking
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel

from clausebot_api.models.agent_memory import (
    AgentTask, TaskDependency, ReadyWorkItem, AgentMemoryStats,
    TaskStatus, TaskPriority, TaskType, DependencyType, BatchTaskCreate
)
from clausebot_api.services.agent_memory_service import agent_memory, ReadyWorkConfig

router = APIRouter()

# Request/Response Models
class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    task_type: TaskType = TaskType.TASK
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None
    category: Optional[str] = None
    clause_ref: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class UpdateTaskRequest(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None

class AddDependencyRequest(BaseModel):
    dependent_task_id: str
    blocks_task_id: str
    dependency_type: DependencyType = DependencyType.BLOCKS
    notes: Optional[str] = None

class AgentMemoryResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None

# Agent Memory Endpoints (Beads-inspired)

@router.post("/agent/memory/task", response_model=AgentMemoryResponse)
def create_agent_task(request: CreateTaskRequest):
    """Create a new agent task (Beads bd create pattern)"""
    
    try:
        task = agent_memory.create_task(
            title=request.title,
            description=request.description,
            priority=request.priority,
            task_type=request.task_type,
            assignee=request.assignee,
            labels=request.labels,
            source="api",
            category=request.category,
            clause_ref=request.clause_ref,
            session_id=request.session_id,
            context=request.context
        )
        
        return AgentMemoryResponse(
            success=True,
            data=task.dict(),
            message=f"Task {task.id} created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.post("/agent/memory/tasks/batch", response_model=AgentMemoryResponse)
def batch_create_tasks(request: BatchTaskCreate):
    """Batch create tasks from agent discovery (Beads pattern)"""
    
    try:
        tasks = agent_memory.batch_create_tasks(
            task_data=request.tasks,
            source=request.source,
            session_id=request.session_id,
            parent_task_id=request.parent_task_id
        )
        
        return AgentMemoryResponse(
            success=True,
            data=[task.dict() for task in tasks],
            message=f"Created {len(tasks)} tasks successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch create tasks: {str(e)}")

@router.get("/agent/memory/ready", response_model=AgentMemoryResponse)
def get_ready_work(
    limit: int = Query(20, ge=1, le=100, description="Maximum items to return"),
    sort: str = Query("hybrid", description="Sort strategy: hybrid, priority, oldest"),
    category: Optional[str] = Query(None, description="Filter by category"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    priority: Optional[int] = Query(None, description="Filter by priority (0-4)")
):
    """Get ready work - tasks with no blockers (Beads bd ready pattern)"""
    
    try:
        config = ReadyWorkConfig(
            max_items=limit,
            sort_strategy=sort
        )
        
        priority_filter = TaskPriority(priority) if priority is not None else None
        
        ready_items = agent_memory.get_ready_work(
            config=config,
            category_filter=category,
            assignee_filter=assignee,
            priority_filter=priority_filter
        )
        
        return AgentMemoryResponse(
            success=True,
            data=[item.dict() for item in ready_items],
            message=f"Found {len(ready_items)} ready work items"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ready work: {str(e)}")

@router.get("/agent/memory/blocked", response_model=AgentMemoryResponse)
def get_blocked_tasks():
    """Get blocked tasks and their blockers (Beads bd blocked pattern)"""
    
    try:
        blocked_tasks = agent_memory.get_blocked_tasks()
        
        blocked_data = []
        for task, blockers in blocked_tasks:
            blocked_data.append({
                "task": task.dict(),
                "blockers": blockers,
                "blocker_count": len(blockers)
            })
        
        return AgentMemoryResponse(
            success=True,
            data=blocked_data,
            message=f"Found {len(blocked_tasks)} blocked tasks"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get blocked tasks: {str(e)}")

@router.get("/agent/memory/stats", response_model=AgentMemoryResponse)
def get_agent_memory_stats():
    """Get agent memory statistics (Beads bd stats pattern)"""
    
    try:
        stats = agent_memory.get_stats()
        
        return AgentMemoryResponse(
            success=True,
            data=stats.dict(),
            message="Agent memory statistics retrieved"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/agent/memory/task/{task_id}", response_model=AgentMemoryResponse)
def get_task(task_id: str):
    """Get specific task details (Beads bd show pattern)"""
    
    task = agent_memory.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Get task dependencies
    dependencies = []
    for dep in agent_memory.dependencies.values():
        if dep.dependent_task_id == task_id or dep.blocks_task_id == task_id:
            dependencies.append(dep.dict())
    
    return AgentMemoryResponse(
        success=True,
        data={
            "task": task.dict(),
            "dependencies": dependencies,
            "blockers": agent_memory.get_task_blockers(task_id)
        },
        message=f"Task {task_id} details retrieved"
    )

@router.put("/agent/memory/task/{task_id}", response_model=AgentMemoryResponse)
def update_task(task_id: str, request: UpdateTaskRequest):
    """Update task (Beads bd update pattern)"""
    
    try:
        task = agent_memory.update_task(
            task_id=task_id,
            status=request.status,
            priority=request.priority,
            assignee=request.assignee,
            labels=request.labels,
            context=request.context
        )
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return AgentMemoryResponse(
            success=True,
            data=task.dict(),
            message=f"Task {task_id} updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

@router.post("/agent/memory/dependency", response_model=AgentMemoryResponse)
def add_dependency(request: AddDependencyRequest):
    """Add task dependency (Beads bd dep add pattern)"""
    
    try:
        dependency = agent_memory.add_dependency(
            dependent_task_id=request.dependent_task_id,
            blocks_task_id=request.blocks_task_id,
            dependency_type=request.dependency_type,
            notes=request.notes
        )
        
        if not dependency:
            raise HTTPException(
                status_code=400, 
                detail="Failed to create dependency - check that both tasks exist"
            )
        
        return AgentMemoryResponse(
            success=True,
            data=dependency.dict(),
            message=f"Dependency created: {request.dependent_task_id} depends on {request.blocks_task_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add dependency: {str(e)}")

@router.delete("/agent/memory/dependency")
def remove_dependency(
    dependent_task_id: str = Query(..., description="Task that depends on another"),
    blocks_task_id: str = Query(..., description="Task that blocks the dependent")
):
    """Remove task dependency (Beads bd dep remove pattern)"""
    
    try:
        removed = agent_memory.remove_dependency(dependent_task_id, blocks_task_id)
        
        if not removed:
            raise HTTPException(
                status_code=404,
                detail=f"Dependency not found: {dependent_task_id} -> {blocks_task_id}"
            )
        
        return AgentMemoryResponse(
            success=True,
            data=None,
            message=f"Dependency removed: {dependent_task_id} -> {blocks_task_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove dependency: {str(e)}")

@router.get("/agent/memory/tasks", response_model=AgentMemoryResponse)
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[int] = Query(None, description="Filter by priority"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    category: Optional[str] = Query(None, description="Filter by category"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum tasks to return")
):
    """List tasks with filters (Beads bd list pattern)"""
    
    try:
        tasks = list(agent_memory.tasks.values())
        
        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        if priority is not None:
            tasks = [t for t in tasks if t.priority.value == priority]
        if assignee:
            tasks = [t for t in tasks if t.assignee == assignee]
        if category:
            tasks = [t for t in tasks if t.category == category]
        if task_type:
            tasks = [t for t in tasks if t.task_type.value == task_type]
        
        # Sort by created_at desc and limit
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        tasks = tasks[:limit]
        
        return AgentMemoryResponse(
            success=True,
            data=[task.dict() for task in tasks],
            message=f"Retrieved {len(tasks)} tasks"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")

@router.post("/agent/memory/export", response_model=AgentMemoryResponse)
def export_agent_memory():
    """Export agent memory to JSON (Beads persistence pattern)"""
    
    try:
        export_data = agent_memory.export_to_json()
        
        return AgentMemoryResponse(
            success=True,
            data=export_data,
            message="Agent memory exported successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export memory: {str(e)}")

@router.post("/agent/memory/import")
def import_agent_memory(data: Dict[str, Any] = Body(...)):
    """Import agent memory from JSON (Beads persistence pattern)"""
    
    try:
        success = agent_memory.import_from_json(data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to import agent memory")
        
        return AgentMemoryResponse(
            success=True,
            data=None,
            message="Agent memory imported successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import memory: {str(e)}")
