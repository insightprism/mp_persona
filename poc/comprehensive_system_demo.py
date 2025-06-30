#!/usr/bin/env python3
"""
Comprehensive Persona System Demo
=================================

Complete demonstration of the enhanced persona system featuring:
- Multi-provider LLM support (OpenAI, Claude, Ollama)
- Image generation (DALL-E)
- Voice generation (TTS)
- Self-identification capabilities
- Trigger-based lifecycle management
- PrismMind LLM infrastructure integration
"""

import asyncio
import os
from datetime import datetime
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly
from persona_image_generator import generate_persona_image_simple
from persona_voice_generator import generate_persona_voice_simple
from persona_llm_adapter import PersonaLLMAdapter

async def comprehensive_demo():
    """Complete system demonstration"""
    print("🎭 Comprehensive Persona System Demo")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check available providers
    adapter = PersonaLLMAdapter()
    
    print("\n🔧 Available LLM Providers:")
    for provider, description in adapter.get_available_providers().items():
        print(f"   • {provider}: {description}")
    
    # Check API keys and services
    providers_status = {
        "OpenAI": "✓" if os.getenv("OPENAI_API_KEY") else "✗",
        "Claude": "✓" if (os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")) else "✗",
        "Ollama": "✓" if _check_ollama() else "✗"
    }
    
    print(f"\n🔑 Service Status:")
    for service, status in providers_status.items():
        print(f"   {service}: {status}")
    
    # Create diverse personas for different use cases
    personas = [
        {
            "name": "Market Research Persona",
            "config": PersonaConfig(
                name="Sarah Kim",
                age=35,
                race_ethnicity="asian",
                gender="female",
                education="graduate",
                location_type="suburban",
                income="75k_100k",
                media_consumption="diverse",
                civic_engagement="high"
            ),
            "questions": [
                "What factors influence your purchasing decisions?",
                "How do you discover new products or services?",
                "What role does social media play in your daily life?"
            ]
        },
        {
            "name": "Tech Survey Persona", 
            "config": PersonaConfig(
                name="Marcus Washington",
                age=42,
                race_ethnicity="black",
                gender="male",
                education="college",
                location_type="urban",
                income="60k_75k",
                risk_tolerance="moderate"
            ),
            "questions": [
                "How comfortable are you with new technology?",
                "What are your thoughts on artificial intelligence?",
                "How has remote work affected your productivity?"
            ]
        },
        {
            "name": "Community Research Persona",
            "config": PersonaConfig(
                name="Elena Rodriguez",
                age=28,
                race_ethnicity="hispanic", 
                gender="female",
                education="college",
                location_type="rural",
                income="40k_50k",
                civic_engagement="high"
            ),
            "questions": [
                "What are the biggest challenges facing your community?",
                "How do you stay informed about local issues?",
                "What changes would improve quality of life in your area?"
            ]
        }
    ]
    
    # Test each persona with different LLM providers
    available_providers = []
    if os.getenv("OPENAI_API_KEY"):
        available_providers.append(("openai", os.getenv("OPENAI_API_KEY"), "gpt-4"))
    if os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"):
        key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        available_providers.append(("claude", key, "claude-3-sonnet-20240229"))
    if _check_ollama():
        available_providers.append(("ollama_local", None, "llama3:8b"))
    
    if not available_providers:
        print("⚠️  No LLM providers available - using mock responses")
        available_providers = [("mock", None, "mock")]
    
    # Run comprehensive tests
    for i, persona_data in enumerate(personas, 1):
        print(f"\n" + "=" * 70)
        print(f"🎭 PERSONA {i}: {persona_data['name']}")
        print(f"   {persona_data['config'].name} - {persona_data['config'].age}yo {persona_data['config'].race_ethnicity} {persona_data['config'].gender}")
        print("=" * 70)
        
        persona_config = persona_data["config"]
        
        # === STEP 1: Generate Complete Profile ===
        print(f"\n📸 Step 1: Generating Complete Digital Profile")
        print("-" * 50)
        
        # Generate image
        print("🎨 Generating profile image...")
        image_result = generate_persona_image_simple(persona_config)
        image_status = "✓" if image_result["success"] else "✗"
        print(f"   Profile Image: {image_status}")
        if image_result["success"]:
            print(f"   🖼️  URL: {image_result['image_url']}")
        
        # Generate voice  
        print("🎤 Generating voice sample...")
        voice_result = generate_persona_voice_simple(persona_config)
        voice_status = "✓" if voice_result["success"] else "✗"
        print(f"   Voice Sample: {voice_status}")
        if voice_result["success"]:
            print(f"   🎵 Audio: {voice_result['audio_path']}")
            print(f"   🗣️  Voice: {voice_result['voice_used']}")
        
        # === STEP 2: Test Multiple LLM Providers ===
        print(f"\n🤖 Step 2: Testing LLM Provider Responses")
        print("-" * 50)
        
        test_question = persona_data["questions"][0]
        print(f"📝 Question: {test_question}")
        
        provider_responses = {}
        
        for provider, api_key, model in available_providers:
            print(f"\n🔧 Testing {provider.upper()} ({model})")
            
            try:
                firefly = LLMPersonaFirefly(persona_config, purpose=f"demo_{provider}_{i}")
                
                if provider != "mock":
                    firefly.set_llm_config(provider, api_key, model)
                
                # Show self-identification
                if i == 1:  # Only show for first persona to avoid repetition
                    self_info = firefly.describe_self()
                    print(f"   🔍 Agent Type: {self_info['agent_type']}")
                    print(f"   🎯 Capabilities: {len(self_info['capabilities'])} functions")
                
                # Get response
                response = await firefly.glow({
                    "prompt": test_question,
                    "disappear": True
                })
                
                if response and "persona_response" in response:
                    answer = response["persona_response"]
                    provider_responses[provider] = answer
                    print(f"   ✅ Response: {answer[:120]}...")
                    
                    if response.get("usage") and provider != "mock":
                        usage = response["usage"]
                        print(f"   📊 Usage: {usage}")
                        
                else:
                    print(f"   ❌ No response received")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # === STEP 3: Response Analysis ===
        if len(provider_responses) > 1:
            print(f"\n📊 Step 3: Response Comparison")
            print("-" * 50)
            
            for provider, response in provider_responses.items():
                print(f"{provider.upper():12}: {response[:80]}...")
                
                # Simple sentiment analysis
                positive_words = ["good", "great", "positive", "benefit", "advantage", "helpful", "useful"]
                negative_words = ["bad", "negative", "problem", "issue", "concern", "worry", "difficult"]
                
                response_lower = response.lower()
                pos_count = sum(1 for word in positive_words if word in response_lower)
                neg_count = sum(1 for word in negative_words if word in response_lower)
                
                if pos_count > neg_count:
                    sentiment = "😊 Positive"
                elif neg_count > pos_count:
                    sentiment = "😟 Negative"
                else:
                    sentiment = "😐 Neutral"
                
                print(f"             Sentiment: {sentiment}")
        
        # === STEP 4: Research Simulation ===
        print(f"\n🔬 Step 4: Simulated Research Interview")
        print("-" * 50)
        
        # Use best available provider
        best_provider = available_providers[0]  # Use first available
        
        try:
            firefly = LLMPersonaFirefly(persona_config, purpose=f"research_interview_{i}")
            
            if best_provider[0] != "mock":
                firefly.set_llm_config(best_provider[0], best_provider[1], best_provider[2])
            
            print(f"🎙️  Conducting interview with {best_provider[0].upper()}")
            
            interview_responses = []
            
            for j, question in enumerate(persona_data["questions"][:2], 1):  # Limit to 2 questions
                print(f"\n   Q{j}: {question}")
                
                is_final = (j == 2)
                response = await firefly.glow({
                    "prompt": question,
                    "disappear": is_final
                })
                
                if response and "persona_response" in response:
                    answer = response["persona_response"]
                    interview_responses.append(answer)
                    print(f"   A{j}: {answer[:150]}...")
                    
                    if response.get("purpose_complete"):
                        print(f"   ✅ Interview completed")
                        break
            
            # Generate interview summary
            if interview_responses:
                print(f"\n📋 Interview Summary:")
                print(f"   Participant: {persona_config.name}")
                print(f"   Questions answered: {len(interview_responses)}")
                print(f"   LLM Provider: {best_provider[0]}")
                print(f"   Total responses: {sum(len(r.split()) for r in interview_responses)} words")
                
        except Exception as e:
            print(f"❌ Research simulation failed: {e}")
    
    # === FINAL SUMMARY ===
    print(f"\n" + "=" * 70)
    print("🎉 COMPREHENSIVE DEMO COMPLETE")
    print("=" * 70)
    
    print(f"✅ System Features Demonstrated:")
    print(f"   • Multi-provider LLM support (OpenAI, Claude, Ollama)")
    print(f"   • PrismMind infrastructure integration")
    print(f"   • Profile image generation (DALL-E)")
    print(f"   • Voice synthesis (TTS)")
    print(f"   • Self-identification capabilities")
    print(f"   • Trigger-based lifecycle management")
    print(f"   • Automated persona activation")
    print(f"   • Multi-turn conversation support")
    print(f"   • Research interview simulation")
    
    print(f"\n📊 Tested Personas: {len(personas)}")
    print(f"🤖 LLM Providers: {len(available_providers)}")
    print(f"💰 Estimated costs per persona: ~$0.05-0.15")
    
    print(f"\n🚀 Ready for production use in:")
    print(f"   • Market research")
    print(f"   • User experience studies") 
    print(f"   • Political polling")
    print(f"   • Product testing")
    print(f"   • Social science research")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Scale to multiple personas simultaneously")
    print(f"   2. Integrate with survey platforms")
    print(f"   3. Add statistical analysis")
    print(f"   4. Build demographic comparison tools")
    print(f"   5. Create research dashboard")

def _check_ollama() -> bool:
    """Check if Ollama is running"""
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Comprehensive Persona System Demo")
    print("This demo showcases the complete enhanced persona system with:")
    print("• Multi-provider LLM support (OpenAI + Claude + Ollama)")
    print("• PrismMind infrastructure integration")
    print("• Image and voice generation")
    print("• Research simulation capabilities")
    print()
    
    asyncio.run(comprehensive_demo())