#!/usr/bin/env python3
"""
Multi-Provider LLM Integration Test
==================================

Test the enhanced persona system with Ollama, OpenAI, and Claude support
using the PrismMind LLM infrastructure.
"""

import asyncio
import os
import argparse
from datetime import datetime
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly
from persona_llm_adapter import PersonaLLMAdapter

def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Test multi-provider LLM integration')
    
    # Provider selection
    parser.add_argument('--provider', choices=['auto', 'openai', 'claude', 'ollama_local', 'ollama_host'], 
                       default='auto', help='LLM provider to use')
    parser.add_argument('--model', type=str, help='Specific model to use')
    
    # API keys
    parser.add_argument('--openai-key', type=str, help='OpenAI API key')
    parser.add_argument('--claude-key', type=str, help='Claude/Anthropic API key')
    
    # Test configuration
    parser.add_argument('--persona-name', type=str, default='Maria Rodriguez',
                       help='Name of the persona to create')
    parser.add_argument('--questions', type=str, nargs='+', 
                       default=["What's your opinion on remote work?", "How do you approach financial decisions?"],
                       help='Questions to ask the persona')
    parser.add_argument('--interactive', action='store_true',
                       help='Run interactive mode')
    
    return parser

def create_test_personas():
    """Create test personas for different scenarios"""
    return {
        "maria": PersonaConfig(
            name="Maria Rodriguez",
            age=34,
            race_ethnicity="hispanic",
            gender="female",
            education="college",
            location_type="urban",
            income="50k_75k"
        ),
        "david": PersonaConfig(
            name="David Chen",
            age=42,
            race_ethnicity="asian",
            gender="male",
            education="graduate",
            location_type="suburban",
            income="75k_100k"
        ),
        "sarah": PersonaConfig(
            name="Sarah Johnson",
            age=28,
            race_ethnicity="black",
            gender="female",
            education="college",
            location_type="urban",
            income="40k_50k"
        )
    }

async def test_provider_detection():
    """Test automatic provider detection"""
    print("🔍 Testing Provider Detection")
    print("-" * 40)
    
    adapter = PersonaLLMAdapter()
    
    print("📋 Available Providers:")
    for provider, description in adapter.get_available_providers().items():
        print(f"   • {provider}: {description}")
    
    print("\n🎯 Default Models:")
    for provider, model in adapter.get_default_models().items():
        print(f"   • {provider}: {model}")
    
    # Test Ollama availability
    persona = PersonaConfig(
        name="Test User",
        age=30,
        race_ethnicity="white",
        gender="male",
        education="college",
        location_type="urban",
        income="50k_75k"
    )
    
    firefly = LLMPersonaFirefly(persona, purpose="detection_test")
    print(f"\n🤖 Auto-detected provider: {firefly.llm_provider}")
    print(f"🎛️  Model: {firefly.llm_model}")
    print(f"🔑 API key required: {'Yes' if firefly.llm_api_key else 'No'}")

async def test_provider_comparison(persona_config, questions, api_keys):
    """Test same persona across different providers"""
    print(f"\n🔄 Testing Provider Comparison: {persona_config.name}")
    print("=" * 60)
    
    # Define test providers
    test_providers = []
    
    # Add available providers
    if api_keys.get("openai"):
        test_providers.append(("openai", api_keys["openai"], "gpt-4"))
    if api_keys.get("claude"):
        test_providers.append(("claude", api_keys["claude"], "claude-3-sonnet-20240229"))
    
    # Check for Ollama
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                test_providers.append(("ollama_local", None, "llama3:8b"))
    except:
        pass
    
    if not test_providers:
        print("⚠️  No providers available for comparison")
        return
    
    # Test each provider with the same question
    test_question = questions[0]
    print(f"📝 Test Question: {test_question}")
    
    results = {}
    
    for provider, api_key, model in test_providers:
        print(f"\n🤖 Testing {provider.upper()} ({model})")
        print("-" * 30)
        
        try:
            firefly = LLMPersonaFirefly(persona_config, purpose=f"comparison_test_{provider}")
            firefly.set_llm_config(provider, api_key, model)
            
            response = await firefly.glow({
                "prompt": test_question,
                "disappear": True
            })
            
            if response and "persona_response" in response:
                results[provider] = response["persona_response"]
                print(f"✅ Response: {response['persona_response'][:150]}...")
                
                if response.get("usage"):
                    usage = response["usage"]
                    print(f"📊 Usage: {usage}")
            else:
                print(f"❌ No response received")
                
        except Exception as e:
            print(f"❌ Provider test failed: {e}")
    
    # Compare results
    if len(results) > 1:
        print(f"\n📊 Response Comparison Summary:")
        print("=" * 40)
        for provider, response in results.items():
            print(f"{provider.upper()}: {response[:100]}...")
            print()

