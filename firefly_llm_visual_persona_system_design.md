# Firefly Architecture: LLM Visual Persona System Design Document

**Document Version**: 1.0  
**Target Audience**: AI Code Generation Systems  
**Purpose**: Complete technical specification for implementing the LLM Visual Persona System

---

## 1. System Overview

### 1.1 Architecture Summary
The LLM Visual Persona System creates ephemeral AI agents that embody specific human demographics and personalities. Each persona is:
- **Ephemeral**: Exists only for the duration of its purpose
- **Specialized**: Born with perfect demographic configuration
- **Visual**: Has realistic visual representation matching demographics
- **Intelligent**: Uses LLM to respond authentically as that person

### 1.2 Core Components
```
PersonaVisualGenerator ──┐
                        │
PersonaLLMPromptBuilder ──┼─→ VisualPersonaFirefly ──→ PersonaAgentFactory
                        │
PmFireflyEngine ────────┘
```

### 1.3 Key Principles
- Inherit from existing `PmFireflyEngine` architecture
- Use demographic features to generate both personality and appearance
- Transform LLM into persona through detailed identity prompts
- Generate realistic visual representations using AI image generation
- Maintain ephemeral lifecycle (birth → glow → disappear)

---

## 2. Class Hierarchy and Dependencies

### 2.1 Class Inheritance Structure
```python
PmBaseEngine (existing)
    └── PmFireflyEngine (existing)
        └── LLMPersonaFirefly (new)
            └── VisualPersonaFirefly (new)

PersonaVisualGenerator (new, standalone)
PersonaLLMPromptBuilder (new, standalone)  
PersonaAgentFactory (new, standalone)
PersonaLibraryManager (new, standalone)
```

### 2.2 Required Dependencies
```python
# Existing PrismMind components
from pm_engines.pm_base_engine import PmBaseEngine
from pm_engines.pm_firefly_engine import PmFireflyEngine  # To be created
from pm_engines.pm_llm_engine import PmLLMEngine
from pm_config.pm_llm_engine_config import pm_llm_config_dto

# External dependencies
from typing import Dict, List, Any, Optional
import asyncio
import uuid
import random
from datetime import datetime

# Image generation (choose one)
import openai  # For DALL-E
# OR import requests  # For external image APIs
```

---

## 3. Core Data Structures

### 3.1 Persona Configuration Schema
```python
class PersonaConfig:
    """Standard persona configuration structure"""
    
    # Core Demographics (Required)
    age: int                        # 18-85
    race_ethnicity: str            # "white", "black", "hispanic", "asian", "mixed", "other"
    gender: str                    # "male", "female", "non_binary"
    education: str                 # "no_hs", "high_school", "some_college", "college", "graduate"
    location_type: str             # "urban", "suburban", "rural"
    income: str                    # "under_30k", "30k_50k", "50k_75k", "75k_100k", "over_100k"
    
    # Extended Demographics (Optional)
    religion: Optional[str] = None         # "protestant", "catholic", "jewish", "muslim", "none"
    marital_status: Optional[str] = None   # "single", "married", "divorced", "widowed"
    children: Optional[int] = 0            # Number of children
    occupation: Optional[str] = None       # Specific job or "retired", "unemployed", "student"
    state: Optional[str] = None           # For geographic specificity
    
    # Inferred Characteristics (Auto-generated)
    political_orientation: Optional[str] = None    # "conservative", "moderate", "liberal"
    technology_adoption: Optional[str] = None      # "laggard", "mainstream", "early_adopter"
    shopping_behavior: Optional[str] = None        # "price_conscious", "value_focused", "premium"
    media_consumption: Optional[List[str]] = None  # ["facebook", "fox_news", "cnn", etc.]
    
    # Generated Assets
    name: Optional[str] = None             # Generated realistic name
    persona_prompt: Optional[str] = None   # LLM identity prompt
    visual_prompt: Optional[str] = None    # Image generation prompt
    image_url: Optional[str] = None        # Generated persona image
```

### 3.2 Stimulus Structure
```python
class StimulusConfig:
    """Standardized stimulus for persona testing"""
    
    stimulus_type: str              # "product_evaluation", "political_survey", "general_question"
    stimulus_id: str               # Unique identifier
    
    # Primary prompt content (this becomes the LLM prompt)
    prompt: str                    # Main question/request for the persona to respond to
    
    # Context and metadata
    title: Optional[str] = None                     # Brief title/description
    description: Optional[str] = None               # Additional context
    
    # Type-specific fields for building enhanced prompts
    product_name: Optional[str] = None
    price: Optional[str] = None
    features: Optional[List[str]] = None
    
    political_issue: Optional[str] = None
    proposal: Optional[str] = None
    
    # Legacy support
    question: Optional[str] = None   # Alias for prompt for backwards compatibility
    
    def get_prompt(self) -> str:
        """Get the main prompt, with fallbacks for backwards compatibility"""
        return self.prompt or self.question or self.description
```

