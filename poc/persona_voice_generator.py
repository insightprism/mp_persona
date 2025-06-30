#!/usr/bin/env python3
"""
Persona Voice Generator
======================

Generate persona-appropriate voices using OpenAI's TTS API.
Takes key persona features and creates appropriate voice samples.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from persona_config import PersonaConfig

class PersonaVoiceGenerator:
    """Generate voice samples for personas using OpenAI TTS"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize voice generator
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Available TTS voices with characteristics
        self.voice_profiles = {
            "alloy": {"gender": "neutral", "age": "young", "style": "clear"},
            "echo": {"gender": "male", "age": "middle", "style": "professional"},
            "fable": {"gender": "male", "age": "mature", "style": "warm"},
            "onyx": {"gender": "male", "age": "deep", "style": "authoritative"},
            "nova": {"gender": "female", "age": "young", "style": "energetic"},
            "shimmer": {"gender": "female", "age": "middle", "style": "friendly"}
        }
    
    def select_voice_for_persona(self, persona_config: PersonaConfig) -> str:
        """
        Select appropriate voice based on persona demographics
        
        Args:
            persona_config: Persona configuration
            
        Returns:
            Voice name for TTS
        """
        age = persona_config.age
        gender = persona_config.gender.lower()
        education = persona_config.education.lower()
        income = persona_config.income.lower()
        
        # Age-based selection
        if age < 30:
            age_category = "young"
        elif age < 50:
            age_category = "middle"
        else:
            age_category = "mature"
        
        # Professional context based on education/income
        is_professional = (
            education in ["graduate", "professional"] or 
            "over_100k" in income or 
            "75k_100k" in income
        )
        
        # Voice selection logic
        if gender == "female":
            if age_category == "young":
                return "nova"  # Young, energetic female
            else:
                return "shimmer"  # Mature, friendly female
        
        elif gender == "male":
            if is_professional:
                if age_category == "mature":
                    return "fable"  # Mature, warm male
                else:
                    return "echo"  # Professional male
            else:
                if age_category == "young":
                    return "echo"  # Clear male voice
                else:
                    return "onyx"  # Deep, authoritative male
        
        else:  # Non-binary or other
            return "alloy"  # Neutral voice
    
    def generate_persona_script(self, persona_config: PersonaConfig) -> str:
        """
        Generate a sample script that represents the persona's voice style
        
        Args:
            persona_config: Persona configuration
            
        Returns:
            Text script for voice generation
        """
        name = persona_config.name
        age = persona_config.age
        location = self._format_location(persona_config.location_type)
        occupation = self._infer_occupation(persona_config.education, persona_config.income)
        
        # Generate persona-appropriate introduction
        script = f"""Hi, I'm {name}. I'm {age} years old and I live in a {location} area. {occupation} 
        
I'd like to share my perspective on a few topics that matter to me. When it comes to technology, I think it's important to find the right balance between innovation and practicality. 

As someone from my background and community, I've seen how changes affect real people in real ways. I believe in staying informed and making thoughtful decisions based on both facts and personal experience.

Thank you for taking the time to listen to what I have to say."""
        
        return script
    
    def _format_location(self, location_type: str) -> str:
        """Format location type for natural speech"""
        location_map = {
            "urban": "urban",
            "suburban": "suburban", 
            "rural": "rural"
        }
        return location_map.get(location_type.lower(), "local")
    
    def _infer_occupation(self, education: str, income: str) -> str:
        """Infer occupation description from education and income"""
        if education == "graduate" or "over_100k" in income:
            return "I work in a professional role that I find both challenging and rewarding."
        elif education == "college" or income in ["75k_100k", "50k_75k"]:
            return "I have a job that allows me to support my family and contribute to my community."
        elif education == "high_school":
            return "I work hard every day to provide for myself and my loved ones."
        else:
            return "I'm focused on building a good life for myself and those around me."
    
    async def generate_persona_voice(self, persona_config: PersonaConfig, output_dir: str = "voice_samples") -> Dict[str, Any]:
        """
        Generate persona voice sample using TTS
        
        Args:
            persona_config: Persona configuration
            output_dir: Directory to save audio files
            
        Returns:
            Dict with audio file path and metadata
        """
        try:
            # Select appropriate voice
            voice = self.select_voice_for_persona(persona_config)
            
            # Generate script
            script = self.generate_persona_script(persona_config)
            
            # Create output directory
            Path(output_dir).mkdir(exist_ok=True)
            
            # Generate filename
            safe_name = persona_config.name.replace(" ", "_").lower()
            audio_filename = f"{safe_name}_voice_sample.mp3"
            audio_path = Path(output_dir) / audio_filename
            
            print(f"🎤 Generating voice for {persona_config.name}")
            print(f"🗣️  Selected voice: {voice} ({self.voice_profiles[voice]})")
            print(f"📝 Script: {script[:100]}...")
            
            # Generate audio using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",  # Standard quality (cheaper than tts-1-hd)
                voice=voice,
                input=script,
                speed=1.0
            )
            
            # Save audio file
            response.stream_to_file(audio_path)
            
            return {
                "success": True,
                "audio_path": str(audio_path),
                "voice_used": voice,
                "voice_characteristics": self.voice_profiles[voice],
                "script_text": script,
                "persona_name": persona_config.name,
                "demographics": {
                    "age": persona_config.age,
                    "gender": persona_config.gender,
                    "race_ethnicity": persona_config.race_ethnicity,
                    "location_type": persona_config.location_type,
                    "income": persona_config.income,
                    "education": persona_config.education
                },
                "file_size_mb": round(audio_path.stat().st_size / 1024 / 1024, 2) if audio_path.exists() else 0,
                "model": "tts-1"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "voice_used": voice if 'voice' in locals() else None,
                "script_text": script if 'script' in locals() else None,
                "persona_name": persona_config.name
            }
    
    def generate_mock_response(self, persona_config: PersonaConfig) -> Dict[str, Any]:
        """Generate mock response for testing without API calls"""
        voice = self.select_voice_for_persona(persona_config)
        script = self.generate_persona_script(persona_config)
        
        return {
            "success": True,
            "audio_path": f"voice_samples/{persona_config.name.replace(' ', '_').lower()}_voice_sample.mp3",
            "voice_used": voice,
            "voice_characteristics": self.voice_profiles[voice],
            "script_text": script,
            "persona_name": persona_config.name,
            "demographics": {
                "age": persona_config.age,
                "gender": persona_config.gender,
                "race_ethnicity": persona_config.race_ethnicity,
                "location_type": persona_config.location_type,
                "income": persona_config.income,
                "education": persona_config.education
            },
            "file_size_mb": 0.5,  # Mock file size
            "model": "mock"
        }

    async def generate_custom_voice_sample(self, persona_config: PersonaConfig, custom_text: str, output_dir: str = "voice_samples") -> Dict[str, Any]:
        """
        Generate voice sample with custom text
        
        Args:
            persona_config: Persona configuration
            custom_text: Custom text to speak
            output_dir: Directory to save audio files
            
        Returns:
            Dict with audio file path and metadata
        """
        try:
            voice = self.select_voice_for_persona(persona_config)
            
            # Create output directory
            Path(output_dir).mkdir(exist_ok=True)
            
            # Generate filename
            safe_name = persona_config.name.replace(" ", "_").lower()
            timestamp = int(asyncio.get_event_loop().time())
            audio_filename = f"{safe_name}_custom_{timestamp}.mp3"
            audio_path = Path(output_dir) / audio_filename
            
            print(f"🎤 Generating custom voice for {persona_config.name}")
            print(f"📝 Custom text: {custom_text[:100]}...")
            
            # Generate audio
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=custom_text,
                speed=1.0
            )
            
            response.stream_to_file(audio_path)
            
            return {
                "success": True,
                "audio_path": str(audio_path),
                "voice_used": voice,
                "voice_characteristics": self.voice_profiles[voice],
                "script_text": custom_text,
                "persona_name": persona_config.name,
                "file_size_mb": round(audio_path.stat().st_size / 1024 / 1024, 2),
                "model": "tts-1"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "persona_name": persona_config.name
            }


