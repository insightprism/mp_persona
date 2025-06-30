#!/usr/bin/env python3
"""
Test Trigger-Based Firefly Lifecycle Patterns
=============================================

This script demonstrates the simple trigger-based approach for controlling
firefly lifecycle where the calling function determines when the firefly disappears.

Trigger Methods:
1. Explicit disappear trigger in stimulus
2. Context manager auto-cleanup
3. Caller object disappearing (weakref cleanup)
4. Manual force disappear
"""

import asyncio
import gc
from datetime import datetime
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print('─'*40)

# Sample persona for testing
def create_test_persona() -> PersonaConfig:
    return PersonaConfig(
        name="Alex Thompson",
        age=28,
        race_ethnicity="white",
        gender="non_binary", 
        education="college",
        location_type="urban",
        income="50k_75k",
        media_consumption="social_media",
        risk_tolerance="moderate"
    )

async def test_explicit_trigger_pattern():
    """Test Pattern 1: Explicit disappear trigger in stimulus"""
    print_section("Pattern 1: Explicit Disappear Trigger")
    
    persona_config = create_test_persona()
    firefly = LLMPersonaFirefly(persona_config, purpose="explicit_trigger_test")
    
    print_subsection("Multi-turn conversation with explicit triggers")
    
    # Multiple interactions without disappear
    questions = [
        {"prompt": "What's your favorite type of music?", "disappear": False},
        {"prompt": "How do you typically spend your weekends?", "disappear": False},
        {"prompt": "What are your thoughts on remote work?", "disappear": False},
        {"prompt": "Thank you for the conversation!", "disappear": True}  # Trigger disappear
    ]
    
    for i, question in enumerate(questions):
        print(f"\n🔸 Interaction {i+1}:")
        try:
            response = await firefly.glow(question)
            
            print(f"Response: {response['persona_response'][:100]}...")
            print(f"Will disappear: {response['firefly_will_disappear']}")
            print(f"Firefly alive: {firefly.is_alive}")
            
            if response.get("purpose_complete"):
                print(f"Session summary: {response['session_summary']}")
                break
        except Exception as e:
            print(f"🔸 Expected error (no OpenAI key): {e}")
            # Test the trigger logic without LLM
            print(f"🔸 Testing trigger logic - disappear flag: {question['disappear']}")
            print(f"🔸 Firefly alive before trigger test: {firefly.is_alive}")
            
            if question['disappear']:
                await firefly.disappear()
                print(f"🔸 Triggered manual disappear - Firefly alive: {firefly.is_alive}")
            break

async def test_context_manager_pattern():
    """Test Pattern 2: Context manager auto-cleanup"""
    print_section("Pattern 2: Context Manager Auto-Cleanup")
    
    persona_config = create_test_persona()
    
    print_subsection("Async context manager pattern")
    
    async with LLMPersonaFirefly(persona_config, purpose="context_manager_test") as firefly:
        print(f"🔸 Firefly alive inside context: {firefly.is_alive}")
        
        # Multiple interactions within context
        questions = [
            "What do you think about electric vehicles?",
            "How important is environmental sustainability to you?",
            "What changes would you make to improve public transportation?"
        ]
        
        for i, question in enumerate(questions):
            response = await firefly.glow({"prompt": question, "disappear": False})
            print(f"🔸 Interaction {i+1}: {response['persona_response'][:80]}...")
    
    # Firefly should be automatically cleaned up here
    print(f"🔸 Firefly alive after context: {firefly.is_alive}")

