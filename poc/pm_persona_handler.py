"""
PmLLMEngine Persona Handler

This handler integrates with the existing PmLLMEngine to transform LLMs into specific personas.
It follows the exact pattern used in pm_llm_engine.py handlers.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Import the persona classes from our POC
from persona_config import PersonaConfig
from persona_prompt_builder import PersonaLLMPromptBuilder

# Import PrismMind utilities (would normally be from pm_utils)
# For POC, we'll simulate these
def pm_trace_handler_log_dec(func):
    """Mock decorator for logging"""
    return func


def build_poll_behavioral_context(poll_data: Dict[str, Any], persona_config: PersonaConfig) -> str:
    """
    Build behavioral context from poll data for persona transformation.
    
    Args:
        poll_data: Dictionary containing poll information structured by calling function
        persona_config: The persona configuration for demographic context
    
    Returns:
        Formatted string with behavioral guidance based on poll data
    """
    if not poll_data:
        return ""
    
    context_parts = ["BEHAVIORAL DATA FROM YOUR DEMOGRAPHIC GROUP:"]
    context_parts.append("The following polling data shows how people with your background typically respond:\n")
    
    # Process different types of poll data
    for topic, data in poll_data.items():
        if isinstance(data, dict):
            # Structured poll data
            position = data.get('position', 'neutral')
            confidence = data.get('confidence', 0.5)
            source = data.get('source', 'polling data')
            
            confidence_desc = "strongly" if confidence > 0.8 else "moderately" if confidence > 0.6 else "somewhat"
            
            context_parts.append(f"• {topic.upper()}: Your demographic {confidence_desc} tends toward '{position}' (source: {source})")
            
            # Add specific behavioral guidance if available
            if 'behavior_notes' in data:
                context_parts.append(f"  - {data['behavior_notes']}")
                
        elif isinstance(data, str):
            # Simple text-based poll data
            context_parts.append(f"• {topic.upper()}: {data}")
    
    context_parts.append("\nYou should respond authentically based on these patterns while staying true to your individual personality.")
    context_parts.append("These statistics inform your likely perspectives, but you're still a unique individual with personal experiences.\n")
    
    return "\n".join(context_parts)


async def pm_call_llm(llm_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock pm_call_llm for POC - simulates the real PrismMind LLM caller
    In production, this would use the actual pm_call_llm from pm_utils
    """
    try:
        from openai import OpenAI
        
        api_key = llm_payload.get("llm_api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "output": f"[MOCK] Persona response from {llm_payload['messages'][0]['content'][:100]}...",
                "success": False,
                "error": "No API key"
            }
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=llm_payload["llm_name"],
            messages=llm_payload["messages"],
            temperature=llm_payload["temperature"],
            max_tokens=500
        )
        
        return {
            "output": response.choices[0].message.content,
            "success": True,
            "usage": response.usage.model_dump() if hasattr(response.usage, 'model_dump') else {}
        }
        
    except Exception as e:
        return {
            "output": f"[MOCK] Simulated persona response based on demographics",
            "success": False,
            "error": str(e)
        }


# Handler specification metadata (following PmLLMEngine pattern)
pm_handler_input_field_dto = type('pm_handler_input_field_dto', (), {})
pm_handler_output_field_dto = type('pm_handler_output_field_dto', (), {})


