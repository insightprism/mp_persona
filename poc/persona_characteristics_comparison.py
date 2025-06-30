"""
Comparison: Table-Driven vs Text-Driven Persona Characteristics

This demonstrates both approaches for defining persona characteristics
and their trade-offs for AI consumption.
"""

import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass
from persona_config import PersonaConfig


# =============================================================================
# APPROACH 1: TABLE-DRIVEN CHARACTERISTICS
# =============================================================================

class TableDrivenPersonaBuilder:
    """Uses structured tables to define persona characteristics"""
    
    def __init__(self):
        # Political orientation lookup table
        self.political_orientation_table = pd.DataFrame([
            # [age_min, age_max, education, location, race, income_min, income_max, orientation, confidence]
            [18, 35, "graduate", "urban", "any", 0, 200, "liberal", 0.8],
            [18, 35, "college", "urban", "any", 0, 200, "liberal", 0.7],
            [18, 35, "any", "urban", "black", 0, 200, "liberal", 0.9],
            [18, 35, "any", "urban", "hispanic", 0, 200, "liberal", 0.8],
            
            [50, 85, "high_school", "rural", "white", 0, 75, "conservative", 0.9],
            [50, 85, "some_college", "rural", "white", 0, 75, "conservative", 0.8],
            [35, 65, "any", "rural", "white", 0, 100, "conservative", 0.7],
            
            [25, 65, "college", "suburban", "any", 50, 150, "moderate", 0.6],
            [25, 65, "graduate", "suburban", "white", 75, 200, "moderate_liberal", 0.6],
            
            # Default rules
            [18, 85, "any", "any", "any", 0, 200, "moderate", 0.3]
        ], columns=["age_min", "age_max", "education", "location", "race", "income_min", "income_max", "orientation", "confidence"])
        
        # Shopping behavior table
        self.shopping_behavior_table = pd.DataFrame([
            # [income_bracket, age_group, location, behavior, description]
            ["under_30k", "any", "any", "price_conscious", "Shops sales, uses coupons, buys generic brands"],
            ["30k_50k", "under_40", "any", "value_focused", "Balances price and quality, researches before buying"],
            ["50k_75k", "any", "suburban", "convenience_focused", "Values time savings, shops at target/costco"],
            ["75k_100k", "any", "urban", "brand_conscious", "Willing to pay for quality brands and experiences"],
            ["over_100k", "any", "any", "premium_focused", "Buys high-end, values luxury and status"]
        ], columns=["income", "age_group", "location", "behavior", "description"])
        
        # Communication style table
        self.communication_table = pd.DataFrame([
            # [education, age, region, style, vocabulary, tone]
            ["no_hs", "any", "any", "direct", "simple", "practical"],
            ["high_school", "any", "rural", "plain_spoken", "everyday", "straightforward"],
            ["high_school", "any", "urban", "casual", "street_smart", "confident"],
            ["some_college", "any", "any", "conversational", "mixed", "relatable"],
            ["college", "under_40", "any", "articulate", "professional", "informed"],
            ["college", "over_40", "any", "measured", "formal", "experienced"],
            ["graduate", "any", "urban", "sophisticated", "complex", "analytical"],
            ["graduate", "any", "suburban", "diplomatic", "nuanced", "thoughtful"]
        ], columns=["education", "age", "location", "style", "vocabulary", "tone"])
    
    def get_political_orientation(self, persona: PersonaConfig) -> str:
        """Get political orientation using table lookup"""
        
        # Convert income to numeric for comparison
        income_map = {
            "under_30k": 25, "30k_50k": 40, "50k_75k": 62, 
            "75k_100k": 87, "over_100k": 150
        }
        income_numeric = income_map.get(persona.income, 50)
        
        # Filter table based on persona characteristics
        matches = self.political_orientation_table[
            (self.political_orientation_table['age_min'] <= persona.age) &
            (self.political_orientation_table['age_max'] >= persona.age) &
            ((self.political_orientation_table['education'] == persona.education) | 
             (self.political_orientation_table['education'] == "any")) &
            ((self.political_orientation_table['location'] == persona.location_type) | 
             (self.political_orientation_table['location'] == "any")) &
            ((self.political_orientation_table['race'] == persona.race_ethnicity) | 
             (self.political_orientation_table['race'] == "any")) &
            (self.political_orientation_table['income_min'] <= income_numeric) &
            (self.political_orientation_table['income_max'] >= income_numeric)
        ]
        
        if not matches.empty:
            # Get highest confidence match
            best_match = matches.loc[matches['confidence'].idxmax()]
            return best_match['orientation']
        
        return "moderate"  # Default
    
    def get_shopping_behavior(self, persona: PersonaConfig) -> Dict[str, str]:
        """Get shopping behavior using table lookup"""
        
        age_group = "under_40" if persona.age < 40 else "over_40"
        
        matches = self.shopping_behavior_table[
            ((self.shopping_behavior_table['income'] == persona.income) | 
             (self.shopping_behavior_table['income'] == "any")) &
            ((self.shopping_behavior_table['age_group'] == age_group) | 
             (self.shopping_behavior_table['age_group'] == "any")) &
            ((self.shopping_behavior_table['location'] == persona.location_type) | 
             (self.shopping_behavior_table['location'] == "any"))
        ]
        
        if not matches.empty:
            match = matches.iloc[0]
            return {
                "behavior": match['behavior'],
                "description": match['description']
            }
        
        return {"behavior": "practical", "description": "Makes thoughtful purchasing decisions"}
    
    def get_communication_style(self, persona: PersonaConfig) -> Dict[str, str]:
        """Get communication style using table lookup"""
        
        age_group = "under_40" if persona.age < 40 else "over_40"
        
        matches = self.communication_table[
            ((self.communication_table['education'] == persona.education) | 
             (self.communication_table['education'] == "any")) &
            ((self.communication_table['age'] == age_group) | 
             (self.communication_table['age'] == "any")) &
            ((self.communication_table['location'] == persona.location_type) | 
             (self.communication_table['location'] == "any"))
        ]
        
        if not matches.empty:
            match = matches.iloc[0]
            return {
                "style": match['style'],
                "vocabulary": match['vocabulary'],
                "tone": match['tone']
            }
        
        return {"style": "conversational", "vocabulary": "everyday", "tone": "friendly"}


