# 🤖 LLM API Setup Guide

## Quick Start Commands

### 1. Install Required Packages
```bash
pip install openai anthropic
```

### 2. Set API Keys (Choose One Method)

#### Method A: Environment Variables (Recommended)
```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# For Claude/Anthropic  
export ANTHROPIC_API_KEY="sk-ant-your-claude-api-key-here"

# Then run tests
python3 test_llm_integration.py
```

#### Method B: Command Line Arguments
```bash
# OpenAI
python3 test_llm_integration.py --openai-key "sk-your-key-here"

# Claude
python3 test_llm_integration.py --claude-key "sk-ant-your-key-here"

# Specify provider
python3 test_llm_integration.py --openai-key "sk-your-key" --provider openai
```

#### Method C: Interactive Mode
```bash
python3 test_llm_integration.py --interactive
# Will prompt you to enter API keys
```

#### Method D: Manual Configuration in Code
```python
# In your Python script
firefly = LLMPersonaFirefly(persona_config, purpose="test")
firefly.set_llm_config("openai", "sk-your-openai-key-here")
# or
firefly.set_llm_config("claude", "sk-ant-your-claude-key-here")
```

## 🎯 Test Commands

### Basic Tests
```bash
# Simple test with mock responses (no API key needed)
python3 test_simple_triggers.py

# LLM integration test (needs API key)
python3 test_llm_integration.py

# Interactive chat mode
python3 test_llm_integration.py --interactive

# Image generation test (needs OpenAI API key)
python3 test_image_generation.py

# Voice generation test (needs OpenAI API key)
python3 test_voice_generation.py

# Complete system demo (image + voice + LLM)
python3 complete_persona_demo.py

# Multi-provider LLM test (OpenAI + Claude + Ollama)
python3 test_multi_llm_integration.py

# Interactive multi-provider mode
python3 test_multi_llm_integration.py --interactive
```

### Advanced Tests
```bash
# Test specific persona with custom questions
python3 test_llm_integration.py \
  --persona-name "Maria Rodriguez" \
  --questions "What's your opinion on remote work?" "How do you use technology?"

# Use Claude API specifically
python3 test_llm_integration.py \
  --claude-key "sk-ant-your-key" \
  --provider claude

# Test conversation flow
python3 test_llm_integration.py --openai-key "sk-your-key"
```

## 🔑 Getting API Keys & Setup

### OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Set as environment variable: `export OPENAI_API_KEY="sk-your-key"`

### Claude/Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign in to your Anthropic account
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)
6. Set as environment variable: `export ANTHROPIC_API_KEY="sk-ant-your-key"`

### Ollama Setup (Local LLM)
1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Start Ollama service: `ollama serve`
3. Download a model: `ollama pull llama3:8b`
4. Verify: `ollama list` (should show installed models)
5. No API key needed - runs locally

## 💡 Usage Examples

### Example 1: Single Question with OpenAI
```bash
export OPENAI_API_KEY="sk-your-openai-key"
python3 test_llm_integration.py --questions "What do you think about AI?"
```

### Example 2: Interactive Chat with Claude
```bash
export ANTHROPIC_API_KEY="sk-ant-your-claude-key"
python3 test_llm_integration.py --interactive --provider claude
```

### Example 3: Market Research Simulation
```bash
export OPENAI_API_KEY="sk-your-key"
python3 test_llm_integration.py --persona-name "Sarah Johnson"
```

### Example 4: Custom Python Script
```python
import asyncio
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly

async def main():
    # Create persona
    persona = PersonaConfig(
        name="John Smith",
        age=45,
        race_ethnicity="white", 
        gender="male",
        education="college",
        location_type="suburban",
        income="75k_100k"
    )
    
    # Create firefly
    firefly = LLMPersonaFirefly(persona, purpose="my_test")
    
    # Set API key (or use environment variable)
    firefly.set_llm_config("openai", "sk-your-openai-key")
    
    # Ask question
    response = await firefly.glow({
        "prompt": "What's your opinion on electric vehicles?",
        "disappear": True
    })
    
    print(f"Response: {response['persona_response']}")

# Run it
asyncio.run(main())
```

