from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete
from typing import List, Optional
from datetime import datetime, date
from app.core.database import get_db, AsyncSessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.message import Message
from app.models.chat_session import ChatSession
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate, TaskWithAssignees
from app.routers.auth import get_current_user
from app.core.websocket import manager
from app.services.email_service import email_service
from pydantic import BaseModel
import logging
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

# Redis client for notifications
redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

async def send_task_assignment_notification(
    worker_id: int, 
    task: Task, 
    assigner_name: str,
    action: str = "assigned"
):
    """Send a notification to the worker about task assignment"""
    try:
        async with AsyncSessionLocal() as db:
            # Get worker info
            worker_query = select(User).where(User.id == worker_id)
            worker_result = await db.execute(worker_query)
            worker = worker_result.scalar_one_or_none()
            
            if not worker:
                logger.error(f"Worker {worker_id} not found")
                return
            
            # Find or create chat session for this worker
            chat_query = select(ChatSession).where(
                ChatSession.user_id == worker_id,
                ChatSession.team_id == worker.team_id
            ).order_by(ChatSession.created_at.desc())
            
            chat_result = await db.execute(chat_query)
            chat_session = chat_result.scalars().first()
            
            if not chat_session:
                chat_session = ChatSession(user_id=worker_id, team_id=worker.team_id)
                db.add(chat_session)
                await db.commit()
                await db.refresh(chat_session)
            
            # Create notification message based on action
            if action == "assigned":
                emoji = "📋"
                action_text = "assigned to"
            elif action == "updated":
                emoji = "✏️"
                action_text = "updated in"
            else:
                emoji = "ℹ️"
                action_text = "modified in"
            
            # Build notification message
            notification_text = f"{emoji} **Task {action_text.upper()}** by {assigner_name}\n\n"
            notification_text += f"**Task:** {task.title}\n"
            if task.description:
                notification_text += f"**Description:** {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            notification_text += f"**Priority:** {task.priority.title()}\n"
            notification_text += f"**Status:** {task.status.title()}\n"
            
            if task.due_date:
                notification_text += f"**Due Date:** {task.due_date.strftime('%Y-%m-%d')}\n"
            
            if task.location:
                notification_text += f"**Location:** {task.location}\n"
            
            if task.estimated_hours:
                notification_text += f"**Estimated Hours:** {task.estimated_hours}h\n"
            
            notification_text += f"\n*Task created: {task.created_at.strftime('%Y-%m-%d %H:%M')}*"
            
            # Save notification as a chat message
            notification_message = Message(
                content=notification_text,
                chat_id=chat_session.id,
                sender="System"  # System message to differentiate from regular chat
            )
            db.add(notification_message)
            await db.commit()
            
            # Send real-time notification via WebSocket if worker is connected
            await manager.send_to_worker(worker_id, f"🔔 Task Assignment: {notification_text}")
            
            # Also publish via Redis for real-time updates
            await redis_client.publish(
                f"chat_{chat_session.id}", 
                f"🤖 System: {notification_text}"
            )
            
            logger.info(f"Task assignment notification sent to worker {worker_id} for task {task.id}")
            
    except Exception as e:
        logger.error(f"Failed to send task assignment notification to worker {worker_id}: {e}")

class TaskStatusUpdate(BaseModel):
    status: str

