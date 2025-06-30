"""
Show a complete persona identity generation
"""
import asyncio
from persona_config import PersonaConfig
from persona_prompt_builder import PersonaLLMPromptBuilder


async def show_complete_persona():
    """Show the full persona identity for Maria Rodriguez"""
    
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
    
    # Build her persona
    builder = PersonaLLMPromptBuilder(maria)
    persona_prompt = builder.build_persona_prompt()
    
    print("=" * 80)
    print("COMPLETE PERSONA IDENTITY: Maria Rodriguez")
    print("=" * 80)
    print(f"Total words: {len(persona_prompt.split())}")
    print("=" * 80)
    print(persona_prompt)
    print("=" * 80)
    
    # Show how this combines with a user prompt
    print("\n\nHOW IT WORKS WITH HANDLER PATTERN:")
    print("=" * 80)
    print("User Prompt (input_data):")
    print("  'What features are most important to you when buying a new smartphone?'")
    print("\nPersona Identity (rag_data):")
    print(f"  [The {len(persona_prompt.split())} word persona identity above]")
    print("\nHandler combines them to create:")
    print("  - LLM becomes Maria Rodriguez")
    print("  - Responds authentically based on her background")
    print("  - Answer reflects teacher salary, parent needs, suburban lifestyle")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(show_complete_persona())