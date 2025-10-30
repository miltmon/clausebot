"""
Beads-inspired Agent Memory System for ClauseBot
Provides persistent memory, dependency tracking, and ready work detection
"""
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress" 
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(int, Enum):
    CRITICAL = 0  # P0 - Critical issues
    HIGH = 1      # P1 - High priority
    MEDIUM = 2    # P2 - Medium priority (default)
    LOW = 3       # P3 - Low priority
    BACKLOG = 4   # P4 - Backlog items

class TaskType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    EPIC = "epic"
    CHORE = "chore"
    CONTENT_REVIEW = "content_review"
    QUESTION_VALIDATION = "question_validation"
    AWS_UPDATE = "aws_update"

class DependencyType(str, Enum):
    BLOCKS = "blocks"           # Hard blocker - affects ready work detection
    RELATED = "related"         # Soft relationship
    PARENT_CHILD = "parent-child"  # Hierarchical
    DISCOVERED_FROM = "discovered-from"  # Found during other work

class AgentTask(BaseModel):
    """Beads-inspired task model for agent memory"""
    id: str = Field(..., description="Unique task identifier (e.g., cb-42)")
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority = TaskPriority.MEDIUM
    task_type: TaskType = TaskType.TASK
    assignee: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    
    # Beads-inspired metadata
    source: str = Field(default="agent", description="Who/what created this task")
    category: Optional[str] = None  # AWS category, question type, etc.
    clause_ref: Optional[str] = None  # AWS D1.1 clause reference
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Agent context
    session_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)

class TaskDependency(BaseModel):
    """Task dependency relationship"""
    id: str = Field(..., description="Unique dependency ID")
    dependent_task_id: str = Field(..., description="Task that depends on another")
    blocks_task_id: str = Field(..., description="Task that blocks the dependent")
    dependency_type: DependencyType = DependencyType.BLOCKS
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class ReadyWorkItem(BaseModel):
    """Task ready for work (no blockers)"""
    task: AgentTask
    ready_since: datetime
    blocking_count: int = 0  # How many tasks this would unblock
    priority_score: float = Field(..., description="Calculated priority score")

class AgentMemoryStats(BaseModel):
    """Agent memory statistics"""
    total_tasks: int
    open_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    ready_tasks: int
    completed_tasks: int
    dependencies: int
    avg_completion_time_hours: Optional[float] = None

class BatchTaskCreate(BaseModel):
    """Batch task creation from agent discovery"""
    tasks: List[Dict[str, Any]]
    source: str = "agent_discovery"
    session_id: Optional[str] = None
    parent_task_id: Optional[str] = None  # Link discovered tasks to parent

class AgentWorkSession(BaseModel):
    """Agent work session tracking"""
    session_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    tasks_created: int = 0
    tasks_completed: int = 0
    tasks_updated: int = 0
    agent_type: str = "coding_agent"
    context: Dict[str, Any] = Field(default_factory=dict)