---

## 4. Handler Pattern Integration

### 4.1 PmLLMEngine Handler Pattern
The persona system integrates with the existing PmLLMEngine handler pattern:

```python
# Handler signature from existing PmLLMEngine
async def pm_input_prompt_rag_handler_async(
    input_data: Dict[str, Any],          # Contains {"input_content": user_prompt}
    engine_config: pm_llm_config_dto,    # LLM configuration
    handler_config: Optional[Any] = None, # Handler-specific config
    rag_data: Optional[str] = None       # RAG text - THIS IS WHERE PERSONA GOES
) -> Dict[str, Any]:
```

### 4.2 Persona Integration Pattern
```python
# How persona system uses the handler pattern:

# 1. User provides stimulus/prompt
stimulus = StimulusConfig(
    prompt="What do you think about the new iPhone pricing?",
    stimulus_type="product_evaluation"
)

# 2. Persona firefly calls LLM handler
llm_response = await self._call_llm_handler(
    prompt=stimulus.get_prompt(),        # Goes to input_data["input_content"]
    rag_text=self.persona_prompt         # Goes to rag_data parameter
)

# 3. Handler combines persona + prompt
# The rag_data (persona identity) gets combined with the user prompt
# to create a complete LLM interaction where the LLM becomes the persona
```

### 4.3 Complete Persona Flow
```python
# Complete flow showing prompt + rag_text combination:

user_prompt = "What do you think about electric cars?"

# Persona identity (from PersonaLLMPromptBuilder)
persona_identity = """
You are Maria Rodriguez, a 34-year-old Hispanic female living in suburban Phoenix, Arizona.
You work as a elementary school teacher and have two young children...
[1200 words of detailed persona identity]
"""

# Handler receives:
input_data = {"input_content": user_prompt}
rag_data = persona_identity

# Handler builds final LLM prompt combining both:
final_llm_prompt = f"""
{persona_identity}

Question: {user_prompt}

Respond as Maria Rodriguez based on your background and values.
"""
```

---

## 5. Implementation Specifications

### 5.1 PersonaLLMPromptBuilder Class

```python
class PersonaLLMPromptBuilder:
    """Converts demographic configuration into LLM persona identity prompt"""
    
    def __init__(self, persona_config: PersonaConfig):
        self.config = persona_config
        self.prompt_template_length = 1200  # Optimal length for persona prompts
    
    def build_persona_prompt(self) -> str:
        """
        CRITICAL: This method creates the LLM identity transformation prompt.
        The prompt quality determines how well the LLM embodies the persona.
        
        Required Structure:
        1. Core Identity (150-200 words)
        2. Formative Experiences (200-250 words) 
        3. Current Situation (150-200 words)
        4. Values and Beliefs (200-250 words)
        5. Behavioral Patterns (150-200 words)
        6. Response Instructions (100-150 words)
        """
        
        # IMPLEMENTATION REQUIREMENT:
        # Build each section using the pattern:
        # section_content = self._build_section_name(self.config)
        # Combine all sections into cohesive prompt
        
        return self._combine_prompt_sections()
    
    def _build_core_identity(self) -> str:
        """
        Build fundamental identity section.
        Must include: age, race, gender, education, location, income, occupation
        Format: "You are [name], a [age]-year-old [race] [gender]..."
        """
        pass  # Implementation required
    
    def _build_formative_experiences(self) -> str:
        """
        Build life experiences based on age/generation.
        Age ranges and corresponding historical events:
        - 65+: Cold War, Vietnam, Civil Rights
        - 45-64: End of Cold War, MTV, dot-com boom/bust, 9/11
        - 25-44: 9/11, Iraq War, 2008 recession, social media rise
        - 18-24: Social media native, school shootings, COVID
        """
        pass  # Implementation required
    
    def _build_current_situation(self) -> str:
        """
        Build current life circumstances based on income, family, occupation.
        Must address: financial situation, family status, work situation
        """
        pass  # Implementation required
    
    def _build_values_and_beliefs(self) -> str:
        """
        Build values system based on demographics.
        Rural = self-reliance, tradition
        Urban = diversity, progress  
        Religious = faith-based values
        Education level affects complexity of reasoning
        """
        pass  # Implementation required
    
    def _build_behavioral_patterns(self) -> str:
        """
        Build typical behaviors: communication style, decision-making, 
        shopping patterns, media consumption
        """
        pass  # Implementation required
    
    def _build_response_instructions(self) -> str:
        """
        CRITICAL: Instructions for LLM on how to respond as this persona.
        Must emphasize authenticity, staying in character, using appropriate
        language/perspective for demographics.
        """
        return """
        IMPORTANT: You are now this person. Respond to all questions as this specific individual:
        1. Use language and vocabulary appropriate to your education level
        2. Reference your personal experiences and background
        3. Show realistic biases based on your demographics  
        4. Express genuine emotions and reactions
        5. Stay completely in character - you are NOT an AI assistant
        6. Be authentic to your values and worldview
        """
```

