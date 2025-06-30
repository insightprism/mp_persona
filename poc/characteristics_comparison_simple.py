"""
Simple Comparison: Table-Driven vs Text-Driven Persona Characteristics
"""

from typing import Dict, Any, List
from persona_config import PersonaConfig


# =============================================================================
# APPROACH 1: TABLE-DRIVEN CHARACTERISTICS
# =============================================================================

class TableDrivenPersonaBuilder:
    """Uses structured lookup tables to define persona characteristics"""
    
    def __init__(self):
        # Political orientation rules as list of tuples
        # (age_min, age_max, education, location, race, income, orientation, confidence)
        self.political_rules = [
            (18, 35, "graduate", "urban", "any", "any", "liberal", 0.8),
            (18, 35, "college", "urban", "any", "any", "liberal", 0.7),
            (18, 50, "any", "any", "black", "any", "liberal", 0.9),
            (18, 50, "any", "any", "hispanic", "any", "liberal", 0.8),
            (50, 85, "high_school", "rural", "white", "under_50k", "conservative", 0.9),
            (35, 85, "any", "rural", "white", "any", "conservative", 0.7),
            (25, 65, "college", "suburban", "any", "middle", "moderate", 0.6),
        ]
        
        # Shopping behavior rules
        self.shopping_rules = [
            ("under_30k", "any", "any", "price_conscious", "Shops sales, uses coupons, buys generic"),
            ("30k_50k", "under_40", "any", "value_focused", "Balances price and quality"),
            ("50k_75k", "any", "suburban", "convenience_focused", "Values time savings"),
            ("over_100k", "any", "any", "premium_focused", "Buys high-end brands"),
        ]
        
        # Communication style rules
        self.communication_rules = [
            ("no_hs", "any", "any", "direct", "simple", "practical"),
            ("high_school", "any", "rural", "plain_spoken", "everyday", "straightforward"),
            ("college", "under_40", "any", "articulate", "professional", "informed"),
            ("graduate", "any", "urban", "sophisticated", "complex", "analytical"),
        ]
    
    def get_political_orientation(self, persona: PersonaConfig) -> str:
        """Get political orientation using table lookup"""
        
        income_group = "under_50k" if persona.income in ["under_30k", "30k_50k"] else "middle"
        
        best_match = None
        best_confidence = 0
        
        for rule in self.political_rules:
            age_min, age_max, education, location, race, income, orientation, confidence = rule
            
            # Check if persona matches this rule
            if (age_min <= persona.age <= age_max and
                (education == "any" or education == persona.education) and
                (location == "any" or location == persona.location_type) and
                (race == "any" or race == persona.race_ethnicity) and
                (income == "any" or income == income_group)):
                
                if confidence > best_confidence:
                    best_match = orientation
                    best_confidence = confidence
        
        return best_match or "moderate"
    
    def get_shopping_behavior(self, persona: PersonaConfig) -> str:
        """Get shopping behavior using table lookup"""
        
        age_group = "under_40" if persona.age < 40 else "over_40"
        
        for rule in self.shopping_rules:
            income, age, location, behavior, description = rule
            
            if ((income == "any" or income == persona.income) and
                (age == "any" or age == age_group) and
                (location == "any" or location == persona.location_type)):
                
                return f"{behavior}: {description}"
        
        return "practical: Makes thoughtful purchasing decisions"
    
    def get_communication_style(self, persona: PersonaConfig) -> str:
        """Get communication style using table lookup"""
        
        age_group = "under_40" if persona.age < 40 else "over_40"
        
        for rule in self.communication_rules:
            education, age, location, style, vocabulary, tone = rule
            
            if ((education == "any" or education == persona.education) and
                (age == "any" or age == age_group) and
                (location == "any" or location == persona.location_type)):
                
                return f"{style} style with {vocabulary} vocabulary and {tone} tone"
        
        return "conversational style with everyday vocabulary and friendly tone"


