"""
Complete PrismMind Persona Integration

This file shows exactly how to integrate the persona handler into the existing
PmLLMEngine system. This would be added to pm_llm_engine.py in production.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from persona_config import PersonaConfig
from persona_prompt_builder import PersonaLLMPromptBuilder


# This is what would be added to pm_llm_engine.py
# ------------------------------------------------------

@pm_trace_handler_log_dec
async def pm_persona_transform_handler_async(
    input_content: str,
    llm_config: Any,
    handler_config: Optional[Any] = None,
    rag_data: Optional[PersonaConfig] = None
) -> Dict[str, Any]:
    """
    Persona transformation handler for PmLLMEngine.
    
    Transforms the LLM into a specific demographic persona based on 
    PersonaConfig passed via rag_data parameter.
    
    Args:
        input_content (str): User's prompt/question
        llm_config (Any): LLM configuration (pm_llm_config_dto)
        handler_config (Any): Optional handler-specific config
        rag_data (PersonaConfig): Persona configuration object
    
    Returns:
        Dict: Standard PmLLMEngine response format with persona response
    """
    
    # Validate persona config
    if not rag_data or not isinstance(rag_data, PersonaConfig):
        raise ValueError("rag_data must be a PersonaConfig object for persona transformation")
    
    if not input_content:
        raise ValueError("input_content (user prompt) is required")
    
    persona_config = rag_data
    
    # Build detailed persona identity
    prompt_builder = PersonaLLMPromptBuilder(persona_config)
    persona_identity = prompt_builder.build_persona_prompt()
    
    # Create system message that establishes persona transformation context
    system_message = (
        "You are a persona simulation system. You must fully embody the character "
        "described below. Respond as that specific person would, drawing from their "
        "background, values, life experiences, and demographic characteristics. "
        "Never break character or acknowledge being an AI."
    )
    
    # Combine persona identity with user prompt
    full_prompt = f"""{persona_identity}

User: {input_content}

