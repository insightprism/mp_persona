#!/usr/bin/env python3
"""
Test Persona Image Generation
============================

Test the persona image generator with various personas.
"""

import asyncio
import os
from persona_config import PersonaConfig
from persona_image_generator import PersonaImageGenerator, generate_persona_image_simple

async def test_image_generation():
    """Test image generation with different personas"""
    print("🎨 Testing Persona Image Generation")
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
        )
    ]
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("🔑 OpenAI API key found - generating real images")
        print("💰 Using DALL-E 2 (256x256) for low cost")
    else:
        print("⚠️  No API key - showing mock responses")
        print("💡 Set OPENAI_API_KEY to generate real images")
    
    try:
        generator = PersonaImageGenerator(api_key) if api_key else None
        
        for i, persona in enumerate(test_personas, 1):
            print(f"\n👤 Test {i}: {persona.name}")
            print(f"   Demographics: {persona.age}yo {persona.race_ethnicity} {persona.gender}")
            print(f"   Background: {persona.education} education, {persona.location_type}, {persona.income}")
            
            if generator:
                # Real API call
                result = await generator.generate_persona_image(persona, size="256x256")
            else:
                # Mock response
                mock_gen = PersonaImageGenerator.__new__(PersonaImageGenerator)
                result = mock_gen.generate_mock_response(persona)
            
            if result["success"]:
                print(f"   ✅ Image generated successfully!")
                print(f"   🔗 URL: {result['image_url']}")
                print(f"   📝 Prompt: {result['prompt']}")
                
                if result.get("model") == "dall-e-2":
                    print(f"   💰 Cost: ~$0.02 (DALL-E 2, 256x256)")
                
            else:
                print(f"   ❌ Generation failed: {result['error']}")
        
        print(f"\n🎯 Test Summary:")
        print(f"   • Generated {len(test_personas)} persona images")
        print(f"   • Using {'DALL-E 2 API' if api_key else 'mock responses'}")
        print(f"   • Total estimated cost: ~${0.02 * len(test_personas):.2f}" if api_key else "")
        
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
    result = generate_persona_image_simple(persona)
    
    if result["success"]:
        print(f"✅ Simple function works!")
        print(f"📝 Generated prompt: {result['prompt']}")
        print(f"🔗 Image URL: {result['image_url']}")
    else:
        print(f"❌ Simple function failed: {result['error']}")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_image_generation())
    test_simple_function()
    
    print(f"\n💡 Usage Examples:")
    print("=" * 50)
    print("# Set API key")
    print("export OPENAI_API_KEY='sk-your-key-here'")
    print()
    print("# Run test")
    print("python3 test_image_generation.py")
    print()
    print("# Simple usage in code:")
    print("from persona_image_generator import generate_persona_image_simple")
    print("result = generate_persona_image_simple(persona_config)")
    print("image_url = result['image_url']")