@pm_trace_handler_log_dec
async def pm_persona_transform_handler_async(
    input_content: str,
    llm_config: Any,
    handler_config: Optional[Any] = None,
    rag_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Persona transformation handler for PmLLMEngine.
    
    This handler accepts a PersonaConfig object via rag_data and transforms
    the LLM into that specific demographic persona.
    
    Args:
        input_content (str): The user's prompt/question
        llm_config (Any): LLM configuration (temperature, model, etc.)
        handler_config (Any): Optional handler-specific config
        rag_data (PersonaConfig): The persona configuration object
    
    Returns:
        Dict containing the persona's authentic response
    """
    print(f"🎭 Persona handler activated")
    
    # Validate inputs
    if not rag_data or 'persona' not in rag_data:
        return {
            "success": False,
            "error": "rag_data must contain 'persona' key with PersonaConfig object",
            "output_content": "",
            "output_format": "str"
        }
    
    if not input_content:
        return {
            "success": False,
            "error": "input_content (user prompt) is required",
            "output_content": "",
            "output_format": "str"
        }
    
    try:
        # Extract persona configuration and poll data
        persona_config = rag_data['persona']
        poll_data = rag_data.get('poll_data', {})
        
        print(f"🧬 Transforming LLM into {persona_config.name} ({persona_config.age}-year-old {persona_config.race_ethnicity} {persona_config.gender})")
        if poll_data:
            print(f"📊 Using {len(poll_data)} poll data points for behavioral context")
        
        # Build detailed persona identity using our prompt builder
        prompt_builder = PersonaLLMPromptBuilder(persona_config)
        persona_identity = prompt_builder.build_persona_prompt()
        
        # Add poll data behavioral context if provided
        poll_context = ""
        if poll_data:
            poll_context = build_poll_behavioral_context(poll_data, persona_config)
        
        total_words = len(persona_identity.split()) + len(poll_context.split())
        print(f"📝 Generated {total_words} word persona context ({len(persona_identity.split())} identity + {len(poll_context.split())} behavioral data)")
        
        # Construct the complete prompt that transforms the LLM
        system_prompt = "You are a persona simulation system. Fully embody the character described below. Respond as that person would, drawing from their background, values, and life experiences."
        
        # Combine persona identity, poll data, and user prompt
        complete_user_prompt = f"""{persona_identity}

{poll_context}

User: {input_content}

{persona_config.name}:"""
        
        # Build LLM payload following PmLLMEngine pattern
        llm_payload = {
            "llm_provider": llm_config.llm_provider,
            "llm_name": llm_config.llm_name,
            "temperature": llm_config.temperature or 0.8,  # Higher temp for personality
            "chat_completion_url": getattr(llm_config, "chat_completion_url", None),
            "llm_api_key": getattr(llm_config, "llm_api_key", None),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": complete_user_prompt}
            ]
        }
        
        # Call LLM through PrismMind infrastructure
        print(f"🧠 Calling LLM as {persona_config.name}...")
        result_data = await pm_call_llm(llm_payload)
        
        output_content = result_data.get("output", "")
        
        print(f"✅ {persona_config.name} responded: {output_content[:100]}...")
        
        # Return in PmLLMEngine expected format
        return {
            "success": True,
            "llm_response": result_data,
            "output_content": output_content,
            "output_format": "str",
            "metadata": {
                "provider": llm_payload["llm_provider"],
                "model": llm_payload["llm_name"],
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
                "poll_data_length": len(poll_context.split()),
                "total_context_length": total_words,
                "response_timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ Persona handler error: {e}")
        return {
            "success": False,
            "error": f"Persona transformation failed: {str(e)}",
            "output_content": "",
            "output_format": "str",
            "metadata": {
                "persona_name": getattr(rag_data, 'name', 'Unknown') if rag_data else 'Unknown',
                "error_timestamp": datetime.utcnow().isoformat()
            }
        }


# Handler metadata (following PmLLMEngine pattern)
pm_persona_transform_handler_async.__input_key__ = "input_content"

# Input specification
pm_persona_transform_handler_async.input_spec = [
    type('pm_handler_input_field_dto', (), {
        'input_field': 'input_content',
        'dtype': ['str'],
        'description': 'User prompt/question for the persona to respond to',
        'primary_input_flag': True
    })()
]

# Output specification  
pm_persona_transform_handler_async.output_spec = [
    type('pm_handler_output_field_dto', (), {
        'output_field': 'output_content',
        'dtype': ['str'],
        'format': 'str',
        'description': 'Authentic persona response based on demographic background',
        'primary_output_flag': True
    })()
]


# Additional handler for persona activation/confirmation
@pm_trace_handler_log_dec
async def pm_persona_activation_handler_async(
    input_content: str,
    llm_config: Any,
    handler_config: Optional[Any] = None,
    rag_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Persona activation handler - confirms LLM has adopted the persona identity.
    
    This is used during the persona "birth" phase to verify the LLM 
    understands and can embody the persona.
    
    Args:
        input_content (str): Activation prompt (usually "Please introduce yourself")
        llm_config (Any): LLM configuration
        handler_config (Any): Optional handler config
        rag_data (PersonaConfig): The persona to activate
    
    Returns:
        Dict with activation response and success indicators
    """
    print(f"🔥 Persona activation handler started")
    
    if not rag_data or 'persona' not in rag_data:
        return {
            "success": False,
            "error": "rag_data must contain 'persona' key with PersonaConfig object",
            "output_content": "",
            "activation_success": False
        }
    
    try:
        persona_config = rag_data['persona']
        
        # Build persona identity
        prompt_builder = PersonaLLMPromptBuilder(persona_config)
        persona_identity = prompt_builder.build_persona_prompt()
        
        # Create activation prompt
        activation_prompt = f"""{persona_identity}

To confirm you understand your identity, please introduce yourself as {persona_config.name} in 2-3 sentences, mentioning your age, where you live, and what you do.

{persona_config.name}:"""
        
        # Call LLM
        llm_payload = {
            "llm_provider": llm_config.llm_provider,
            "llm_name": llm_config.llm_name,
            "temperature": 0.8,
            "chat_completion_url": getattr(llm_config, "chat_completion_url", None),
            "llm_api_key": getattr(llm_config, "llm_api_key", None),
            "messages": [
                {"role": "system", "content": "You are a persona simulation. Embody the character described."},
                {"role": "user", "content": activation_prompt}
            ]
        }
        
        result_data = await pm_call_llm(llm_payload)
        response_text = result_data.get("output", "").lower()
        
        # Verify activation by checking response contains identity markers
        identity_confirmed = (
            persona_config.name.lower().split()[0] in response_text and
            str(persona_config.age) in response_text and
            any(word in response_text for word in ["i am", "i'm", "my name"])
        )
        
        return {
            "success": True,
            "llm_response": result_data,
            "output_content": result_data.get("output", ""),
            "output_format": "str",
            "activation_success": identity_confirmed,
            "metadata": {
                "persona_name": persona_config.name,
                "identity_confirmed": identity_confirmed,
                "activation_timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output_content": "",
            "activation_success": False
        }


# Handler metadata
pm_persona_activation_handler_async.__input_key__ = "input_content"
pm_persona_activation_handler_async.input_spec = [
    type('pm_handler_input_field_dto', (), {
        'input_field': 'input_content',
        'dtype': ['str'],
        'description': 'Activation prompt for persona confirmation',
        'primary_input_flag': True
    })()
]

pm_persona_activation_handler_async.output_spec = [
    type('pm_handler_output_field_dto', (), {
        'output_field': 'output_content',
        'dtype': ['str'],
        'format': 'str',
        'description': 'Persona activation response',
        'primary_output_flag': True
    })()
]