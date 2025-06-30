"""
LLM Persona Firefly - Simplified POC without external dependencies
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from persona_config import PersonaConfig, StimulusConfig
from persona_prompt_builder import PersonaLLMPromptBuilder


class PersonaActivationError(Exception):
    """Raised when LLM fails to activate as persona"""
    pass


class MockPmFireflyEngine:
    """Mock base class for POC - simulates PmFireflyEngine"""
    def __init__(self, purpose: str, behavioral_class: str = "butterfly"):
        self.purpose = purpose
        self.behavioral_class = behavioral_class
        self.is_alive = False
    
    async def birth(self):
        """Initialize firefly"""
        self.is_alive = True
        print(f"🔥 Firefly born with purpose: {self.purpose}")
    
    async def disappear(self):
        """Clean up firefly"""
        self.is_alive = False
        print(f"✨ Firefly disappeared after fulfilling purpose: {self.purpose}")


class LLMPersonaFirefly(MockPmFireflyEngine):
    """
    A firefly that transforms an LLM into a specific demographic persona.
    """
    
    def __init__(self, persona_config: PersonaConfig, purpose: str = "persona_interaction"):
        """Initialize the persona firefly."""
        super().__init__(purpose=purpose, behavioral_class="butterfly")
        
        self.persona_config = persona_config
        self.firefly_id = str(uuid.uuid4())
        self.prompt_builder = PersonaLLMPromptBuilder(persona_config)
        
        self.persona_prompt = None
        self.agent_activated = False
        self.activation_timestamp = None
        self.total_interactions = 0
    
    async def birth(self):
        """Initialize the persona with perfect specialization."""
        await super().birth()
        
        print(f"🎭 Building persona identity for {self.persona_config.name}...")
        self.persona_prompt = self.prompt_builder.build_persona_prompt()
        print(f"📝 Generated {len(self.persona_prompt.split())} word persona identity")
        
        print(f"🧠 Activating LLM as {self.persona_config.name}...")
        activation_success = await self._activate_persona_agent()
        
        if not activation_success:
            raise PersonaActivationError(f"Failed to activate persona: {self.persona_config.name}")
        
        self.activation_timestamp = datetime.utcnow()
        print(f"✅ Successfully activated {self.persona_config.name}!")
    
    async def _activate_persona_agent(self) -> bool:
        """Transform the LLM into the persona using identity prompt."""
        # For demo, simulate successful activation
        mock_response = f"Hi, I'm {self.persona_config.name}. I'm {self.persona_config.age} years old and live in a {self.persona_config.location_type} area where I work as a {self.persona_config.occupation}."
        
        print(f"🔍 Activation response: {mock_response}")
        
        self.agent_activated = True
        return True
    
    async def glow(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution: persona responds to stimulus."""
        if not self.agent_activated:
            await self.birth()
        
        try:
            # Handle both dict and StimulusConfig
            if isinstance(stimulus, StimulusConfig):
                user_prompt = stimulus.get_prompt()
                stimulus_type = stimulus.stimulus_type
            else:
                user_prompt = stimulus.get("prompt") or stimulus.get("question") or stimulus.get("description")
                stimulus_type = stimulus.get("stimulus_type", "general_question")
            
            if not user_prompt:
                raise ValueError("No prompt provided in stimulus")
            
            print(f"💬 {self.persona_config.name} responding to: {user_prompt[:100]}...")
            
            response = await self._persona_respond_to_stimulus(user_prompt, stimulus_type)
            self.total_interactions += 1
            
            if await self._is_purpose_complete(response):
                response["purpose_complete"] = True
            
            return response
            
        finally:
            await self.disappear()
    
    async def _persona_respond_to_stimulus(self, user_prompt: str, stimulus_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate authentic persona response (simulated for POC)."""
        
        # Simulate demographic-appropriate responses
        llm_response = await self._generate_mock_response(user_prompt, stimulus_type)
        
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
    
    async def _generate_mock_response(self, prompt: str, stimulus_type: str) -> Dict[str, Any]:
        """Generate mock responses that demonstrate demographic patterns."""
        
        # Maria - 34, Hispanic, teacher, suburban, married with 2 kids
        if self.persona_config.name == "Maria Rodriguez":
            if "smartphone" in prompt.lower():
                response = (
                    "Oh, for me it's all about practicality! As a teacher and mom of two, "
                    "I need a phone with amazing battery life - I can't have it dying during "
                    "parent-teacher conferences. The camera is super important too for capturing "
                    "my kids' moments. Honestly, I'd love the latest iPhone but on a teacher's "
                    "salary with two kids? I'd probably spend $400-600 max. Maybe I'll get last "
                    "year's model on sale. Storage is important too - between all the educational "
                    "apps and kid photos, I'm always running out of space!"
                )
            else:
                response = f"As a 34-year-old teacher and mom, here's my perspective on {prompt[:50]}..."
        
        # Bob - 52, white, mechanic, rural, divorced
        elif self.persona_config.name == "Bob Johnson":
            if "electric" in prompt.lower() and "car" in prompt.lower():
                response = (
                    "Look, I've been fixing cars for 30 years, and this electric car mandate "
                    "is just wrong. The government shouldn't tell us what to drive. Here in rural "
                    "Ohio, we need reliable trucks that can haul equipment and go 300+ miles without "
                    "stopping. Where are all these charging stations gonna be? Not out here, that's "
                    "for sure. This is gonna hurt working folks like me who can't afford fancy "
                    "new electric vehicles. My customers drive older cars because that's what they "
                    "can afford. Plus, what happens to all us mechanics? The politicians in Washington "
                    "don't understand life in rural America."
                )
            else:
                response = f"Well, as a 52-year-old mechanic who's seen a lot, I'd say {prompt[:50]}..."
        
        # Ashley - 28, Asian, software engineer, urban, single
        elif self.persona_config.name == "Ashley Chen":
            if "work" in prompt.lower() and "home" in prompt.lower():
                response = (
                    "I absolutely LOVE working from home! As a software engineer, I'm so much more "
                    "productive without the open office distractions. I save 2 hours daily not commuting "
                    "on the Caltrain, which I can use for coding or my yoga practice. My ideal setup is "
                    "definitely hybrid - maybe 2-3 days at home for deep work and 2 days in the office "
                    "for collaboration and team meetings. Plus, living in San Francisco is expensive, so "
                    "being able to work from anywhere means I could potentially move somewhere more affordable. "
                    "The only downside is sometimes I miss the spontaneous discussions with colleagues, "
                    "but Slack and video calls work pretty well for that."
                )
            else:
                response = f"From my perspective as a 28-year-old tech worker in SF, {prompt[:50]}..."
        
        else:
            # Generic response based on demographics
            response = (
                f"As a {self.persona_config.age}-year-old {self.persona_config.occupation} "
                f"living in a {self.persona_config.location_type} area, I think {prompt[:100]}... "
                f"My {self.persona_config.education} education and {self.persona_config.income} "
                f"income definitely shape my perspective on this."
            )
        
        return {
            "output_content": response,
            "success": True,
            "mock_response": True
        }
    
    async def _is_purpose_complete(self, response: Dict[str, Any]) -> bool:
        """Determine if the firefly's purpose is complete."""
        return True  # Ephemeral - disappears after each use