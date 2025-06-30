"""
Test script for Persona Firefly Proof of Concept
"""
import asyncio
from persona_config import PersonaConfig, StimulusConfig
from llm_persona_firefly import LLMPersonaFirefly


async def test_maria_teacher():
    """Test Maria Rodriguez - suburban teacher persona"""
    print("=" * 80)
    print("TEST 1: Maria Rodriguez - Suburban Teacher")
    print("=" * 80)
    
    # Create Maria's configuration
    maria = PersonaConfig(
        name="Maria Rodriguez",
        age=34,
        race_ethnicity="hispanic",
        gender="female",
        education="college",
        location_type="suburban",
        income="50k_75k",
        occupation="elementary school teacher",
        marital_status="married",
        children=2,
        state="Arizona"
    )
    
    # Create persona firefly
    persona = LLMPersonaFirefly(
        persona_config=maria,
        purpose="market_research_smartphone_features"
    )
    
    # Test 1: Product evaluation
    print("\n📱 Asking about smartphone features...")
    stimulus1 = {
        "prompt": "What features are most important to you when buying a new smartphone? How much would you be willing to spend?",
        "stimulus_type": "product_evaluation"
    }
    
    response1 = await persona.glow(stimulus1)
    print(f"\n{response1['persona_name']}'s response:")
    print(response1['persona_response'])
    print(f"\nMetadata: {response1['interaction_number']} interactions, Type: {response1['stimulus_type']}")


async def test_bob_mechanic():
    """Test Bob Johnson - rural mechanic persona"""
    print("\n" + "=" * 80)
    print("TEST 2: Bob Johnson - Rural Mechanic")
    print("=" * 80)
    
    # Create Bob's configuration
    bob = PersonaConfig(
        name="Bob Johnson",
        age=52,
        race_ethnicity="white",
        gender="male",
        education="high_school",
        location_type="rural",
        income="30k_50k",
        occupation="auto mechanic",
        marital_status="divorced",
        children=3,
        state="Ohio"
    )
    
    # Create persona firefly
    persona = LLMPersonaFirefly(
        persona_config=bob,
        purpose="political_opinion_research"
    )
    
    # Test 2: Political opinion
    print("\n🗳️ Asking about electric vehicle mandate...")
    stimulus2 = StimulusConfig(
        stimulus_type="political_survey",
        stimulus_id="ev_mandate_001",
        prompt="What do you think about the government requiring all new cars to be electric by 2035?",
        political_issue="Electric Vehicle Mandate",
        proposal="Federal requirement for all new vehicles to be electric by 2035"
    )
    
    response2 = await persona.glow(stimulus2)
    print(f"\n{response2['persona_name']}'s response:")
    print(response2['persona_response'])
    print(f"\nDemographics: {response2['persona_demographics']}")


async def test_ashley_tech():
    """Test Ashley Chen - urban tech worker persona"""
    print("\n" + "=" * 80)
    print("TEST 3: Ashley Chen - Urban Tech Worker")
    print("=" * 80)
    
    # Create Ashley's configuration
    ashley = PersonaConfig(
        name="Ashley Chen",
        age=28,
        race_ethnicity="asian",
        gender="female",
        education="graduate",
        location_type="urban",
        income="over_100k",
        occupation="software engineer",
        marital_status="single",
        children=0,
        state="California"
    )
    
    # Create persona firefly
    persona = LLMPersonaFirefly(
        persona_config=ashley,
        purpose="lifestyle_preferences_research"
    )
    
    # Test 3: Lifestyle question
    print("\n🏠 Asking about work-from-home preferences...")
    stimulus3 = {
        "prompt": "How do you feel about working from home versus going to an office? What's your ideal work setup?",
        "stimulus_type": "general_question"
    }
    
    response3 = await persona.glow(stimulus3)
    print(f"\n{response3['persona_name']}'s response:")
    print(response3['persona_response'])


async def test_persona_activation_only():
    """Test just the activation process"""
    print("\n" + "=" * 80)
    print("TEST 4: Activation Process Demo")
    print("=" * 80)
    
    # Create a simple persona
    test_persona = PersonaConfig(
        name="John Smith",
        age=45,
        race_ethnicity="white",
        gender="male",
        education="some_college",
        location_type="suburban",
        income="75k_100k",
        occupation="sales manager",
        marital_status="married",
        children=1
    )
    
    # Create and activate firefly
    persona = LLMPersonaFirefly(
        persona_config=test_persona,
        purpose="demo_activation"
    )
    
    # Just test activation
    await persona.birth()
    print(f"\n✅ Persona activated: {persona.agent_activated}")
    print(f"📊 Persona prompt length: {len(persona.persona_prompt.split())} words")
    
    # Show a snippet of the persona prompt
    print(f"\n📄 First 500 characters of persona identity:")
    print(persona.persona_prompt[:500] + "...")


async def main():
    """Run all tests"""
    print("\n🎭 PERSONA FIREFLY PROOF OF CONCEPT")
    print("=" * 80)
    print("This demonstrates how demographic configurations become living personas")
    print("that respond authentically based on their backgrounds.")
    print("=" * 80)
    
    # Run tests
    await test_persona_activation_only()
    await test_maria_teacher()
    await test_bob_mechanic()
    await test_ashley_tech()
    
    print("\n" + "=" * 80)
    print("✅ All tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    # Note: Set OPENAI_API_KEY environment variable for real responses
    # Without it, you'll get mock responses
    asyncio.run(main())