{persona_config.name}:"""
    
    # Build LLM payload following existing PmLLMEngine pattern
    llm_payload = {
        "llm_provider": llm_config.llm_provider,
        "llm_name": llm_config.llm_name,
        "temperature": llm_config.temperature or 0.8,  # Higher for personality variation
        "chat_completion_url": llm_config.chat_completion_url,
        "llm_api_key": llm_config.llm_api_key,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": full_prompt}
        ]
    }
    
    # Call LLM using existing PrismMind infrastructure
    result_data = await pm_call_llm(llm_payload)
    output_content = result_data.get("output", "")
    
    # Return in standard PmLLMEngine format
    return {
        "success": True,
        "llm_response": result_data,
        "output_content": output_content,
        "output_format": "str",
        "metadata": {
            "provider": llm_payload["llm_provider"],
            "model": llm_payload["llm_name"],
            "handler_type": "persona_transform",
            "persona_name": persona_config.name,
            "persona_demographics": {
                "age": persona_config.age,
                "gender": persona_config.gender,
                "race_ethnicity": persona_config.race_ethnicity,
                "location": persona_config.location_type,
                "education": persona_config.education,
                "income": persona_config.income,
                "occupation": persona_config.occupation
            },
            "persona_prompt_length": len(persona_identity.split()),
            "transformation_timestamp": datetime.utcnow().isoformat()
        }
    }


# Handler metadata (required for PmLLMEngine registration)
pm_persona_transform_handler_async.__input_key__ = "input_content"

pm_persona_transform_handler_async.input_spec = [
    pm_handler_input_field_dto(
        input_field="input_content",
        dtype=["str"],
        description="User prompt/question for persona to respond to",
        primary_input_flag=True
    )
]

pm_persona_transform_handler_async.output_spec = [
    pm_handler_output_field_dto(
        output_field="output_content",
        dtype=["str"],
        format="str",
        description="Authentic response from transformed persona",
        primary_output_flag=True
    )
]


# Usage Examples
# ------------------------------------------------------

async def example_basic_persona_usage():
    """Basic usage example"""
    
    # 1. Create persona configuration
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
    
    # 2. Configure LLM with persona handler
    llm_config = pm_llm_config_dto(
        llm_provider="openai",
        llm_name="gpt-4",
        temperature=0.8,
        handler_name="pm_persona_transform_handler_async"
    )
    
    # 3. Set up user input
    input_data = {
        "input_content": "What smartphone features are most important to you?"
    }
    
    # 4. Create LLM engine
    engine = PmLLMEngine(
        input_data=input_data,
        engine_config=llm_config,
        handler_config=None
    )
    
    # 5. KEY: Pass persona via rag_data
    engine.rag_data = maria  # PersonaConfig object
    
    # 6. Execute - handler transforms LLM into Maria
    result = await engine.run()
    
    # 7. Get authentic persona response
    return result["output_content"]
    # Expected: "As a teacher and mom, I need great battery life and camera..."


async def example_market_research_batch():
    """Market research with multiple personas"""
    
    # Define different personas for market research
    personas = [
        PersonaConfig(
            name="Maria Rodriguez", age=34, race_ethnicity="hispanic",
            gender="female", education="college", location_type="suburban",
            income="50k_75k", occupation="teacher"
        ),
        PersonaConfig(
            name="Bob Johnson", age=52, race_ethnicity="white",
            gender="male", education="high_school", location_type="rural",
            income="30k_50k", occupation="mechanic"
        ),
        PersonaConfig(
            name="Ashley Chen", age=28, race_ethnicity="asian",
            gender="female", education="graduate", location_type="urban",
            income="over_100k", occupation="software engineer"
        )
    ]
    
    # Market research question
    question = "What features would make you switch to a new smartphone brand?"
    
    # Configure LLM
    llm_config = pm_llm_config_dto(
        llm_provider="openai",
        llm_name="gpt-4",
        temperature=0.8,
        handler_name="pm_persona_transform_handler_async"
    )
    
    results = []
    
    for persona in personas:
        # Create engine for each persona
        engine = PmLLMEngine(
            input_data={"input_content": question},
            engine_config=llm_config,
            handler_config=None
        )
        
        # Set persona
        engine.rag_data = persona
        
        # Get response
        result = await engine.run()
        
        results.append({
            "persona": persona.name,
            "demographics": {
                "age": persona.age,
                "income": persona.income,
                "location": persona.location_type,
                "education": persona.education
            },
            "response": result["output_content"]
        })
    
    return results


async def example_persona_conversation():
    """Extended conversation with persona"""
    
    # Create persona
    bob = PersonaConfig(
        name="Bob Johnson", age=52, race_ethnicity="white",
        gender="male", education="high_school", location_type="rural",
        income="30k_50k", occupation="auto mechanic"
    )
    
    # Configure LLM
    llm_config = pm_llm_config_dto(
        llm_provider="openai",
        llm_name="gpt-4",
        temperature=0.8,
        handler_name="pm_persona_transform_handler_async"
    )
    
    conversation = []
    
    questions = [
        "What do you think about electric vehicles?",
        "How has technology changed your work?",
        "What's your biggest concern about the future?"
    ]
    
    for question in questions:
        engine = PmLLMEngine(
            input_data={"input_content": question},
            engine_config=llm_config,
            handler_config=None
        )
        
        engine.rag_data = bob
        result = await engine.run()
        
        conversation.append({
            "question": question,
            "bob_response": result["output_content"]
        })
    
    return conversation


# Integration with existing PrismMind handlers
# ------------------------------------------------------

def add_persona_handlers_to_prismind():
    """
    This shows what would need to be added to PmLLMEngine.get_available_builtin_handlers()
    """
    
    # In pm_llm_engine.py, add to get_available_builtin_handlers():
    handlers = {
        # ... existing handlers ...
        "pm_persona_transform_handler_async": pm_persona_transform_handler_async,
        # ... rest of handlers ...
    }
    
    return handlers


# FastAPI Integration Example
# ------------------------------------------------------

async def fastapi_persona_endpoint_example():
    """Example FastAPI endpoint using persona handler"""
    
    from fastapi import FastAPI, HTTPException
    
    app = FastAPI()
    
    @app.post("/persona/ask")
    async def ask_persona(
        persona_demographics: dict,
        question: str
    ):
        try:
            # Create persona from demographics
            persona = PersonaConfig(**persona_demographics)
            
            # Configure LLM
            llm_config = pm_llm_config_dto(
                llm_provider="openai",
                llm_name="gpt-4",
                temperature=0.8,
                handler_name="pm_persona_transform_handler_async"
            )
            
            # Create engine
            engine = PmLLMEngine(
                input_data={"input_content": question},
                engine_config=llm_config,
                handler_config=None
            )
            
            # Set persona
            engine.rag_data = persona
            
            # Get response
            result = await engine.run()
            
            return {
                "persona_name": persona.name,
                "question": question,
                "response": result["output_content"],
                "metadata": result["metadata"]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


if __name__ == "__main__":
    print("PrismMind Persona Integration Examples")
    print("=" * 50)
    print("This file shows complete integration patterns for personas in PrismMind")
    print("\nKey integration points:")
    print("1. Add pm_persona_transform_handler_async to pm_llm_engine.py")
    print("2. PersonaConfig objects passed via engine.rag_data")
    print("3. Handler extracts demographics and builds persona identity")
    print("4. Standard PmLLMEngine response format maintained")
    print("5. Works with existing infrastructure (pm_call_llm, etc.)")
    print("\nReady for production integration!")