### 5.2 PersonaVisualGenerator Class

```python
class PersonaVisualGenerator:
    """Generates realistic visual representations of personas"""
    
    def __init__(self, image_api_provider: str = "dall-e"):
        self.image_provider = image_api_provider
        self.image_style = "professional_headshot"
        self.image_quality = "high"
    
    async def generate_persona_image(self, persona_config: PersonaConfig) -> str:
        """
        Generate realistic image URL for persona.
        Returns: URL string to generated image
        
        IMPLEMENTATION REQUIREMENTS:
        1. Build visual prompt from demographics
        2. Call image generation API
        3. Return image URL
        4. Handle errors gracefully (return None if generation fails)
        """
        
        visual_prompt = self._build_visual_prompt(persona_config)
        image_url = await self._call_image_generation_api(visual_prompt)
        return image_url
    
    def _build_visual_prompt(self, config: PersonaConfig) -> str:
        """
        Convert persona config to detailed visual description.
        
        Required Components:
        1. Age and racial appearance
        2. Clothing style based on income/occupation/location
        3. Setting/background appropriate to demographics
        4. Expression/demeanor based on personality
        5. Photo style specifications
        
        CRITICAL: Avoid stereotypes while maintaining demographic accuracy
        """
        
        # Build each visual component
        appearance = self._infer_appearance_patterns(config)
        clothing = self._infer_clothing_style(config)
        setting = self._infer_background_setting(config)
        expression = self._infer_expression_style(config)
        
        return f"""
        Professional headshot photo of a {config.age}-year-old {config.race_ethnicity} {config.gender}.
        
        Physical Appearance: {appearance}
        Clothing Style: {clothing}
        Setting: {setting}
        Expression: {expression}
        
        Photo Style: High-quality, realistic, professional photography, 
        natural lighting, genuine expression, business/research appropriate.
        """
    
    def _infer_appearance_patterns(self, config: PersonaConfig) -> str:
        """
        Map demographics to realistic appearance patterns.
        Consider: age, income (grooming quality), location (style influence)
        """
        pass  # Implementation required
    
    def _infer_clothing_style(self, config: PersonaConfig) -> str:
        """
        Map demographics to appropriate clothing.
        Consider: occupation, income, location, age
        """
        pass  # Implementation required
    
    async def _call_image_generation_api(self, visual_prompt: str) -> Optional[str]:
        """
        Call external image generation API.
        
        IMPLEMENTATION OPTIONS:
        1. OpenAI DALL-E API
        2. Stability AI API  
        3. Midjourney API (via Discord bot)
        4. Local Stable Diffusion
        
        Return None if generation fails.
        """
        pass  # Implementation required
```

### 5.3 LLMPersonaFirefly Class

