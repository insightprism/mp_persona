"""
HYBRID APPROACH: Structured Data + Natural Language Generation

This combines the precision of table-driven data with the natural flow
of text generation for optimal LLM persona creation.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from persona_config import PersonaConfig


@dataclass
class CharacteristicRule:
    """Structured rule for persona characteristics"""
    # Matching criteria
    age_min: int
    age_max: int
    education_levels: List[str]  # ["college", "graduate"] or ["any"]
    location_types: List[str]    # ["urban", "suburban"] or ["any"] 
    race_ethnicities: List[str]  # ["hispanic", "black"] or ["any"]
    income_levels: List[str]     # ["50k_75k", "75k_100k"] or ["any"]
    
    # Output data
    primary_value: str           # "liberal", "conservative", etc.
    confidence: float           # 0.0 to 1.0
    reasoning_factors: List[str] # ["urban diversity", "higher education"]
    context_modifiers: List[str] # ["but practical about implementation"]
    
    def matches(self, persona: PersonaConfig) -> bool:
        """Check if persona matches this rule"""
        return (
            self.age_min <= persona.age <= self.age_max and
            ("any" in self.education_levels or persona.education in self.education_levels) and
            ("any" in self.location_types or persona.location_type in self.location_types) and
            ("any" in self.race_ethnicities or persona.race_ethnicity in self.race_ethnicities) and
            ("any" in self.income_levels or persona.income in self.income_levels)
        )


class HybridPersonaBuilder:
    """
    Hybrid approach: Structured rules generate natural language explanations
    
    Best of both worlds:
    - Structured data for consistency and modifiability
    - Natural language output for LLM consumption
    """
    
    def __init__(self):
        self.political_rules = [
            # Urban, educated, young liberals
            CharacteristicRule(
                age_min=18, age_max=40,
                education_levels=["college", "graduate"],
                location_types=["urban"],
                race_ethnicities=["any"],
                income_levels=["any"],
                primary_value="liberal",
                confidence=0.8,
                reasoning_factors=["urban exposure to diversity", "higher education perspectives"],
                context_modifiers=["though pragmatic about implementation"]
            ),
            
            # Minority demographics tend liberal
            CharacteristicRule(
                age_min=18, age_max=85,
                education_levels=["any"],
                location_types=["any"],
                race_ethnicities=["black", "hispanic"],
                income_levels=["any"],
                primary_value="liberal",
                confidence=0.9,
                reasoning_factors=["lived experience with systemic challenges", "community solidarity values"],
                context_modifiers=["with strong family and community focus"]
            ),
            
            # Rural, older, white conservatives
            CharacteristicRule(
                age_min=45, age_max=85,
                education_levels=["no_hs", "high_school", "some_college"],
                location_types=["rural"],
                race_ethnicities=["white"],
                income_levels=["under_30k", "30k_50k", "50k_75k"],
                primary_value="conservative",
                confidence=0.9,
                reasoning_factors=["rural self-reliance values", "traditional community expectations"],
                context_modifiers=["but supportive of programs that help working families"]
            ),
            
            # Suburban moderates
            CharacteristicRule(
                age_min=25, age_max=65,
                education_levels=["college"],
                location_types=["suburban"],
                race_ethnicities=["white", "asian"],
                income_levels=["50k_75k", "75k_100k"],
                primary_value="moderate",
                confidence=0.7,
                reasoning_factors=["suburban balance of urban and rural influences", "middle-class stability concerns"],
                context_modifiers=["leaning liberal on social issues, conservative on fiscal matters"]
            )
        ]
        
        self.shopping_rules = [
            CharacteristicRule(
                age_min=18, age_max=85,
                education_levels=["any"],
                location_types=["any"], 
                race_ethnicities=["any"],
                income_levels=["under_30k", "30k_50k"],
                primary_value="price_conscious",
                confidence=0.9,
                reasoning_factors=["tight budget constraints", "necessity-driven purchases"],
                context_modifiers=["but willing to splurge occasionally on family"]
            ),
            
            CharacteristicRule(
                age_min=18, age_max=45,
                education_levels=["college", "graduate"],
                location_types=["urban", "suburban"],
                race_ethnicities=["any"],
                income_levels=["75k_100k", "over_100k"],
                primary_value="convenience_focused",
                confidence=0.8,
                reasoning_factors=["busy professional lifestyle", "time more valuable than money"],
                context_modifiers=["though still comparison shops for major purchases"]
            ),
            
            CharacteristicRule(
                age_min=45, age_max=85,
                education_levels=["any"],
                location_types=["any"],
                race_ethnicities=["any"],
                income_levels=["any"],
                primary_value="relationship_focused",
                confidence=0.7,
                reasoning_factors=["preference for personal service", "trust built through relationships"],
                context_modifiers=["especially for major purchases like cars or appliances"]
            )
        ]
    
    def get_political_orientation(self, persona: PersonaConfig) -> str:
        """Generate political orientation using structured rules + natural language"""
        
        # Find best matching rule
        best_rule = None
        best_confidence = 0
        
        for rule in self.political_rules:
            if rule.matches(persona) and rule.confidence > best_confidence:
                best_rule = rule
                best_confidence = rule.confidence
        
        if not best_rule:
            return "You're politically moderate, taking each issue on its own merits."
        
        # Generate natural language explanation
        factors = " and ".join(best_rule.reasoning_factors)
        context = best_rule.context_modifiers[0] if best_rule.context_modifiers else ""
        
        if best_rule.primary_value == "liberal":
            base_text = f"You lean liberal, shaped by {factors}. You support social programs, diversity, and government action on inequality"
        elif best_rule.primary_value == "conservative":
            base_text = f"You lean conservative, influenced by {factors}. You believe in personal responsibility, traditional values, and limited government"
        else:  # moderate
            base_text = f"You're politically moderate, influenced by {factors}. You see merit in both conservative and liberal approaches"
        
        if context:
            return f"{base_text}, {context}."
        else:
            return f"{base_text}."
    
    def get_shopping_behavior(self, persona: PersonaConfig) -> str:
        """Generate shopping behavior using structured rules + natural language"""
        
        # Find best matching rule
        best_rule = None
        best_confidence = 0
        
        for rule in self.shopping_rules:
            if rule.matches(persona) and rule.confidence > best_confidence:
                best_rule = rule
                best_confidence = rule.confidence
        
        if not best_rule:
            return "You shop thoughtfully, balancing price, quality, and convenience based on your needs."
        
        # Generate natural language explanation
        factors = " and ".join(best_rule.reasoning_factors)
        context = best_rule.context_modifiers[0] if best_rule.context_modifiers else ""
        
        behavior_descriptions = {
            "price_conscious": f"You're very price-conscious when shopping, driven by {factors}",
            "convenience_focused": f"You prioritize convenience when shopping, motivated by {factors}",
            "relationship_focused": f"You prefer building relationships with trusted retailers, valuing {factors}"
        }
        
        base_text = behavior_descriptions.get(best_rule.primary_value, "You shop thoughtfully")
        
        if context:
            return f"{base_text}, {context}."
        else:
            return f"{base_text}."
    
    def generate_complete_profile(self, persona: PersonaConfig) -> Dict[str, str]:
        """Generate complete personality profile using hybrid approach"""
        
        return {
            "political_orientation": self.get_political_orientation(persona),
            "shopping_behavior": self.get_shopping_behavior(persona),
            "communication_style": self._get_communication_style(persona),
            "social_values": self._get_social_values(persona),
            "economic_priorities": self._get_economic_priorities(persona)
        }
    
    def _get_communication_style(self, persona: PersonaConfig) -> str:
        """Generate communication style with structured logic"""
        
        # Base style from education
        education_styles = {
            "no_hs": "You communicate directly and practically, drawing from life experience",
            "high_school": "You speak plainly and straightforwardly, valuing common sense",
            "some_college": "You communicate clearly, mixing casual conversation with informed insights",
            "college": "You're articulate and well-informed, adjusting your style for different audiences",
            "graduate": "You communicate with sophistication, comfortable with complex topics"
        }
        
        base_style = education_styles.get(persona.education, "You communicate naturally")
        
        # Add cultural modifiers
        modifiers = []
        
        if persona.location_type == "rural":
            modifiers.append("using down-to-earth expressions and regional sayings")
        elif persona.location_type == "urban":
            modifiers.append("incorporating current trends and diverse cultural references")
        
        if persona.age < 35:
            modifiers.append("comfortable with digital communication and casual interaction")
        elif persona.age > 55:
            modifiers.append("preferring more formal, respectful conversation")
        
        if modifiers:
            return f"{base_style}, {' and '.join(modifiers)}."
        
        return f"{base_style}."
    
    def _get_social_values(self, persona: PersonaConfig) -> str:
        """Generate social values with age and cultural considerations"""
        
        if persona.age < 30:
            base = "You're progressive on social issues, seeing equality and inclusion as fundamental rights"
        elif persona.age > 60:
            base = "You've witnessed significant social changes and generally support equality, though the pace sometimes feels rapid"
        else:
            base = "You balance traditional values with evolving social norms"
        
        # Add cultural context
        if persona.race_ethnicity in ["black", "hispanic"]:
            return f"{base}, with personal understanding of discrimination and the importance of civil rights."
        elif persona.location_type == "rural":
            return f"{base}, though you prefer gradual change that respects community traditions."
        elif persona.location_type == "urban":
            return f"{base}, embracing diversity as a daily reality in your community."
        
        return f"{base}, taking each issue on its own merits."
    
    def _get_economic_priorities(self, persona: PersonaConfig) -> str:
        """Generate economic priorities based on income and life situation"""
        
        if persona.income in ["under_30k", "30k_50k"]:
            return "You prioritize policies that help working families: higher minimum wage, affordable healthcare, and job security."
        elif persona.income in ["75k_100k", "over_100k"]:
            return "You support free market policies but recognize the need for smart regulation and public investment."
        else:
            return "You want economic policies that protect middle-class gains while ensuring opportunity for others."


# =============================================================================
# COMPARISON TEST
# =============================================================================

def test_hybrid_approach():
    """Test the hybrid approach with different personas"""
    
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
    
    builder = HybridPersonaBuilder()
    
    print("🔄 HYBRID APPROACH: Structured Rules → Natural Language")
    print("=" * 80)
    print("Combines data precision with natural language flow")
    print()
    
    for persona in personas:
        print(f"🎭 {persona.name} ({persona.age}yo {persona.race_ethnicity} {persona.gender})")
        print(f"   {persona.education} education, {persona.location_type}, {persona.income}")
        print("-" * 70)
        
        profile = builder.generate_complete_profile(persona)
        
        for category, description in profile.items():
            category_display = category.replace("_", " ").title()
            print(f"   {category_display}: {description}")
        
        print()
    
    print("🎯 HYBRID APPROACH BENEFITS:")
    print("=" * 50)
    print("✅ Structured rules ensure consistency")
    print("✅ Natural language explanations for LLM consumption") 
    print("✅ Easy to modify rules systematically")
    print("✅ Captures reasoning behind characteristics")
    print("✅ Flexible context modifiers for nuance")
    print("✅ Best of both table-driven and text-driven approaches")
    print()
    print("🚀 RECOMMENDATION FOR LLM PERSONAS:")
    print("Use HYBRID approach because it provides:")
    print("• Precise, data-driven character assignment")
    print("• Natural language explanations LLMs understand")
    print("• Systematic rule modification for research")
    print("• Rich context for authentic persona responses")


if __name__ == "__main__":
    test_hybrid_approach()