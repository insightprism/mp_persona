# Persona Firefly Proof of Concept

This proof of concept demonstrates the LLM Persona Firefly system that transforms language models into authentic demographic personas.

## Overview

The POC shows how:
1. **Demographic data** becomes a detailed persona identity (~1200 words)
2. **LLM activation** transforms the AI into that specific person
3. **Authentic responses** reflect the persona's background and values
4. **Firefly lifecycle** works (birth → glow → disappear)

## Files

- `persona_config.py` - Data classes for persona demographics and stimuli
- `persona_prompt_builder.py` - Builds detailed persona identities from demographics
- `llm_persona_firefly.py` - Main firefly implementation
- `test_persona_poc.py` - Test scenarios with different personas

## Key Concepts

### 1. Persona Configuration
```python
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
```

### 2. Persona Identity Generation
The `PersonaLLMPromptBuilder` creates a ~1200 word identity covering:
- Core identity and demographics
- Life experiences based on generation
- Current situation and challenges
- Values shaped by background
- Communication style
- Behavioral instructions

### 3. LLM Transformation
The handler pattern combines:
- **User prompt**: "What features matter in a smartphone?"
- **Persona identity**: 1200-word description via `rag_text`
- **Result**: Authentic response as that person

### 4. Example Responses

**Maria (34, teacher, suburban)**:
> "As a busy mom and teacher, I really need a phone with great battery life and a good camera for capturing my kids' moments. Price matters too - on a teacher's salary with two kids, I can't justify spending $1000 on a phone..."

**Bob (52, mechanic, rural)**:
> "Electric cars by 2035? That's government overreach. Here in rural Ohio, we need trucks that can haul and go 300+ miles. Where are all these charging stations supposed to come from? This hurts working people like me..."

**Ashley (28, software engineer, urban)**:
> "I absolutely love working from home! I can code without distractions, save 2 hours of commute time, and my productivity has actually increased. My ideal setup is hybrid - home for focus work, office for collaboration..."

## Running the POC

### Option 1: With OpenAI API (Real Responses)
```bash
export OPENAI_API_KEY="your-api-key"
python test_persona_poc.py
```

### Option 2: Without API (Mock Responses)
```bash
python test_persona_poc.py
```

## How It Works

1. **Birth Phase**
   - Generate 1200-word persona identity
   - Activate LLM with identity confirmation
   - Verify persona understood their identity

2. **Glow Phase**
   - Receive user stimulus/question
   - Combine with persona identity
   - Generate authentic response
   - Return with metadata

3. **Disappear Phase**
   - Clean up after purpose fulfilled
   - True ephemeral existence

## Integration Pattern

In production, this integrates with PrismMind's handler pattern:

```python
# Handler receives:
input_data = {"input_content": "What's your opinion on..."}
rag_data = "[1200 word persona identity]"

# Handler combines into:
final_prompt = f"""
{persona_identity}

User: {question}

Respond as Maria Rodriguez based on your background...
"""
```

## Key Insights

1. **Demographics Drive Behavior**: Age, location, education, and income create predictable response patterns
2. **Generational Context Matters**: Boomers vs Gen Z have fundamentally different worldviews
3. **Authentic Language**: Education level determines vocabulary and communication style
4. **Purpose-Driven**: Each persona exists only as long as needed

## Next Steps

To integrate with full PrismMind:
1. Create `PmFireflyEngine` base class with lifecycle management
2. Integrate with `pm_input_prompt_rag_handler_async` in PmLLMEngine
3. Add visual generation with PersonaVisualGenerator
4. Create PersonaAgentFactory for batch creation
5. Add FastAPI endpoints for research APIs

## Limitations

This POC:
- Uses mock base classes (real would inherit from PmFireflyEngine)
- Calls OpenAI directly (real would use PmLLMEngine handlers)
- Has simple lifecycle (real would have environmental orchestration)
- Lacks visual generation (full version includes persona images)

## Try It!

Run the test script to see Maria the teacher, Bob the mechanic, and Ashley the software engineer come to life with authentic responses based on their demographics!