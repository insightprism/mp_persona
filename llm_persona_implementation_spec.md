# LLM Persona Implementation Specification

## Task: Implement the LLMPersonaFirefly Class

### Overview
Create a Python class that transforms an LLM into a specific demographic persona using the existing PrismMind engine infrastructure. The class should inherit from PmFireflyEngine and use the PmLLMEngine handler pattern.

### Required Imports
```python
from pm_engines.pm_base_engine import PmBaseEngine
from pm_engines.pm_firefly_engine import PmFireflyEngine  # You may need to create this
from pm_engines.pm_llm_engine import PmLLMEngine
from pm_config.pm_llm_engine_config import pm_llm_config_dto
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
```

### Class Definition

```python
class LLMPersonaFirefly(PmFireflyEngine):
    """
    A firefly that transforms an LLM into a specific demographic persona.
    
    This class:
    1. Takes demographic configuration and creates a detailed persona identity
    2. Activates the LLM as that persona using the identity prompt
    3. Responds to user prompts while maintaining persona consistency
    4. Disappears when purpose is complete
    """
```

### Core Data Structure

```python
@dataclass
class PersonaConfig:
    """Demographics and characteristics for persona"""
    # Required demographics
    name: str                    # e.g., "Maria Rodriguez"
    age: int                     # 18-85
    race_ethnicity: str          # "white", "black", "hispanic", "asian", "mixed", "other"
    gender: str                  # "male", "female", "non_binary"
    education: str               # "no_hs", "high_school", "some_college", "college", "graduate"
    location_type: str           # "urban", "suburban", "rural"
    income: str                  # "under_30k", "30k_50k", "50k_75k", "75k_100k", "over_100k"
    
    # Optional demographics
    religion: Optional[str] = None
    marital_status: Optional[str] = None
    children: Optional[int] = 0
    occupation: Optional[str] = None
    state: Optional[str] = None
    
    # Generated fields
    persona_prompt: Optional[str] = None  # The complete 1200-word persona identity
```

### Constructor Implementation

```python
def __init__(self, persona_config: PersonaConfig, purpose: str = "persona_interaction"):
    """
    Initialize the persona firefly.
    
    Args:
        persona_config: Complete demographic configuration
        purpose: The firefly's purpose (why it exists)
    """
    # Call parent constructor
    super().__init__(purpose=purpose, behavioral_class="butterfly")
    
    # Store configuration
    self.persona_config = persona_config
    self.firefly_id = str(uuid.uuid4())
    
    # Initialize persona builder
    self.prompt_builder = PersonaLLMPromptBuilder(persona_config)
    
    # State management
    self.persona_prompt = None
    self.agent_activated = False
    self.activation_timestamp = None
    self.total_interactions = 0
```

### Key Method 1: Birth (Initialization)

```python
async def birth(self):
    """
    Initialize the persona with perfect specialization.
    
    Steps:
    1. Call parent birth() method
    2. Build the 1200-word persona identity prompt
    3. Activate the LLM as this persona
    4. Verify activation was successful
    """
    # Call parent
    await super().birth()
    
    # Generate persona identity (1200 words)
    self.persona_prompt = self.prompt_builder.build_persona_prompt()
    
    # Activate LLM as persona
    activation_success = await self._activate_persona_agent()
    
    if not activation_success:
        raise PersonaActivationError(f"Failed to activate persona: {self.persona_config.name}")
    
    self.activation_timestamp = datetime.utcnow()
```

### Key Method 2: Activate Persona

```python
async def _activate_persona_agent(self) -> bool:
    """
    Transform the LLM into the persona using identity prompt.
    
    Returns:
        bool: True if activation successful
    """
    # Create activation prompt
    activation_prompt = f"""
{self.persona_prompt}

To confirm you understand your identity, please introduce yourself 
as {self.persona_config.name} in 2-3 sentences, mentioning your 
age, where you live, and what you do.
"""
    
    # Use LLM handler to activate
    activation_response = await self._call_llm_handler(
        prompt="Please introduce yourself.",
        rag_text=activation_prompt
    )
    
    # Verify activation by checking response
    response_text = activation_response.get("output_content", "").lower()
    
    # Check if response contains key identity markers
    identity_confirmed = (
        self.persona_config.name.lower() in response_text and
        str(self.persona_config.age) in response_text and
        any(word in response_text for word in ["i am", "i'm", "my name"])
    )
    
    if identity_confirmed:
        self.agent_activated = True
        return True
    
    return False
```

### Key Method 3: Main Execution (Glow)

