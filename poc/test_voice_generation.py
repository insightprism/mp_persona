#!/usr/bin/env python3
"""
Test Persona Voice Generation
============================

Test the persona voice generator with various personas and use cases.
"""

import asyncio
import os
from pathlib import Path
from persona_config import PersonaConfig
from persona_voice_generator import PersonaVoiceGenerator, generate_persona_voice_simple

async def test_voice_generation():
    """Test voice generation with different personas"""
    print("🎤 Testing Persona Voice Generation")
    print("=" * 50)
    
    # Test personas with different characteristics
    test_personas = [
        PersonaConfig(
            name="Jennifer Walsh",
            age=38,
            race_ethnicity="white",
            gender="female",
            education="college",
            location_type="rural",
            income="30k_50k"
        ),
        PersonaConfig(
            name="Marcus Thompson",
            age=45,
            race_ethnicity="black",
            gender="male",
            education="graduate",
            location_type="urban",
            income="over_100k"
        ),
        PersonaConfig(
            name="Elena Gonzalez",
            age=25,
            race_ethnicity="hispanic",
            gender="female",
            education="high_school",
            location_type="suburban",
            income="25k_40k"
        ),
        PersonaConfig(
            name="Alex Kim",
            age=30,
            race_ethnicity="asian",
            gender="non-binary",
            education="college",
            location_type="urban",
            income="50k_75k"
        )
    ]
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("🔑 OpenAI API key found - generating real voice samples")
        print("💰 Using TTS-1 model for cost efficiency")
    else:
        print("⚠️  No API key - showing mock responses")
        print("💡 Set OPENAI_API_KEY to generate real voice samples")
    
    try:
        generator = PersonaVoiceGenerator(api_key) if api_key else None
        total_cost = 0
        
        for i, persona in enumerate(test_personas, 1):
            print(f"\n👤 Test {i}: {persona.name}")
            print(f"   Demographics: {persona.age}yo {persona.race_ethnicity} {persona.gender}")
            print(f"   Background: {persona.education} education, {persona.location_type}, {persona.income}")
            
            if generator:
                # Real API call
                result = await generator.generate_persona_voice(persona)
            else:
                # Mock response
                mock_gen = PersonaVoiceGenerator.__new__(PersonaVoiceGenerator)
                mock_gen.voice_profiles = {
                    "alloy": {"gender": "neutral", "age": "young", "style": "clear"},
                    "echo": {"gender": "male", "age": "middle", "style": "professional"},
                    "fable": {"gender": "male", "age": "mature", "style": "warm"},
                    "onyx": {"gender": "male", "age": "deep", "style": "authoritative"},
                    "nova": {"gender": "female", "age": "young", "style": "energetic"},
                    "shimmer": {"gender": "female", "age": "middle", "style": "friendly"}
                }
                result = mock_gen.generate_mock_response(persona)
            
            if result["success"]:
                print(f"   ✅ Voice generated successfully!")
                print(f"   🎵 Audio file: {result['audio_path']}")
                print(f"   🗣️  Voice: {result['voice_used']} - {result['voice_characteristics']}")
                print(f"   💾 File size: {result['file_size_mb']} MB")
                print(f"   📝 Script preview: {result['script_text'][:80]}...")
                
                if result.get("model") == "tts-1":
                    cost = len(result['script_text']) * 0.000015
                    total_cost += cost
                    print(f"   💰 Cost: ~${cost:.4f}")
                
            else:
                print(f"   ❌ Generation failed: {result['error']}")
        
        print(f"\n🎯 Test Summary:")
        print(f"   • Generated {len(test_personas)} persona voice samples")
        print(f"   • Using {'OpenAI TTS-1 API' if api_key else 'mock responses'}")
        if api_key:
            print(f"   • Total estimated cost: ~${total_cost:.4f}")
            print(f"   • Audio files saved in voice_samples/ directory")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_simple_function():
    """Test the simple convenience function"""
    print(f"\n🔧 Testing Simple Function")
    print("-" * 30)
    
    persona = PersonaConfig(
        name="Test User",
        age=30,
        race_ethnicity="asian",
        gender="male",
        education="college",
        location_type="urban",
        income="50k_75k"
    )
    
    # Test simple function
    result = generate_persona_voice_simple(persona)
    
    if result["success"]:
        print(f"✅ Simple function works!")
        print(f"🎵 Audio file: {result['audio_path']}")
        print(f"🗣️  Selected voice: {result['voice_used']}")
        print(f"📝 Script preview: {result['script_text'][:100]}...")
    else:
        print(f"❌ Simple function failed: {result['error']}")

