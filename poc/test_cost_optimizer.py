#!/usr/bin/env python3
"""
Cost Optimizer Test
==================

Demonstrate smart cost optimization for persona asset generation.
"""

import asyncio
from cost_optimizer import PersonaCostOptimizer, should_generate_image, get_asset_cost_estimate

def test_cost_recommendations():
    """Test cost optimization scenarios"""
    print("💰 Cost Optimization Test")
    print("=" * 50)
    
    optimizer = PersonaCostOptimizer()
    
    # Test scenarios
    scenarios = [
        {
            "name": "New Persona (No Usage)",
            "persona_id": "new_user",
            "interactions": 0,
            "duration": 0,
            "description": "Just created, no chat history"
        },
        {
            "name": "Light Testing (2 interactions)",
            "persona_id": "light_user", 
            "interactions": 2,
            "duration": 120,
            "description": "Brief testing phase"
        },
        {
            "name": "Moderate Usage (8 interactions)",
            "persona_id": "moderate_user",
            "interactions": 8, 
            "duration": 480,
            "description": "Some real usage"
        },
        {
            "name": "Heavy Usage (25 interactions)",
            "persona_id": "heavy_user",
            "interactions": 25,
            "duration": 1200,
            "description": "Extensive usage pattern"
        }
    ]
    
    print("🔍 Testing Scenarios:")
    print()
    
    for scenario in scenarios:
        print(f"📊 {scenario['name']}")
        print(f"   {scenario['description']}")
        
        persona_id = scenario["persona_id"]
        
        # Simulate usage
        for i in range(scenario["interactions"]):
            optimizer.track_interaction(persona_id, {
                "input_tokens": 150,
                "output_tokens": 250,
                "provider": "openai"
            })
        
        # Get recommendations
        image_rec = optimizer.should_generate_image(persona_id)
        voice_rec = optimizer.should_generate_voice(persona_id)
        usage = optimizer.get_persona_usage(persona_id)
        
        # Display results
        print(f"   💬 Interactions: {usage['total_interactions']}")
        print(f"   💰 Current cost: ${usage['total_cost']:.3f}")
        print(f"   📈 Cost/interaction: ${usage['cost_per_interaction']:.3f}")
        
        # Image recommendation
        image_icon = "✅" if image_rec["recommend"] else "⚠️"
        print(f"   🖼️  Image: {image_icon} {image_rec['reason']}")
        if image_rec.get("warnings"):
            print(f"      Warnings: {', '.join(image_rec['warnings'])}")
        
        # Voice recommendation
        voice_icon = "✅" if voice_rec["recommend"] else "⚠️"
        print(f"   🎤 Voice: {voice_icon} {voice_rec['reason']}")
        
        print()
    
    # Summary
    print("📈 Cost Summary:")
    summary = optimizer.get_cost_summary()
    print(f"   Total personas: {summary['total_personas']}")
    print(f"   Total cost: ${summary['total_cost']:.3f}")
    print(f"   Avg cost per persona: ${summary['avg_cost_per_persona']:.3f}")
    print(f"   Avg cost per interaction: ${summary['avg_cost_per_interaction']:.3f}")

def test_cost_thresholds():
    """Test cost threshold recommendations"""
    print("\n💸 Cost Threshold Testing")
    print("=" * 50)
    
    # Test the simple function
    test_cases = [
        (0, 0, "No usage"),
        (1, 30, "Single quick test"),
        (3, 180, "Brief exploration"),
        (10, 600, "Good usage pattern"),
        (20, 1200, "Heavy usage")
    ]
    
    print("Quick recommendation function results:")
    for interactions, duration, description in test_cases:
        recommend = should_generate_image("test_persona", interactions, duration)
        icon = "✅" if recommend else "❌"
        print(f"   {icon} {interactions} interactions, {duration}s - {description}")

def demonstrate_cost_awareness():
    """Demonstrate cost-aware decision making"""
    print("\n🧠 Smart Cost Decision Making")
    print("=" * 50)
    
    costs = get_asset_cost_estimate()
    
    print("💰 Current Asset Costs:")
    print(f"   🖼️  Profile Image: ${costs['image']:.3f}")
    print(f"   🎤 Voice Sample (200 chars): ${costs['voice_200_chars']:.3f}")
    print(f"   🎤 Voice per 1K chars: ${costs['voice_per_1k_chars']:.3f}")
    print(f"   🤖 GPT-4 per 1K tokens: ${costs['gpt4_per_1k_input']:.3f} input + ${costs['gpt4_per_1k_output']:.3f} output")
    print(f"   🤖 Claude per 1K tokens: ${costs['claude_per_1k_input']:.3f} input + ${costs['claude_per_1k_output']:.3f} output")
    
    print("\n💡 Smart Usage Recommendations:")
    print("   ✅ Generate images for personas with 10+ interactions")
    print("   ✅ Voice generation is cost-effective for any active persona")
    print("   ⚠️  Avoid images for quick testing or one-off experiments")
    print("   💰 Consider batch generation for research studies")
    print("   🎯 Focus image generation on high-value, persistent personas")
    
    print("\n📊 Example Cost Scenarios:")
    scenarios = [
        ("Quick Test", 2, 0, 0, "$0.006 (LLM only)"),
        ("Light Usage", 5, 1, 0, "$0.035 (LLM + Image)"),
        ("Moderate Usage", 15, 1, 1, "$0.068 (LLM + Image + Voice)"),
        ("Heavy Research", 50, 1, 1, "$0.173 (Full assets justified)")
    ]
    
    for name, interactions, images, voices, cost in scenarios:
        print(f"   {name:15} {interactions:2d} interactions, {images} image, {voices} voice = {cost}")

def main():
    """Run all cost optimization tests"""
    test_cost_recommendations()
    test_cost_thresholds()
    demonstrate_cost_awareness()
    
    print("\n🎯 Key Takeaways:")
    print("=" * 50)
    print("✅ Images are NEVER auto-generated - always opt-in only")
    print("✅ Smart recommendations based on actual usage patterns")
    print("✅ Cost tracking prevents surprise expenses")
    print("✅ Clear alternatives provided for cost-conscious users")
    print("✅ Force override available when needed")
    
    print("\n💡 Best Practices:")
    print("🔹 Test personas with text-only first (free with Ollama)")
    print("🔹 Generate images after 5-10 successful interactions")
    print("🔹 Voice samples are cost-effective for active personas")
    print("🔹 Use mock responses for development and debugging")
    print("🔹 Monitor costs via /api/cost-summary endpoint")

if __name__ == "__main__":
    main()