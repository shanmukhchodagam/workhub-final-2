from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    upcoming = "upcoming"
    ongoing = "ongoing"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"

class TaskPriority(str, Enum):
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"

class EmployeeBasic(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    team_id: int

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[List[int]] = None  # List of user IDs
    status: TaskStatus = TaskStatus.upcoming
    priority: TaskPriority = TaskPriority.normal
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @field_validator('due_date', mode='before')
    @classmethod
    def validate_due_date(cls, v):
        if v == "" or v is None:
            return None
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[List[int]] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @field_validator('due_date', mode='before')
    @classmethod
    def validate_due_date(cls, v):
        if v == "" or v is None:
            return None
        return v

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: List[int]
    assigned_by: Optional[int]
    team_id: int
    due_date: Optional[datetime]
    location: Optional[str]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TaskWithAssignees(TaskResponse):
    assigned_users: List[EmployeeBasic] = []

# Removed duplicate TaskResponse class - using the TaskWithAssignees version above

class TeamMemberResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True

class TaskStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    urgent_tasks: int
    unassigned_tasks: int