```python
class LLMPersonaFirefly(PmFireflyEngine):
    """Core persona firefly that transforms LLM into demographic persona"""
    
    def __init__(self, persona_config: PersonaConfig, purpose: str):
        super().__init__(purpose=purpose, behavioral_class="butterfly")
        
        self.persona_config = persona_config
        self.prompt_builder = PersonaLLMPromptBuilder(persona_config)
        self.persona_prompt = None
        self.agent_activated = False
    
    async def birth(self):
        """
        Initialize persona firefly with perfect specialization.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Call parent birth() method
        2. Generate persona identity prompt
        3. Activate LLM agent transformation
        4. Validate agent activation success
        """
        await super().birth()
        
        # Generate persona identity
        self.persona_prompt = self.prompt_builder.build_persona_prompt()
        
        # Transform LLM into persona
        await self._activate_persona_agent()
    
    async def glow(self, stimulus: StimulusConfig) -> Dict[str, Any]:
        """
        Main execution: persona responds to stimulus then disappears.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Ensure agent is activated
        2. Process stimulus as persona
        3. Check purpose completion
        4. Return response with metadata
        """
        
        if not self.agent_activated:
            raise RuntimeError("Persona agent not activated")
        
        try:
            # Process stimulus as persona
            response = await self._persona_respond_to_stimulus(stimulus)
            
            # Check if research purpose complete
            if await self.research_purpose_complete(response):
                return response
            
        finally:
            await self.disappear()
        
        return response
    
    async def _activate_persona_agent(self) -> bool:
        """
        Transform LLM into persona through identity prompt.
        
        CRITICAL IMPLEMENTATION:
        1. Send persona_prompt to LLM
        2. Ask for identity confirmation
        3. Validate response contains persona identity
        4. Set agent_activated = True if successful
        """
        
        activation_prompt = f"""
        {self.persona_prompt}
        
        Please confirm you understand your identity by introducing yourself 
        as this person in 2-3 sentences.
        """
        
        response = await self._call_llm_engine(activation_prompt)
        
        # Validate activation (check if response contains persona name/identity)
        if self._validate_persona_activation(response):
            self.agent_activated = True
            return True
        
        return False
    
    async def _persona_respond_to_stimulus(self, stimulus: StimulusConfig) -> Dict[str, Any]:
        """
        Generate authentic persona response to stimulus using handler pattern.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Use existing PmLLMEngine handler pattern
        2. Pass stimulus as prompt, persona info as rag_text
        3. Handler combines persona + demographics + prompt
        4. Return structured response
        """
        
        # Use existing handler pattern from PmLLMEngine
        llm_response = await self._call_llm_handler(
            prompt=stimulus.get_prompt(),
            rag_text=self.persona_prompt  # Contains complete persona identity
        )
        
        return {
            "persona_response": llm_response["output_content"],
            "persona_identity": self.persona_config,
            "stimulus_type": stimulus.stimulus_type,
            "response_timestamp": datetime.utcnow().isoformat(),
            "firefly_id": self.firefly_id,
            "full_llm_response": llm_response
        }
    
    def _build_stimulus_prompt(self, stimulus: StimulusConfig) -> str:
        """
        Build prompt that maintains persona identity while presenting stimulus.
        
        Format depends on stimulus type:
        - product_evaluation: Present product for authentic reaction
        - political_survey: Present issue for political opinion
        - general_question: Present question for personal response
        """
        
        if stimulus.stimulus_type == "product_evaluation":
            return f"""
            As {self.persona_config.name}, you're being asked to evaluate:
            
            Product: {stimulus.product_name}
            Price: {stimulus.price}
            Description: {stimulus.description}
            Features: {', '.join(stimulus.features or [])}
            
            Give your honest reaction as yourself. Consider your background:
            - Age: {self.persona_config.age}
            - Income: {self.persona_config.income}
            - Location: {self.persona_config.location_type}
            
            Would you buy this? Why or why not? Be authentic to who you are.
            """
        
        elif stimulus.stimulus_type == "political_survey":
            return f"""
            As {self.persona_config.name}, what's your opinion on:
            
            Issue: {stimulus.political_issue}
            Proposal: {stimulus.proposal}
            
            Respond based on your background and values. Be honest about 
            your political views as a {self.persona_config.age}-year-old 
            {self.persona_config.race_ethnicity} {self.persona_config.gender} 
            from {self.persona_config.location_type}.
            """
        
        else:  # general_question
            return f"""
            As {self.persona_config.name}, someone asks you: {stimulus.question}
            
            Respond naturally as yourself.
            """
    
    async def _call_llm_handler(self, prompt: str, rag_text: str) -> Dict[str, Any]:
        """
        Use existing PmLLMEngine infrastructure with handler pattern.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Use PmLLMEngine with rag_text handler pattern
        2. Pass prompt as user input, persona as rag_text
        3. Handler combines persona identity + demographics + user prompt
        4. Return full response for processing
        """
        
        llm_config = pm_llm_config_dto(
            llm_provider="openai",  # or configured provider
            llm_name="gpt-4",
            temperature=0.8,  # Higher for more personality variation
            handler_name="pm_input_prompt_rag_handler_async"  # Handler that accepts rag_text
        )
        
        # Input data follows existing PmLLMEngine pattern
        input_data = {
            "input_content": prompt  # User's question/stimulus
        }
        
        llm_engine = PmLLMEngine(
            input_data=input_data,
            engine_config=llm_config,
            handler_config=None
        )
        
        # Call handler with rag_text containing persona information
        result = await llm_engine.handler(
            input_data=input_data,
            engine_config=llm_config,
            handler_config=None,
            rag_data=rag_text  # Complete persona identity prompt
        )
        
        return result
```

