#!/usr/bin/env python3
"""
Test if AI agent messages are being saved to database
"""
import asyncio
import httpx

async def test_ai_message_persistence():
    """Test that AI messages persist in chat history"""
    print("🧪 Testing AI Message Persistence")
    print("=" * 50)
    
    test_message = "There's a gas leak in the basement - urgent!"
    
    async with httpx.AsyncClient() as client:
        print(f"📤 Sending test message: '{test_message}'")
        
        # Send message to AI agent
        response = await client.post(
            "http://localhost:8001/process-message",
            json={
                "message": test_message,
                "sender_id": 6,  # Test worker
                "chat_id": 1
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Response: {result['response']}")
            print(f"🎯 Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        else:
            print(f"❌ Agent error: {response.status_code}")
            return
        
        # Small delay for database save
        await asyncio.sleep(1)
        
        # Check if messages are saved via backend API
        print(f"\n🔍 Checking message history...")
        
        # Get chat messages (assuming worker has auth token)
        # This would normally require authentication
        history_response = await client.get(
            "http://localhost:8000/my-messages",
            headers={
                "Authorization": "Bearer your_token_here"  # This would need real auth
            }
        )
        
        if history_response.status_code == 200:
            messages = history_response.json()
            print(f"📚 Found {len(messages)} messages in history:")
            
            # Check for our test message and AI response
            found_user_msg = False
            found_ai_msg = False
            
            for msg in messages[-10:]:  # Check last 10 messages
                print(f"  - {msg['sender']}: {msg['content'][:50]}...")
                if test_message in msg['content']:
                    found_user_msg = True
                if "AI:" in msg['content'] and "gas leak" in msg['content'].lower():
                    found_ai_msg = True
            
            if found_user_msg and found_ai_msg:
                print("✅ SUCCESS: Both user message and AI response found in history!")
            elif found_user_msg:
                print("⚠️  User message found, but AI response missing from history")
            else:
                print("❌ Messages not found in history")
                
        else:
            print(f"❌ Could not retrieve message history: {history_response.status_code}")
        
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("✅ If AI responses persist after page refresh → FIXED!")
    print("❌ If AI responses disappear → Still needs work")
    print("\n🌐 Test manually at: http://localhost:3000/worker")
    print("   1. Send a message to AI")  
    print("   2. Refresh the page")
    print("   3. Check if AI response is still there")

if __name__ == "__main__":
    asyncio.run(test_ai_message_persistence())