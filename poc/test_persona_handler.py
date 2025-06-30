"""
Test the Persona Handler Integration with PmLLMEngine Pattern

This demonstrates how the persona handler integrates with the existing
PmLLMEngine infrastructure, passing persona configs via rag_data.
"""

import asyncio
import os
from persona_config import PersonaConfig
from pm_persona_handler import pm_persona_transform_handler_async, pm_persona_activation_handler_async


# Mock LLM config to simulate pm_llm_config_dto
class MockLLMConfig:
    def __init__(self):
        self.llm_provider = "openai"
        self.llm_name = "gpt-4"
        self.temperature = 0.8
        self.chat_completion_url = None
        self.llm_api_key = os.getenv("OPENAI_API_KEY")


async def test_persona_handler_integration():
    """Test the persona handler with different personas"""
    
    print("=" * 80)
    print("PERSONA HANDLER INTEGRATION TEST")
    print("=" * 80)
    print("This shows how PersonaConfig objects integrate with PmLLMEngine handlers")
    print("via the rag_data parameter.\n")
    
    # Create LLM config
    llm_config = MockLLMConfig()
    
    # Test 1: Maria Rodriguez - Suburban Teacher
    print("TEST 1: Maria Rodriguez - Suburban Teacher")
    print("-" * 50)
    
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
    
    # Test activation handler
    print("\n🔥 Testing persona activation...")
    activation_result = await pm_persona_activation_handler_async(
        input_content="Please introduce yourself",
        llm_config=llm_config,
        handler_config=None,
        rag_data=maria  # PersonaConfig passed via rag_data
    )
    
    print(f"Activation Success: {activation_result.get('activation_success')}")
    print(f"Activation Response: {activation_result.get('output_content', '')[:200]}...")
    
    # Test main handler
    print("\n🎭 Testing persona transformation...")
    user_prompt = "What smartphone features are most important to you? How much would you spend?"
    
    response = await pm_persona_transform_handler_async(
        input_content=user_prompt,
        llm_config=llm_config,
        handler_config=None,
        rag_data=maria  # PersonaConfig passed via rag_data
    )
    
    print(f"\nPrompt: {user_prompt}")
    print(f"Maria's Response: {response.get('output_content', '')}")
    print(f"Metadata: {response.get('metadata', {})}")
    
    
    # Test 2: Bob Johnson - Rural Mechanic
    print("\n\n" + "=" * 80)
    print("TEST 2: Bob Johnson - Rural Mechanic")
    print("-" * 50)
    
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
    
    # Test political question
    political_prompt = "What do you think about the government requiring all new cars to be electric by 2035?"
    
    response = await pm_persona_transform_handler_async(
        input_content=political_prompt,
        llm_config=llm_config,
        handler_config=None,
        rag_data=bob  # PersonaConfig passed via rag_data
    )
    
    print(f"\nPrompt: {political_prompt}")
    print(f"Bob's Response: {response.get('output_content', '')}")
    print(f"Demographics: {response.get('metadata', {}).get('persona_demographics', {})}")
    
    
    # Test 3: Error handling
    print("\n\n" + "=" * 80)
    print("TEST 3: Error Handling")
    print("-" * 50)
    
    # Test with invalid rag_data
    error_response = await pm_persona_transform_handler_async(
        input_content="Test question",
        llm_config=llm_config,
        handler_config=None,
        rag_data="invalid_data"  # Wrong type
    )
    
    print(f"Error handling test: {error_response.get('error', 'No error')}")
    
    
    print("\n" + "=" * 80)
    print("INTEGRATION PATTERN SUMMARY")
    print("=" * 80)
    print("Key Points:")
    print("1. PersonaConfig objects are passed via rag_data parameter")
    print("2. Handler extracts demographics and builds persona identity")
    print("3. LLM is transformed into that specific person")
    print("4. Responses reflect authentic demographic patterns")
    print("5. Metadata includes persona information for analysis")
    print("\nThis integrates seamlessly with existing PmLLMEngine infrastructure!")


async def demonstrate_handler_call_pattern():
    """Show exactly how this would work in PrismMind"""
    
    print("\n" + "=" * 80)
    print("PRISMIND INTEGRATION EXAMPLE")
    print("=" * 80)
    
    # This shows how it would work with real PmLLMEngine
    print("""
# In production PrismMind code:

from pm_engines.pm_llm_engine import PmLLMEngine
from pm_config.pm_llm_engine_config import pm_llm_config_dto
from persona_config import PersonaConfig

# 1. Create persona configuration
maria = PersonaConfig(
    name="Maria Rodriguez",
    age=34,
    race_ethnicity="hispanic",
    gender="female",
    education="college",
    location_type="suburban",
    income="50k_75k",
    occupation="elementary school teacher"
)

# 2. Configure LLM engine with persona handler
llm_config = pm_llm_config_dto(
    llm_provider="openai",
    llm_name="gpt-4", 
    temperature=0.8,
    handler_name="pm_persona_transform_handler_async"
)

# 3. Set up input data
input_data = {
    "input_content": "What features matter most in a smartphone?"
}

# 4. Create engine and set rag_data to persona
engine = PmLLMEngine(
    input_data=input_data,
    engine_config=llm_config,
    handler_config=None
)

# 5. KEY: Pass persona via rag_data
engine.rag_data = maria  # PersonaConfig object

# 6. Run engine - handler receives persona via rag_data
result = await engine.run()

# 7. Get authentic persona response
persona_response = result["output_content"]
# "As a busy mom and teacher, I need great battery life and a good camera..."
    """)
    
    print("This shows the complete integration pattern!")


if __name__ == "__main__":
    print("🎭 PERSONA HANDLER INTEGRATION TEST")
    print("This demonstrates PersonaConfig → rag_data → authentic responses")
    
    asyncio.run(test_persona_handler_integration())
    asyncio.run(demonstrate_handler_call_pattern())