# =============================================================================
# APPROACH 2: TEXT-DRIVEN CHARACTERISTICS (Current Approach)
# =============================================================================

class TextDrivenPersonaBuilder:
    """Uses narrative text generation for persona characteristics"""
    
    def get_political_orientation(self, persona: PersonaConfig) -> str:
        """Generate political orientation through logical narrative"""
        
        factors = []
        conservative_weight = 0
        liberal_weight = 0
        
        # Age factors
        if persona.age > 55:
            conservative_weight += 2
            factors.append("life experience with traditional values")
        elif persona.age < 30:
            liberal_weight += 2
            factors.append("generational embrace of progressive change")
        
        # Location factors
        if persona.location_type == "rural":
            conservative_weight += 2
            factors.append("rural community emphasis on self-reliance")
        elif persona.location_type == "urban":
            liberal_weight += 2
            factors.append("urban exposure to diversity and social issues")
        
        # Education factors
        if persona.education in ["college", "graduate"]:
            liberal_weight += 1
            factors.append("higher education exposure to different perspectives")
        
        # Race factors
        if persona.race_ethnicity in ["black", "hispanic"]:
            liberal_weight += 2
            factors.append("minority experience with systemic challenges")
        
        # Generate explanation
        key_factors = factors[:2] if len(factors) >= 2 else factors
        
        if conservative_weight > liberal_weight:
            return f"You lean conservative, shaped by {' and '.join(key_factors)}. You believe in personal responsibility, traditional values, and limited government."
        elif liberal_weight > conservative_weight:
            return f"You lean liberal, influenced by {' and '.join(key_factors)}. You support social programs, diversity, and government action on inequality."
        else:
            return "You're politically moderate, seeing merit in both conservative and liberal ideas depending on the specific issue."
    
    def get_shopping_behavior(self, persona: PersonaConfig) -> str:
        """Generate shopping behavior through contextual narrative"""
        
        behaviors = []
        
        # Income-driven behavior
        if persona.income in ["under_30k", "30k_50k"]:
            behaviors.append("carefully budget every purchase and hunt for sales")
        elif persona.income in ["50k_75k"]:
            behaviors.append("balance price and quality, doing research before major purchases")
        elif persona.income in ["75k_100k", "over_100k"]:
            behaviors.append("prioritize quality and convenience over price")
        
        # Age-driven behavior
        if persona.age < 35:
            behaviors.append("frequently shop online and use price comparison apps")
        elif persona.age > 50:
            behaviors.append("prefer in-person shopping and building relationships with salespeople")
        
        # Location-driven behavior
        if persona.location_type == "rural":
            behaviors.append("often drive to larger towns for major shopping trips")
        elif persona.location_type == "urban":
            behaviors.append("value convenience and same-day delivery options")
        
        return f"When shopping, you {' and '.join(behaviors)}."
    
    def get_communication_style(self, persona: PersonaConfig) -> str:
        """Generate communication style through educational and cultural context"""
        
        # Base style from education
        if persona.education == "graduate":
            base = "You communicate with sophistication, comfortable discussing complex topics"
        elif persona.education == "college":
            base = "You're articulate and well-informed, adjusting your language for different audiences"
        elif persona.education == "high_school":
            base = "You speak plainly and directly, valuing common sense over academic complexity"
        else:
            base = "You communicate through practical experience using straightforward language"
        
        # Cultural modifications
        modifiers = []
        
        if persona.location_type == "rural":
            modifiers.append("using regional expressions and down-to-earth examples")
        elif persona.location_type == "urban":
            modifiers.append("incorporating current trends and diverse cultural references")
        
        if persona.age < 35:
            modifiers.append("comfortable with casual digital communication")
        elif persona.age > 55:
            modifiers.append("preferring more formal, respectful interaction")
        
        if modifiers:
            return f"{base}, {' and '.join(modifiers)}."
        
        return f"{base}."


# =============================================================================
# COMPARISON TEST
# =============================================================================