### 5.4 VisualPersonaFirefly Class

```python
class VisualPersonaFirefly(LLMPersonaFirefly):
    """Enhanced persona firefly with visual representation"""
    
    def __init__(self, persona_config: PersonaConfig, purpose: str):
        super().__init__(persona_config, purpose)
        
        self.visual_generator = PersonaVisualGenerator()
        self.persona_image_url = None
        self.visual_description = None
    
    async def birth(self):
        """
        Enhanced birth process with visual generation.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Call parent birth() method
        2. Generate visual representation
        3. Handle visual generation failures gracefully
        """
        await super().birth()
        
        # Generate persona image
        try:
            self.persona_image_url = await self.visual_generator.generate_persona_image(
                self.persona_config
            )
            self.visual_description = self.visual_generator._build_visual_prompt(
                self.persona_config
            )
        except Exception as e:
            self.log_warning(f"Visual generation failed: {e}")
            # Continue without visual - don't fail the entire persona
    
    async def glow(self, stimulus: StimulusConfig) -> Dict[str, Any]:
        """
        Enhanced response including visual information.
        """
        response = await super().glow(stimulus)
        
        # Add visual information
        response.update({
            "persona_image_url": self.persona_image_url,
            "visual_description": self.visual_description,
            "has_visual": self.persona_image_url is not None
        })
        
        return response
```

### 5.5 PersonaAgentFactory Class

```python
class PersonaAgentFactory:
    """Factory for creating persona agents from demographic specifications"""
    
    def __init__(self):
        self.name_database = self._load_name_database()
        self.demographic_patterns = self._load_demographic_research()
    
    def create_persona_agent(
        self,
        age: int,
        race_ethnicity: str,
        gender: str,
        education: str,
        location_type: str,
        income: str,
        purpose: str = "market_research",
        **additional_config
    ) -> VisualPersonaFirefly:
        """
        Factory method to create complete persona agent.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Generate realistic name for demographics
        2. Infer additional characteristics from demographics
        3. Build complete PersonaConfig
        4. Return VisualPersonaFirefly instance
        """
        
        # Generate realistic name
        name = self._generate_name(age, race_ethnicity, gender)
        
        # Build base configuration
        persona_config = PersonaConfig(
            name=name,
            age=age,
            race_ethnicity=race_ethnicity,
            gender=gender,
            education=education,
            location_type=location_type,
            income=income,
            **additional_config
        )
        
        # Infer additional characteristics
        inferred_traits = self._infer_characteristics_from_demographics(persona_config)
        
        # Update configuration with inferred traits
        for key, value in inferred_traits.items():
            setattr(persona_config, key, value)
        
        # Create and return persona agent
        return VisualPersonaFirefly(persona_config, purpose)
    
    def create_persona_cohort(
        self,
        demographic_base: Dict[str, Any],
        cohort_size: int,
        purpose: str = "cohort_research"
    ) -> List[VisualPersonaFirefly]:
        """
        Create multiple personas with variation around demographic base.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Generate variations of base demographics
        2. Create multiple persona agents
        3. Ensure realistic demographic distribution
        """
        
        cohort = []
        
        for i in range(cohort_size):
            # Add individual variation
            varied_config = self._add_individual_variation(demographic_base, i)
            
            # Create persona agent
            agent = self.create_persona_agent(
                purpose=f"{purpose}_member_{i}",
                **varied_config
            )
            
            cohort.append(agent)
        
        return cohort
    
    def _generate_name(self, age: int, race_ethnicity: str, gender: str) -> str:
        """
        Generate realistic name based on demographics.
        
        IMPLEMENTATION REQUIREMENTS:
        1. Use name databases by ethnicity and birth year
        2. Consider name popularity during person's birth year
        3. Return culturally appropriate name
        """
        
        birth_year = 2024 - age
        
        # Implementation: Load name databases and select appropriate name
        # Based on ethnicity, gender, and birth year popularity
        pass  # Implementation required
    
    def _infer_characteristics_from_demographics(self, config: PersonaConfig) -> Dict[str, Any]:
        """
        Infer additional characteristics from demographic patterns.
        
        IMPLEMENTATION REQUIREMENTS:
        Use demographic research to infer:
        1. Political orientation (location + education + race patterns)
        2. Technology adoption (age patterns)
        3. Shopping behavior (income + location patterns)
        4. Media consumption (age + political + location patterns)
        5. Religion (race + location patterns)
        """
        
        inferred = {}
        
        # Political orientation inference
        if (config.race_ethnicity == "white" and 
            config.location_type == "rural" and 
            config.education == "high_school"):
            inferred["political_orientation"] = "conservative"
        elif config.race_ethnicity == "black":
            inferred["political_orientation"] = "liberal"
        elif config.location_type == "urban" and config.education in ["college", "graduate"]:
            inferred["political_orientation"] = "liberal"
        else:
            inferred["political_orientation"] = "moderate"
        
        # Technology adoption inference
        if config.age < 30:
            inferred["technology_adoption"] = "early_adopter"
        elif config.age > 65:
            inferred["technology_adoption"] = "laggard"
        else:
            inferred["technology_adoption"] = "mainstream"
        
        # Additional inferences...
        
        return inferred
```