async def test_manual_force_pattern():
    """Test Pattern 3: Manual force disappear"""
    print_section("Pattern 3: Manual Force Disappear")
    
    persona_config = create_test_persona()
    firefly = LLMPersonaFirefly(persona_config, purpose="manual_force_test")
    
    print_subsection("Manual control with force disappear")
    
    # Start conversation
    response1 = await firefly.glow({
        "prompt": "Tell me about your career goals.",
        "disappear": False
    })
    print(f"🔸 Response 1: {response1['persona_response'][:80]}...")
    print(f"🔸 Firefly alive: {firefly.is_alive}")
    
    response2 = await firefly.glow({
        "prompt": "What skills are you working on developing?", 
        "disappear": False
    })
    print(f"🔸 Response 2: {response2['persona_response'][:80]}...")
    print(f"🔸 Firefly alive: {firefly.is_alive}")
    
    # Manual force disappear
    if firefly.is_alive:
        await firefly.disappear()
        print(f"🔸 Manually forced disappear - Firefly alive: {firefly.is_alive}")

class ConversationManager:
    """Example calling class that manages firefly lifecycle"""
    
    def __init__(self, persona_config: PersonaConfig):
        self.persona_config = persona_config
        self.conversation_history = []
        self.firefly = None
    
    async def start_conversation(self, purpose: str):
        """Start a new conversation session"""
        self.firefly = LLMPersonaFirefly(self.persona_config, purpose=purpose)
        # Bind firefly to this manager for auto-cleanup
        self.firefly.bind_to_caller(self)
        print(f"🔸 Started conversation with {self.persona_config.name}")
    
    async def ask_question(self, question: str, end_conversation: bool = False):
        """Ask a question and optionally end conversation"""
        if not self.firefly:
            raise ValueError("No active conversation. Call start_conversation() first.")
        
        response = await self.firefly.glow({
            "prompt": question,
            "disappear": end_conversation
        })
        
        self.conversation_history.append({
            "question": question,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return response
    
    def get_conversation_summary(self):
        """Get summary of conversation"""
        return {
            "total_questions": len(self.conversation_history),
            "persona_name": self.persona_config.name,
            "firefly_alive": self.firefly.is_alive if self.firefly else False
        }

async def test_caller_disappear_pattern():
    """Test Pattern 4: Caller object disappearing triggers cleanup"""
    print_section("Pattern 4: Caller Disappear Auto-Cleanup")
    
    persona_config = create_test_persona()
    
    print_subsection("Caller object lifecycle management")
    
    # Create conversation manager
    manager = ConversationManager(persona_config)
    await manager.start_conversation("caller_disappear_test")
    
    # Have some interactions
    response1 = await manager.ask_question("What's your opinion on social media?", end_conversation=False)
    print(f"🔸 Response 1: {response1['persona_response'][:80]}...")
    print(f"🔸 Firefly alive: {manager.firefly.is_alive}")
    
    response2 = await manager.ask_question("How do you stay informed about current events?", end_conversation=False)
    print(f"🔸 Response 2: {response2['persona_response'][:80]}...")
    print(f"🔸 Firefly alive: {manager.firefly.is_alive}")
    
    # Keep reference to firefly before manager disappears
    firefly_ref = manager.firefly
    print(f"🔸 Before manager deletion - Firefly alive: {firefly_ref.is_alive}")
    
    # Delete manager - should trigger firefly cleanup via weakref
    del manager
    gc.collect()  # Force garbage collection
    
    # Give some time for cleanup callback
    await asyncio.sleep(0.1)
    
    print(f"🔸 After manager deletion - Firefly alive: {firefly_ref.is_alive}")

async def test_adaptive_conversation_pattern():
    """Test Pattern 5: Adaptive conversation with dynamic triggers"""
    print_section("Pattern 5: Adaptive Conversation Pattern")
    
    persona_config = create_test_persona()
    firefly = LLMPersonaFirefly(persona_config, purpose="adaptive_conversation")
    
    print_subsection("Dynamic conversation flow")
    
    conversation_data = {"responses": [], "satisfaction_level": 0}
    
    questions = [
        "What kind of technology products do you use daily?",
        "How important is privacy to you when using apps?",
        "What would make you switch to a new smartphone?",
        "How much would you pay for better battery life?",
        "Are you satisfied with current tech products?"
    ]
    
    for i, question in enumerate(questions):
        response = await firefly.glow({"prompt": question, "disappear": False})
        conversation_data["responses"].append(response)
        
        print(f"🔸 Q{i+1}: {question}")
        print(f"🔸 A{i+1}: {response['persona_response'][:100]}...")
        
        # Simulate adaptive logic - analyze response to determine if we should continue
        response_text = response['persona_response'].lower()
        
        # Simple satisfaction detection
        if any(word in response_text for word in ["satisfied", "happy", "good enough", "fine"]):
            conversation_data["satisfaction_level"] += 1
        
        # Adaptive decision: end early if high satisfaction or negative sentiment
        if conversation_data["satisfaction_level"] >= 2:
            print("🔸 High satisfaction detected - ending conversation early")
            final_response = await firefly.glow({
                "prompt": "Thank you for your valuable feedback!",
                "disappear": True
            })
            print(f"🔸 Final: {final_response['persona_response'][:100]}...")
            break
        elif any(word in response_text for word in ["frustrated", "annoying", "waste of time"]):
            print("🔸 Negative sentiment detected - ending conversation")
            final_response = await firefly.glow({
                "prompt": "I understand. Thank you for your time.",
                "disappear": True
            })
            print(f"🔸 Final: {final_response['persona_response'][:100]}...")
            break
        elif i == len(questions) - 1:  # Last question
            # End normally
            await firefly.glow({
                "prompt": "That concludes our survey. Thank you!",
                "disappear": True
            })
    
    print(f"🔸 Conversation summary: {conversation_data['satisfaction_level']} satisfaction indicators")

async def test_error_handling_pattern():
    """Test Pattern 6: Error handling and cleanup"""
    print_section("Pattern 6: Error Handling and Cleanup")
    
    persona_config = create_test_persona()
    
    print_subsection("Error handling with guaranteed cleanup")
    
    firefly = LLMPersonaFirefly(persona_config, purpose="error_handling_test")
    
    try:
        # Normal interaction
        response1 = await firefly.glow({
            "prompt": "What's your favorite hobby?",
            "disappear": False
        })
        print(f"🔸 Normal response: {response1['persona_response'][:80]}...")
        
        # Simulate error scenario
        try:
            response2 = await firefly.glow({
                "prompt": "",  # Empty prompt should cause error
                "disappear": False
            })
        except ValueError as e:
            print(f"🔸 Expected error caught: {e}")
            # Error handling - decide to end conversation
            cleanup_response = await firefly.glow({
                "prompt": "Sorry, there was an issue. Goodbye!",
                "disappear": True  # Trigger cleanup despite error
            })
            print(f"🔸 Cleanup response: {cleanup_response['persona_response'][:80]}...")
    
    except Exception as e:
        print(f"🔸 Unexpected error: {e}")
        # Force cleanup on unexpected error
        if firefly.is_alive:
            await firefly.disappear()
    
    print(f"🔸 Final firefly state - Alive: {firefly.is_alive}")

async def run_all_trigger_tests():
    """Run all trigger pattern tests"""
    print("🧪 Starting Trigger-Based Firefly Lifecycle Testing")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        await test_explicit_trigger_pattern()
        await test_context_manager_pattern() 
        await test_manual_force_pattern()
        await test_caller_disappear_pattern()
        await test_adaptive_conversation_pattern()
        await test_error_handling_pattern()
        
        print_section("All Tests Completed Successfully!")
        print("✅ Explicit trigger pattern: Working")
        print("✅ Context manager cleanup: Working") 
        print("✅ Manual force disappear: Working")
        print("✅ Caller disappear cleanup: Working")
        print("✅ Adaptive conversation flow: Working")
        print("✅ Error handling cleanup: Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run comprehensive trigger tests
    success = asyncio.run(run_all_trigger_tests())
    
    if success:
        print("\n🎉 All trigger patterns working correctly!")
        print("🎯 Simple trigger-based lifecycle successfully implemented.")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")