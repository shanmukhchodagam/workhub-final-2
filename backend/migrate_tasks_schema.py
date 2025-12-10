#!/usr/bin/env python3
"""
Migration script to update tasks table schema for the new task management system
"""
import asyncio
import json
from app.core.database import engine
from sqlalchemy import text

async def migrate_tasks_schema():
    print("Starting tasks table migration...")
    
    async with engine.begin() as conn:
        # 1. First, let's backup existing tasks data
        print("1. Backing up existing tasks...")
        result = await conn.execute(text("SELECT * FROM tasks"))
        existing_tasks = result.fetchall()
        print(f"   Found {len(existing_tasks)} existing tasks")
        
        # 2. Add the new columns if they don't exist
        print("2. Adding new columns...")
        
        # Add tags column (JSON array)
        try:
            await conn.execute(text("ALTER TABLE tasks ADD COLUMN tags JSON DEFAULT '[]'"))
            print("   ✓ Added tags column")
        except Exception as e:
            if "already exists" in str(e):
                print("   - tags column already exists")
            else:
                print(f"   ✗ Error adding tags column: {e}")
        
        # 3. Convert assigned_to from integer to JSON array
        print("3. Converting assigned_to column...")
        
        # Create a temporary column
        try:
            await conn.execute(text("ALTER TABLE tasks ADD COLUMN assigned_to_new JSON DEFAULT '[]'"))
            print("   ✓ Added temporary assigned_to_new column")
        except Exception as e:
            if "already exists" in str(e):
                print("   - assigned_to_new column already exists")
            else:
                print(f"   ✗ Error adding assigned_to_new column: {e}")
                return
        
        # 4. Migrate existing assigned_to values to the new format
        print("4. Migrating assigned_to values...")
        for task in existing_tasks:
            task_id = task[0]  # Assuming first column is id
            old_assigned_to = task[4]  # Based on the schema we saw earlier
            
            # Convert single user ID to array format
            if old_assigned_to is not None:
                new_assigned_to = [old_assigned_to]
            else:
                new_assigned_to = []
            
            await conn.execute(
                text("UPDATE tasks SET assigned_to_new = :assigned_to WHERE id = :id"),
                {"assigned_to": json.dumps(new_assigned_to), "id": task_id}
            )
        
        print(f"   ✓ Migrated {len(existing_tasks)} tasks")
        
        # 5. Drop old assigned_to column and rename new one
        print("5. Finalizing assigned_to column...")
        await conn.execute(text("ALTER TABLE tasks DROP COLUMN assigned_to"))
        await conn.execute(text("ALTER TABLE tasks RENAME COLUMN assigned_to_new TO assigned_to"))
        print("   ✓ Column migration complete")
        
        print("Migration completed successfully! ✅")

if __name__ == "__main__":
    asyncio.run(migrate_tasks_schema())