import os
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import operator
import json
import re
from datetime import datetime
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables - try multiple paths
load_dotenv()  # Default behavior
load_dotenv('/app/.env')  # Explicit path in container
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  # Relative path

# Print environment status for debugging
GROQ_KEY = os.getenv("GROQ_API_KEY")
if GROQ_KEY:
    print(f"✅ GROQ_API_KEY loaded: {GROQ_KEY[:20]}...")
else:
    print("❌ GROQ_API_KEY not found!")

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
    print("✅ LangChain Groq available")
except ImportError as e:
    GROQ_AVAILABLE = False
    print(f"❌ Groq not available: {e}")

class WorkerMessageState(TypedDict):
    """State for processing worker messages"""
    messages: Annotated[List[str], operator.add]
    raw_message: str
    sender_id: int
    intent: str
    confidence: float
    entities: Dict[str, Any]
    database_action: str
    response_message: str
    requires_manager_attention: bool
    timestamp: str

# Intent patterns for quick classification - COMPREHENSIVE PATTERNS
INTENT_PATTERNS = {
    "task_update": [
        r"(completed|finished|done|complete|completing)",
        r"(started|starting|beginning|begin|working on)",
        r"(progress|update|status|advancement)",
        r"(task|work|job|assignment|project)",
        r"(material|tool|equipment|resource).*(need|require|want)",
        r"(delayed|behind|late|slow|stuck)",
        r"(on schedule|on time|ahead|early)",
        r"(almost done|nearly finished|halfway)",
        r"(repair|fix|install|build|construct)"
    ],
    "incident_report": [
        r"(incident|accident|emergency|problem|issue|trouble)",
        r"(safety|danger|hazard|risk|unsafe)",
        r"(broken|damaged|malfunction|fault|failure|not working)",
        r"(injury|hurt|injured|medical|first aid)",
        r"(leak|spill|fire|gas|smoke|explosion)",
        r"(urgent|emergency|critical|serious|help)",
        r"(pipe.*broken|pipe.*leak|water.*damage)",
        r"(electrical.*problem|power.*out|short circuit)",
        r"(security.*breach|unauthorized.*access)"
    ],
    "permission_request": [
        r"(permission|access|authorize|authorization|approval)",
        r"(overtime|extra hours|weekend work|holiday work)",
        r"(restricted|locked|secure|private|blocked)",
        r"(can i|may i|allowed to|permit|let me)",
        r"(approve|clearance|sign off)",
        r"(budget|purchase|expense|cost)",
        r"(leave|time off|vacation|sick day)"
    ],
    "attendance": [
        r"(check in|checked in|arrived|here|present|on site)",
        r"(check out|checking out|leaving|finished|going home)",
        r"(break|lunch|rest|meal)",
        r"(sick|ill|absent|leave|not coming)",
        r"(at location|reached|on site|at work)",
        r"(clocking in|clocking out|time card)",
        r"(shift.*start|shift.*end)"
    ],
    "question": [
        r"(how|what|when|where|why|help|assist)",
        r"(instruction|procedure|guideline|manual)",
        r"(don't know|not sure|confused|unclear|unsure)",
        r"(explain|clarify|understand|learn|show me)",
        r"(\?|help me|need help|assistance)",
        r"(new.*equipment|operate|use.*machine)"
    ]
}

def classify_intent_rule_based(message: str) -> tuple[str, float]:
    """Enhanced rule-based intent classification with better scoring"""
    message_lower = message.lower()
    
    intent_scores = {}
    
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        matches = 0
        
        for pattern in patterns:
            if re.search(pattern, message_lower):
                matches += 1
                # Weight longer, more specific patterns higher
                score += len(pattern.split('|')[0]) / 10  # Normalize by pattern complexity
        
        if matches > 0:
            # Calculate confidence based on matches and message relevance
            base_confidence = matches / len(patterns)
            
            # Boost confidence for very specific patterns
            if any(re.search(pattern, message_lower) for pattern in patterns):
                # Give bonus for multi-word matches that are very specific
                specific_patterns = {
                    "incident_report": ["gas leak", "pipe.*broken", "emergency", "urgent", "safety", "injury", "broken"],
                    "task_update": ["finished", "completed", "started", "progress", "need.*material"],
                    "permission_request": ["permission", "approval", "overtime", "access", "authorize"],
                    "attendance": ["check in", "check out", "arrived", "leaving", "on site"],
                    "question": ["how.*", "what.*", "help", "procedure", "unclear"]
                }
                
                for specific_pattern in specific_patterns.get(intent, []):
                    if re.search(specific_pattern, message_lower):
                        base_confidence += 0.3  # Significant boost for specific matches
                        break
            
            intent_scores[intent] = min(0.95, base_confidence)  # Cap at 95%
    
    if not intent_scores:
        return "general", 0.5
    
    best_intent = max(intent_scores, key=intent_scores.get)
    confidence = intent_scores[best_intent]
    
    return best_intent, confidence

