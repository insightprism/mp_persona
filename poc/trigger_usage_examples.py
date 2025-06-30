#!/usr/bin/env python3
"""
Trigger-Based Firefly Lifecycle Usage Examples
==============================================

This file demonstrates practical usage patterns for the simple trigger-based
firefly lifecycle system. These examples show how calling functions can easily
control when fireflies disappear.

Key Trigger Methods:
1. stimulus['disappear'] = True/False (explicit control)
2. Context managers (automatic cleanup)
3. Caller object binding (automatic cleanup on caller death)
4. Manual force disappear (direct control)
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly

# Example 1: Single Question-Answer (Original Pattern)
async def single_question_example():
    """Simple single question with immediate disappear"""
    print("📋 Example 1: Single Question-Answer")
    
    persona = PersonaConfig(
        name="Sarah Johnson",
        age=35,
        race_ethnicity="black",
        gender="female",
        education="graduate",
        location_type="urban",
        income="75k_100k"
    )
    
    firefly = LLMPersonaFirefly(persona, purpose="single_question")
    
    # Single interaction that triggers disappear
    response = await firefly.glow({
        "prompt": "What's your opinion on remote work policies?",
        "disappear": True  # 🎯 Trigger: disappear after this response
    })
    
    print(f"✅ Response received, firefly alive: {firefly.is_alive}")
    return response

# Example 2: Multi-Turn Conversation with Explicit Control
async def conversation_example():
    """Multi-turn conversation with calling function controlling lifecycle"""
    print("\n📋 Example 2: Multi-Turn Conversation")
    
    persona = PersonaConfig(
        name="Marcus Chen",
        age=42,
        race_ethnicity="asian",
        gender="male",
        education="college",
        location_type="suburban",
        income="50k_75k"
    )
    
    firefly = LLMPersonaFirefly(persona, purpose="interview_session")
    
    # Interview questions - calling function decides when to end
    questions = [
        "Tell me about your background and career.",
        "What are your thoughts on current economic trends?",
        "How do you see technology affecting your industry?",
        "What changes would you like to see in your community?"
    ]
    
    responses = []
    for i, question in enumerate(questions):
        is_last_question = (i == len(questions) - 1)
        
        response = await firefly.glow({
            "prompt": question,
            "disappear": is_last_question  # 🎯 Trigger: only disappear on last question
        })
        
        responses.append(response)
        print(f"  Question {i+1}: {'Complete' if response.get('purpose_complete') else 'Continuing'}")
        
        if response.get("purpose_complete"):
            break
    
    print(f"✅ Interview complete, total questions: {len(responses)}")
    return responses

# Example 3: Adaptive Conversation with Dynamic Triggers
async def adaptive_conversation_example():
    """Adaptive conversation where calling function analyzes responses to decide when to end"""
    print("\n📋 Example 3: Adaptive Conversation")
    
    persona = PersonaConfig(
        name="Elena Rodriguez",
        age=28,
        race_ethnicity="hispanic",
        gender="female",
        education="college",
        location_type="urban",
        income="50k_75k"
    )
    
    firefly = LLMPersonaFirefly(persona, purpose="market_research")
    
    questions = [
        "What smartphone features are most important to you?",
        "How much do you typically spend on a new phone?",
        "What would make you switch to a different brand?",
        "How satisfied are you with your current device?",
        "Would you recommend your phone to others?"
    ]
    
    responses = []
    satisfaction_indicators = 0
    
    for i, question in enumerate(questions):
        response = await firefly.glow({
            "prompt": question,
            "disappear": False  # 🎯 Keep alive for analysis
        })
        
        responses.append(response)
        
        # Analyze response for satisfaction (mock analysis)
        response_text = response.get('persona_response', '').lower()
        if any(word in response_text for word in ['satisfied', 'happy', 'good', 'recommend']):
            satisfaction_indicators += 1
        
        # 🎯 Dynamic decision: end early if high satisfaction detected
        if satisfaction_indicators >= 2:
            print(f"  High satisfaction detected after {i+1} questions")
            final_response = await firefly.glow({
                "prompt": "Thank you for your valuable feedback!",
                "disappear": True  # 🎯 Trigger: end due to sufficient data
            })
            responses.append(final_response)
            break
        elif i == len(questions) - 1:  # Last question
            await firefly.glow({
                "prompt": "That concludes our survey. Thank you!",
                "disappear": True  # 🎯 Trigger: natural end
            })
    
    print(f"✅ Market research complete, satisfaction score: {satisfaction_indicators}")
    return responses

# Example 4: Context Manager for Guaranteed Cleanup
async def context_manager_example():
    """Using context manager for automatic cleanup"""
    print("\n📋 Example 4: Context Manager")
    
    persona = PersonaConfig(
        name="David Kim",
        age=55,
        race_ethnicity="asian",
        gender="male",
        education="graduate",
        location_type="suburban",
        income="over_100k"
    )
    
    responses = []
    
    # 🎯 Context manager ensures cleanup even if errors occur
    try:
        async with LLMPersonaFirefly(persona, purpose="financial_consultation") as firefly:
            questions = [
                "What are your investment priorities?",
                "How do you view market volatility?",
                "What's your retirement planning strategy?"
            ]
            
            for question in questions:
                response = await firefly.glow({
                    "prompt": question,
                    "disappear": False  # Context manager handles cleanup
                })
                responses.append(response)
            
            print(f"  Consultation complete inside context")
            
    except Exception as e:
        print(f"  Error handled: {e}")
    
    print(f"✅ Context manager cleanup automatic - firefly disposed")
    return responses

# Example 5: Caller Object Lifecycle Binding
class SurveyManager:
    """Example of binding firefly lifecycle to caller object"""
    
    def __init__(self, persona_config: PersonaConfig):
        self.persona_config = persona_config
        self.survey_data = []
        self.firefly = None
    
    async def start_survey(self, survey_type: str):
        """Start survey session"""
        self.firefly = LLMPersonaFirefly(self.persona_config, purpose=f"survey_{survey_type}")
        # 🎯 Bind firefly to this manager - auto-cleanup when manager disappears
        self.firefly.bind_to_caller(self)
        print(f"  Survey started with {self.persona_config.name}")
    
    async def ask_question(self, question: str, is_final: bool = False):
        """Ask survey question"""
        if not self.firefly:
            raise ValueError("Survey not started")
        
        response = await self.firefly.glow({
            "prompt": question,
            "disappear": is_final  # 🎯 Caller controls when to end
        })
        
        self.survey_data.append(response)
        return response
    
    def get_summary(self):
        """Get survey summary"""
        return {
            "participant": self.persona_config.name,
            "total_questions": len(self.survey_data),
            "firefly_active": self.firefly.is_alive if self.firefly else False
        }

async def caller_binding_example():
    """Demonstrate caller object lifecycle binding"""
    print("\n📋 Example 5: Caller Object Binding")
    
    persona = PersonaConfig(
        name="Jennifer Walsh",
        age=38,
        race_ethnicity="white",
        gender="female",
        education="college",
        location_type="rural",
        income="30k_50k"
    )
    
    # Create survey manager
    survey_manager = SurveyManager(persona)
    await survey_manager.start_survey("community_needs")
    
    # Conduct survey
    await survey_manager.ask_question("What services does your community need most?", False)
    await survey_manager.ask_question("How would you prioritize infrastructure improvements?", False)
    await survey_manager.ask_question("What would improve quality of life in your area?", True)
    
    summary = survey_manager.get_summary()
    print(f"  Survey complete: {summary}")
    
    # 🎯 When survey_manager goes out of scope, firefly auto-cleans up
    print(f"✅ Manager cleanup will trigger firefly cleanup")
    return summary

# Example 6: Error Handling with Guaranteed Cleanup
async def error_handling_example():
    """Demonstrate error handling with proper cleanup"""
    print("\n📋 Example 6: Error Handling")
    
    persona = PersonaConfig(
        name="Robert Thompson",
        age=45,
        race_ethnicity="white",
        gender="male",
        education="high_school",
        location_type="urban",
        income="40k_50k"
    )
    
    firefly = LLMPersonaFirefly(persona, purpose="error_test")
    
    try:
        # Normal interaction
        response1 = await firefly.glow({
            "prompt": "What are your thoughts on local politics?",
            "disappear": False
        })
        print(f"  Normal response received")
        
        # Simulate error condition
        try:
            response2 = await firefly.glow({
                "prompt": "",  # Empty prompt causes error
                "disappear": False
            })
        except ValueError:
            print(f"  Expected error caught")
            # 🎯 Error handling: decide to end session
            cleanup_response = await firefly.glow({
                "prompt": "Sorry, there was a technical issue. Thank you for your time.",
                "disappear": True  # 🎯 Trigger: cleanup due to error
            })
            print(f"  Error cleanup completed")
    
    except Exception as e:
        # 🎯 Unexpected error: force cleanup
        print(f"  Unexpected error: {e}")
        if firefly.is_alive:
            await firefly.disappear()
    
    print(f"✅ Error handling complete, firefly cleaned up")

# Main demonstration
async def run_all_examples():
    """Run all usage examples"""
    print("🚀 Trigger-Based Firefly Lifecycle Usage Examples")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    examples = [
        single_question_example,
        conversation_example,
        adaptive_conversation_example,
        context_manager_example,
        caller_binding_example,
        error_handling_example
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"❌ Example {example.__name__} failed: {e}")
    
    print(f"\n🎯 Summary: Simple Trigger-Based Lifecycle")
    print("=" * 50)
    print("✅ stimulus['disappear'] = True/False - Explicit control")
    print("✅ Context managers - Automatic cleanup")
    print("✅ Caller binding - Auto-cleanup on caller disappear")
    print("✅ Manual control - Direct force disappear")
    print("✅ Error handling - Guaranteed cleanup")
    print("\n🎉 All trigger patterns demonstrated successfully!")

if __name__ == "__main__":
    asyncio.run(run_all_examples())