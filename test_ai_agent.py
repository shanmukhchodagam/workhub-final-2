#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_ai_agent():
    """Test the AI agent with different messages to see if responses are AI-generated"""
    
    # Test messages with different intents
    test_messages = [
        "I finished fixing the plumbing in Building A",
        "There's a gas leak in the basement - this is urgent!",
        "Can I get permission to work overtime this weekend?",
        "I'm checking in at the construction site",
        "How do I operate this new welding machine?",
        "Hello, can you help me with something?"
    ]
    
    agent_url = "http://localhost:8001/process-message"
    
    print("🤖 Testing AI Agent with Groq...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for i, message in enumerate(test_messages, 1):
            print(f"\n#{i} Testing: '{message}'")
            print("-" * 40)
            
            try:
                payload = {
                    "message": message,
                    "sender_id": 6,  # john.worker@test.com
                    "chat_id": 1
                }
                
                async with session.post(agent_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
                        print(f"🤖 Response: {result['response']}")
                        print(f"⚠️  Manager Attention: {result['requires_manager_attention']}")
                    else:
                        error = await response.text()
                        print(f"❌ Error {response.status}: {error}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_agent())