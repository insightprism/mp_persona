# Poll Data Integration with Persona Handler

## Overview

The persona handler has been updated to integrate polling data for authentic demographic-based responses. The calling function selects relevant poll data and passes it via `rag_data`, while the persona agent focuses purely on embodiment.

## Updated Architecture

### Handler Signature
```python
async def pm_persona_transform_handler_async(
    input_content: str,                    # User's question
    llm_config: Any,                      # LLM configuration  
    handler_config: Optional[Any] = None,
    rag_data: Optional[Dict[str, Any]] = None  # Updated: Now expects dict
) -> Dict[str, Any]:
```

### rag_data Structure
```python
rag_data = {
    'persona': PersonaConfig,              # The persona identity
    'poll_data': Dict[str, Any]           # Selected polling data
}
```

## Poll Data Format

### Structured Format
```python
poll_data = {
    "healthcare": {
        "position": "supports universal healthcare",
        "confidence": 0.73,                    # 0.0 to 1.0
        "source": "Pew Research 2024",
        "behavior_notes": "Hispanic college-educated women show 73% support"
    },
    "economy": {
        "position": "concerned about inflation impact",
        "confidence": 0.81,
        "source": "University of Michigan Consumer Sentiment",
        "behavior_notes": "Teachers prioritize family financial security"
    }
}
```

### Simple Format
```python
poll_data = {
    "technology": "Hispanic suburban mothers research purchases extensively",
    "voting": "Tends to vote Democratic in local elections"
}
```

## Integration Flow

1. **Calling Function** analyzes query and selects relevant polls
2. **Calling Function** structures rag_data with persona + poll data
3. **Persona Handler** receives structured data
4. **Handler** builds poll behavioral context automatically
5. **Handler** combines persona identity + poll context + user query
6. **LLM** responds as authentic persona informed by real polling data

## Context Budget

- **Persona Identity**: ~650 words
- **Poll Data**: 100-1000+ words (caller controlled)
- **Total Context**: 750-2000+ words depending on poll selection

## Example Usage

```python
# Caller selects relevant polls based on query
query = "What are your thoughts on healthcare?"

# Select healthcare-related polling data
relevant_polls = {
    "healthcare": {
        "position": "supports government involvement",
        "confidence": 0.73,
        "source": "Gallup 2024"
    }
}

# Call persona handler
response = await pm_persona_transform_handler_async(
    input_content=query,
    llm_config=config,
    rag_data={
        'persona': maria_persona,
        'poll_data': relevant_polls
    }
)
```

## Benefits

### Clean Separation of Concerns
- **Calling Function**: Query analysis, poll selection, data preparation
- **Persona Handler**: Pure persona embodiment and response generation

### Maximum Flexibility
- Caller controls poll relevance and context budget
- Handler accepts any structured poll format
- Easy to experiment with different poll selection strategies

### Authentic Responses
- Real polling data informs behavioral patterns
- Confidence levels indicate strength of demographic trends
- Source attribution for transparency

### Firefly Architecture Alignment
- Purpose-driven: Agent gets exactly the data needed for this conversation
- Ephemeral: No persistent poll data storage in agent
- Specialized: Agent focuses purely on persona transformation

## Context Optimization

The system automatically tracks context usage:

```python
{
    "persona_prompt_length": 644,        # Words in persona identity
    "poll_data_length": 145,             # Words in poll context
    "total_context_length": 789          # Total words sent to LLM
}
```

This enables dynamic poll selection based on:
- Model context limits
- Query complexity
- Desired response depth

## Future Enhancements

1. **Dynamic Poll Selection**: API integration with live polling data
2. **Historical Context**: Time-based poll data for scenario testing
3. **Cross-Demographic Analysis**: How persona differs from population average
4. **Confidence Weighting**: Stronger poll data influences response more heavily

## Implementation Status

✅ **Complete**: Updated handler with poll integration  
✅ **Complete**: Flexible poll data format support  
✅ **Complete**: Context budget tracking  
✅ **Complete**: Test framework with mock data  
✅ **Ready**: For integration with live polling sources