@router.get("/", response_model=List[TaskWithAssignees])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
):
    """Get tasks with filters for the current user's team"""
    try:
        # Build query for tasks in the current user's team
        query = select(Task).where(Task.team_id == current_user.team_id)
        
        # Apply filters
        if status:
            query = query.where(Task.status == status)
        if assigned_to:
            # This will need to be updated when we implement many-to-many assignment
            query = query.where(Task.assigned_to.contains([assigned_to]))
        if priority:
            query = query.where(Task.priority == priority)
        if date_from:
            query = query.where(Task.due_date >= date_from)
        if date_to:
            query = query.where(Task.due_date <= date_to)
            
        query = query.order_by(Task.created_at.desc())
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # Get assignee information for each task
        tasks_with_assignees = []
        for task in tasks:
            # Get assigned users
            if task.assigned_to:
                assigned_users_query = select(User).where(
                    User.id.in_(task.assigned_to)
                )
                assigned_result = await db.execute(assigned_users_query)
                assigned_users = assigned_result.scalars().all()
                
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assigned_to": task.assigned_to,
                    "assigned_by": task.assigned_by,
                    "team_id": task.team_id,
                    "due_date": task.due_date,
                    "location": task.location,
                    "estimated_hours": task.estimated_hours,
                    "actual_hours": task.actual_hours,
                    "tags": task.tags,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                    "assigned_users": [
                        {
                            "id": user.id,
                            "email": user.email,
                            "full_name": user.full_name,
                            "role": user.role,
                            "team_id": user.team_id
                        }
                        for user in assigned_users
                    ]
                }
                tasks_with_assignees.append(task_dict)
        
        return tasks_with_assignees
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    try:
        # Verify assigned users are in the same team
        if task_data.assigned_to:
            assigned_users_query = select(User).where(
                User.id.in_(task_data.assigned_to),
                User.team_id == current_user.team_id
            )
            assigned_result = await db.execute(assigned_users_query)
            assigned_users = assigned_result.scalars().all()
            
            if len(assigned_users) != len(task_data.assigned_to):
                raise HTTPException(
                    status_code=400, 
                    detail="Some assigned users are not in your team"
                )
        
        # Create task
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            assigned_to=task_data.assigned_to or [],
            assigned_by=current_user.id,
            team_id=current_user.team_id,
            due_date=task_data.due_date,
            location=task_data.location,
            estimated_hours=task_data.estimated_hours,
            tags=task_data.tags
        )
        
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        
        # Send notifications to assigned users
        if new_task.assigned_to:
            for user_id in new_task.assigned_to:
                await send_task_assignment_notification(
                    user_id, 
                    new_task, 
                    current_user.full_name or current_user.email,
                    "assigned"
                )
                
                # Send email notification to assigned user
                try:
                    # Get user info for email
                    user_query = select(User).where(User.id == user_id)
                    user_result = await db.execute(user_query)
                    assigned_user = user_result.scalar_one_or_none()
                    
                    if assigned_user:
                        due_date_str = new_task.due_date.strftime("%Y-%m-%d") if new_task.due_date else "No deadline set"
                        
                        await email_service.send_task_assignment_email(
                            employee_email=assigned_user.email,
                            employee_name=assigned_user.full_name or assigned_user.email.split('@')[0],
                            task_title=new_task.title,
                            task_description=new_task.description or "No description provided",
                            due_date=due_date_str,
                            assigned_by=current_user.full_name or current_user.email.split('@')[0]
                        )
                        print(f"✅ Task assignment email sent to: {assigned_user.email}")
                        
                except Exception as email_error:
                    print(f"⚠️ Failed to send task assignment email to user {user_id}: {email_error}")
                    # Don't fail the task creation if email fails
        
        return TaskResponse(
            id=new_task.id,
            title=new_task.title,
            description=new_task.description,
            status=new_task.status,
            priority=new_task.priority,
            assigned_to=new_task.assigned_to,
            assigned_by=new_task.assigned_by,
            team_id=new_task.team_id,
            due_date=new_task.due_date,
            location=new_task.location,
            estimated_hours=new_task.estimated_hours,
            actual_hours=new_task.actual_hours,
            tags=new_task.tags,
            created_at=new_task.created_at,
            updated_at=new_task.updated_at
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")

@router.get("/{task_id}", response_model=TaskWithAssignees)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.team_id == current_user.team_id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get assigned users
    assigned_users = []
    if task.assigned_to:
        assigned_users_query = select(User).where(
            User.id.in_(task.assigned_to)
        )
        assigned_result = await db.execute(assigned_users_query)
        assigned_users = [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "team_id": user.team_id
            }
            for user in assigned_result.scalars().all()
        ]
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assigned_to": task.assigned_to,
        "assigned_by": task.assigned_by,
        "team_id": task.team_id,
        "due_date": task.due_date,
        "location": task.location,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "tags": task.tags,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assigned_users": assigned_users
    }

