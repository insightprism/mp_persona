#!/usr/bin/env python3
"""
Persona Image Generator
======================

Generate persona profile images using OpenAI DALL-E API.
Takes key persona features and creates appropriate image prompts.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from openai import OpenAI
from persona_config import PersonaConfig

class PersonaImageGenerator:
    """Generate profile images for personas using DALL-E"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize image generator
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def build_image_prompt(self, persona_config: PersonaConfig) -> str:
        """
        Build DALL-E prompt from persona features
        
        Args:
            persona_config: Persona configuration
            
        Returns:
            String prompt for DALL-E
        """
        # Core demographic features
        age_desc = self._get_age_description(persona_config.age)
        gender = persona_config.gender
        ethnicity = self._get_ethnicity_description(persona_config.race_ethnicity)
        
        # Style and setting based on demographics
        setting = self._get_setting_description(persona_config.location_type)
        clothing = self._get_clothing_style(persona_config.income, persona_config.education)
        
        # Build prompt
        prompt = f"Professional headshot photo of a {age_desc} {ethnicity} {gender}, {clothing}, {setting}, natural lighting, friendly expression, high quality portrait photography"
        
        return prompt
    
    def _get_age_description(self, age: int) -> str:
        """Convert age to descriptive range"""
        if age < 25:
            return "young adult"
        elif age < 35:
            return "young professional"
        elif age < 45:
            return "middle-aged professional"
        elif age < 55:
            return "experienced professional"
        else:
            return "mature professional"
    
    def _get_ethnicity_description(self, race_ethnicity: str) -> str:
        """Convert race/ethnicity to image-appropriate description"""
        ethnicity_map = {
            "white": "Caucasian",
            "black": "African American",
            "hispanic": "Hispanic",
            "asian": "Asian",
            "native_american": "Native American",
            "mixed": "mixed ethnicity",
            "other": "diverse"
        }
        return ethnicity_map.get(race_ethnicity.lower(), "diverse")
    
    def _get_setting_description(self, location_type: str) -> str:
        """Get setting based on location type"""
        setting_map = {
            "urban": "modern office background",
            "suburban": "home office background", 
            "rural": "casual indoor setting"
        }
        return setting_map.get(location_type.lower(), "neutral background")
    
    def _get_clothing_style(self, income: str, education: str) -> str:
        """Determine clothing style from income and education"""
        # Simple mapping for appropriate attire
        if education in ["graduate", "professional"] or "over_100k" in income:
            return "wearing business professional attire"
        elif education == "college" or income in ["75k_100k", "50k_75k"]:
            return "wearing business casual attire"
        else:
            return "wearing casual professional attire"
    
    async def generate_persona_image(self, persona_config: PersonaConfig, size: str = "256x256") -> Dict[str, Any]:
        """
        Generate persona image using DALL-E
        
        Args:
            persona_config: Persona configuration
            size: Image size ("256x256", "512x512", or "1024x1024")
            
        Returns:
            Dict with image URL and metadata
        """
        try:
            # Build prompt
            prompt = self.build_image_prompt(persona_config)
            
            print(f"🎨 Generating image for {persona_config.name}")
            print(f"📝 Prompt: {prompt}")
            
            # Generate image (using DALL-E 2 for lower cost)
            response = self.client.images.generate(
                model="dall-e-2",  # Cheaper than DALL-E 3
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            # Extract result
            image_url = response.data[0].url
            
            return {
                "success": True,
                "image_url": image_url,
                "prompt": prompt,
                "persona_name": persona_config.name,
                "demographics": {
                    "age": persona_config.age,
                    "gender": persona_config.gender,
                    "race_ethnicity": persona_config.race_ethnicity,
                    "location_type": persona_config.location_type,
                    "income": persona_config.income,
                    "education": persona_config.education
                },
                "image_size": size,
                "model": "dall-e-2"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt if 'prompt' in locals() else None,
                "persona_name": persona_config.name
            }
    
    def generate_mock_response(self, persona_config: PersonaConfig) -> Dict[str, Any]:
        """Generate mock response for testing without API calls"""
        prompt = self.build_image_prompt(persona_config)
        
        return {
            "success": True,
            "image_url": "https://mock-image-url.com/persona_image.jpg",
            "prompt": prompt,
            "persona_name": persona_config.name,
            "demographics": {
                "age": persona_config.age,
                "gender": persona_config.gender,
                "race_ethnicity": persona_config.race_ethnicity,
                "location_type": persona_config.location_type,
                "income": persona_config.income,
                "education": persona_config.education
            },
            "image_size": "256x256",
            "model": "mock"
        }


# Convenience function for simple usage
def generate_persona_image_simple(persona_config: PersonaConfig, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Simple function to generate persona image
    
    Args:
        persona_config: PersonaConfig object with demographic info
        api_key: OpenAI API key (optional)
        
    Returns:
        Dict with image URL and metadata
    """
    try:
        generator = PersonaImageGenerator(api_key)
        return asyncio.run(generator.generate_persona_image(persona_config))
    except ValueError as e:
        # If no API key, return mock response
        if "API key required" in str(e):
            generator = PersonaImageGenerator.__new__(PersonaImageGenerator)
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
        """Demo the image generator"""
        print("🎨 Persona Image Generator Demo")
        print("=" * 40)
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  No OPENAI_API_KEY found - using mock responses")
            print("💡 Set OPENAI_API_KEY environment variable for real image generation")
            
        try:
            generator = PersonaImageGenerator(api_key)
            
            for persona in personas:
                print(f"\n👤 Generating image for {persona.name}")
                
                if api_key:
                    result = await generator.generate_persona_image(persona, size="256x256")
                else:
                    result = generator.generate_mock_response(persona)
                
                if result["success"]:
                    print(f"✅ Success! Image URL: {result['image_url']}")
                    print(f"📝 Prompt used: {result['prompt']}")
                else:
                    print(f"❌ Failed: {result['error']}")
        
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    # Run demo
    asyncio.run(demo())