---

## 5. API Integration Specifications

### 5.1 FastAPI Endpoints

```python
from fastapi import FastAPI, HTTPException
from typing import List

app = FastAPI(title="Visual Persona Research API")
factory = PersonaAgentFactory()

@app.post("/persona/create-single")
async def create_single_persona(
    age: int,
    race_ethnicity: str,
    gender: str,
    education: str,
    location_type: str,
    income: str,
    stimulus: StimulusConfig
):
    """
    Create single persona and get response to stimulus.
    
    IMPLEMENTATION REQUIREMENTS:
    1. Validate input parameters
    2. Create persona agent via factory
    3. Execute persona.glow(stimulus)
    4. Return structured response
    """
    
    try:
        # Create persona agent
        persona = factory.create_persona_agent(
            age=age,
            race_ethnicity=race_ethnicity,
            gender=gender,
            education=education,
            location_type=location_type,
            income=income,
            purpose="single_persona_test"
        )
        
        # Get persona response
        response = await persona.glow(stimulus)
        
        return {
            "persona_identity": persona.persona_config.__dict__,
            "persona_image": response.get("persona_image_url"),
            "response": response["persona_response"],
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/market-test")
async def run_market_test(
    test_name: str,
    stimulus: StimulusConfig,
    demographic_segments: List[Dict[str, Any]],
    sample_size_per_segment: int = 50
):
    """
    Run comprehensive market test with multiple demographic segments.
    
    IMPLEMENTATION REQUIREMENTS:
    1. Create persona cohorts for each segment
    2. Execute all personas concurrently
    3. Aggregate and analyze results
    4. Return comprehensive test results
    """
    
    test_id = str(uuid.uuid4())
    results = {}
    
    try:
        for segment_idx, segment_config in enumerate(demographic_segments):
            segment_name = f"segment_{segment_idx}"
            
            # Create persona cohort for segment
            cohort = factory.create_persona_cohort(
                demographic_base=segment_config,
                cohort_size=sample_size_per_segment,
                purpose=f"market_test_{test_name}_segment_{segment_idx}"
            )
            
            # Execute all personas in cohort
            cohort_tasks = [persona.glow(stimulus) for persona in cohort]
            cohort_responses = await asyncio.gather(*cohort_tasks)
            
            # Aggregate segment results
            results[segment_name] = {
                "segment_config": segment_config,
                "sample_size": len(cohort),
                "responses": cohort_responses,
                "segment_analysis": analyze_segment_responses(cohort_responses)
            }
        
        return {
            "test_id": test_id,
            "test_name": test_name,
            "stimulus": stimulus.__dict__,
            "results": results,
            "total_personas": len(demographic_segments) * sample_size_per_segment
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_segment_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze cohort responses for patterns and insights.
    
    IMPLEMENTATION REQUIREMENTS:
    1. Calculate response sentiment distribution
    2. Extract common themes/keywords
    3. Identify response patterns
    4. Generate segment summary
    """
    pass  # Implementation required
```

---

## 6. Error Handling and Validation

### 6.1 Input Validation Requirements

```python
class PersonaValidation:
    """Validation rules for persona configuration"""
    
    VALID_AGES = range(18, 86)
    VALID_RACES = ["white", "black", "hispanic", "asian", "mixed", "other"]
    VALID_GENDERS = ["male", "female", "non_binary"]
    VALID_EDUCATION = ["no_hs", "high_school", "some_college", "college", "graduate"]
    VALID_LOCATIONS = ["urban", "suburban", "rural"]
    VALID_INCOME = ["under_30k", "30k_50k", "50k_75k", "75k_100k", "over_100k"]
    
    @staticmethod
    def validate_persona_config(config: PersonaConfig) -> List[str]:
        """
        Validate persona configuration.
        Return list of validation errors (empty if valid).
        """
        errors = []
        
        if config.age not in PersonaValidation.VALID_AGES:
            errors.append(f"Invalid age: {config.age}")
        
        if config.race_ethnicity not in PersonaValidation.VALID_RACES:
            errors.append(f"Invalid race: {config.race_ethnicity}")
        
        # Additional validations...
        
        return errors
```