# =============================================================================
# APPROACH 2: TEXT-DRIVEN CHARACTERISTICS (Current Approach)
# =============================================================================

class TextDrivenPersonaBuilder:
    """Uses narrative text generation for persona characteristics"""
    
    def get_political_orientation(self, persona: PersonaConfig) -> str:
        """Generate political orientation through logical narrative"""
        
        conservative_factors = []
        liberal_factors = []
        
        # Age-based factors
        if persona.age > 55:
            conservative_factors.append("traditional values from life experience")
        elif persona.age < 30:
            liberal_factors.append("progressive views from younger generation")
        
        # Location-based factors
        if persona.location_type == "rural":
            conservative_factors.append("rural community values and self-reliance")
        elif persona.location_type == "urban":
            liberal_factors.append("urban diversity and progressive environment")
        
        # Education-based factors
        if persona.education in ["college", "graduate"]:
            liberal_factors.append("higher education exposure to diverse ideas")
        elif persona.education in ["no_hs", "high_school"]:
            conservative_factors.append("practical life experience over academic theory")
        
        # Race-based factors
        if persona.race_ethnicity in ["black", "hispanic"]:
            liberal_factors.append("minority experience with systemic challenges")
        
        # Income-based factors
        if persona.income in ["under_30k", "30k_50k"]:
            liberal_factors.append("support for social programs and worker protections")
        elif persona.income == "over_100k":
            conservative_factors.append("concern about high taxes and regulations")
        
        # Generate narrative explanation
        if len(conservative_factors) > len(liberal_factors):
            factors_text = ", ".join(conservative_factors[:2])
            return f"You lean conservative due to {factors_text}. You believe in personal responsibility, traditional values, and limited government intervention."
        elif len(liberal_factors) > len(conservative_factors):
            factors_text = ", ".join(liberal_factors[:2])
            return f"You lean liberal because of {factors_text}. You support social programs, diversity, and government action on inequality."
        else:
            return "You're politically moderate, seeing merit in both conservative and liberal ideas depending on the specific issue."
    
    def get_shopping_behavior(self, persona: PersonaConfig) -> str:
        """Generate shopping behavior through contextual narrative"""
        
        behaviors = []
        
        # Income-driven behavior
        if persona.income in ["under_30k", "30k_50k"]:
            behaviors.append("you carefully budget every purchase and look for sales")
        elif persona.income in ["50k_75k"]:
            behaviors.append("you balance price and quality, researching before major purchases")
        elif persona.income in ["75k_100k", "over_100k"]:
            behaviors.append("you're willing to pay more for quality and convenience")
        
        # Age-driven behavior
        if persona.age < 35:
            behaviors.append("you often shop online and use apps to compare prices")
        elif persona.age > 50:
            behaviors.append("you prefer shopping in person and building relationships with salespeople")
        
        # Location-driven behavior
        if persona.location_type == "rural":
            behaviors.append("you often drive to larger towns for major shopping")
        elif persona.location_type == "urban":
            behaviors.append("you value convenience and same-day delivery")
        
        return f"When shopping, {' and '.join(behaviors)}."
    
    def get_communication_style(self, persona: PersonaConfig) -> str:
        """Generate communication style through educational and cultural context"""
        
        base_style = ""
        
        # Education-based style
        if persona.education == "graduate":
            base_style = "You communicate with sophistication and nuance, able to discuss complex topics"
        elif persona.education == "college":
            base_style = "You're articulate and well-informed, adjusting your language based on the audience"
        elif persona.education == "high_school":
            base_style = "You speak plainly and directly, valuing common sense over academic complexity"
        else:
            base_style = "You communicate through practical experience and straightforward language"
        
        # Cultural modifications
        cultural_additions = []
        
        if persona.location_type == "rural":
            cultural_additions.append("using regional expressions and down-to-earth examples")
        elif persona.location_type == "urban":
            cultural_additions.append("incorporating current trends and diverse perspectives")
        
        if persona.age < 35:
            cultural_additions.append("comfortable with digital communication and casual tone")
        elif persona.age > 55:
            cultural_additions.append("preferring more formal communication and face-to-face interaction")
        
        if cultural_additions:
            return f"{base_style}, {' and '.join(cultural_additions)}."
        
        return f"{base_style}."


