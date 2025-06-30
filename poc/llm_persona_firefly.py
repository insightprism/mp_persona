"""
LLM Persona Firefly - Proof of Concept Implementation
"""
import asyncio
import uuid
import weakref
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import inspect
from persona_config import PersonaConfig, StimulusConfig
from persona_prompt_builder import PersonaLLMPromptBuilder

# Import the new LLM adapter
try:
    from persona_llm_adapter import PersonaLLMAdapter
    LLM_ADAPTER_AVAILABLE = True
except ImportError:
    LLM_ADAPTER_AVAILABLE = False
    print("⚠️  PersonaLLMAdapter not available - using fallback OpenAI/Claude implementation")

# Import the image matcher
try:
    from persona_image_matcher import SimplePersonaImageMatcher
    IMAGE_MATCHER_AVAILABLE = True
except ImportError:
    IMAGE_MATCHER_AVAILABLE = False
    print("⚠️  PersonaImageMatcher not available - image generation only")


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
        
        # LLM API setup
        self.llm_provider = None
        self.llm_api_key = None
        self.llm_model = None
        self.llm_adapter = PersonaLLMAdapter() if LLM_ADAPTER_AVAILABLE else None
        self._setup_llm_config()
        
        # Image matching setup
        self.image_matcher = SimplePersonaImageMatcher() if IMAGE_MATCHER_AVAILABLE else None
        
        # Lifecycle management
        self._caller_ref = None  # Will be set by calling function
    
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
                - disappear: bool (optional, triggers firefly disappear after response)
        
        Returns:
            Dict containing persona response and metadata
        """
        # Ensure we're initialized
        if not self.agent_activated:
            await self.birth()
        
        # Check for disappear trigger from calling function
        should_disappear = stimulus.get("disappear", False)
        
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
            
            # Add lifecycle information to response
            response["firefly_will_disappear"] = should_disappear
            response["interaction_number"] = self.total_interactions
            
            return response
            
        finally:
            # Only disappear if triggered by calling function
            if should_disappear:
                response["purpose_complete"] = True
                response["session_summary"] = self._generate_session_summary()
                await self.disappear()
                print(f"✨ {self.persona_config.name} firefly completed purpose and disappeared")
            else:
                print(f"🔄 {self.persona_config.name} firefly ready for next interaction")
    
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
        Enhanced LLM handler supporting Ollama, OpenAI, Claude via PrismMind infrastructure.
        
        Args:
            prompt: User's question
            rag_text: Persona identity context
        
        Returns:
            Dict with response and metadata
        """
        # Use PrismMind LLM adapter if available
        if self.llm_adapter and self.llm_provider != "mock" and self.llm_api_key:
            try:
                result = await self.llm_adapter.call_llm(
                    provider=self.llm_provider,
                    api_key=self.llm_api_key,
                    prompt=prompt,
                    rag_text=rag_text,
                    model=self.llm_model
                )
                
                if result["success"]:
                    return {
                        "output_content": result["output_content"],
                        "success": True,
                        "provider": result["provider"],
                        "model": result.get("model"),
                        "usage": result.get("usage", {})
                    }
                else:
                    print(f"❌ LLM call failed: {result['error']}")
                    return self._generate_mock_response(prompt)
                    
            except Exception as e:
                print(f"❌ LLM adapter error: {e}")
                return self._generate_mock_response(prompt)
        
        # Fallback to original implementation
        if self.llm_provider == "mock" or not self.llm_api_key:
            return self._generate_mock_response(prompt)
        
        elif self.llm_provider == "openai":
            return await self._call_openai(prompt, rag_text)
        
        elif self.llm_provider == "claude":
            return await self._call_claude(prompt, rag_text)
        
        else:
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock response for testing without API keys"""
        return {
            "output_content": f"[Mock response as {self.persona_config.name}]: This is a simulated response to '{prompt}' from a {self.persona_config.age}-year-old {self.persona_config.race_ethnicity} {self.persona_config.gender}.",
            "success": True,
            "provider": "mock"
        }
    
    async def _call_openai(self, prompt: str, rag_text: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.llm_api_key)
            
            # Build enhanced system prompt
            system_prompt = f"""You are a persona simulation system. Fully embody the character described below. Respond authentically as this person would, using their voice, perspective, and communication style.

{rag_text}

