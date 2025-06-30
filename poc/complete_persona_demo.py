#!/usr/bin/env python3
"""
Complete Persona System Demo
============================

Demonstrates the full persona system with:
- LLM text responses
- Image generation 
- Voice generation
- Self-identification capabilities
- Trigger-based lifecycle
"""

import asyncio
import os
from datetime import datetime
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly
from persona_image_generator import generate_persona_image_simple
from persona_voice_generator import generate_persona_voice_simple

async def complete_persona_demo():
    """Complete demonstration of all persona capabilities"""
    print("🎭 Complete Persona System Demo")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("🔑 OpenAI API key found - using real APIs")
        print("💰 Using cost-optimized settings")
    else:
        print("⚠️  No API key - using mock responses")
        print("💡 Set OPENAI_API_KEY to use real APIs")
    
    # Create sample persona
    persona = PersonaConfig(
        name="Sarah Chen",
        age=35,
        race_ethnicity="asian",
        gender="female",
        education="graduate",
        location_type="urban",
        income="75k_100k",
        media_consumption="diverse",
        risk_tolerance="moderate",
        civic_engagement="high"
    )
    
    print(f"\n👤 Creating complete persona profile for: {persona.name}")
    print(f"   Demographics: {persona.age}yo {persona.race_ethnicity} {persona.gender}")
    print(f"   Background: {persona.education} education, {persona.location_type}, {persona.income}")
    
    try:
        # === STEP 1: Generate Persona Image ===
        print(f"\n🎨 Step 1: Generating Profile Image")
        print("-" * 40)
        
        image_result = generate_persona_image_simple(persona, api_key)
        
        if image_result["success"]:
            print(f"✅ Profile image generated!")
            print(f"🖼️  Image URL: {image_result['image_url']}")
            print(f"📝 Image prompt: {image_result['prompt']}")
            if image_result.get("model") == "dall-e-2":
                print(f"💰 Image cost: ~$0.02")
        else:
            print(f"❌ Image generation failed: {image_result['error']}")
        
        # === STEP 2: Generate Persona Voice ===
        print(f"\n🎤 Step 2: Generating Voice Sample")
        print("-" * 40)
        
        voice_result = generate_persona_voice_simple(persona, api_key)
        
        if voice_result["success"]:
            print(f"✅ Voice sample generated!")
            print(f"🎵 Audio file: {voice_result['audio_path']}")
            print(f"🗣️  Voice: {voice_result['voice_used']} - {voice_result['voice_characteristics']}")
            print(f"📝 Script preview: {voice_result['script_text'][:100]}...")
            if voice_result.get("model") == "tts-1":
                cost = len(voice_result['script_text']) * 0.000015
                print(f"💰 Voice cost: ~${cost:.4f}")
        else:
            print(f"❌ Voice generation failed: {voice_result['error']}")
        
        # === STEP 3: Create Interactive Persona ===
        print(f"\n🧠 Step 3: Creating Interactive LLM Persona")
        print("-" * 40)
        
        firefly = LLMPersonaFirefly(persona, purpose="complete_demo")
        
        # Set API config if available
        if api_key:
            firefly.set_llm_config("openai", api_key)
        
        # Show self-identification capabilities
        print(f"🔍 Persona Self-Identification:")
        capabilities = firefly.describe_capabilities()
        print(f"   Available functions: {len(capabilities)}")
        
        self_desc = firefly.describe_self()
        print(f"   Agent type: {self_desc['agent_type']}")
        print(f"   Firefly ID: {self_desc['firefly_metadata']['firefly_id'][:8]}...")
        
        # === STEP 4: Interactive Demo Questions ===
        print(f"\n💬 Step 4: Interactive Q&A Session")
        print("-" * 40)
        
        demo_questions = [
            "Tell me about your background and what's important to you.",
            "What's your opinion on remote work and technology in the workplace?",
            "How do you approach financial decisions and investments?",
            "What changes would you like to see in your community?"
        ]
        
        total_llm_cost = 0
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n📋 Question {i}: {question}")
            
            is_final = (i == len(demo_questions))
            
            try:
                response = await firefly.glow({
                    "prompt": question,
                    "disappear": is_final  # Trigger disappear on last question
                })
                
                print(f"🤖 {persona.name}: {response['persona_response']}")
                
                # Track usage and cost
                if response.get("usage") and api_key:
                    usage = response["usage"]
                    if "input_tokens" in usage:
                        input_cost = usage.get("input_tokens", 0) * 0.00003
                        output_cost = usage.get("output_tokens", 0) * 0.00006
                        total_llm_cost += input_cost + output_cost
                        print(f"📊 Tokens: {usage.get('input_tokens', 0)} in, {usage.get('output_tokens', 0)} out")
                
                if response.get("purpose_complete"):
                    print(f"✅ Demo session completed - firefly disappeared")
                    break
                    
            except Exception as e:
                print(f"❌ LLM interaction failed: {e}")
                if firefly.is_alive:
                    await firefly.disappear()
                break
        
        # === STEP 5: Summary ===
        print(f"\n🎯 Demo Summary")
        print("=" * 60)
        print(f"✅ Profile image: {'Generated' if image_result['success'] else 'Failed'}")
        print(f"✅ Voice sample: {'Generated' if voice_result['success'] else 'Failed'}")
        print(f"✅ LLM interaction: {len(demo_questions)} questions answered")
        print(f"✅ Firefly lifecycle: Completed and cleaned up")
        
        if api_key:
            total_cost = 0.02 + (len(voice_result['script_text']) * 0.000015) + total_llm_cost
            print(f"\n💰 Total estimated cost: ~${total_cost:.4f}")
            print(f"   • Image (DALL-E 2): ~$0.02")
            print(f"   • Voice (TTS-1): ~${len(voice_result['script_text']) * 0.000015:.4f}")
            print(f"   • LLM (GPT-4): ~${total_llm_cost:.4f}")
        
        print(f"\n📁 Generated files:")
        if image_result['success']:
            print(f"   🖼️  {image_result['image_url']}")
        if voice_result['success']:
            print(f"   🎵 {voice_result['audio_path']}")
        
        print(f"\n🚀 Complete persona profile created for {persona.name}!")
        print("   Ready for market research, behavioral analysis, and user studies.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

async def quick_persona_creation(name: str, age: int, demographics: dict):
    """Quick function to create a complete persona profile"""
    print(f"\n⚡ Quick Persona Creation: {name}")
    print("-" * 30)
    
    # Create persona config
    persona = PersonaConfig(
        name=name,
        age=age,
        **demographics
    )
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Generate all assets
    tasks = []
    
    # Image generation
    print(f"🎨 Generating image...")
    image_result = generate_persona_image_simple(persona, api_key)
    
    # Voice generation
    print(f"🎤 Generating voice...")
    voice_result = generate_persona_voice_simple(persona, api_key)
    
    # Create firefly for capabilities
    firefly = LLMPersonaFirefly(persona, purpose="quick_creation")
    if api_key:
        firefly.set_llm_config("openai", api_key)
    
    print(f"✅ {name} persona created!")
    print(f"   Image: {'✓' if image_result['success'] else '✗'}")
    print(f"   Voice: {'✓' if voice_result['success'] else '✗'}")
    print(f"   LLM: {'✓' if firefly else '✗'}")
    
    return {
        "persona": persona,
        "image": image_result,
        "voice": voice_result,
        "firefly": firefly
    }

if __name__ == "__main__":
    print("🚀 Persona System - Complete Demo")
    print("This demo showcases the full persona generation pipeline:")
    print("• Demographics → Image → Voice → Interactive LLM")
    print()
    
    # Run complete demo
    asyncio.run(complete_persona_demo())
    
    # Show quick creation examples
    print(f"\n" + "=" * 60)
    print("⚡ Quick Persona Creation Examples")
    
    # Example personas for different use cases
    examples = [
        ("Market Research", "Jennifer Walsh", 42, {
            "race_ethnicity": "white", 
            "gender": "female",
            "education": "college",
            "location_type": "rural",
            "income": "30k_50k"
        }),
        ("Tech Survey", "Alex Rivera", 28, {
            "race_ethnicity": "hispanic",
            "gender": "non-binary", 
            "education": "college",
            "location_type": "urban",
            "income": "50k_75k"
        })
    ]
    
    for use_case, name, age, demographics in examples:
        print(f"\n📊 {use_case} Persona:")
        result = asyncio.run(quick_persona_creation(name, age, demographics))
    
    print(f"\n💡 Next Steps:")
    print("=" * 60)
    print("1. Set OPENAI_API_KEY for real generation")
    print("2. Use generated assets in research studies")
    print("3. Scale up with multiple personas")
    print("4. Integrate with survey platforms")
    print("5. Analyze behavioral patterns across demographics")
    
    print(f"\n🎉 Demo complete! Ready for production use.")