# Convenience function for simple usage
def generate_persona_voice_simple(persona_config: PersonaConfig, api_key: Optional[str] = None, custom_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Simple function to generate persona voice
    
    Args:
        persona_config: PersonaConfig object with demographic info
        api_key: OpenAI API key (optional)
        custom_text: Custom text to speak (optional, uses default script if not provided)
        
    Returns:
        Dict with audio file path and metadata
    """
    try:
        generator = PersonaVoiceGenerator(api_key)
        
        if custom_text:
            return asyncio.run(generator.generate_custom_voice_sample(persona_config, custom_text))
        else:
            return asyncio.run(generator.generate_persona_voice(persona_config))
            
    except ValueError as e:
        # If no API key, return mock response
        if "API key required" in str(e):
            generator = PersonaVoiceGenerator.__new__(PersonaVoiceGenerator)
            generator.voice_profiles = {
                "alloy": {"gender": "neutral", "age": "young", "style": "clear"},
                "echo": {"gender": "male", "age": "middle", "style": "professional"},
                "fable": {"gender": "male", "age": "mature", "style": "warm"},
                "onyx": {"gender": "male", "age": "deep", "style": "authoritative"},
                "nova": {"gender": "female", "age": "young", "style": "energetic"},
                "shimmer": {"gender": "female", "age": "middle", "style": "friendly"}
            }
            return generator.generate_mock_response(persona_config)
        raise


# Example usage
if __name__ == "__main__":
    # Create sample personas
    personas = [
        PersonaConfig(
            name="Maria Rodriguez",
            age=34,
            race_ethnicity="hispanic",
            gender="female",
            education="college",
            location_type="urban",
            income="50k_75k"
        ),
        PersonaConfig(
            name="David Chen",
            age=42,
            race_ethnicity="asian", 
            gender="male",
            education="graduate",
            location_type="suburban",
            income="75k_100k"
        ),
        PersonaConfig(
            name="Sarah Johnson",
            age=28,
            race_ethnicity="black",
            gender="female",
            education="college",
            location_type="urban",
            income="40k_50k"
        )
    ]
    
    async def demo():
        """Demo the voice generator"""
        print("🎤 Persona Voice Generator Demo")
        print("=" * 40)
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  No OPENAI_API_KEY found - using mock responses")
            print("💡 Set OPENAI_API_KEY environment variable for real voice generation")
            
        try:
            generator = PersonaVoiceGenerator(api_key) if api_key else None
            
            for persona in personas:
                print(f"\n👤 Generating voice for {persona.name}")
                
                if generator:
                    # Real API call
                    result = await generator.generate_persona_voice(persona)
                else:
                    # Mock response
                    mock_gen = PersonaVoiceGenerator.__new__(PersonaVoiceGenerator)
                    mock_gen.voice_profiles = PersonaVoiceGenerator.voice_profiles
                    result = mock_gen.generate_mock_response(persona)
                
                if result["success"]:
                    print(f"✅ Voice generated successfully!")
                    print(f"🎵 Audio file: {result['audio_path']}")
                    print(f"🗣️  Voice: {result['voice_used']} - {result['voice_characteristics']}")
                    print(f"💾 File size: {result['file_size_mb']} MB")
                    
                    if result.get("model") == "tts-1":
                        print(f"💰 Cost: ~${len(result['script_text']) * 0.000015:.4f}")
                    
                else:
                    print(f"❌ Generation failed: {result['error']}")
        
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    # Run demo
    asyncio.run(demo())