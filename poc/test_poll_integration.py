"""
Test Poll Data Integration with Persona Handler

This demonstrates how polling data is passed to the persona handler
and integrated into the behavioral context for authentic responses.
"""

import asyncio
from typing import Dict, Any
from persona_config import PersonaConfig
from pm_persona_handler import pm_persona_transform_handler_async, build_poll_behavioral_context


class MockLLMConfig:
    """Mock LLM configuration for testing"""
    def __init__(self):
        self.llm_provider = "openai"
        self.llm_name = "gpt-4"
        self.temperature = 0.8
        self.llm_api_key = None  # Will use mock response


async def test_poll_integration():
    """Test the updated persona handler with poll data"""
    
    print("🧪 TESTING POLL DATA INTEGRATION")
    print("=" * 80)
    
    # Create test persona
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
        children=2
    )
    
    # Sample poll data from calling function
    sample_poll_data = {
        "healthcare": {
            "position": "supports universal healthcare",
            "confidence": 0.73,
            "source": "Pew Research 2024",
            "behavior_notes": "Hispanic college-educated women show 73% support for government healthcare programs"
        },
        "economy": {
            "position": "concerned about inflation impact on families",
            "confidence": 0.81,
            "source": "University of Michigan Consumer Sentiment",
            "behavior_notes": "Teachers with children prioritize economic stability and family financial security"
        },
        "education": {
            "position": "strongly supports increased education funding",
            "confidence": 0.89,
            "source": "NEA Polling Data",
            "behavior_notes": "Hispanic teachers advocate for bilingual education resources and smaller class sizes"
        },
        "technology": "Hispanic suburban mothers research purchases extensively before buying, especially for family-related items"
    }
    
    # Test the poll context builder
    print("📊 POLL CONTEXT GENERATION:")
    print("-" * 50)
    poll_context = build_poll_behavioral_context(sample_poll_data, maria)
    print(poll_context)
    print(f"\nContext length: {len(poll_context.split())} words")
    
    # Test the complete handler
    print("\n🎭 PERSONA HANDLER TEST:")
    print("-" * 50)
    
    # Structure rag_data as expected by updated handler
    rag_data = {
        'persona': maria,
        'poll_data': sample_poll_data
    }
    
    test_questions = [
        "What are your thoughts on healthcare policy?",
        "How do you feel about the current economy?",
        "What smartphone features are most important to you?"
    ]
    
    llm_config = MockLLMConfig()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing question: '{question}'")
        print("-" * 60)
        
        try:
            result = await pm_persona_transform_handler_async(
                input_content=question,
                llm_config=llm_config,
                rag_data=rag_data
            )
            
            if result['success']:
                print(f"✅ Success: {result['output_content']}")
                print(f"📏 Context info: {result['metadata']['total_context_length']} total words")
                print(f"   - Persona: {result['metadata']['persona_prompt_length']} words")
                print(f"   - Poll data: {result['metadata']['poll_data_length']} words")
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    print("\n🎯 INTEGRATION SUMMARY:")
    print("=" * 50)
    print("✅ Handler now accepts structured poll data via rag_data['poll_data']")
    print("✅ Poll context automatically integrated into persona transformation")
    print("✅ Calling function controls poll data selection and relevance")
    print("✅ Agent focuses purely on persona embodiment with provided data")
    print("✅ Flexible poll data format supports various polling sources")
    
    print("\n💡 EXAMPLE CALLING PATTERN:")
    print("-" * 40)
    print("""
    # Caller selects relevant polls based on query
    query = "What are your thoughts on healthcare?"
    relevant_polls = select_healthcare_polls(persona_demographics)
    
    # Pass everything to persona handler
    rag_data = {
        'persona': persona_config,
        'poll_data': relevant_polls
    }
    
    response = await pm_persona_transform_handler_async(
        input_content=query,
        llm_config=config,
        rag_data=rag_data
    )
    """)


if __name__ == "__main__":
    asyncio.run(test_poll_integration())