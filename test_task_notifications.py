#!/usr/bin/env python3
"""
Test task assignment notification functionality
"""
import asyncio
import aiohttp
import json

async def test_task_assignment_notification():
    """Test creating a task and sending notification to assigned user"""
    
    # Manager login credentials
    manager_email = "manager@test.com"
    manager_password = "password123"
    
    # Employee to assign task to
    employee_id = 9  # sruthi@gmail.com
    
    async with aiohttp.ClientSession() as session:
        # 1. Login as manager
        print("🔐 Logging in as manager...")
        login_data = {
            "username": manager_email,
            "password": manager_password
        }
        
        async with session.post(
            "http://localhost:8000/auth/login",
            data=login_data
        ) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result["access_token"]
                print(f"✅ Manager login successful")
            else:
                print(f"❌ Manager login failed: {response.status}")
                return
        
        # 2. Create a task assigned to the employee
        print(f"📋 Creating task assigned to employee {employee_id}...")
        
        task_data = {
            "title": "Test Notification Task",
            "description": "This is a test task to verify assignment notifications work correctly.",
            "status": "upcoming",
            "priority": "normal",
            "assigned_to": [employee_id],
            "location": "Building A - Room 101",
            "estimated_hours": 2.5,
            "due_date": "2025-12-10",
            "tags": ["test", "notification"]
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with session.post(
            "http://localhost:8000/tasks/",
            json=task_data,
            headers=headers
        ) as response:
            if response.status == 200:
                task_result = await response.json()
                print(f"✅ Task created successfully!")
                print(f"   Task ID: {task_result['id']}")
                print(f"   Title: {task_result['title']}")
                print(f"   Assigned to: {task_result['assigned_to']}")
                print(f"\n🔔 Notification should have been sent to employee {employee_id}")
                
                # 3. Update the task to test update notifications
                print(f"\n📝 Updating task to test update notifications...")
                
                update_data = {
                    "description": "Updated description to test notification system",
                    "priority": "high"
                }
                
                async with session.put(
                    f"http://localhost:8000/tasks/{task_result['id']}",
                    json=update_data,
                    headers=headers
                ) as update_response:
                    if update_response.status == 200:
                        print(f"✅ Task updated successfully!")
                        print(f"🔔 Update notification should have been sent to employee {employee_id}")
                    else:
                        print(f"❌ Task update failed: {update_response.status}")
                        
            else:
                error_text = await response.text()
                print(f"❌ Task creation failed: {response.status}")
                print(f"Error: {error_text}")

if __name__ == "__main__":
    print("🧪 Testing Task Assignment Notification System")
    print("=" * 50)
    asyncio.run(test_task_assignment_notification())
    print("=" * 50)
    print("🎯 Test completed!")
    print("\n📱 To verify notifications:")
    print("1. Login as sruthi@gmail.com / password123")
    print("2. Go to worker chat interface")
    print("3. Check for task assignment notifications")