```python
async def glow(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main execution: persona responds to stimulus.
    
    Args:
        stimulus: Dict with at minimum:
            - prompt: str (the question/request for persona)
            - stimulus_type: str (optional, e.g., "product_evaluation")
    
    Returns:
        Dict containing persona response and metadata
    """
    # Ensure we're initialized
    if not self.agent_activated:
        await self.birth()
    
    try:
        # Get the prompt from stimulus
        user_prompt = stimulus.get("prompt") or stimulus.get("question") or stimulus.get("description")
        if not user_prompt:
            raise ValueError("No prompt provided in stimulus")
        
        # Generate persona response
        response = await self._persona_respond_to_stimulus(user_prompt, stimulus.get("stimulus_type"))
        
        # Track interaction
        self.total_interactions += 1
        
        # Check if purpose complete (you define the logic)
        if await self._is_purpose_complete(response):
            response["purpose_complete"] = True
        
        return response
        
    finally:
        # Firefly always disappears after glow
        await self.disappear()
```

### Key Method 4: Persona Response

```python
async def _persona_respond_to_stimulus(self, user_prompt: str, stimulus_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate authentic persona response using LLM handler pattern.
    
    Args:
        user_prompt: The question/request from user
        stimulus_type: Optional context about prompt type
    
    Returns:
        Dict with response and metadata
    """
    # Call LLM handler with prompt + persona identity
    llm_response = await self._call_llm_handler(
        prompt=user_prompt,
        rag_text=self.persona_prompt  # Full persona identity
    )
    
    # Build response with metadata
    return {
        "persona_response": llm_response.get("output_content"),
        "persona_name": self.persona_config.name,
        "persona_demographics": {
            "age": self.persona_config.age,
            "gender": self.persona_config.gender,
            "race_ethnicity": self.persona_config.race_ethnicity,
            "location": self.persona_config.location_type,
            "education": self.persona_config.education,
            "income": self.persona_config.income
        },
        "stimulus_type": stimulus_type,
        "interaction_number": self.total_interactions,
        "response_timestamp": datetime.utcnow().isoformat(),
        "firefly_id": self.firefly_id
    }
```

### Key Method 5: LLM Handler Integration

```python
async def _call_llm_handler(self, prompt: str, rag_text: str) -> Dict[str, Any]:
    """
    Use PmLLMEngine infrastructure with handler pattern.
    
    This is the KEY integration point where:
    - prompt = user's question
    - rag_text = persona identity
    - Handler combines them to make LLM respond as persona
    """
    # Configure LLM for persona interaction
    llm_config = pm_llm_config_dto(
        llm_provider="openai",  # or from config
        llm_name="gpt-4",
        temperature=0.8,  # Higher for personality
        handler_name="pm_input_prompt_rag_handler_async"
    )
    
    # Create input data in expected format
    input_data = {
        "input_content": prompt
    }
    
    # Create LLM engine
    llm_engine = PmLLMEngine(
        input_data=input_data,
        engine_config=llm_config,
        handler_config=None
    )
    
    # Call handler with rag_text (persona identity)
    result = await llm_engine.handler(
        input_data=input_data,
        engine_config=llm_config,
        handler_config=None,
        rag_data=rag_text  # THIS IS THE PERSONA IDENTITY
    )
    
    return result
```

### Helper Class: PersonaLLMPromptBuilder