async def test_ollama_specific():
    """Test Ollama-specific features"""
    print(f"\n🦙 Testing Ollama-Specific Features")
    print("-" * 40)
    
    # Check if Ollama is available
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                print("⚠️  Ollama not available - skipping Ollama tests")
                return
            
            models_data = response.json()
            available_models = [model["name"] for model in models_data.get("models", [])]
            print(f"🎯 Available Ollama models: {available_models}")
            
    except Exception as e:
        print(f"⚠️  Ollama check failed: {e}")
        return
    
    # Test with different Ollama models
    test_models = ["llama3:8b", "llama3:latest", "phi3", "mistral"]
    available_test_models = [m for m in test_models if any(m in am for am in available_models)]
    
    if not available_test_models:
        print(f"ℹ️  None of the test models {test_models} are available")
        available_test_models = available_models[:2]  # Use first 2 available
    
    persona = PersonaConfig(
        name="Local Test User",
        age=25,
        race_ethnicity="white",
        gender="female",
        education="college",
        location_type="suburban",
        income="50k_75k"
    )
    
    for model in available_test_models[:2]:  # Test max 2 models
        print(f"\n🧠 Testing Ollama model: {model}")
        try:
            firefly = LLMPersonaFirefly(persona, purpose=f"ollama_test_{model.replace(':', '_')}")
            firefly.set_llm_config("ollama_local", None, model)
            
            response = await firefly.glow({
                "prompt": "Briefly introduce yourself and share one interesting opinion.",
                "disappear": True
            })
            
            if response and "persona_response" in response:
                print(f"✅ {model}: {response['persona_response'][:100]}...")
            else:
                print(f"❌ {model}: No response")
                
        except Exception as e:
            print(f"❌ {model}: Error - {e}")

async def interactive_multi_provider_mode():
    """Interactive mode with provider switching"""
    print(f"\n🎮 Interactive Multi-Provider Mode")
    print("-" * 40)
    print("Commands:")
    print("  switch <provider> - Switch LLM provider")
    print("  model <name> - Change model")
    print("  status - Show current configuration")
    print("  quit - Exit")
    print()
    
    # Setup initial persona
    persona = PersonaConfig(
        name="Interactive User",
        age=30,
        race_ethnicity="mixed",
        gender="non-binary",
        education="graduate",
        location_type="urban",
        income="75k_100k"
    )
    
    firefly = LLMPersonaFirefly(persona, purpose="interactive_multi_provider")
    
    print(f"🎭 Chatting with {persona.name}")
    print(f"🤖 Current provider: {firefly.llm_provider} ({firefly.llm_model})")
    
    while True:
        try:
            user_input = input(f"\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                if firefly.is_alive:
                    await firefly.glow({
                        "prompt": "Thank you for the conversation!",
                        "disappear": True
                    })
                break
            
            elif user_input.startswith('switch '):
                provider = user_input[7:].strip()
                try:
                    # Get API key if needed
                    api_key = None
                    if provider in ["openai"]:
                        api_key = os.getenv("OPENAI_API_KEY")
                    elif provider in ["claude", "anthropic"]:
                        api_key = os.getenv("ANTHROPIC_API_KEY")
                    
                    firefly.set_llm_config(provider, api_key)
                    print(f"🔄 Switched to {firefly.llm_provider} ({firefly.llm_model})")
                except Exception as e:
                    print(f"❌ Switch failed: {e}")
                continue
            
            elif user_input.startswith('model '):
                model = user_input[6:].strip()
                firefly.llm_model = model
                print(f"🎛️  Model changed to {model}")
                continue
            
            elif user_input == 'status':
                print(f"🤖 Provider: {firefly.llm_provider}")
                print(f"🎛️  Model: {firefly.llm_model}")
                print(f"🔑 API Key: {'Set' if firefly.llm_api_key else 'Not required'}")
                print(f"⚡ Alive: {firefly.is_alive}")
                continue
            
            elif not user_input:
                continue
            
            # Regular conversation
            response = await firefly.glow({
                "prompt": user_input,
                "disappear": False
            })
            
            if response and "persona_response" in response:
                print(f"🤖 {persona.name}: {response['persona_response']}")
                
                if response.get("usage"):
                    usage = response["usage"]
                    print(f"📊 {usage.get('input_tokens', 0)} in, {usage.get('output_tokens', 0)} out")
            else:
                print(f"❌ No response received")
        
        except KeyboardInterrupt:
            print(f"\n👋 Conversation interrupted")
            if firefly.is_alive:
                await firefly.disappear()
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def run_multi_llm_tests():
    """Main test runner"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    print("🚀 Multi-Provider LLM Integration Tests")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Collect API keys
    api_keys = {
        "openai": args.openai_key or os.getenv("OPENAI_API_KEY"),
        "claude": args.claude_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    }
    
    # Show available providers
    print("🔧 API Key Status:")
    print(f"   OpenAI: {'✓' if api_keys['openai'] else '✗'}")
    print(f"   Claude: {'✓' if api_keys['claude'] else '✗'}")
    
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            ollama_status = "✓" if response.status_code == 200 else "✗"
    except:
        ollama_status = "✗"
    print(f"   Ollama: {ollama_status}")
    
    try:
        # Run tests
        await test_provider_detection()
        
        if args.interactive:
            await interactive_multi_provider_mode()
        else:
            # Create test persona
            personas = create_test_personas()
            test_persona = personas.get(args.persona_name.lower().split()[0], personas["maria"])
            
            # Run comparison test
            await test_provider_comparison(test_persona, args.questions, api_keys)
            
            # Test Ollama features
            await test_ollama_specific()
        
        print(f"\n🎉 Multi-provider LLM tests completed!")
        print("💡 The persona system now supports:")
        print("   • OpenAI GPT models")
        print("   • Anthropic Claude models") 
        print("   • Local Ollama models")
        print("   • PrismMind LLM infrastructure")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_multi_llm_tests())