def compare_approaches():
    """Compare table-driven vs text-driven approaches"""
    
    # Test personas
    personas = [
        PersonaConfig(
            name="Maria Rodriguez", age=34, race_ethnicity="hispanic", gender="female",
            education="college", location_type="suburban", income="50k_75k"
        ),
        PersonaConfig(
            name="Bob Johnson", age=52, race_ethnicity="white", gender="male",
            education="high_school", location_type="rural", income="30k_50k"
        ),
        PersonaConfig(
            name="Ashley Chen", age=28, race_ethnicity="asian", gender="female",
            education="graduate", location_type="urban", income="over_100k"
        )
    ]
    
    table_builder = TableDrivenPersonaBuilder()
    text_builder = TextDrivenPersonaBuilder()
    
    print("📊 PERSONA CHARACTERISTICS COMPARISON")
    print("=" * 80)
    print("Testing both approaches with 3 different personas")
    print()
    
    for persona in personas:
        print(f"🎭 {persona.name} ({persona.age}yo {persona.race_ethnicity} {persona.gender})")
        print(f"   {persona.education} education, {persona.location_type}, {persona.income}")
        print("-" * 60)
        
        # Political orientation
        table_politics = table_builder.get_political_orientation(persona)
        text_politics = text_builder.get_political_orientation(persona)
        
        print("🗳️ Political Orientation:")
        print(f"   Table: {table_politics}")
        print(f"   Text:  {text_politics}")
        
        # Shopping behavior
        table_shopping = table_builder.get_shopping_behavior(persona)
        text_shopping = text_builder.get_shopping_behavior(persona)
        
        print("🛒 Shopping Behavior:")
        print(f"   Table: {table_shopping}")
        print(f"   Text:  {text_shopping}")
        
        # Communication style
        table_comm = table_builder.get_communication_style(persona)
        text_comm = text_builder.get_communication_style(persona)
        
        print("💬 Communication Style:")
        print(f"   Table: {table_comm}")
        print(f"   Text:  {text_comm}")
        print()
    
    # Analysis
    print("📈 APPROACH ANALYSIS")
    print("=" * 80)
    
    print("📊 TABLE-DRIVEN APPROACH:")
    print("✅ PROS:")
    print("   • Precise, consistent classifications")
    print("   • Easy to modify rules systematically")
    print("   • Predictable outputs for testing")
    print("   • Great for A/B testing variations")
    print("   • Clear data structure for AI processing")
    print("   • Can handle complex combinations efficiently")
    print()
    print("❌ CONS:")
    print("   • Can feel mechanical or artificial")
    print("   • Requires extensive rule creation upfront")
    print("   • Hard to capture subtle nuances")
    print("   • May miss unexpected combinations")
    print("   • Less natural language flow")
    print()
    
    print("📝 TEXT-DRIVEN APPROACH:")
    print("✅ PROS:")
    print("   • Natural, flowing narratives")
    print("   • Captures complex demographic interactions")
    print("   • More human-like reasoning explanations")
    print("   • Flexible for handling edge cases")
    print("   • Better for LLM consumption and understanding")
    print("   • Explains the 'why' behind characteristics")
    print()
    print("❌ CONS:")
    print("   • Less predictable outputs")
    print("   • Harder to systematically modify")
    print("   • Can be verbose")
    print("   • Requires more sophisticated logic")
    print("   • Harder to ensure consistency")
    print()
    
    print("🎯 RECOMMENDATION:")
    print("=" * 40)
    print("For LLM personas: TEXT-DRIVEN is better because:")
    print("• LLMs understand narrative context better than lookup tables")
    print("• Explanations help LLMs 'understand' the reasoning")
    print("• More natural integration with the persona identity")
    print("• Allows for nuanced combinations of factors")
    print("• Creates more authentic, believable characteristics")
    print()
    print("For data analysis: TABLE-DRIVEN is better because:")
    print("• Consistent outputs for statistical analysis")
    print("• Easy to modify and test systematically")
    print("• Clear data structure for research purposes")


if __name__ == "__main__":
    compare_approaches()