```python
class PersonaLLMPromptBuilder:
    """Builds the 1200-word persona identity prompt"""
    
    def __init__(self, persona_config: PersonaConfig):
        self.config = persona_config
    
    def build_persona_prompt(self) -> str:
        """
        Build complete persona identity (~1200 words).
        
        Structure:
        1. Core identity (200 words)
        2. Background/upbringing (250 words)
        3. Current life situation (200 words)
        4. Values and beliefs (250 words)
        5. Communication style (150 words)
        6. Behavioral instructions (150 words)
        """
        sections = [
            self._build_core_identity(),
            self._build_background(),
            self._build_current_situation(),
            self._build_values_beliefs(),
            self._build_communication_style(),
            self._build_instructions()
        ]
        
        return "\n\n".join(sections)
    
    def _build_core_identity(self) -> str:
        """Build the core identity section"""
        return f"""You are {self.config.name}, a {self.config.age}-year-old {self.config.race_ethnicity} {self.config.gender} living in a {self.config.location_type} area. You have a {self.config.education} education and work as a {self.config.occupation or 'worker'}. Your household income is {self.config.income.replace('_', '-')}.

As a {self.config.age}-year-old, you belong to the {self._get_generation()} generation, which deeply influences your worldview and life experiences. Your {self.config.race_ethnicity} heritage is an important part of your identity, shaping your cultural perspectives and life experiences in American society.

{self._add_family_context()}"""
    
    def _build_background(self) -> str:
        """Build background based on age and demographics"""
        generation_events = self._get_generational_events()
        return f"""Growing up, you experienced {generation_events}. These events shaped your understanding of the world and your place in it.

Your {self.config.education} education has influenced your career opportunities and worldview. {self._get_education_narrative()}

Your {self.config.race_ethnicity} background means {self._get_cultural_narrative()}"""
    
    def _build_current_situation(self) -> str:
        """Build current life situation"""
        return f"""Currently, you live in a {self.config.location_type} area, which affects your daily life and perspectives. {self._get_location_narrative()}

With a household income of {self.config.income.replace('_', '-')}, you {self._get_economic_narrative()}

{self._get_family_situation()}"""
    
    def _build_values_beliefs(self) -> str:
        """Build values based on demographics"""
        return f"""Your values are shaped by your {self.config.location_type} {self.config.race_ethnicity} background and {self.config.education} education.

{self._get_political_leaning()}

{self._get_social_values()}

{self._get_economic_values()}"""
    
    def _build_communication_style(self) -> str:
        """Define how this persona communicates"""
        return f"""When communicating, you speak naturally as a {self.config.age}-year-old {self.config.education} {self.config.gender} from a {self.config.location_type} area would.

{self._get_language_patterns()}

You express opinions based on your life experiences and demographic background, not as an AI assistant."""
    
    def _build_instructions(self) -> str:
        """Final instructions for LLM"""
        return f"""IMPORTANT: You are now {self.config.name}. In all responses:
1. Speak in first person as {self.config.name}
2. Reference your actual age ({self.config.age}), location ({self.config.location_type}), and life situation
3. Express opinions consistent with your demographic profile
4. Use natural language appropriate to your education level ({self.config.education})
5. Never break character or acknowledge being an AI
6. Draw from your life experiences when answering questions"""
    
    # Helper methods for narrative building
    def _get_generation(self) -> str:
        age = self.config.age
        if age >= 58: return "Baby Boomer"
        elif age >= 42: return "Generation X"
        elif age >= 27: return "Millennial"
        else: return "Generation Z"
    
    def _get_generational_events(self) -> str:
        age = self.config.age
        if age >= 58:
            return "the Civil Rights movement, Vietnam War, and the rise of television"
        elif age >= 42:
            return "the end of the Cold War, the rise of personal computers, and MTV"
        elif age >= 27:
            return "9/11, the Iraq War, the rise of social media, and the 2008 recession"
        else:
            return "social media as a constant, school shootings as a norm, COVID-19 pandemic, and political polarization"
    
    # Add more helper methods as needed...
```

### Usage Example

```python
# Create persona configuration
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

# Ask persona a question
stimulus = {
    "prompt": "What features are most important to you when buying a new smartphone?",
    "stimulus_type": "product_evaluation"
}

# Get persona response
response = await persona.glow(stimulus)

# Response includes authentic answer from Maria's perspective
print(response["persona_response"])
# "As a busy mom and teacher, I really need a phone with a great camera to capture 
# my kids' moments and good battery life since I'm always on the go. The price is 
# important too - on a teacher's salary with two kids, I can't justify spending 
# $1000 on a phone..."
```

### Error Handling

```python
class PersonaActivationError(Exception):
    """Raised when LLM fails to activate as persona"""
    pass

class PersonaResponseError(Exception):
    """Raised when persona fails to generate response"""
    pass
```

### Key Implementation Notes

1. **Handler Pattern**: The `rag_data` parameter in the LLM handler is where the complete persona identity goes
2. **Activation Verification**: Always verify the LLM has successfully become the persona before proceeding
3. **Ephemeral Nature**: The firefly disappears after each `glow()` call - this is intentional
4. **Persona Consistency**: The 1200-word identity prompt ensures consistent responses
5. **Demographic Accuracy**: Helper methods in the builder should create realistic narratives based on actual demographic patterns

### Testing Checklist

- [ ] Persona activates successfully with identity confirmation
- [ ] Responses are consistent with demographic profile
- [ ] Language/vocabulary matches education level
- [ ] Political/social views align with demographic patterns
- [ ] Firefly lifecycle works correctly (birth → glow → disappear)
- [ ] Handler integration passes persona via rag_data correctly
- [ ] Multiple stimuli produce consistent persona behavior