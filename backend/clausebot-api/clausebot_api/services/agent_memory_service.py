"""
Beads-inspired Agent Memory Service for ClauseBot
Implements ready work detection, dependency tracking, and agent memory persistence
"""
import os
import json
import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from clausebot_api.models.agent_memory import (
    AgentTask, TaskDependency, ReadyWorkItem, AgentMemoryStats,
    TaskStatus, TaskPriority, TaskType, DependencyType
)

@dataclass
class ReadyWorkConfig:
    """Configuration for ready work detection"""
    max_items: int = 20
    priority_boost_hours: int = 24  # Boost priority for old tasks
    sort_strategy: str = "hybrid"   # hybrid, priority, oldest

class AgentMemoryService:
    """Beads-inspired agent memory with ready work detection"""
    
    def __init__(self):
        self.tasks: Dict[str, AgentTask] = {}
        self.dependencies: Dict[str, TaskDependency] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        
    def _generate_task_id(self) -> str:
        """Generate ClauseBot task ID (cb-N format)"""
        task_id = f"cb-{self._next_id}"
        self._next_id += 1
        return task_id
    
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        task_type: TaskType = TaskType.TASK,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        source: str = "agent",
        category: Optional[str] = None,
        clause_ref: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentTask:
        """Create a new task (Beads-inspired)"""
        
        task_id = self._generate_task_id()
        
        task = AgentTask(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            task_type=task_type,
            assignee=assignee,
            labels=labels or [],
            source=source,
            category=category,
            clause_ref=clause_ref,
            session_id=session_id,
            context=context or {}
        )
        
        self.tasks[task_id] = task
        return task
    
    def batch_create_tasks(
        self,
        task_data: List[Dict[str, Any]],
        source: str = "agent_discovery",
        session_id: Optional[str] = None,
        parent_task_id: Optional[str] = None
    ) -> List[AgentTask]:
        """Batch create tasks from agent discovery (Beads pattern)"""
        
        created_tasks = []
        
        for data in task_data:
            task = self.create_task(
                title=data.get("title", "Discovered Task"),
                description=data.get("description"),
                priority=TaskPriority(data.get("priority", 2)),
                task_type=TaskType(data.get("task_type", "task")),
                labels=data.get("labels", []),
                source=source,
                category=data.get("category"),
                clause_ref=data.get("clause_ref"),
                session_id=session_id,
                context=data.get("context", {})
            )
            
            # Link to parent if specified (discovered-from relationship)
            if parent_task_id and parent_task_id in self.tasks:
                self.add_dependency(
                    task.id, 
                    parent_task_id, 
                    DependencyType.DISCOVERED_FROM
                )
            
            created_tasks.append(task)
        
        return created_tasks
    
    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentTask]:
        """Update task (Beads-inspired)"""
        
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        task.updated_at = datetime.utcnow()
        
        if status is not None:
            task.status = status
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
                
        if priority is not None:
            task.priority = priority
            
        if assignee is not None:
            task.assignee = assignee
            
        if labels is not None:
            task.labels = labels
            
        if context is not None:
            task.context.update(context)
        
        return task
    
    def add_dependency(
        self,
        dependent_task_id: str,
        blocks_task_id: str,
        dependency_type: DependencyType = DependencyType.BLOCKS,
        notes: Optional[str] = None
    ) -> Optional[TaskDependency]:
        """Add task dependency (Beads core feature)"""
        
        if dependent_task_id not in self.tasks or blocks_task_id not in self.tasks:
            return None
            
        dep_id = f"dep-{uuid.uuid4().hex[:8]}"
        
        dependency = TaskDependency(
            id=dep_id,
            dependent_task_id=dependent_task_id,
            blocks_task_id=blocks_task_id,
            dependency_type=dependency_type,
            notes=notes
        )
        
        self.dependencies[dep_id] = dependency
        return dependency
    
    def remove_dependency(self, dependent_task_id: str, blocks_task_id: str) -> bool:
        """Remove task dependency"""
        
        for dep_id, dep in list(self.dependencies.items()):
            if (dep.dependent_task_id == dependent_task_id and 
                dep.blocks_task_id == blocks_task_id):
                del self.dependencies[dep_id]
                return True
        return False
    
    def get_task_blockers(self, task_id: str) -> List[str]:
        """Get tasks blocking this task (Beads core algorithm)"""
        
        blockers = []
        for dep in self.dependencies.values():
            if (dep.dependent_task_id == task_id and 
                dep.dependency_type == DependencyType.BLOCKS):
                
                # Only count as blocker if blocking task is not completed
                blocking_task = self.tasks.get(dep.blocks_task_id)
                if blocking_task and blocking_task.status != TaskStatus.COMPLETED:
                    blockers.append(dep.blocks_task_id)
        
        return blockers
    
    def get_ready_work(
        self,
        config: Optional[ReadyWorkConfig] = None,
        category_filter: Optional[str] = None,
        assignee_filter: Optional[str] = None,
        priority_filter: Optional[TaskPriority] = None
    ) -> List[ReadyWorkItem]:
        """Get ready work - tasks with no blockers (Beads killer feature)"""
        
        if config is None:
            config = ReadyWorkConfig()
        
        ready_items = []
        now = datetime.utcnow()
        
        for task in self.tasks.values():
            # Skip completed/cancelled tasks
            if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                continue
                
            # Apply filters
            if category_filter and task.category != category_filter:
                continue
            if assignee_filter and task.assignee != assignee_filter:
                continue
            if priority_filter and task.priority != priority_filter:
                continue
            
            # Check if task has blockers
            blockers = self.get_task_blockers(task.id)
            if blockers:
                continue  # Task is blocked
            
            # Calculate how many tasks this would unblock
            blocking_count = sum(
                1 for dep in self.dependencies.values()
                if (dep.blocks_task_id == task.id and 
                    dep.dependency_type == DependencyType.BLOCKS and
                    self.tasks.get(dep.dependent_task_id, {}).status != TaskStatus.COMPLETED)
            )
            
            # Calculate priority score (Beads hybrid algorithm)
            priority_score = self._calculate_priority_score(task, now, config)
            
            ready_item = ReadyWorkItem(
                task=task,
                ready_since=task.created_at,
                blocking_count=blocking_count,
                priority_score=priority_score
            )
            
            ready_items.append(ready_item)
        
        # Sort by strategy
        if config.sort_strategy == "priority":
            ready_items.sort(key=lambda x: (x.task.priority.value, -x.priority_score))
        elif config.sort_strategy == "oldest":
            ready_items.sort(key=lambda x: x.task.created_at)
        else:  # hybrid (default)
            ready_items.sort(key=lambda x: -x.priority_score)
        
        return ready_items[:config.max_items]
    
    def _calculate_priority_score(
        self, 
        task: AgentTask, 
        now: datetime, 
        config: ReadyWorkConfig
    ) -> float:
        """Calculate priority score for ready work sorting (Beads algorithm)"""
        
        # Base score from priority (lower number = higher priority)
        base_score = 10 - task.priority.value * 2
        
        # Age boost - older tasks get priority boost
        age_hours = (now - task.created_at).total_seconds() / 3600
        if age_hours > config.priority_boost_hours:
            age_boost = min(5.0, age_hours / config.priority_boost_hours)
            base_score += age_boost
        
        # Type boost
        type_boost = {
            TaskType.BUG: 3.0,
            TaskType.AWS_UPDATE: 2.5,
            TaskType.CONTENT_REVIEW: 2.0,
            TaskType.FEATURE: 1.0,
            TaskType.TASK: 0.0,
            TaskType.CHORE: -1.0
        }.get(task.task_type, 0.0)
        
        base_score += type_boost
        
        return max(0.0, base_score)
    
    def get_blocked_tasks(self) -> List[Tuple[AgentTask, List[str]]]:
        """Get tasks that are blocked and their blockers"""
        
        blocked_tasks = []
        
        for task in self.tasks.values():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                continue
                
            blockers = self.get_task_blockers(task.id)
            if blockers:
                blocked_tasks.append((task, blockers))
        
        return blocked_tasks
    
    def get_stats(self) -> AgentMemoryStats:
        """Get agent memory statistics (Beads-inspired)"""
        
        total_tasks = len(self.tasks)
        status_counts = {}
        
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate average completion time
        completed_tasks = [t for t in self.tasks.values() 
                          if t.status == TaskStatus.COMPLETED and t.completed_at]
        
        avg_completion_time = None
        if completed_tasks:
            total_time = sum(
                (t.completed_at - t.created_at).total_seconds() / 3600
                for t in completed_tasks
            )
            avg_completion_time = total_time / len(completed_tasks)
        
        ready_count = len(self.get_ready_work())
        
        return AgentMemoryStats(
            total_tasks=total_tasks,
            open_tasks=status_counts.get("open", 0),
            in_progress_tasks=status_counts.get("in_progress", 0),
            blocked_tasks=len(self.get_blocked_tasks()),
            ready_tasks=ready_count,
            completed_tasks=status_counts.get("completed", 0),
            dependencies=len(self.dependencies),
            avg_completion_time_hours=avg_completion_time
        )
    
    def export_to_json(self) -> Dict[str, Any]:
        """Export agent memory to JSON (Beads JSONL pattern)"""
        
        return {
            "tasks": {k: v.dict() for k, v in self.tasks.items()},
            "dependencies": {k: v.dict() for k, v in self.dependencies.items()},
            "exported_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
    
    def import_from_json(self, data: Dict[str, Any]) -> bool:
        """Import agent memory from JSON"""
        
        try:
            # Import tasks
            for task_id, task_data in data.get("tasks", {}).items():
                self.tasks[task_id] = AgentTask(**task_data)
            
            # Import dependencies  
            for dep_id, dep_data in data.get("dependencies", {}).items():
                self.dependencies[dep_id] = TaskDependency(**dep_data)
            
            # Update next ID counter
            if self.tasks:
                max_id = max(
                    int(task_id.split("-")[1]) 
                    for task_id in self.tasks.keys() 
                    if task_id.startswith("cb-")
                )
                self._next_id = max_id + 1
            
            return True
            
        except Exception as e:
            print(f"[agent_memory] Import failed: {e}")
            return False

# Global instance (singleton pattern for now)
agent_memory = AgentMemoryService()