async def test_custom_text():
    """Test custom text generation"""
    print(f"\n🎨 Testing Custom Text Generation")
    print("-" * 40)
    
    persona = PersonaConfig(
        name="Survey Respondent",
        age=40,
        race_ethnicity="white",
        gender="female",
        education="graduate",
        location_type="suburban",
        income="75k_100k"
    )
    
    custom_texts = [
        "I think remote work has been a game-changer for work-life balance, but I do miss the in-person collaboration.",
        "When it comes to technology, I'm cautiously optimistic. It's important to consider both the benefits and potential risks.",
        "Climate change is definitely something I worry about. We need practical solutions that don't hurt the economy."
    ]
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        if api_key:
            generator = PersonaVoiceGenerator(api_key)
            
            for i, text in enumerate(custom_texts, 1):
                print(f"\n📝 Custom sample {i}: {text[:50]}...")
                result = await generator.generate_custom_voice_sample(persona, text)
                
                if result["success"]:
                    print(f"   ✅ Generated: {result['audio_path']}")
                    print(f"   🗣️  Voice: {result['voice_used']}")
                    print(f"   💾 Size: {result['file_size_mb']} MB")
                else:
                    print(f"   ❌ Failed: {result['error']}")
        else:
            print("⚠️  No API key - skipping custom text generation")
            print("💡 Set OPENAI_API_KEY to test custom text features")
            
    except Exception as e:
        print(f"❌ Custom text test failed: {e}")

def show_voice_characteristics():
    """Show available voice characteristics"""
    print(f"\n🎭 Available Voice Characteristics")
    print("-" * 40)
    
    # Voice profiles from the class
    voice_profiles = {
        "alloy": {"gender": "neutral", "age": "young", "style": "clear"},
        "echo": {"gender": "male", "age": "middle", "style": "professional"},
        "fable": {"gender": "male", "age": "mature", "style": "warm"},
        "onyx": {"gender": "male", "age": "deep", "style": "authoritative"},
        "nova": {"gender": "female", "age": "young", "style": "energetic"},
        "shimmer": {"gender": "female", "age": "middle", "style": "friendly"}
    }
    
    for voice_name, characteristics in voice_profiles.items():
        print(f"🗣️  {voice_name}: {characteristics['gender']} voice, {characteristics['age']} age, {characteristics['style']} style")

if __name__ == "__main__":
    # Show voice options first
    show_voice_characteristics()
    
    # Run tests
    asyncio.run(test_voice_generation())
    test_simple_function()
    asyncio.run(test_custom_text())
    
    print(f"\n💡 Usage Examples:")
    print("=" * 50)
    print("# Set API key")
    print("export OPENAI_API_KEY='sk-your-key-here'")
    print()
    print("# Run test")
    print("python3 test_voice_generation.py")
    print()
    print("# Simple usage in code:")
    print("from persona_voice_generator import generate_persona_voice_simple")
    print("result = generate_persona_voice_simple(persona_config)")
    print("audio_file = result['audio_path']")
    print()
    print("# Custom text:")
    print("result = generate_persona_voice_simple(persona_config, custom_text='Hello world!')")
    print()
    print("# Audio files saved to: voice_samples/")
    
    # Show what files would be created
    if os.path.exists("voice_samples"):
        files = list(Path("voice_samples").glob("*.mp3"))
        if files:
            print(f"\n🎵 Generated audio files ({len(files)}):")
            for file in files[:5]:  # Show first 5
                print(f"   • {file.name}")
            if len(files) > 5:
                print(f"   • ... and {len(files) - 5} more")
    else:
        print(f"\n📁 Audio files will be saved to: voice_samples/ (directory will be created)")