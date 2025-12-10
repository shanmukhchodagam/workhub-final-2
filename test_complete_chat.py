#!/usr/bin/env python3
"""
Comprehensive test for AI message persistence
"""
import asyncio
import httpx
import json

async def test_complete_chat_flow():
    """Test the complete chat flow including persistence"""
    print("🧪 Testing Complete Chat Flow with Message Persistence")
    print("=" * 60)
    
    # Test message
    test_message = "There's a gas leak in building 3 - this is urgent!"
    user_id = 6  # john.worker
    
    async with httpx.AsyncClient() as client:
        
        print("Step 1: Get initial message count")
        print("-" * 30)
        
        # First get auth token (simplified for testing)
        login_response = await client.post(
            "http://localhost:8000/token",
            data={"username": "john.worker@test.com", "password": "password123"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print("Note: This is expected if user doesn't exist")
            token = None
        else:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful")
        
        # Get initial message history
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            initial_response = await client.get(
                "http://localhost:8000/my-messages",
                headers=headers
            )
            
            if initial_response.status_code == 200:
                initial_messages = initial_response.json()
                initial_count = len(initial_messages)
                print(f"📊 Initial message count: {initial_count}")
                
                # Show last few messages
                print("📚 Recent messages:")
                for msg in initial_messages[-3:]:
                    sender = msg.get('sender', 'Unknown')
                    content = msg.get('content', '')[:60] + "..."
                    print(f"   {sender}: {content}")
            else:
                print(f"⚠️  Could not get initial messages: {initial_response.status_code}")
                initial_count = 0
        else:
            print("⚠️  Skipping message history check (no auth)")
            initial_count = 0
        
        print(f"\nStep 2: Send message to AI agent")
        print("-" * 30)
        
        # Send message through AI agent
        agent_response = await client.post(
            "http://localhost:8001/process-message",
            json={
                "message": test_message,
                "sender_id": user_id,
                "chat_id": 1
            }
        )
        
        if agent_response.status_code == 200:
            result = agent_response.json()
            print(f"✅ Agent processed message:")
            print(f"   Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
            print(f"   Response: {result['response'][:80]}...")
            print(f"   Manager Alert: {result['requires_manager_attention']}")
        else:
            print(f"❌ Agent failed: {agent_response.status_code}")
            return
        
        # Wait a bit for message processing
        print(f"\n⏳ Waiting for message processing...")
        await asyncio.sleep(2)
        
        print(f"\nStep 3: Check if messages are persisted")
        print("-" * 30)
        
        if token:
            # Get updated message history
            final_response = await client.get(
                "http://localhost:8000/my-messages",
                headers=headers
            )
            
            if final_response.status_code == 200:
                final_messages = final_response.json()
                final_count = len(final_messages)
                new_messages = final_count - initial_count
                
                print(f"📊 Final message count: {final_count}")
                print(f"📈 New messages added: {new_messages}")
                
                # Look for our test message and AI response
                found_user_msg = False
                found_ai_msg = False
                
                print(f"\n🔍 Looking for our test message in last {min(10, len(final_messages))} messages:")
                for msg in final_messages[-10:]:
                    sender = msg.get('sender', 'Unknown')
                    content = msg.get('content', '')
                    timestamp = msg.get('created_at', 'No timestamp')
                    
                    print(f"   [{timestamp}] {sender}: {content[:60]}...")
                    
                    # Check for our specific test message
                    if test_message.lower() in content.lower() and sender == "Worker":
                        found_user_msg = True
                        print("     ✅ Found our test message!")
                    
                    # Check for AI response about gas leak
                    if ("AI:" in content or sender == "System") and "gas" in content.lower():
                        found_ai_msg = True
                        print("     ✅ Found AI response!")
                
                # Results
                print(f"\n🎯 PERSISTENCE TEST RESULTS:")
                print("=" * 40)
                
                if found_user_msg and found_ai_msg:
                    print("✅ SUCCESS: Both user message AND AI response are persisted!")
                    print("🎉 Message persistence is working correctly!")
                elif found_user_msg:
                    print("⚠️  PARTIAL: User message saved, but AI response missing")
                    print("🔧 AI response persistence needs fixing")
                elif found_ai_msg:
                    print("⚠️  PARTIAL: AI response found, but user message missing")  
                    print("🔧 User message persistence needs fixing")
                else:
                    print("❌ FAILED: Neither user message nor AI response found")
                    print("🔧 Message persistence is not working")
                
                if new_messages >= 2:
                    print(f"✅ Expected message count increase: {new_messages} new messages")
                elif new_messages == 1:
                    print(f"⚠️  Only 1 new message - AI response might not be saved")
                else:
                    print(f"❌ No new messages detected - persistence failed")
                    
            else:
                print(f"❌ Could not get final messages: {final_response.status_code}")
        else:
            print("⚠️  Cannot check persistence without authentication")
        
        print(f"\n📱 MANUAL TESTING:")
        print("=" * 30)
        print("🌐 Open: http://localhost:3000/worker")
        print("🔑 Login: john.worker@test.com / password123") 
        print("💬 Send message: 'Help! Equipment malfunction!'")
        print("🔄 Refresh page and check if AI response persists")
        print("✅ If AI response is still there → SUCCESS!")
        print("❌ If AI response disappears → NEEDS MORE WORK")

if __name__ == "__main__":
    asyncio.run(test_complete_chat_flow())