def extract_entities(message: str, intent: str) -> Dict[str, Any]:
    """Extract relevant entities from the message"""
    entities = {}
    message_lower = message.lower()
    
    # Extract time mentions
    time_patterns = [
        r"(\d{1,2}:\d{2})",  # 14:30
        r"(morning|afternoon|evening|night)",
        r"(today|tomorrow|yesterday)",
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            entities["time_mentions"] = matches
    
    # Extract location mentions
    location_patterns = [
        r"(building|floor|room|site|area|zone)\s*([a-z0-9]+)",
        r"(basement|roof|office|warehouse|factory)"
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            entities["locations"] = [f"{match[0]} {match[1]}" if len(match) > 1 else match[0] for match in matches]
    
    # Extract equipment mentions
    equipment_patterns = [
        r"(generator|pump|valve|motor|machine|equipment|tool)",
        r"(electrical|plumbing|hvac|mechanical)"
    ]
    
    for pattern in equipment_patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            entities["equipment"] = matches
    
    # Extract urgency indicators
    urgency_patterns = [
        r"(urgent|emergency|asap|immediately|critical)",
        r"(low priority|when possible|no rush)"
    ]
    
    for pattern in urgency_patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            entities["urgency"] = matches
    
    return entities

async def llm_classify_intent(message: str) -> tuple[str, float]:
    """Enhanced LLM classification for complex cases"""
    if not GROQ_AVAILABLE or not os.getenv("GROQ_API_KEY"):
        return "general", 0.3
    
    try:
        llm = ChatGroq(
            temperature=0.1,
            model_name="llama-3.3-70b-versatile",  # Latest Llama model 
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = f"""
        You are a WorkHub AI assistant analyzing worker messages. Classify this message into the MOST APPROPRIATE category:

        CATEGORIES:
        • task_update: Work progress, completion, repairs, installations, material needs
        • incident_report: Safety issues, accidents, equipment failures, emergencies, broken items
        • permission_request: Requests for access, approval, authorization, overtime, leave
        • attendance: Check-in/out, breaks, location updates, shift changes
        • question: Asking for help, instructions, clarification, how-to questions
        • general: Casual conversation or unclear intent

        EXAMPLES:
        "pipe is broken" → incident_report|0.9
        "finished the repair" → task_update|0.9  
        "need overtime approval" → permission_request|0.9
        "checked in at site" → attendance|0.9
        "how do I use this?" → question|0.9

        Message: "{message}"
        
        Respond ONLY with: CATEGORY|CONFIDENCE (0.0-1.0)
        """
        
        response = await llm.ainvoke(prompt)
        result = response.content.strip().split('|')
        
        if len(result) == 2:
            intent = result[0].strip()
            confidence = float(result[1].strip())
            return intent, confidence
        
    except Exception as e:
        print(f"LLM classification failed: {e}")
    
    return "general", 0.3

async def intent_classifier(state: WorkerMessageState) -> Dict:
    """Advanced intent classification - prioritize LLM for accuracy"""
    message = state["raw_message"]
    
    # Try LLM first for best accuracy (when available)
    if GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
        print(f"🤖 Using LLM for primary classification...")
        llm_intent, llm_confidence = await llm_classify_intent(message)
        
        # If LLM confidence is reasonable, use it
        if llm_confidence > 0.4:
            print(f"✅ LLM classification: {llm_intent} (confidence: {llm_confidence:.2f})")
            return {
                "intent": llm_intent,
                "confidence": llm_confidence,
                "entities": extract_entities(message, llm_intent)
            }
        else:
            print(f"⚠️ LLM confidence too low ({llm_confidence:.2f}), trying rules...")
    else:
        print("🔧 Groq unavailable, using rule-based classification...")
    
    # Fallback to rule-based
    rule_intent, rule_confidence = classify_intent_rule_based(message)
    print(f"📋 Rule-based result: {rule_intent} (confidence: {rule_confidence:.2f})")
    
    return {
        "intent": rule_intent,
        "confidence": rule_confidence,
        "entities": extract_entities(message, rule_intent)
    }

def database_router(state: WorkerMessageState) -> Dict:
    """Route to appropriate database action based on intent"""
    intent = state["intent"]
    confidence = state["confidence"]
    entities = state["entities"]
    
    # Only auto-process if confidence is high enough
    auto_process = confidence > 0.6
    
    database_actions = {
        "task_update": "update_task_progress",
        "incident_report": "create_incident_record", 
        "permission_request": "create_permission_request",
        "attendance": "update_attendance_record",
        "question": "route_to_support",
        "general": "log_general_message"
    }
    
    action = database_actions.get(intent, "log_general_message")
    
    # Determine if manager attention is needed
    manager_attention = (
        intent in ["incident_report", "permission_request"] or 
        confidence < 0.5 or
        "urgent" in str(entities.get("urgency", "")).lower()
    )
    
    return {
        "database_action": action,
        "requires_manager_attention": manager_attention
    }

async def generate_llm_response(message: str, intent: str, confidence: float, entities: Dict) -> str:
    """Generate intelligent, contextual response using Groq LLM or smart fallbacks"""
    if not GROQ_AVAILABLE or not os.getenv("GROQ_API_KEY"):
        return generate_intelligent_fallback_response(message, intent, confidence, entities)
    
    try:
        llm = ChatGroq(
            temperature=0.4,  # Balanced creativity for helpful responses
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Extract context for smarter responses
        urgency = entities.get("urgency", [])
        time_mentions = entities.get("time_mentions", [])
        equipment = entities.get("equipment", [])
        locations = entities.get("locations", [])
        
        # Build intelligent context
        context_info = []
        if urgency: context_info.append(f"Urgency detected: {urgency}")
        if equipment: context_info.append(f"Equipment mentioned: {equipment}")
        if locations: context_info.append(f"Location: {locations}")
        if time_mentions: context_info.append(f"Time mentioned: {time_mentions}")
        
        context_str = " | ".join(context_info) if context_info else "Standard message"
        
        prompt = f"""
        You are WorkHub AI Assistant helping field workers. Generate a helpful, professional response.

        WORKER MESSAGE: "{message}"
        DETECTED INTENT: {intent} (confidence: {confidence:.2f})
        CONTEXT: {context_str}

        GUIDELINES:
        • Be specific to their actual message content
        • Acknowledge what action you're taking based on intent
        • Be encouraging and supportive
        • Keep it concise (1-2 sentences max)
        • Use appropriate emojis for clarity
        • Show you understand their specific situation

        RESPONSE EXAMPLES BY INTENT:
        task_update: "✅ Great work on [specific task]! I've logged your progress and updated the system."
        incident_report: "🚨 Incident recorded immediately! Manager notified. Please prioritize your safety."
        permission_request: "📋 Request submitted for approval! Your manager will review and respond soon."
        attendance: "✅ Successfully logged! Welcome to [location]. Have a productive day!"
        question: "💡 I can help with that! [specific guidance] or connecting you with the right expert."

        Generate response for: {intent}
        """
        
        response = await llm.ainvoke(prompt)
        return response.content.strip()
        
    except Exception as e:
        print(f"LLM response generation failed: {e}")
        return generate_intelligent_fallback_response(message, intent, confidence, entities)

def generate_intelligent_fallback_response(message: str, intent: str, confidence: float, entities: Dict) -> str:
    """Generate intelligent responses without LLM by analyzing the message content"""
    
    # Extract key information from the message
    message_lower = message.lower()
    urgency = entities.get("urgency", [])
    equipment = entities.get("equipment", [])
    locations = entities.get("locations", [])
    
    # Determine if urgent
    is_urgent = any(word in message_lower for word in ['urgent', 'emergency', 'critical', 'asap', 'immediately', 'help'])
    
    if intent == "incident_report":
        if 'leak' in message_lower:
            return "🚨 Gas/water leak reported! Manager and safety team notified immediately. Please evacuate the area and ensure your safety first!"
        elif 'fire' in message_lower:
            return "🔥 Fire emergency logged! Emergency services and management alerted. Please follow evacuation procedures!"
        elif 'injury' in message_lower or 'hurt' in message_lower:
            return "🏥 Injury incident recorded! First aid team and manager notified. Please seek immediate medical attention if needed."
        elif 'broken' in message_lower or 'damaged' in message_lower:
            return f"⚠️ Equipment damage reported! Maintenance team alerted. Area marked for safety - please avoid using damaged equipment."
        else:
            return "🚨 Incident documented and manager immediately notified! Please prioritize your safety and follow proper protocols."
    
    elif intent == "task_update":
        if 'finished' in message_lower or 'completed' in message_lower or 'done' in message_lower:
            return f"✅ Excellent work completing your task! Progress logged and team updated. Great job!"
        elif 'started' in message_lower or 'beginning' in message_lower:
            return f"🚀 Task start logged! Good luck with the work. Let me know if you need any assistance."
        elif 'need' in message_lower and ('material' in message_lower or 'tool' in message_lower):
            return f"📦 Material request noted! Forwarded to procurement team. You should receive an update on availability soon."
        elif 'delayed' in message_lower or 'behind' in message_lower:
            return f"⏰ Delay reported and logged. Manager notified to help resolve any issues. Keep up the good work!"
        else:
            return f"📝 Task update received and logged! Your progress is noted and team informed."
    
    elif intent == "permission_request":
        if 'overtime' in message_lower:
            return "📋 Overtime request submitted to your manager! You should receive approval status within a few hours."
        elif 'access' in message_lower or 'restricted' in message_lower:
            return "🔐 Access request forwarded to security and your manager for approval. Please wait for clearance before proceeding."
        elif 'budget' in message_lower or 'purchase' in message_lower:
            return "💼 Budget approval request sent to management. Finance team will review and respond soon."
        else:
            return "📋 Permission request submitted and forwarded to appropriate approvers! You'll receive an update shortly."
    
    elif intent == "attendance":
        if 'check in' in message_lower or 'arrived' in message_lower:
            location_text = f" at {locations[0]}" if locations else ""
            return f"✅ Successfully checked in{location_text}! Welcome to work. Have a productive and safe day!"
        elif 'check out' in message_lower or 'leaving' in message_lower:
            return f"👋 Check-out recorded! Thank you for your hard work today. Travel safely!"
        elif 'break' in message_lower or 'lunch' in message_lower:
            return f"☕ Break time logged! Enjoy your rest and remember to stay hydrated."
        else:
            return f"⏰ Attendance update recorded! Your time tracking is up to date."
    
    elif intent == "question":
        if 'how' in message_lower and ('operate' in message_lower or 'use' in message_lower):
            equipment_text = f" for {equipment[0]}" if equipment else ""
            return f"💡 Equipment operation question noted{equipment_text}! Connecting you with a technical expert or finding the manual."
        elif 'procedure' in message_lower or 'protocol' in message_lower:
            return f"📋 Procedure question logged! Sending you the relevant guidelines or connecting you with a supervisor."
        elif 'safety' in message_lower:
            return f"⛑️ Safety question is important! Forwarding to safety officer for immediate guidance. Safety first!"
        else:
            return f"❓ Question received! Getting you the right information or connecting you with someone who can help."
    
    else:  # general
        if is_urgent:
            return f"⚠️ Message marked as urgent and immediately forwarded to your manager! You should receive a response soon."
        else:
            return f"📝 Message received and logged! Appropriate team members have been notified."

async def response_generator(state: WorkerMessageState) -> Dict:
    """Generate appropriate response to worker using LLM"""
    intent = state["intent"]
    confidence = state["confidence"]
    message = state["raw_message"]
    entities = state["entities"]
    
    # Generate contextual response using LLM
    print(f"🤖 Generating LLM response for: {intent}")
    llm_response = await generate_llm_response(message, intent, confidence, entities)
    
    # Add confidence indicator for low confidence
    if confidence < 0.5:
        llm_response += "\n\n(I'm not 100% sure what you meant, so I've flagged this for manager review)"
    
    return {
        "response_message": llm_response,
        "timestamp": datetime.now().isoformat()
    }

# Create the workflow
def create_agent_workflow():
    """Create the LangGraph workflow for processing worker messages"""
    workflow = StateGraph(WorkerMessageState)
    
    # Add nodes
    workflow.add_node("classify_intent", intent_classifier)
    workflow.add_node("route_database", database_router)  
    workflow.add_node("generate_response", response_generator)
    
    # Set entry point
    workflow.set_entry_point("classify_intent")
    
    # Add edges
    workflow.add_edge("classify_intent", "route_database")
    workflow.add_edge("route_database", "generate_response") 
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()

# Create the compiled workflow
agent_app = create_agent_workflow()

async def process_worker_message(message: str, sender_id: int) -> Dict:
    """Main function to process worker messages"""
    initial_state = WorkerMessageState(
        messages=[],
        raw_message=message,
        sender_id=sender_id,
        intent="",
        confidence=0.0,
        entities={},
        database_action="",
        response_message="",
        requires_manager_attention=False,
        timestamp=""
    )
    
    result = await agent_app.ainvoke(initial_state)
    return result

# Test function 
def test_agent():
    """Test the agent with sample messages"""
    test_messages = [
        "Just finished the plumbing repair in Building A",
        "There's a gas leak in the basement - urgent!",
        "Can I get approval for overtime this weekend?", 
        "Checked in at the construction site",
        "How do I operate this new equipment?"
    ]
    
    print("🤖 Testing WorkHub Agent...")
    for msg in test_messages:
        print(f"\n📨 Message: {msg}")
        
        # Simulate processing
        intent, confidence = classify_intent_rule_based(msg)
        entities = extract_entities(msg, intent)
        
        print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")
        print(f"📋 Entities: {entities}")
        print("-" * 50)

if __name__ == "__main__":
    test_agent()