@router.put("/{task_id}", response_model=TaskWithAssignees)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    # Get existing task
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.team_id == current_user.team_id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Store original assigned_to for comparison
    original_assigned_to = task.assigned_to or []
    
    # Update fields that are provided
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Verify assigned users if provided
    if "assigned_to" in update_data and update_data["assigned_to"]:
        assigned_users_query = select(User).where(
            User.id.in_(update_data["assigned_to"]),
            User.team_id == current_user.team_id
        )
        assigned_result = await db.execute(assigned_users_query)
        assigned_users = assigned_result.scalars().all()
        
        if len(assigned_users) != len(update_data["assigned_to"]):
            raise HTTPException(
                status_code=400, 
                detail="Some assigned users are not in your team"
            )
    
    # Update the task
    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(**update_data)
    )
    
    await db.commit()
    await db.refresh(task)
    
    # Send notifications for assignment changes
    if "assigned_to" in update_data:
        new_assigned_to = task.assigned_to or []
        
        # Find newly assigned users
        newly_assigned = set(new_assigned_to) - set(original_assigned_to)
        
        # Send notifications to newly assigned users
        for user_id in newly_assigned:
            await send_task_assignment_notification(
                user_id, 
                task, 
                current_user.full_name or current_user.email,
                "assigned"
            )
        
        # Send update notifications to previously assigned users who are still assigned
        still_assigned = set(new_assigned_to) & set(original_assigned_to)
        for user_id in still_assigned:
            await send_task_assignment_notification(
                user_id, 
                task, 
                current_user.full_name or current_user.email,
                "updated"
            )
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assigned_to=task.assigned_to,
        assigned_by=task.assigned_by,
        team_id=task.team_id,
        due_date=task.due_date,
        location=task.location,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        tags=task.tags,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.patch("/{task_id}/status")
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update only the status of a task (for drag and drop)"""
    # Validate status
    valid_statuses = ["upcoming", "ongoing", "completed"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Update task status
    result = await db.execute(
        update(Task)
        .where(
            Task.id == task_id,
            Task.team_id == current_user.team_id
        )
        .values(
            status=status_update.status,
            completed_at=datetime.utcnow() if status_update.status == "completed" else None,
            started_at=datetime.utcnow() if status_update.status == "ongoing" else Task.started_at
        )
    )
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.commit()
    return {"message": "Task status updated successfully"}

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task"""
    result = await db.execute(
        delete(Task).where(
            Task.id == task_id,
            Task.team_id == current_user.team_id
        )
    )
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.commit()
    return {"message": "Task deleted successfully"}

@router.get("/stats/dashboard", response_model=dict)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics for the current team"""
    try:
        team_id = current_user.team_id
        
        # Get task statistics
        pending_tasks_query = select(Task).where(
            Task.team_id == team_id,
            Task.status.in_(["upcoming", "pending"])
        )
        pending_result = await db.execute(pending_tasks_query)
        pending_tasks = len(pending_result.scalars().all())
        
        ongoing_tasks_query = select(Task).where(
            Task.team_id == team_id,
            Task.status == "ongoing"
        )
        ongoing_result = await db.execute(ongoing_tasks_query)
        ongoing_tasks = len(ongoing_result.scalars().all())
        
        completed_tasks_query = select(Task).where(
            Task.team_id == team_id,
            Task.status == "completed"
        )
        completed_result = await db.execute(completed_tasks_query)
        completed_tasks = len(completed_result.scalars().all())
        
        # Get active workers (employees with recent activity)
        from app.models.user import User as UserModel
        active_workers_query = select(UserModel).where(
            UserModel.team_id == team_id,
            UserModel.role == "Employee"
        )
        active_result = await db.execute(active_workers_query)
        active_workers = len(active_result.scalars().all())
        
        # Get incidents count (by reported_by user's team)
        from app.models.incident import Incident
        incidents_query = select(Incident).join(User, Incident.reported_by == User.id).where(
            User.team_id == team_id,
            Incident.status != "resolved"
        )
        incidents_result = await db.execute(incidents_query)
        incidents = len(incidents_result.scalars().all())
        
        return {
            "activeWorkers": active_workers,
            "pendingTasks": pending_tasks,
            "ongoingTasks": ongoing_tasks,
            "completedTasks": completed_tasks,
            "incidents": incidents,
            "totalTasks": pending_tasks + ongoing_tasks + completed_tasks
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard statistics")

@router.get("/team/employees", response_model=List[dict])
async def get_team_employees(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all employees in the current user's team for task assignment"""
    result = await db.execute(
        select(User).where(
            User.team_id == current_user.team_id,
            User.role == "Employee"
        ).order_by(User.full_name)
    )
    employees = result.scalars().all()
    
    return [
        {
            "id": emp.id,
            "email": emp.email,
            "full_name": emp.full_name,
            "role": emp.role,
            "team_id": emp.team_id
        }
        for emp in employees
    ]