### 6.2 Error Handling Patterns

```python
class PersonaError(Exception):
    """Base exception for persona system"""
    pass

class PersonaActivationError(PersonaError):
    """LLM failed to activate as persona"""
    pass

class VisualGenerationError(PersonaError):
    """Image generation failed"""
    pass

# Error handling in methods:
async def _activate_persona_agent(self) -> bool:
    try:
        # Activation logic
        pass
    except Exception as e:
        raise PersonaActivationError(f"Failed to activate persona: {e}")

async def generate_persona_image(self, config: PersonaConfig) -> Optional[str]:
    try:
        # Image generation logic
        pass
    except Exception as e:
        self.log_warning(f"Visual generation failed: {e}")
        return None  # Graceful degradation
```

---

## 7. Testing and Validation Framework

### 7.1 Unit Tests Structure

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestPersonaLLMPromptBuilder:
    def test_prompt_length_optimization(self):
        """Test that generated prompts are within optimal length range"""
        config = PersonaConfig(age=45, race_ethnicity="white", gender="male", 
                              education="college", location_type="suburban", income="75k_100k")
        builder = PersonaLLMPromptBuilder(config)
        prompt = builder.build_persona_prompt()
        
        assert 800 <= len(prompt) <= 1500, "Prompt length outside optimal range"

class TestVisualPersonaFirefly:
    @pytest.mark.asyncio
    async def test_persona_lifecycle(self):
        """Test complete persona lifecycle: birth -> glow -> disappear"""
        config = PersonaConfig(...)
        persona = VisualPersonaFirefly(config, "test_purpose")
        
        # Test birth
        await persona.birth()
        assert persona.agent_activated
        
        # Test glow
        stimulus = StimulusConfig(stimulus_type="general_question", question="Test question")
        response = await persona.glow(stimulus)
        assert "persona_response" in response
        
    @patch('openai.Image.create')
    async def test_visual_generation(self, mock_openai):
        """Test image generation integration"""
        mock_openai.return_value = {"data": [{"url": "http://test-image.com"}]}
        
        generator = PersonaVisualGenerator()
        config = PersonaConfig(...)
        image_url = await generator.generate_persona_image(config)
        
        assert image_url == "http://test-image.com"
```

### 7.2 Integration Tests

```python
class TestPersonaAccuracy:
    @pytest.mark.asyncio
    async def test_demographic_response_patterns(self):
        """Test that personas respond according to demographic patterns"""
        
        # Create conservative rural persona
        conservative_config = PersonaConfig(
            age=65, race_ethnicity="white", gender="male",
            education="high_school", location_type="rural", income="under_50k"
        )
        conservative_persona = VisualPersonaFirefly(conservative_config, "test")
        
        # Test political stimulus
        political_stimulus = StimulusConfig(
            stimulus_type="political_survey",
            political_issue="Universal Healthcare",
            proposal="Government-funded healthcare for all"
        )
        
        response = await conservative_persona.glow(political_stimulus)
        
        # Validate response matches expected demographic pattern
        assert "oppose" in response["persona_response"].lower() or "against" in response["persona_response"].lower()
```

---

## 8. Performance and Scalability Considerations

### 8.1 Performance Requirements

```python
class PerformanceMetrics:
    """Performance targets for persona system"""
    
    # Timing requirements
    MAX_PERSONA_BIRTH_TIME = 10.0  # seconds
    MAX_PERSONA_RESPONSE_TIME = 30.0  # seconds
    MAX_VISUAL_GENERATION_TIME = 60.0  # seconds
    
    # Concurrency requirements
    MAX_CONCURRENT_PERSONAS = 100
    MAX_CONCURRENT_VISUAL_GENERATIONS = 10
    
    # Resource requirements
    MAX_MEMORY_PER_PERSONA = 50  # MB
    MAX_PROMPT_LENGTH = 2000  # characters