Important: Stay completely in character as {self.persona_config.name}. Use first person. Show your personality, background, and demographic perspective in your response."""
            
            # Call OpenAI
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher for personality variation
                max_tokens=500
            )
            
            return {
                "output_content": response.choices[0].message.content,
                "success": True,
                "provider": "openai",
                "model": response.model,
                "usage": response.usage.model_dump() if hasattr(response.usage, 'model_dump') else {}
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return {
                "output_content": f"Sorry, I'm having trouble responding right now. (OpenAI error: {str(e)[:50]}...)",
                "success": False,
                "provider": "openai",
                "error": str(e)
            }
    
    async def _call_claude(self, prompt: str, rag_text: str) -> Dict[str, Any]:
        """Call Claude API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.llm_api_key)
            
            # Build enhanced system prompt for Claude
            system_prompt = f"""You are embodying a specific person for a demographic research simulation. Respond authentically as this person would, using their voice, perspective, and communication style.

{rag_text}

Important guidelines:
- Stay completely in character as {self.persona_config.name}
- Use first person ("I think...", "In my experience...", etc.)
- Show your personality, values, and demographic perspective
- Respond naturally as this person would in real conversation
- Keep responses conversational and authentic (not overly formal)"""
            
            # Call Claude
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0.8,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "output_content": response.content[0].text,
                "success": True,
                "provider": "claude",
                "model": "claude-3-sonnet-20240229",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return {
                "output_content": f"Sorry, I'm having trouble responding right now. (Claude error: {str(e)[:50]}...)",
                "success": False,
                "provider": "claude", 
                "error": str(e)
            }
    
    async def _is_purpose_complete(self, response: Dict[str, Any]) -> bool:
        """
        Determine if the firefly's purpose is complete.
        
        For POC, we'll consider purpose complete after each interaction.
        Real implementation might have more complex logic.
        """
        return True  # Ephemeral - disappears after each use

    def _generate_session_summary(self) -> Dict[str, Any]:
        """Generate summary when firefly disappears"""
        return {
            "total_interactions": self.total_interactions,
            "persona_name": self.persona_config.name,
            "firefly_id": self.firefly_id,
            "purpose": self.purpose,
            "activation_time": self.activation_timestamp.isoformat() if self.activation_timestamp else None,
            "session_duration_seconds": (datetime.utcnow() - self.activation_timestamp).total_seconds() if self.activation_timestamp else 0
        }

    def _setup_llm_config(self):
        """Setup LLM configuration from environment variables or defaults"""
        # Check for OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        
        # Check for Claude API key
        claude_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        
        # Check if Ollama is available (no API key needed)
        ollama_available = self._check_ollama_available()
        
        # Determine provider based on available options
        if openai_key:
            self.llm_provider = "openai"
            self.llm_api_key = openai_key
            self.llm_model = "gpt-4"
            print(f"🤖 Using OpenAI API for {self.persona_config.name}")
        elif claude_key:
            self.llm_provider = "claude"
            self.llm_api_key = claude_key
            self.llm_model = "claude-3-sonnet-20240229"
            print(f"🤖 Using Claude API for {self.persona_config.name}")
        elif ollama_available:
            self.llm_provider = "ollama_local"
            self.llm_api_key = None  # Ollama doesn't need API key
            self.llm_model = "llama3:8b"
            print(f"🤖 Using Ollama local for {self.persona_config.name}")
        else:
            self.llm_provider = "mock"
            self.llm_api_key = None
            self.llm_model = "mock"
            print(f"🤖 No LLM providers available - using mock responses for {self.persona_config.name}")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            import httpx
            with httpx.Client(timeout=2.0) as client:
                response = client.get("http://localhost:11434/api/tags")
                return response.status_code == 200
        except:
            return False

    def set_llm_config(self, provider: str, api_key: str = None, model: str = None):
        """Manually set LLM configuration"""
        # Get available providers from adapter
        available_providers = ["openai", "claude", "anthropic", "ollama_local", "ollama_host"]
        
        if provider.lower() not in available_providers:
            raise ValueError(f"Provider must be one of: {available_providers}")
        
        # Set provider
        if provider.lower() in ["claude", "anthropic"]:
            self.llm_provider = "claude"
        else:
            self.llm_provider = provider.lower()
        
        # Set API key (can be None for Ollama)
        self.llm_api_key = api_key
        
        # Set model or use default
        if model:
            self.llm_model = model
        elif self.llm_adapter:
            defaults = self.llm_adapter.get_default_models()
            self.llm_model = defaults.get(self.llm_provider, "gpt-4")
        else:
            # Fallback defaults
            model_defaults = {
                "openai": "gpt-4",
                "claude": "claude-3-sonnet-20240229",
                "ollama_local": "llama3:8b",
                "ollama_host": "llama3:8b"
            }
            self.llm_model = model_defaults.get(self.llm_provider, "gpt-4")
        
        print(f"🤖 LLM config updated: {self.llm_provider.upper()} ({self.llm_model}) for {self.persona_config.name}")

    def bind_to_caller(self, caller_object):
        """Bind firefly to calling object for automatic cleanup"""
        def cleanup_callback(weak_ref):
            """Called when caller object is garbage collected"""
            if self.is_alive:
                print(f"🧹 Caller disappeared - auto-cleaning up {self.persona_config.name} firefly")
                # Schedule async cleanup
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(self.disappear())
                except RuntimeError:
                    # If no event loop, just mark as dead
                    self.is_alive = False
        
        self._caller_ref = weakref.ref(caller_object, cleanup_callback)
        return self

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - triggers disappear"""
        if self.is_alive:
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.disappear())
            except RuntimeError:
                # If no event loop, just mark as dead
                self.is_alive = False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.birth()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - triggers disappear"""
        if self.is_alive:
            await self.disappear()

    # ========================================
    # IMAGE MATCHING CAPABILITIES
    # ========================================

    async def get_persona_image(self, force_generate: bool = False, min_similarity: float = 0.5) -> Dict[str, Any]:
        """
        Get persona image - prefer pre-generated vector match, fallback to generation.
        
        Args:
            force_generate: Skip vector matching and generate new image
            min_similarity: Minimum similarity threshold for vector match (0.0 to 1.0)
            
        Returns:
            Dict with image URL and metadata
        """
        print(f"🖼️  Getting image for {self.persona_config.name}...")
        
        # Try vector search first (fast + free) unless forced
        if self.image_matcher and not force_generate:
            print("🔍 Searching pre-generated image database...")
            
            match_result = self.image_matcher.find_best_match(
                self.persona_config, 
                min_similarity=min_similarity
            )
            
            if match_result["success"]:
                print(f"✅ Found vector match: {match_result['description']}")
                print(f"   🎯 Similarity: {match_result['similarity_score']:.2f}")
                print(f"   💰 Cost: $0.000 (vs $0.020 for generation)")
                print(f"   ⚡ Time: {match_result['time_taken']}s (vs 3-5s for generation)")
                
                return {
                    "success": True,
                    "image_url": match_result["image_url"],
                    "image_id": match_result.get("image_id"),
                    "method": "pre_generated_vector_match",
                    "similarity_score": match_result["similarity_score"],
                    "description": match_result["description"],
                    "cost": 0.0,
                    "time_taken": match_result["time_taken"],
                    "match_details": match_result.get("match_details", {}),
                    "persona_name": self.persona_config.name
                }
            else:
                print(f"⚠️  No suitable vector match: {match_result['reason']}")
                print(f"   Best similarity: {match_result.get('best_similarity', 0):.2f}")
                
                # Check if we should fallback to generation
                if not force_generate:
                    print("💡 Consider using force_generate=True or lowering min_similarity")
                    return {
                        "success": False,
                        "reason": match_result["reason"],
                        "best_similarity": match_result.get("best_similarity", 0),
                        "alternatives": match_result.get("alternatives", []),
                        "suggestion": "Try force_generate=True or lower min_similarity threshold"
                    }
        
        # Fallback to generation (with cost optimization)
        print("🎨 Falling back to image generation...")
        
        # Import the image generator
        try:
            from persona_image_generator import generate_persona_image_simple
            
            # Check with cost optimizer first
            if hasattr(self, 'cost_optimizer') and not force_generate:
                cost_rec = self.cost_optimizer.should_generate_image(self.firefly_id, force_generate)
                if not cost_rec["recommend"]:
                    return {
                        "success": False,
                        "reason": "Image generation not recommended by cost optimizer",
                        "cost_recommendation": cost_rec,
                        "suggestion": "Use force_generate=True to override cost recommendation"
                    }
            
            # Generate new image
            result = generate_persona_image_simple(self.persona_config)
            
            if result["success"]:
                result["method"] = "generated_new"
                result["persona_name"] = self.persona_config.name
                print(f"✅ Generated new image for {self.persona_config.name}")
            
            return result
            
        except ImportError:
            return {
                "success": False,
                "reason": "Image generation not available - missing persona_image_generator module",
                "suggestion": "Install image generation dependencies or use pre-generated images only"
            }
    
    def get_image_alternatives(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Get top matching pre-generated images for manual selection.
        
        Args:
            top_k: Number of alternatives to return
            
        Returns:
            List of image options with similarity scores
        """
        if not self.image_matcher:
            return []
        
        return self.image_matcher.get_top_matches(self.persona_config, top_k=top_k)

    # ========================================
    # SELF-IDENTIFICATION CAPABILITIES
    # ========================================

    def describe_capabilities(self) -> Dict[str, str]:
        """
        What can I do? Other agents can call this to understand my functions.
        Public method - no security key required.
        """
        return {
            "birth": "Initialize persona with demographic identity and activate LLM",
            "glow": "Respond to stimulus as authentic persona, then disappear", 
            "disappear": "Clean up resources and terminate persona",
            "get_persona_identity": "Return my complete persona prompt (requires secret key)",
            "get_demographics": "Return my demographic configuration",
            "get_behavioral_context": "Return behavioral characteristics and traits",
            "describe_self": "Complete self-description for other agents",
            "can_perform": "Check if I can perform a specific capability",
            "get_current_state": "Return my current operational state"
        }

    def get_available_methods(self) -> List[str]:
        """
        List all my callable methods for other agents.
        Excludes private methods starting with underscore.
        """
        return [name for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
                if not name.startswith('_')]

    def get_method_signature(self, method_name: str) -> str:
        """
        Show function signature for a specific method.
        Public method - no security required.
        """
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return str(inspect.signature(method))
        return f"Method '{method_name}' not found"

    def get_source_code(self, method_name: str, secret_key: str = None) -> str:
        """
        Share my actual source code with other agents.
        Requires secret key for security (like PrismMind engine).
        """
        # Security check
        expected_key = os.getenv("PERSONA_SOURCE_SECRET", "persona_debug_2024")
        if secret_key != expected_key:
            return "❌ Access denied: Invalid secret key required for source code access"
        
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            try:
                return inspect.getsource(method)
            except OSError:
                return f"Source code not available for '{method_name}'"
        return f"Method '{method_name}' not found"

    def describe_self(self) -> Dict[str, Any]:
        """
        Complete self-description for other agents.
        This is the main method other agents should call to understand me.
        """
        return {
            "agent_type": "LLMPersonaFirefly",
            "class_name": self.__class__.__name__,
            "persona_identity": {
                "name": self.persona_config.name,
                "demographics": self.get_demographics()
            },
            "current_state": self.get_current_state(),
            "capabilities": self.describe_capabilities(),
            "available_methods": self.get_available_methods(),
            "behavioral_characteristics": self.get_behavioral_context(),
            "firefly_metadata": {
                "firefly_id": self.firefly_id,
                "purpose": self.purpose,
                "behavioral_class": self.behavioral_class
            },
            "interaction_history": {
                "total_interactions": self.total_interactions,
                "activation_timestamp": self.activation_timestamp.isoformat() if self.activation_timestamp else None
            }
        }

    def can_perform(self, capability: str) -> bool:
        """
        Can I perform this capability?
        """
        return capability in self.describe_capabilities()

    def get_demographics(self) -> Dict[str, Any]:
        """
        Return my demographic configuration for other agents.
        """
        return {
            "name": self.persona_config.name,
            "age": self.persona_config.age,
            "race_ethnicity": self.persona_config.race_ethnicity,
            "gender": self.persona_config.gender,
            "education": self.persona_config.education,
            "location_type": self.persona_config.location_type,
            "income": self.persona_config.income,
            "religion": getattr(self.persona_config, 'religion', None),
            "marital_status": getattr(self.persona_config, 'marital_status', None),
            "occupation": getattr(self.persona_config, 'occupation', None),
            "state": getattr(self.persona_config, 'state', None)
        }

    def get_behavioral_context(self) -> Dict[str, str]:
        """
        Return my behavioral traits for other agents to understand.
        """
        return self.persona_config.get_behavioral_characteristics()

    def get_current_state(self) -> Dict[str, Any]:
        """
        Return my current operational state.
        """
        return {
            "is_alive": self.is_alive,
            "agent_activated": self.agent_activated,
            "total_interactions": self.total_interactions,
            "purpose": self.purpose,
            "has_persona_prompt": self.persona_prompt is not None,
            "llm_configured": self.llm_api_key is not None
        }

    def get_persona_identity(self, secret_key: str = None) -> str:
        """
        Return my complete persona prompt (sensitive information).
        Requires secret key for security.
        """
        # Security check
        expected_key = os.getenv("PERSONA_SOURCE_SECRET", "persona_debug_2024")
        if secret_key != expected_key:
            return "❌ Access denied: Invalid secret key required for persona identity access"
        
        return self.persona_prompt or "Persona prompt not yet generated"

    def share_capabilities_with_agent(self, requesting_agent_id: str = None) -> Dict[str, Any]:
        """
        Structured response when another agent asks 'what can you do?'
        This is the standardized interface for inter-agent communication.
        """
        return {
            "response_type": "capability_sharing",
            "responding_agent": {
                "type": "LLMPersonaFirefly",
                "id": self.firefly_id,
                "name": self.persona_config.name
            },
            "requesting_agent_id": requesting_agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities_summary": self.describe_capabilities(),
            "demographic_profile": self.get_demographics(),
            "current_operational_state": self.get_current_state(),
            "available_for_interaction": self.is_alive,
            "interaction_interface": {
                "primary_method": "glow",
                "input_format": "Dict with 'prompt' or 'question' key",
                "output_format": "Dict with persona_response and metadata",
                "lifecycle": "ephemeral - disappears after interaction"
            },
            "security_note": "Some methods require PERSONA_SOURCE_SECRET environment variable"
        }