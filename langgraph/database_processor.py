import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, Any
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

class DatabaseProcessor:
    """Handles all database operations for the agent"""
    
    def __init__(self):
        # Convert DATABASE_URL to async format for SQLAlchemy
        self.db_url = os.getenv("DATABASE_URL")
        if self.db_url and self.db_url.startswith("postgresql://"):
            self.db_url = self.db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        self.engine = None
        self.async_session = None
    
    async def connect(self):
        """Connect to the database using SQLAlchemy async engine"""
        try:
            self.engine = create_async_engine(
                self.db_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            self.async_session = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.engine:
            await self.engine.dispose()
            print("📴 Disconnected from database")
    
    async def update_task_progress(self, sender_id: int, message: str, entities: Dict) -> bool:
        """Update task progress based on worker message"""
        try:
            if not self.async_session:
                await self.connect()
                
            async with self.async_session() as session:
                # Extract progress indicators
                progress_keywords = {
                    "started": 10, "begun": 15, "beginning": 10,
                    "progress": 50, "halfway": 50, "almost": 80,
                    "completed": 100, "finished": 100, "done": 100
                }
                
                progress = 0
                status = "ongoing"
                
                for keyword, value in progress_keywords.items():
                    if keyword in message.lower():
                        progress = value
                        if value == 100:
                            status = "completed"
                        break
                
                # Find active task for this worker
                task_query = text("""
                    SELECT id FROM tasks 
                    WHERE :sender_id = ANY(assigned_to) AND status IN ('upcoming', 'ongoing')
                    ORDER BY created_at DESC LIMIT 1
                """)
                
                result = await session.execute(task_query, {"sender_id": sender_id})
                task_result = result.scalar_one_or_none()
                
                if task_result:
                    # Update task
                    update_query = text("""
                        UPDATE tasks 
                        SET status = :status, updated_at = NOW()
                        WHERE id = :task_id
                    """)
                    
                    await session.execute(
                        update_query, 
                        {"status": status, "task_id": task_result}
                    )
                    await session.commit()
                    
                    print(f"✅ Updated task {task_result} - Status: {status}")
                    return True
                else:
                    print("⚠️ No active task found for worker")
                    return False
                
        except Exception as e:
            print(f"❌ Task update failed: {e}")
            return False
    
    async def create_incident_record(self, sender_id: int, message: str, entities: Dict) -> bool:
        """Create incident report from worker message"""
        try:
            if not self.async_session:
                await self.connect()
                
            async with self.async_session() as session:
                # Determine severity based on keywords
                severity_map = {
                    "emergency": "critical",
                    "urgent": "critical", 
                    "critical": "critical",
                    "serious": "high",
                    "danger": "high",
                    "safety": "high",
                    "injury": "high",
                    "fire": "critical",
                    "gas": "critical",
                    "problem": "medium",
                    "issue": "medium",
                    "broken": "medium"
                }
                
                severity = "low"
                for keyword, level in severity_map.items():
                    if keyword in message.lower():
                        severity = level
                        break
                
                # Create incident record
                insert_query = text("""
                    INSERT INTO incidents (
                        reported_by, description, severity, 
                        status, created_at
                    ) VALUES (:reported_by, :description, :severity, 'open', NOW())
                    RETURNING id
                """)
                
                result = await session.execute(
                    insert_query, 
                    {
                        "reported_by": sender_id, 
                        "description": message, 
                        "severity": severity
                    }
                )
                incident_id = result.scalar_one()
                await session.commit()
                
                print(f"🚨 Created incident #{incident_id} - Severity: {severity}")
                return True
                
        except Exception as e:
            print(f"❌ Incident creation failed: {e}")
            return False
    
    async def create_permission_request(self, sender_id: int, message: str, entities: Dict) -> bool:
        """Create permission request from worker message"""
        try:
            if not self.async_session:
                await self.connect()
                
            async with self.async_session() as session:
                # Determine request type
                message_lower = message.lower()
                
                if any(word in message_lower for word in ["overtime", "extra hours", "weekend", "holiday"]):
                    request_type = "overtime"
                    title = "Overtime Request"
                elif any(word in message_lower for word in ["vacation", "leave", "time off", "holiday"]):
                    request_type = "vacation"
                    title = "Vacation Request"
                elif any(word in message_lower for word in ["sick", "ill", "medical"]):
                    request_type = "sick_leave"
                    title = "Sick Leave Request"
                elif any(word in message_lower for word in ["access", "permission", "authorization"]):
                    request_type = "special_access"
                    title = "Special Access Request"
                else:
                    request_type = "general"
                    title = "General Permission Request"
                
                # Determine priority
                urgency = entities.get("urgency", [])
                is_urgent = any(word in ["urgent", "emergency", "asap"] for word in urgency)
                priority = "urgent" if is_urgent else "normal"
                
                # Get manager from user's team
                manager_query = text("""
                    SELECT m.id FROM users u 
                    JOIN users m ON u.team_id = m.team_id 
                    WHERE u.id = :user_id AND m.role = 'Manager' 
                    LIMIT 1
                """)
                
                result = await session.execute(manager_query, {"user_id": sender_id})
                manager_id = result.scalar_one_or_none()
                
                if not manager_id:
                    manager_id = 1  # Fallback
                
                # Insert permission request
                create_query = text("""
                    INSERT INTO permission_requests 
                    (user_id, manager_id, request_type, title, description, priority, is_urgent, status)
                    VALUES (:user_id, :manager_id, :request_type, :title, :description, :priority, :is_urgent, 'pending')
                    RETURNING id
                """)
                
                result = await session.execute(
                    create_query, 
                    {
                        "user_id": sender_id,
                        "manager_id": manager_id,
                        "request_type": request_type,
                        "title": title,
                        "description": message,
                        "priority": priority,
                        "is_urgent": is_urgent
                    }
                )
                permission_id = result.scalar_one()
                await session.commit()
                
                print(f"📋 Permission request #{permission_id}: {request_type} - {message}")
                return True
                
        except Exception as e:
            print(f"❌ Permission request failed: {e}")
            return False
    
    async def update_attendance_record(self, sender_id: int, message: str, entities: Dict) -> bool:
        """Update attendance based on worker message"""
        try:
            if not self.async_session:
                await self.connect()
                
            async with self.async_session() as session:
                # Determine attendance action
                message_lower = message.lower()
                
                if any(word in message_lower for word in ["check in", "checked in", "arrived", "here", "present"]):
                    action = "check_in"
                elif any(word in message_lower for word in ["check out", "leaving", "going home", "finished"]):
                    action = "check_out"
                elif any(word in message_lower for word in ["break", "lunch", "rest"]):
                    action = "break_start"
                elif any(word in message_lower for word in ["back", "return", "resume"]):
                    action = "break_end"
                else:
                    action = "check_in"  # default
                
                # Get or create today's attendance record
                today_query = text("""
                    SELECT id, status FROM attendance 
                    WHERE user_id = :user_id AND DATE(created_at) = CURRENT_DATE
                    ORDER BY created_at DESC LIMIT 1
                """)
                
                result = await session.execute(today_query, {"user_id": sender_id})
                existing = result.fetchone()
                
                location = entities.get("locations", [""])[0] if entities.get("locations") else ""
                
                if existing:
                    # Update existing record
                    if action == "check_in":
                        update_query = text("""
                            UPDATE attendance 
                            SET check_in_time = NOW(), status = 'present', 
                                location = :location, notes = :notes, updated_at = NOW()
                            WHERE id = :id
                        """)
                    elif action == "check_out":
                        update_query = text("""
                            UPDATE attendance 
                            SET check_out_time = NOW(), status = 'absent', 
                                notes = :notes, updated_at = NOW()
                            WHERE id = :id
                        """)
                    elif action == "break_start":
                        update_query = text("""
                            UPDATE attendance 
                            SET break_start = NOW(), status = 'on_break', 
                                notes = :notes, updated_at = NOW()
                            WHERE id = :id
                        """)
                    else:  # break_end
                        update_query = text("""
                            UPDATE attendance 
                            SET break_end = NOW(), status = 'present', 
                                notes = :notes, updated_at = NOW()
                            WHERE id = :id
                        """)
                    
                    await session.execute(
                        update_query, 
                        {
                            "id": existing.id,
                            "location": location,
                            "notes": message[:255]
                        }
                    )
                else:
                    # Create new attendance record
                    create_query = text("""
                        INSERT INTO attendance (user_id, check_in_time, status, location, notes)
                        VALUES (:user_id, NOW(), 'present', :location, :notes)
                    """)
                    
                    await session.execute(
                        create_query, 
                        {
                            "user_id": sender_id,
                            "location": location,
                            "notes": message[:255]
                        }
                    )
                
                await session.commit()
                print(f"⏰ Attendance: {action} for worker {sender_id}")
                return True
                
        except Exception as e:
            print(f"❌ Attendance update failed: {e}")
            return False
    
    async def log_general_message(self, sender_id: int, message: str, entities: Dict) -> bool:
        """Log general messages for manager review"""
        try:
            print(f"📝 General message logged from worker {sender_id}: {message}")
            # TODO: Create message log table
            return True
        except Exception as e:
            print(f"❌ Message logging failed: {e}")
            return False

# Global database processor instance
db_processor = DatabaseProcessor()

async def execute_database_action(action: str, sender_id: int, message: str, entities: Dict) -> bool:
    """Execute the appropriate database action"""
    
    if not db_processor.async_session:
        await db_processor.connect()
    
    action_map = {
        "update_task_progress": db_processor.update_task_progress,
        "create_incident_record": db_processor.create_incident_record,
        "create_permission_request": db_processor.create_permission_request,
        "update_attendance_record": db_processor.update_attendance_record,
        "log_general_message": db_processor.log_general_message
    }
    
    handler = action_map.get(action)
    if handler:
        return await handler(sender_id, message, entities)
    else:
        print(f"❌ Unknown action: {action}")
        return False

# Test function
async def test_database():
    """Test database operations"""
    await db_processor.connect()
    
    # Test task update
    await db_processor.update_task_progress(
        1, "Just finished the electrical work in Building A", 
        {"locations": ["Building A"]}
    )
    
    # Test incident creation
    await db_processor.create_incident_record(
        1, "There's a water leak in the basement - urgent!", 
        {"locations": ["basement"], "urgency": ["urgent"]}
    )
    
    await db_processor.disconnect()

if __name__ == "__main__":
    asyncio.run(test_database())