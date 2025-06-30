#!/usr/bin/env python3
"""
Persona LLM Adapter
==================

Integrates the PrismMind LLM infrastructure (pm_call_llm_v4) with the persona system.
Supports Ollama, OpenAI, and Claude providers with unified interface.
"""

import sys
import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Add PrismMind to path
sys.path.append('/home/markly2/PrismMind_v2')

try:
    from pm_utils.pm_call_llm import pm_call_llm_v4
    PRISM_MIND_AVAILABLE = True
except ImportError:
    PRISM_MIND_AVAILABLE = False
    print("⚠️  PrismMind LLM utils not available - using fallback implementation")

class PersonaLLMAdapter:
    """Adapter to use PrismMind's pm_call_llm_v4 with persona system"""
    
    def __init__(self):
        self.supported_providers = ["openai", "claude", "anthropic", "ollama_local", "ollama_host"]
        
        # Default endpoints
        self.default_endpoints = {
            "claude": "https://api.anthropic.com/v1/messages",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "ollama_host": "http://localhost:8005/prismmind/chat_completions",
            "ollama_local": "http://localhost:11434/api/chat"
        }
        
        # Default models
        self.default_models = {
            "openai": "gpt-4",
            "claude": "claude-3-sonnet-20240229",
            "anthropic": "claude-3-sonnet-20240229",
            "ollama_local": "llama3:8b",
            "ollama_host": "llama3:8b"
        }
    
    def build_llm_payload(self, provider: str, api_key: str, prompt: str, rag_text: str, 
                         model: Optional[str] = None, temperature: float = 0.8) -> Dict[str, Any]:
        """
        Build standardized LLM payload for pm_call_llm_v4
        
        Args:
            provider: LLM provider ("openai", "claude", "ollama_local", etc.)
            api_key: API key for the provider
            prompt: User prompt
            rag_text: Context/persona information
            model: Model name (optional, uses default)
            temperature: Temperature setting
            
        Returns:
            Dict payload for pm_call_llm_v4
        """
        if provider not in self.supported_providers:
            raise ValueError(f"Unsupported provider: {provider}. Supported: {self.supported_providers}")
        
        # Use default model if not specified
        if not model:
            model = self.default_models.get(provider, "gpt-4")
        
        # Build system prompt with persona context
        if provider in ["claude", "anthropic"]:
            # Claude uses system message in a different way
            messages = [
                {
                    "role": "user", 
                    "content": f"Context: {rag_text}\n\nUser: {prompt}"
                }
            ]
        else:
            # OpenAI and Ollama can use system messages
            messages = [
                {"role": "system", "content": rag_text},
                {"role": "user", "content": prompt}
            ]
        
        payload = {
            "llm_provider": provider,
            "llm_name": model,
            "llm_api_key": api_key,
            "messages": messages,
            "temperature": temperature
        }
        
        # Add endpoint for providers that need it
        if provider in self.default_endpoints:
            payload["chat_completion_url"] = self.default_endpoints[provider]
        
        return payload
    
    async def call_llm(self, provider: str, api_key: str, prompt: str, rag_text: str,
                      model: Optional[str] = None, temperature: float = 0.8) -> Dict[str, Any]:
        """
        Call LLM using PrismMind infrastructure
        
        Args:
            provider: LLM provider
            api_key: API key
            prompt: User prompt
            rag_text: Persona context
            model: Model name (optional)
            temperature: Temperature setting
            
        Returns:
            Standardized response dict
        """
        if not PRISM_MIND_AVAILABLE:
            return self._fallback_response(provider, prompt, rag_text)
        
        try:
            # Build payload
            payload = self.build_llm_payload(provider, api_key, prompt, rag_text, model, temperature)
            
            print(f"🤖 Calling {provider} via PrismMind infrastructure")
            print(f"   Model: {payload['llm_name']}")
            print(f"   Prompt: {prompt[:100]}...")
            
            # Call PrismMind LLM function
            result = await pm_call_llm_v4(payload)
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                    "provider": provider,
                    "output_content": f"Error: {result['error']}"
                }
            
            # Extract usage information if available
            usage_info = {}
            raw_response = result.get("raw_response")
            if raw_response:
                if hasattr(raw_response, 'usage'):
                    # OpenAI style usage
                    usage_info = {
                        "input_tokens": getattr(raw_response.usage, 'prompt_tokens', 0),
                        "output_tokens": getattr(raw_response.usage, 'completion_tokens', 0),
                        "total_tokens": getattr(raw_response.usage, 'total_tokens', 0)
                    }
                elif isinstance(raw_response, dict) and "usage" in raw_response:
                    # Claude style usage
                    usage_info = raw_response["usage"]
            
            return {
                "success": True,
                "output_content": result.get("output", ""),
                "provider": provider,
                "model": result.get("llm_name", model),
                "usage": usage_info,
                "raw_response": result.get("raw_response")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": provider,
                "output_content": f"Error calling {provider}: {str(e)}"
            }
    
    def _fallback_response(self, provider: str, prompt: str, rag_text: str) -> Dict[str, Any]:
        """Fallback response when PrismMind is not available"""
        return {
            "success": True,
            "output_content": f"[Fallback response for {provider}]: This is a simulated response to '{prompt}' using persona context. PrismMind LLM infrastructure not available.",
            "provider": f"{provider}_fallback",
            "model": "fallback",
            "usage": {"input_tokens": 0, "output_tokens": 0}
        }
    
    def get_available_providers(self) -> Dict[str, str]:
        """Get list of available providers with descriptions"""
        return {
            "openai": "OpenAI GPT models (requires API key)",
            "claude": "Anthropic Claude models (requires API key)", 
            "anthropic": "Anthropic Claude models (alias for claude)",
            "ollama_local": "Local Ollama installation (requires Ollama running on localhost:11434)",
            "ollama_host": "Ollama via PrismMind microservice (requires service running)"
        }
    
    def get_default_models(self) -> Dict[str, str]:
        """Get default models for each provider"""
        return self.default_models.copy()
    
    def set_default_model(self, provider: str, model: str):
        """Set default model for a provider"""
        if provider in self.supported_providers:
            self.default_models[provider] = model
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def set_endpoint(self, provider: str, endpoint: str):
        """Set custom endpoint for a provider"""
        self.default_endpoints[provider] = endpoint