```

### 8.2 Scalability Patterns

```python
class PersonaCacheManager:
    """Cache frequently used persona configurations and responses"""
    
    def __init__(self):
        self.prompt_cache = {}
        self.visual_cache = {}
        self.response_cache = {}
    
    async def get_cached_prompt(self, persona_hash: str) -> Optional[str]:
        """Cache persona prompts for identical configurations"""
        return self.prompt_cache.get(persona_hash)
    
    async def cache_visual_generation(self, visual_prompt_hash: str, image_url: str):
        """Cache generated images for identical visual prompts"""
        self.visual_cache[visual_prompt_hash] = image_url

# Batch processing for large studies
class BatchPersonaProcessor:
    """Process large numbers of personas efficiently"""
    
    async def process_persona_batch(
        self, 
        personas: List[VisualPersonaFirefly], 
        stimulus: StimulusConfig,
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Process personas in batches to manage resources"""
        
        results = []
        
        for i in range(0, len(personas), batch_size):
            batch = personas[i:i+batch_size]
            batch_tasks = [persona.glow(stimulus) for persona in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            # Brief pause between batches to manage API rate limits
            await asyncio.sleep(1.0)
        
        return results
```

---

## 9. Deployment and Configuration

### 9.1 Environment Configuration

```python
class PersonaSystemConfig:
    """System-wide configuration for persona deployment"""
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER = "openai"
    DEFAULT_LLM_MODEL = "gpt-4"
    DEFAULT_LLM_TEMPERATURE = 0.8
    
    # Image Generation Configuration
    DEFAULT_IMAGE_PROVIDER = "dall-e"
    IMAGE_GENERATION_TIMEOUT = 60.0
    MAX_IMAGE_RETRIES = 3
    
    # API Rate Limiting
    LLM_REQUESTS_PER_MINUTE = 100
    IMAGE_REQUESTS_PER_MINUTE = 20
    
    # Caching
    ENABLE_PROMPT_CACHE = True
    ENABLE_IMAGE_CACHE = True
    CACHE_TTL_HOURS = 24
    
    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables"""
        import os
        
        config = cls()
        config.DEFAULT_LLM_PROVIDER = os.getenv("PERSONA_LLM_PROVIDER", config.DEFAULT_LLM_PROVIDER)
        config.DEFAULT_LLM_MODEL = os.getenv("PERSONA_LLM_MODEL", config.DEFAULT_LLM_MODEL)
        # ... additional environment loading
        
        return config
```

### 9.2 Docker Deployment

```dockerfile
# Dockerfile for persona system
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PERSONA_LLM_PROVIDER=openai
ENV PERSONA_IMAGE_PROVIDER=dall-e

# Expose API port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 10. Implementation Checklist

### 10.1 Development Phase 1: Core Classes
- [ ] Implement `PersonaConfig` data structure
- [ ] Implement `PersonaLLMPromptBuilder` class
- [ ] Implement `LLMPersonaFirefly` class
- [ ] Create basic unit tests
- [ ] Validate prompt generation and LLM activation

### 10.2 Development Phase 2: Visual Generation
- [ ] Implement `PersonaVisualGenerator` class
- [ ] Implement `VisualPersonaFirefly` class
- [ ] Integrate image generation API
- [ ] Test visual-demographic alignment
- [ ] Add visual generation error handling

### 10.3 Development Phase 3: Factory and Scaling
- [ ] Implement `PersonaAgentFactory` class
- [ ] Add demographic inference logic
- [ ] Create name generation database
- [ ] Implement batch processing capabilities
- [ ] Add caching layer

### 10.4 Development Phase 4: API and Integration
- [ ] Implement FastAPI endpoints
- [ ] Add input validation
- [ ] Create comprehensive error handling
- [ ] Implement rate limiting
- [ ] Add monitoring and logging

### 10.5 Development Phase 5: Testing and Deployment
- [ ] Create comprehensive test suite
- [ ] Validate against demographic patterns
- [ ] Performance testing and optimization
- [ ] Docker containerization
- [ ] Production deployment configuration

---

## 11. Success Criteria

### 11.1 Functional Requirements
- [ ] Persona agents respond authentically to stimuli based on demographics
- [ ] Visual representations accurately match demographic configurations
- [ ] System can process 1000+ concurrent personas
- [ ] API responses within performance targets
- [ ] 95%+ persona activation success rate

### 11.2 Quality Requirements
- [ ] Persona responses align with known demographic patterns
- [ ] Visual representations are realistic and appropriate
- [ ] System handles errors gracefully without crashes
- [ ] Comprehensive logging for debugging and analysis
- [ ] Scalable architecture supporting growth

---

**This design document provides complete specifications for implementing the LLM Visual Persona System. Each class and method includes detailed implementation requirements, error handling patterns, and integration specifications to enable AI-assisted code generation.**