# =============================================================================
# COMPARISON TEST
# =============================================================================

async def compare_approaches():
    """Compare table-driven vs text-driven approaches"""
    
    # Test persona
    maria = PersonaConfig(
        name="Maria Rodriguez",
        age=34,
        race_ethnicity="hispanic",
        gender="female",
        education="college",
        location_type="suburban",
        income="50k_75k",
        occupation="elementary school teacher"
    )
    
    table_builder = TableDrivenPersonaBuilder()
    text_builder = TextDrivenPersonaBuilder()
    
    print("📊 PERSONA CHARACTERISTICS COMPARISON")
    print("=" * 80)
    print(f"Test Persona: {maria.name} - {maria.age}yo {maria.race_ethnicity} {maria.gender}")
    print(f"Background: {maria.education} education, {maria.location_type}, {maria.income}")
    print()
    
    # Compare political orientation
    print("🗳️ POLITICAL ORIENTATION")
    print("-" * 40)
    
    table_politics = table_builder.get_political_orientation(maria)
    text_politics = text_builder.get_political_orientation(maria)
    
    print(f"Table Approach: {table_politics}")
    print(f"Text Approach:  {text_politics}")
    print()
    
    # Compare shopping behavior
    print("🛒 SHOPPING BEHAVIOR")
    print("-" * 40)
    
    table_shopping = table_builder.get_shopping_behavior(maria)
    text_shopping = text_builder.get_shopping_behavior(maria)
    
    print(f"Table Approach: {table_shopping}")
    print(f"Text Approach:  {text_shopping}")
    print()
    
    # Compare communication style
    print("💬 COMMUNICATION STYLE")
    print("-" * 40)
    
    table_comm = table_builder.get_communication_style(maria)
    text_comm = text_builder.get_communication_style(maria)
    
    print(f"Table Approach: {table_comm}")
    print(f"Text Approach:  {text_comm}")
    print()
    
    # Analysis
    print("📈 ANALYSIS")
    print("=" * 80)
    print("TABLE-DRIVEN PROS:")
    print("✅ Precise, data-driven classifications")
    print("✅ Easy to update/modify rules")
    print("✅ Consistent, predictable outputs")
    print("✅ Great for A/B testing variations")
    print("✅ AI can process structured data efficiently")
    print()
    
    print("TABLE-DRIVEN CONS:")
    print("❌ Can feel mechanical/artificial")
    print("❌ Hard to capture nuanced combinations")
    print("❌ Requires extensive rule creation")
    print("❌ May miss edge cases")
    print()
    
    print("TEXT-DRIVEN PROS:")
    print("✅ Natural, flowing narratives")
    print("✅ Captures complex interactions")
    print("✅ More human-like reasoning")
    print("✅ Flexible for edge cases")
    print("✅ Better for LLM consumption")
    print()
    
    print("TEXT-DRIVEN CONS:")
    print("❌ Less predictable outputs")
    print("❌ Harder to systematically modify")
    print("❌ Can be verbose")
    print("❌ Requires more sophisticated logic")


if __name__ == "__main__":
    import asyncio
    asyncio.run(compare_approaches())