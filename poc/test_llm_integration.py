#!/usr/bin/env python3
"""
LLM Integration Test with API Keys
=================================

This script demonstrates how to use the persona firefly with real LLM APIs.
It supports OpenAI and Claude APIs with multiple ways to provide keys.

Usage Methods:
1. Environment variables
2. Command line arguments
3. Manual configuration
4. Interactive input
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly

def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Test LLM integration with persona firefly')
    
    # API configuration
    parser.add_argument('--openai-key', type=str, help='OpenAI API key')
    parser.add_argument('--claude-key', type=str, help='Claude/Anthropic API key')
    parser.add_argument('--provider', choices=['openai', 'claude', 'auto'], default='auto',
                       help='LLM provider to use (default: auto-detect)')
    
    # Test configuration
    parser.add_argument('--persona-name', type=str, default='Maria Rodriguez',
                       help='Name of the persona to create')
    parser.add_argument('--questions', type=str, nargs='+', 
                       default=["What's your opinion on remote work?", "How do you feel about technology in daily life?"],
                       help='Questions to ask the persona')
    parser.add_argument('--interactive', action='store_true',
                       help='Run interactive mode')
    
    return parser

def get_api_keys_interactive():
    """Get API keys through interactive input"""
    print("🔑 API Key Configuration")
    print("Enter your API keys (press Enter to skip):")
    
    openai_key = input("OpenAI API Key: ").strip()
    claude_key = input("Claude/Anthropic API Key: ").strip()
    
    if not openai_key and not claude_key:
        print("No API keys provided. Will use mock responses.")
        return None, None
    
    return openai_key or None, claude_key or None

def create_sample_personas():
    """Create sample personas for testing"""
    return {
        "maria": PersonaConfig(
            name="Maria Rodriguez",
            age=34,
            race_ethnicity="hispanic",
            gender="female",
            education="college",
            location_type="urban",
            income="50k_75k",
            media_consumption="npr",
            risk_tolerance="moderate",
            civic_engagement="high"
        ),
        "david": PersonaConfig(
            name="David Chen",
            age=42,
            race_ethnicity="asian",
            gender="male",
            education="graduate",
            location_type="suburban",
            income="75k_100k",
            media_consumption="diverse",
            risk_tolerance="conservative"
        ),
        "sarah": PersonaConfig(
            name="Sarah Johnson",
            age=28,
            race_ethnicity="black",
            gender="female",
            education="college",
            location_type="urban",
            income="40k_50k",
            media_consumption="social_media",
            risk_tolerance="moderate"
        )
    }

async def test_single_interaction(persona_config, questions, provider_config):
    """Test single interaction with LLM"""
    print(f"\n🎭 Testing Single Interaction: {persona_config.name}")
    print("-" * 50)
    
    firefly = LLMPersonaFirefly(persona_config, purpose="single_test")
    
    # Set LLM configuration if provided
    if provider_config:
        firefly.set_llm_config(provider_config["provider"], provider_config["api_key"])
    
    for i, question in enumerate(questions):
        print(f"\n📋 Question {i+1}: {question}")
        
        response = await firefly.glow({
            "prompt": question,
            "disappear": i == len(questions) - 1  # Disappear on last question
        })
        
        print(f"🤖 {persona_config.name} ({response.get('provider', 'unknown')}):")
        print(f"   {response['persona_response']}")
        
        if response.get("usage"):
            usage = response["usage"]
            print(f"📊 Usage: {usage}")
        
        if response.get("purpose_complete"):
            print(f"✅ Session complete: {response.get('session_summary', {})}")
            break

async def test_conversation_session(persona_config, provider_config):
    """Test multi-turn conversation session"""
    print(f"\n💬 Testing Conversation Session: {persona_config.name}")
    print("-" * 50)
    
    firefly = LLMPersonaFirefly(persona_config, purpose="conversation_test")
    
    # Set LLM configuration if provided
    if provider_config:
        firefly.set_llm_config(provider_config["provider"], provider_config["api_key"])
    
    conversation_questions = [
        "Tell me a bit about yourself and your background.",
        "What are the biggest challenges you face in your daily life?",
        "How do you see technology changing your community?",
        "What would you change about your current situation if you could?",
        "Is there anything else you'd like to share?"
    ]
    
    total_usage = {"input_tokens": 0, "output_tokens": 0}
    
    for i, question in enumerate(conversation_questions):
        print(f"\n📋 Turn {i+1}: {question}")
        
        response = await firefly.glow({
            "prompt": question,
            "disappear": i == len(conversation_questions) - 1
        })
        
        print(f"🤖 {persona_config.name}:")
        print(f"   {response['persona_response']}")
        
        # Track usage
        if response.get("usage"):
            usage = response["usage"]
            if "input_tokens" in usage:
                total_usage["input_tokens"] += usage.get("input_tokens", 0)
                total_usage["output_tokens"] += usage.get("output_tokens", 0)
        
        if response.get("purpose_complete"):
            print(f"\n📊 Total Usage: {total_usage}")
            print(f"✅ Conversation complete")
            break

async def test_adaptive_research(persona_config, provider_config):
    """Test adaptive market research scenario"""
    print(f"\n📊 Testing Adaptive Research: {persona_config.name}")
    print("-" * 50)
    
    firefly = LLMPersonaFirefly(persona_config, purpose="market_research")
    
    # Set LLM configuration if provided
    if provider_config:
        firefly.set_llm_config(provider_config["provider"], provider_config["api_key"])
    
    research_questions = [
        "What smartphone features are most important to you?",
        "How much do you typically spend on technology?",
        "What influences your purchasing decisions for tech products?",
        "How satisfied are you with your current devices?",
        "Would you recommend your current phone to friends?"
    ]
    
    satisfaction_score = 0
    responses = []
    
    for i, question in enumerate(research_questions):
        print(f"\n📋 Research Q{i+1}: {question}")
        
        response = await firefly.glow({
            "prompt": question,
            "disappear": False  # Keep alive for analysis
        })
        
        responses.append(response)
        
        print(f"🤖 {persona_config.name}:")
        print(f"   {response['persona_response']}")
        
        # Simple satisfaction analysis
        response_text = response['persona_response'].lower()
        if any(word in response_text for word in ['satisfied', 'happy', 'good', 'recommend', 'love']):
            satisfaction_score += 1
            print(f"   📈 Satisfaction indicator detected")
        
        # Adaptive decision: end early if high satisfaction
        if satisfaction_score >= 2 and i >= 2:  # At least 3 questions, high satisfaction
            print(f"\n🎯 High satisfaction detected ({satisfaction_score}/{i+1}) - ending research early")
            final_response = await firefly.glow({
                "prompt": "Thank you for your valuable feedback! Your insights are very helpful.",
                "disappear": True
            })
            print(f"🤖 {persona_config.name}:")
            print(f"   {final_response['persona_response']}")
            break
        elif i == len(research_questions) - 1:  # Last question
            await firefly.glow({
                "prompt": "That concludes our research. Thank you for your time!",
                "disappear": True
            })
    
    print(f"\n📊 Research Summary:")
    print(f"   Questions asked: {len(responses)}")
    print(f"   Satisfaction score: {satisfaction_score}/{len(responses)}")
    print(f"   Completion reason: {'Early satisfaction' if satisfaction_score >= 2 else 'All questions asked'}")

async def interactive_mode(provider_config):
    """Run interactive conversation mode"""
    print(f"\n🎮 Interactive Mode")
    print("-" * 50)
    print("Type your questions and press Enter. Type 'quit' to exit.")
    
    # Let user choose persona
    personas = create_sample_personas()
    print("\nAvailable personas:")
    for key, persona in personas.items():
        print(f"  {key}: {persona.name} ({persona.age}yo {persona.race_ethnicity} {persona.gender})")
    
    persona_choice = input("\nChoose persona (maria/david/sarah): ").strip().lower()
    if persona_choice not in personas:
        persona_choice = "maria"
    
    selected_persona = personas[persona_choice]
    print(f"\n🎭 Starting conversation with {selected_persona.name}")
    
    firefly = LLMPersonaFirefly(selected_persona, purpose="interactive_chat")
    
    # Set LLM configuration if provided
    if provider_config:
        firefly.set_llm_config(provider_config["provider"], provider_config["api_key"])
    
    conversation_count = 0
    
    while True:
        try:
            user_input = input(f"\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                # End conversation
                farewell_response = await firefly.glow({
                    "prompt": "Thank you for the conversation. Have a great day!",
                    "disappear": True
                })
                print(f"🤖 {selected_persona.name}: {farewell_response['persona_response']}")
                break
            
            if not user_input:
                continue
            
            conversation_count += 1
            
            response = await firefly.glow({
                "prompt": user_input,
                "disappear": False  # Keep conversation going
            })
            
            print(f"🤖 {selected_persona.name}: {response['persona_response']}")
            
            if response.get("usage"):
                usage = response["usage"]
                if "input_tokens" in usage:
                    print(f"📊 Tokens: {usage.get('input_tokens', 0)} in, {usage.get('output_tokens', 0)} out")
        
        except KeyboardInterrupt:
            print(f"\n\n👋 Conversation interrupted. Cleaning up...")
            if firefly.is_alive:
                await firefly.disappear()
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print(f"\n✅ Interactive session ended. Total exchanges: {conversation_count}")

async def run_llm_tests():
    """Main test runner"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    print("🚀 LLM Integration Tests for Persona Firefly")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get API keys
    openai_key = args.openai_key or os.getenv("OPENAI_API_KEY")
    claude_key = args.claude_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    
    # Interactive key input if needed
    if not openai_key and not claude_key and args.interactive:
        openai_key, claude_key = get_api_keys_interactive()
    
    # Determine provider configuration
    provider_config = None
    if args.provider == "openai" and openai_key:
        provider_config = {"provider": "openai", "api_key": openai_key}
    elif args.provider == "claude" and claude_key:
        provider_config = {"provider": "claude", "api_key": claude_key}
    elif args.provider == "auto":
        if openai_key:
            provider_config = {"provider": "openai", "api_key": openai_key}
        elif claude_key:
            provider_config = {"provider": "claude", "api_key": claude_key}
    
    if provider_config:
        print(f"🤖 Using {provider_config['provider'].upper()} API")
    else:
        print("🤖 No API keys provided - using mock responses")
        print("💡 Tip: Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
    
    # Create test personas
    personas = create_sample_personas()
    test_persona = personas.get(args.persona_name.lower().replace(" ", "").replace("rodriguez", "maria").replace("chen", "david").replace("johnson", "sarah"), personas["maria"])
    
    try:
        if args.interactive:
            await interactive_mode(provider_config)
        else:
            # Run automated tests
            await test_single_interaction(test_persona, args.questions, provider_config)
            await test_conversation_session(test_persona, provider_config)
            await test_adaptive_research(test_persona, provider_config)
        
        print(f"\n🎉 All LLM integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Install required packages reminder
    print("📦 Required packages: openai, anthropic")
    print("💡 Install with: pip install openai anthropic")
    print()
    
    asyncio.run(run_llm_tests())