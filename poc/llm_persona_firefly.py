"""
LLM Persona Firefly - Proof of Concept Implementation
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import openai
import os
from persona_config import PersonaConfig, StimulusConfig
from persona_prompt_builder import PersonaLLMPromptBuilder


class PersonaActivationError(Exception):
    """Raised when LLM fails to activate as persona"""
    pass


class PersonaResponseError(Exception):
    """Raised when persona fails to generate response"""
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
    
    This class:
    1. Takes demographic configuration and creates a detailed persona identity
    2. Activates the LLM as that persona using the identity prompt
    3. Responds to user prompts while maintaining persona consistency
    4. Disappears when purpose is complete
    """
    
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
        
        # OpenAI setup (for POC)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
    
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
        print(f"🎭 Building persona identity for {self.persona_config.name}...")
        self.persona_prompt = self.prompt_builder.build_persona_prompt()
        print(f"📝 Generated {len(self.persona_prompt.split())} word persona identity")
        
        # Activate LLM as persona
        print(f"🧠 Activating LLM as {self.persona_config.name}...")
        activation_success = await self._activate_persona_agent()
        
        if not activation_success:
            raise PersonaActivationError(f"Failed to activate persona: {self.persona_config.name}")
        
        self.activation_timestamp = datetime.utcnow()
        print(f"✅ Successfully activated {self.persona_config.name}!")
    
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
        
        # Print the activation response for debugging
        print(f"🔍 Activation response: {activation_response.get('output_content', '')[:200]}...")
        
        # Check if response contains key identity markers
        identity_confirmed = (
            self.persona_config.name.lower().split()[0] in response_text and  # Check first name
            str(self.persona_config.age) in response_text and
            any(word in response_text for word in ["i am", "i'm", "my name"])
        )
        
        if identity_confirmed:
            self.agent_activated = True
            return True
        
        return False
    
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
            
            # Generate persona response
            response = await self._persona_respond_to_stimulus(user_prompt, stimulus_type)
            
            # Track interaction
            self.total_interactions += 1
            
            # Check if purpose complete (for POC, complete after response)
            if await self._is_purpose_complete(response):
                response["purpose_complete"] = True
            
            return response
            
        finally:
            # Firefly always disappears after glow
            await self.disappear()
    
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
    
    async def _call_llm_handler(self, prompt: str, rag_text: str) -> Dict[str, Any]:
        """
        Simulate PmLLMEngine handler pattern for POC.
        
        This simulates how the real implementation would:
        - prompt = user's question
        - rag_text = persona identity
        - Handler combines them to make LLM respond as persona
        """
        # For POC, directly call OpenAI
        if not self.openai_api_key:
            # Fallback for testing without API key
            return {
                "output_content": f"[Mock response as {self.persona_config.name}]: This is a simulated response to '{prompt}' from a {self.persona_config.age}-year-old {self.persona_config.race_ethnicity} {self.persona_config.gender}.",
                "success": True
            }
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Build the complete prompt that combines persona + user question
            complete_prompt = f"{rag_text}\n\nUser: {prompt}\n\n{self.persona_config.name}:"
            
            # Call OpenAI
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a persona simulation system. Fully embody the character described."},
                    {"role": "user", "content": complete_prompt}
                ],
                temperature=0.8,  # Higher for personality
                max_tokens=500
            )
            
            return {
                "output_content": response.choices[0].message.content,
                "success": True,
                "model": response.model,
                "usage": response.usage.model_dump() if hasattr(response.usage, 'model_dump') else {}
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            # Fallback response
            return {
                "output_content": f"As a {self.persona_config.age}-year-old {self.persona_config.occupation or 'person'}, I'd say: This is a simulated response to your question about '{prompt[:50]}...'",
                "success": False,
                "error": str(e)
            }
    
    async def _is_purpose_complete(self, response: Dict[str, Any]) -> bool:
        """
        Determine if the firefly's purpose is complete.
        
        For POC, we'll consider purpose complete after each interaction.
        Real implementation might have more complex logic.
        """
        return True  # Ephemeral - disappears after each use