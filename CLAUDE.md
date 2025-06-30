# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The LLM Persona System is a behavioral prediction platform that transforms demographic data into authentic AI personas using Large Language Models (LLMs). It's designed for political campaigns, market research, and policy development, providing statistically significant predictions through 1000+ persona simulations.

## Technology Stack

- **Language**: Python 3.11+
- **LLM Provider**: OpenAI GPT-4 API
- **Database**: SQLite (for historical data and validation)
- **Architecture**: Firefly Architecture (ephemeral, purpose-driven agents)
- **No package management files** - Dependencies are managed externally

## Common Development Commands

```bash
# Run tests (no test framework detected - implement as needed)
python -m pytest poc/tests/

# Run a specific module
python poc/political_analyzer.py
python poc/market_researcher.py

# Database operations
sqlite3 poc/data/poll_history.db
sqlite3 poc/data/validation_results.db
```

## Architecture & Key Components

### Core System (`/poc/`)
- **PersonaConfig**: Defines demographic and psychographic attributes
- **PersonaLLMPromptBuilder**: Constructs system prompts that transform LLMs into personas
- **LLMPersonaFirefly**: Implements the Firefly lifecycle (birth → glow → disappear)

### Business Applications
- **PoliticalAnalyzer**: Predicts election outcomes and policy support
- **MarketResearcher**: Analyzes consumer behavior and preferences
- **SimulationEngine**: Manages large-scale persona simulations

### Data Management
- **PollDatabase**: Historical polling data for validation
- **CensusPersonaGenerator**: Creates representative persona distributions
- **ValidationFramework**: Compares predictions to historical outcomes

### Integration
- **PrismMindHandler**: Adapter for integration with larger PrismMind infrastructure
- Follows handler pattern for seamless system integration

## Firefly Architecture Pattern

Personas follow a three-phase lifecycle:
1. **Birth**: Created with specific demographic configuration
2. **Glow**: Transform LLM into persona and respond to stimuli
3. **Disappear**: Clean up resources after fulfilling purpose

This ensures efficient resource usage and prevents context contamination between simulations.

## Key Development Patterns

1. **Prompt Engineering**: System prompts in PersonaLLMPromptBuilder are critical for accuracy
2. **Statistical Significance**: Always run 1000+ personas for reliable predictions
3. **Validation**: Compare predictions against historical data in validation_results.db
4. **Handler Pattern**: All PrismMind integrations should follow the established handler interface

## API Keys and Configuration

- OpenAI API key required (set as environment variable: `OPENAI_API_KEY`)
- Cost considerations: ~$0.10 per 1000 personas with GPT-4

## Performance Considerations

- Firefly architecture minimizes memory usage through ephemeral agents
- Batch API calls when possible to reduce latency
- SQLite databases are optimized for read-heavy workloads