### Example 5: Generate Persona Images
```python
from persona_config import PersonaConfig
from persona_image_generator import generate_persona_image_simple

# Create persona
persona = PersonaConfig(
    name="Maria Rodriguez",
    age=34,
    race_ethnicity="hispanic",
    gender="female",
    education="college",
    location_type="urban",
    income="50k_75k"
)

# Generate image (requires OPENAI_API_KEY)
result = generate_persona_image_simple(persona)

if result["success"]:
    print(f"Image URL: {result['image_url']}")
    print(f"Prompt used: {result['prompt']}")
else:
    print(f"Error: {result['error']}")
```

### Example 6: Generate Persona Voices
```python
from persona_config import PersonaConfig
from persona_voice_generator import generate_persona_voice_simple

# Create persona
persona = PersonaConfig(
    name="David Chen",
    age=42,
    race_ethnicity="asian",
    gender="male",
    education="graduate",
    location_type="suburban",
    income="75k_100k"
)

# Generate voice sample (requires OPENAI_API_KEY)
result = generate_persona_voice_simple(persona)

if result["success"]:
    print(f"Audio file: {result['audio_path']}")
    print(f"Voice used: {result['voice_used']}")
    print(f"Script: {result['script_text'][:100]}...")
else:
    print(f"Error: {result['error']}")

# Generate voice with custom text
custom_result = generate_persona_voice_simple(persona, 
    custom_text="I think remote work has changed everything for the better.")
```

### Example 7: Multi-Provider LLM Support
```python
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly

# Create persona
persona = PersonaConfig(
    name="Alex Rivera",
    age=30,
    race_ethnicity="hispanic",
    gender="non-binary",
    education="college",
    location_type="urban",
    income="50k_75k"
)

# Auto-detect available LLM provider
firefly = LLMPersonaFirefly(persona, purpose="multi_provider_test")
print(f"Using: {firefly.llm_provider} ({firefly.llm_model})")

# Or manually set provider
firefly.set_llm_config("ollama_local", model="llama3:8b")  # Local Ollama
firefly.set_llm_config("openai", "sk-your-key", "gpt-4")  # OpenAI
firefly.set_llm_config("claude", "sk-ant-your-key", "claude-3-sonnet-20240229")  # Claude

# Use persona
response = await firefly.glow({
    "prompt": "What's your opinion on artificial intelligence?",
    "disappear": True
})
```

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'openai'"**
   ```bash
   pip install openai anthropic
   ```

2. **"Invalid API key"**
   - Check your API key is correct
   - Make sure it's properly set in environment variables
   - For OpenAI: Key should start with `sk-`
   - For Claude: Key should start with `sk-ant-`

3. **"Mock responses only"**
   - This means no API key was detected
   - Set environment variables or use command line arguments

4. **Rate limit errors**
   - You've exceeded your API usage limits
   - Wait a moment and try again
   - Check your API usage on the provider's dashboard

## 📊 API Costs (Approximate)

### OpenAI GPT-4
- ~$0.03 per 1K input tokens
- ~$0.06 per 1K output tokens
- Typical persona response: ~$0.01-0.05

### OpenAI DALL-E 2 (Images)
- $0.020 per image (256x256)
- $0.018 per image (512x512)
- $0.020 per image (1024x1024)

### OpenAI TTS (Voice)
- $0.015 per 1K characters (TTS-1 model)
- $0.030 per 1K characters (TTS-1-HD model)
- Typical persona script: ~$0.002-0.005

### Claude Sonnet
- ~$0.003 per 1K input tokens  
- ~$0.015 per 1K output tokens
- Typical persona response: ~$0.005-0.02

### Cost-Saving Tips
- Use environment variables to avoid accidental key exposure
- Test with mock responses first (no cost)
- Start with shorter conversations
- Use Claude Haiku for lower costs (if available)

## 🔒 Security Best Practices

1. **Never commit API keys to code**
2. **Use environment variables**
3. **Rotate keys regularly**
4. **Set spending limits on API dashboards**
5. **Monitor usage regularly**

## 📞 Support

If you need help:
1. Check this guide first
2. Run basic tests: `python3 test_simple_triggers.py`
3. Try mock mode first: `python3 test_llm_integration.py` (no keys)
4. Check API key format and permissions
5. Review error messages for specific issues