# Convenience function for simple usage
async def call_persona_llm_simple(provider: str, api_key: str, prompt: str, rag_text: str,
                                 model: Optional[str] = None) -> Dict[str, Any]:
    """
    Simple function to call LLM for persona responses
    
    Args:
        provider: LLM provider ("openai", "claude", "ollama_local", etc.)
        api_key: API key (can be None for Ollama local)
        prompt: User prompt
        rag_text: Persona context
        model: Model name (optional)
        
    Returns:
        Response dict with output_content and metadata
    """
    adapter = PersonaLLMAdapter()
    return await adapter.call_llm(provider, api_key, prompt, rag_text, model)


# Example usage and testing
if __name__ == "__main__":
    
    async def demo_llm_adapter():
        """Demo the LLM adapter with different providers"""
        print("🚀 Persona LLM Adapter Demo")
        print("=" * 50)
        
        adapter = PersonaLLMAdapter()
        
        # Show available providers
        print("🔧 Available Providers:")
        for provider, description in adapter.get_available_providers().items():
            print(f"   • {provider}: {description}")
        
        print(f"\n🎯 Default Models:")
        for provider, model in adapter.get_default_models().items():
            print(f"   • {provider}: {model}")
        
        # Sample persona context
        persona_context = """You are Maria Rodriguez, a 34-year-old Hispanic female living in an urban area. 
        You have a college education and work in a professional role. You are thoughtful about technology 
        and social issues, balancing optimism with practical concerns."""
        
        # Test prompts
        test_prompts = [
            "What's your opinion on remote work?",
            "How do you feel about artificial intelligence?",
            "What are your thoughts on climate change?"
        ]
        
        # Test different providers
        test_configs = [
            ("ollama_local", None, "llama3:8b"),
            ("openai", os.getenv("OPENAI_API_KEY"), "gpt-4"),
            ("claude", os.getenv("ANTHROPIC_API_KEY"), "claude-3-sonnet-20240229")
        ]
        
        for provider, api_key, model in test_configs:
            print(f"\n🤖 Testing {provider}")
            print("-" * 30)
            
            if not api_key and provider in ["openai", "claude"]:
                print(f"   ⚠️  No API key for {provider} - skipping")
                continue
            
            try:
                for prompt in test_prompts[:1]:  # Test first prompt only
                    print(f"   📝 Prompt: {prompt}")
                    
                    result = await adapter.call_llm(
                        provider=provider,
                        api_key=api_key,
                        prompt=prompt,
                        rag_text=persona_context,
                        model=model
                    )
                    
                    if result["success"]:
                        print(f"   ✅ Response: {result['output_content'][:100]}...")
                        if result.get("usage"):
                            print(f"   📊 Usage: {result['usage']}")
                    else:
                        print(f"   ❌ Error: {result['error']}")
                    
                    break  # Only test one prompt per provider for demo
                    
            except Exception as e:
                print(f"   ❌ Provider test failed: {e}")
        
        print(f"\n🎉 LLM Adapter demo complete!")
        print(f"💡 Ready to integrate with persona firefly system")
    
    # Run demo
    asyncio.run(demo_llm_adapter())