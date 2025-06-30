"""
Environmentally Aware Persona System

This addresses the critical insight that people with identical demographics behave differently 
based on their social environment. A Hispanic teacher in Dallas acts differently than one in 
Detroit due to social pressures, reference groups, and local demographic composition.

Key Capabilities:
1. Self-understanding: Base demographics and individual traits
2. Environmental understanding: Local demographic composition, political leanings, cultural norms
3. Other agent awareness: Perceive and respond to surrounding persona demographics
4. Social conformity modeling: Pressure to align with local majority behaviors
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math
import random
import inspect
import os
from datetime import datetime
from persona_config import PersonaConfig


class SocialPressureType(Enum):
    """Types of social pressure that influence behavior"""
    CONFORMITY = "conformity"  # Pressure to match local majority
    MINORITY_SOLIDARITY = "minority_solidarity"  # Bonding with similar minorities
    ECONOMIC_PRESSURE = "economic_pressure"  # Local economic conditions
    CULTURAL_NORM = "cultural_norm"  # Local cultural expectations
    POLITICAL_CLIMATE = "political_climate"  # Local political environment


@dataclass
class EnvironmentalContext:
    """Represents the social/demographic environment around a persona"""
    
    # Geographic context
    location_name: str
    location_type: str  # urban, suburban, rural
    state: str
    region: str  # northeast, south, midwest, west
    
    # Demographic composition (percentages)
    racial_composition: Dict[str, float]  # e.g., {"white": 0.65, "hispanic": 0.20, "black": 0.10}
    age_distribution: Dict[str, float]    # e.g., {"18_29": 0.15, "30_44": 0.25, "45_64": 0.35}
    education_levels: Dict[str, float]    # e.g., {"high_school": 0.30, "bachelors": 0.35}
    income_distribution: Dict[str, float] # e.g., {"under_50k": 0.40, "50k_100k": 0.35}
    
    # Political/cultural context
    political_lean: str  # "conservative", "moderate", "liberal"
    political_strength: float  # 0.0-1.0, how strongly political the area is
    religious_composition: Dict[str, float]  # dominant religions
    
    # Economic context
    unemployment_rate: float
    median_income: float
    economic_trend: str  # "declining", "stable", "growing"
    
    # Social dynamics
    social_cohesion: float  # 0.0-1.0, how tight-knit the community is
    cultural_diversity: float  # 0.0-1.0, calculated from demographics
    change_rate: float  # 0.0-1.0, how fast demographics are changing


@dataclass
class SocialPressure:
    """Represents a specific social pressure acting on a persona"""
    pressure_type: SocialPressureType
    strength: float  # 0.0-1.0
    direction: str   # "conform", "resist", "moderate"
    source: str      # what's causing this pressure
    description: str


@dataclass
class ReferenceGroup:
    """People the persona looks to for behavioral cues"""
    group_name: str
    demographic_profile: Dict[str, Any]
    influence_strength: float  # 0.0-1.0
    behavioral_tendencies: Dict[str, Any]


class EnvironmentallyAwarePersona:
    """
    Persona that understands itself, its environment, and other agents around it.
    Adjusts behavior based on social pressures and environmental context.
    """
    
    def __init__(self, base_persona: PersonaConfig, environmental_context: EnvironmentalContext):
        self.base_persona = base_persona
        self.environment = environmental_context
        
        # Calculate environmental pressures
        self.social_pressures = self._calculate_social_pressures()
        self.reference_groups = self._identify_reference_groups()
        self.conformity_tendency = self._calculate_conformity_tendency()
        
        # Track other personas in environment (for multi-agent awareness)
        self.nearby_personas: List['EnvironmentallyAwarePersona'] = []
        self.social_network_influence = 0.0
    
    def _calculate_social_pressures(self) -> List[SocialPressure]:
        """Calculate social pressures based on persona-environment mismatch"""
        pressures = []
        
        # Racial/ethnic conformity pressure
        persona_race = self.base_persona.race_ethnicity.lower()
        if persona_race in self.environment.racial_composition:
            local_percentage = self.environment.racial_composition[persona_race]
            
            if local_percentage < 0.15:  # Minority in area
                pressures.append(SocialPressure(
                    pressure_type=SocialPressureType.MINORITY_SOLIDARITY,
                    strength=min(1.0, (0.15 - local_percentage) * 3),  # Stronger when smaller minority
                    direction="group_solidarity",
                    source=f"Racial minority ({local_percentage:.1%}) in {self.environment.location_name}",
                    description=f"Pressure to maintain group identity as {persona_race} minority"
                ))
                
                pressures.append(SocialPressure(
                    pressure_type=SocialPressureType.CONFORMITY,
                    strength=min(0.8, local_percentage * 2),  # Some pressure to fit in
                    direction="moderate_adaptation",
                    source=f"Majority culture in {self.environment.location_name}",
                    description="Pressure to adapt to local majority culture"
                ))
            
            elif local_percentage > 0.7:  # Strong majority
                pressures.append(SocialPressure(
                    pressure_type=SocialPressureType.CULTURAL_NORM,
                    strength=local_percentage,
                    direction="cultural_expression",
                    source=f"Cultural majority ({local_percentage:.1%}) in area",
                    description="Freedom to express cultural identity openly"
                ))
        
        # Political climate pressure
        persona_likely_politics = self._estimate_political_lean()
        if persona_likely_politics != self.environment.political_lean:
            mismatch_strength = self.environment.political_strength * 0.6
            pressures.append(SocialPressure(
                pressure_type=SocialPressureType.POLITICAL_CLIMATE,
                strength=mismatch_strength,
                direction="moderate" if mismatch_strength < 0.5 else "conform_or_resist",
                source=f"Local political climate: {self.environment.political_lean}",
                description=f"Political minority in {self.environment.political_lean} area"
            ))
        
        # Economic pressure
        persona_income = self.base_persona.income
        if persona_income in self.environment.income_distribution:
            income_fit = self.environment.income_distribution[persona_income]
            if income_fit < 0.2:  # Economic outlier
                economic_pressure_strength = 0.4 + (0.6 * (1 - income_fit))
                pressures.append(SocialPressure(
                    pressure_type=SocialPressureType.ECONOMIC_PRESSURE,
                    strength=economic_pressure_strength,
                    direction="economic_adaptation",
                    source=f"Economic outlier in {self.environment.location_name}",
                    description="Pressure from economic class differences"
                ))
        
        return pressures
    
    def _identify_reference_groups(self) -> List[ReferenceGroup]:
        """Identify groups this persona looks to for behavioral cues"""
        reference_groups = []
        
        # Primary reference group: people like me
        similar_demo_percentage = self._calculate_similar_demographic_percentage()
        reference_groups.append(ReferenceGroup(
            group_name=f"Similar {self.base_persona.race_ethnicity} {self.base_persona.gender}s",
            demographic_profile={
                "race_ethnicity": self.base_persona.race_ethnicity,
                "gender": self.base_persona.gender,
                "age_range": f"{self.base_persona.age-5}-{self.base_persona.age+5}"
            },
            influence_strength=0.4 + (0.3 * similar_demo_percentage),
            behavioral_tendencies=self._estimate_group_behaviors("demographic_similar")
        ))
        
        # Professional reference group
        if hasattr(self.base_persona, 'occupation'):
            reference_groups.append(ReferenceGroup(
                group_name=f"Local {getattr(self.base_persona, 'occupation', 'Professionals')}",
                demographic_profile={"occupation": getattr(self.base_persona, 'occupation', 'professional')},
                influence_strength=0.3,
                behavioral_tendencies=self._estimate_group_behaviors("professional")
            ))
        
        # Local majority group (if different from persona)
        majority_race = max(self.environment.racial_composition.items(), key=lambda x: x[1])
        if majority_race[0] != self.base_persona.race_ethnicity.lower():
            reference_groups.append(ReferenceGroup(
                group_name=f"Local {majority_race[0].title()} Majority",
                demographic_profile={"race_ethnicity": majority_race[0]},
                influence_strength=0.2 + (0.3 * majority_race[1]) - (0.2 * similar_demo_percentage),
                behavioral_tendencies=self._estimate_group_behaviors("local_majority")
            ))
        
        return reference_groups
    
    def _calculate_conformity_tendency(self) -> float:
        """Calculate how much this persona tends to conform vs resist social pressure"""
        base_conformity = 0.5  # Neutral starting point
        
        # Age factor - younger and older tend to conform more
        age = self.base_persona.age
        if age < 30 or age > 65:
            base_conformity += 0.15
        elif 30 <= age <= 45:
            base_conformity -= 0.1  # Peak independence years
        
        # Education factor - higher education = less conformity
        education = self.base_persona.education.lower()
        if "college" in education or "bachelor" in education:
            base_conformity -= 0.1
        elif "advanced" in education or "graduate" in education:
            base_conformity -= 0.2
        elif "high school" in education:
            base_conformity += 0.1
        
        # Minority status - can increase both conformity and resistance
        minority_status = self._calculate_minority_status()
        if minority_status > 0.7:  # Strong minority
            # Bimodal: either high conformity or high resistance
            base_conformity += random.choice([-0.3, 0.3])
        
        # Social cohesion of environment
        base_conformity += self.environment.social_cohesion * 0.2
        
        return max(0.0, min(1.0, base_conformity))
    
    def _calculate_similar_demographic_percentage(self) -> float:
        """Calculate what percentage of local population is demographically similar"""
        similarity_score = 0.0
        
        # Race/ethnicity similarity
        persona_race = self.base_persona.race_ethnicity.lower()
        if persona_race in self.environment.racial_composition:
            similarity_score += self.environment.racial_composition[persona_race] * 0.4
        
        # Age similarity (rough approximation)
        age_group = self._get_age_group(self.base_persona.age)
        if age_group in self.environment.age_distribution:
            similarity_score += self.environment.age_distribution[age_group] * 0.2
        
        # Education similarity
        education_level = self._map_education_to_category(self.base_persona.education)
        if education_level in self.environment.education_levels:
            similarity_score += self.environment.education_levels[education_level] * 0.2
        
        # Income similarity
        if self.base_persona.income in self.environment.income_distribution:
            similarity_score += self.environment.income_distribution[self.base_persona.income] * 0.2
        
        return min(1.0, similarity_score)
    
    def _calculate_minority_status(self) -> float:
        """Calculate how much of a minority this persona is in their environment"""
        persona_race = self.base_persona.race_ethnicity.lower()
        if persona_race in self.environment.racial_composition:
            local_percentage = self.environment.racial_composition[persona_race]
            return 1.0 - local_percentage  # Higher score = more minority
        return 0.8  # Assume minority if not in composition data
    
    def _estimate_political_lean(self) -> str:
        """Estimate persona's political lean based on demographics"""
        # Simplified heuristic - in reality would use polling data
        age = self.base_persona.age
        education = self.base_persona.education.lower()
        race = self.base_persona.race_ethnicity.lower()
        
        conservative_score = 0
        liberal_score = 0
        
        # Age factors
        if age > 60:
            conservative_score += 2
        elif age < 35:
            liberal_score += 1
        
        # Education factors
        if "college" in education or "graduate" in education:
            liberal_score += 2
        elif "high school" in education:
            conservative_score += 1
        
        # Race factors (based on general polling trends)
        if race in ["black", "hispanic", "asian"]:
            liberal_score += 2
        elif race == "white":
            conservative_score += 1
        
        if conservative_score > liberal_score:
            return "conservative"
        elif liberal_score > conservative_score:
            return "liberal"
        else:
            return "moderate"
    
    def _estimate_group_behaviors(self, group_type: str) -> Dict[str, Any]:
        """Estimate behavioral tendencies for different reference groups"""
        # This would be populated from actual behavioral data
        # For now, simplified examples
        if group_type == "demographic_similar":
            return {
                "political_engagement": "moderate",
                "consumer_behavior": "brand_conscious",
                "social_media_usage": "high",
                "community_involvement": "moderate"
            }
        elif group_type == "professional":
            return {
                "political_engagement": "high",
                "consumer_behavior": "value_conscious",
                "social_media_usage": "moderate",
                "community_involvement": "high"
            }
        elif group_type == "local_majority":
            return {
                "political_engagement": "moderate",
                "consumer_behavior": "mainstream",
                "social_media_usage": "moderate",
                "community_involvement": "high"
            }
        return {}
    
    def _get_age_group(self, age: int) -> str:
        """Map age to standard age group categories"""
        if age < 30:
            return "18_29"
        elif age < 45:
            return "30_44"
        elif age < 65:
            return "45_64"
        else:
            return "65_plus"
    
    def _map_education_to_category(self, education: str) -> str:
        """Map education string to standard categories"""
        education_lower = education.lower()
        if "high school" in education_lower:
            return "high_school"
        elif "college" in education_lower or "bachelor" in education_lower:
            return "bachelors"
        elif "graduate" in education_lower or "master" in education_lower or "phd" in education_lower:
            return "graduate"
        else:
            return "some_college"
    
    def add_nearby_persona(self, other_persona: 'EnvironmentallyAwarePersona'):
        """Add another persona to the local social environment"""
        self.nearby_personas.append(other_persona)
        self._update_social_network_influence()
    
    def _update_social_network_influence(self):
        """Update influence based on nearby personas"""
        if not self.nearby_personas:
            self.social_network_influence = 0.0
            return
        
        # Calculate influence based on similarity and proximity
        total_influence = 0.0
        for persona in self.nearby_personas:
            similarity = self._calculate_persona_similarity(persona)
            total_influence += similarity * 0.3  # Each similar persona adds influence
        
        self.social_network_influence = min(1.0, total_influence)
    
    def _calculate_persona_similarity(self, other_persona: 'EnvironmentallyAwarePersona') -> float:
        """Calculate similarity to another persona"""
        similarity = 0.0
        
        # Demographic similarity
        if self.base_persona.race_ethnicity == other_persona.base_persona.race_ethnicity:
            similarity += 0.3
        if self.base_persona.gender == other_persona.base_persona.gender:
            similarity += 0.2
        if abs(self.base_persona.age - other_persona.base_persona.age) < 10:
            similarity += 0.2
        if self.base_persona.education == other_persona.base_persona.education:
            similarity += 0.2
        if self.base_persona.income == other_persona.base_persona.income:
            similarity += 0.1
        
        return similarity
    
    def get_behavioral_adjustment_context(self, scenario_type: str) -> Dict[str, Any]:
        """
        Get context for how environment affects behavior in specific scenarios.
        This is what gets passed to the LLM to adjust persona behavior.
        """
        
        # Calculate overall social pressure
        total_pressure = sum(p.strength for p in self.social_pressures)
        dominant_pressure = max(self.social_pressures, key=lambda p: p.strength) if self.social_pressures else None
        
        # Calculate reference group influence
        primary_reference = max(self.reference_groups, key=lambda g: g.influence_strength) if self.reference_groups else None
        
        context = {
            "environmental_summary": {
                "location": f"{self.environment.location_name}, {self.environment.state}",
                "location_type": self.environment.location_type,
                "demographic_fit": self._calculate_similar_demographic_percentage(),
                "minority_status": self._calculate_minority_status(),
                "political_alignment": self._estimate_political_lean() == self.environment.political_lean
            },
            
            "social_pressures": {
                "total_pressure_strength": total_pressure,
                "dominant_pressure": {
                    "type": dominant_pressure.pressure_type.value,
                    "strength": dominant_pressure.strength,
                    "description": dominant_pressure.description
                } if dominant_pressure else None,
                "conformity_tendency": self.conformity_tendency,
                "all_pressures": [
                    {
                        "type": p.pressure_type.value,
                        "strength": p.strength,
                        "direction": p.direction,
                        "description": p.description
                    } for p in self.social_pressures
                ]
            },
            
            "reference_groups": {
                "primary_reference": {
                    "group": primary_reference.group_name,
                    "influence": primary_reference.influence_strength,
                    "behaviors": primary_reference.behavioral_tendencies
                } if primary_reference else None,
                "all_groups": [
                    {
                        "group": g.group_name,
                        "influence": g.influence_strength,
                        "behaviors": g.behavioral_tendencies
                    } for g in self.reference_groups
                ]
            },
            
            "social_network": {
                "nearby_personas_count": len(self.nearby_personas),
                "social_influence_strength": self.social_network_influence,
                "similar_personas_nearby": sum(1 for p in self.nearby_personas 
                                             if self._calculate_persona_similarity(p) > 0.5)
            },
            
            "behavioral_guidance": self._generate_behavioral_guidance(scenario_type)
        }
        
        return context
    
    def _generate_behavioral_guidance(self, scenario_type: str) -> Dict[str, str]:
        """Generate specific behavioral guidance based on environment and scenario"""
        guidance = {}
        
        minority_status = self._calculate_minority_status()
        similar_demo_pct = self._calculate_similar_demographic_percentage()
        
        if scenario_type == "political":
            if minority_status > 0.7:  # Strong minority
                if self.conformity_tendency > 0.6:
                    guidance["political_expression"] = "Be more cautious about expressing political views, tend to moderate positions to fit in"
                else:
                    guidance["political_expression"] = "May express minority political views more strongly as form of identity assertion"
            else:
                guidance["political_expression"] = "Feel comfortable expressing political views that align with local majority"
        
        elif scenario_type == "consumer":
            if similar_demo_pct < 0.3:  # Few similar people around
                guidance["purchase_decisions"] = "More likely to choose mainstream brands to fit in, avoid culturally specific products"
            else:
                guidance["purchase_decisions"] = "Comfortable choosing products that reflect personal/cultural identity"
        
        elif scenario_type == "social":
            social_cohesion = self.environment.social_cohesion
            if social_cohesion > 0.7:
                guidance["social_behavior"] = "Strong pressure to conform to local social norms and participate in community activities"
            else:
                guidance["social_behavior"] = "More individual freedom in social choices, less community pressure"
        
        # General guidance based on dominant social pressure
        if self.social_pressures:
            dominant = max(self.social_pressures, key=lambda p: p.strength)
            if dominant.pressure_type == SocialPressureType.CONFORMITY:
                guidance["general_tendency"] = "Tend to moderate opinions and behaviors to match local norms"
            elif dominant.pressure_type == SocialPressureType.MINORITY_SOLIDARITY:
                guidance["general_tendency"] = "More likely to maintain group identity and resist assimilation"
            elif dominant.pressure_type == SocialPressureType.POLITICAL_CLIMATE:
                guidance["general_tendency"] = "Political views influenced by need to navigate local political environment"
        
        return guidance
    
    def generate_llm_prompt_context(self, scenario_description: str, scenario_type: str) -> str:
        """Generate context string for LLM prompt that includes environmental awareness"""
        
        context = self.get_behavioral_adjustment_context(scenario_type)
        
        prompt_parts = [
            f"You are {self.base_persona.name}, a {self.base_persona.age}-year-old {self.base_persona.race_ethnicity} {self.base_persona.gender} living in {self.environment.location_name}, {self.environment.state}.",
            f"Your basic demographics: {self.base_persona.education} education, {self.base_persona.income} income, {self.environment.location_type} environment.",
            "",
            "IMPORTANT - Environmental Context:",
            f"• You live in an area that is {self.environment.racial_composition} racially/ethnically",
            f"• The local political climate is {self.environment.political_lean} (strength: {self.environment.political_strength:.1f})",
            f"• You represent {context['environmental_summary']['demographic_fit']:.1%} demographic similarity to local population",
        ]
        
        if context['environmental_summary']['minority_status'] > 0.5:
            prompt_parts.append(f"• You are a demographic minority in this area (minority status: {context['environmental_summary']['minority_status']:.1%})")
        
        prompt_parts.extend([
            "",
            "Social Pressures Affecting Your Behavior:"
        ])
        
        for pressure in context['social_pressures']['all_pressures']:
            prompt_parts.append(f"• {pressure['description']} (strength: {pressure['strength']:.1f})")
        
        if context['reference_groups']['primary_reference']:
            primary_ref = context['reference_groups']['primary_reference']
            prompt_parts.extend([
                "",
                f"Primary Reference Group: {primary_ref['group']} (influence: {primary_ref['influence']:.1f})",
                f"Their typical behaviors: {primary_ref['behaviors']}"
            ])
        
        if context['behavioral_guidance']:
            prompt_parts.extend([
                "",
                "Behavioral Guidance Based on Your Environment:"
            ])
            for key, guidance in context['behavioral_guidance'].items():
                prompt_parts.append(f"• {key}: {guidance}")
        
        prompt_parts.extend([
            "",
            f"Conformity Tendency: {self.conformity_tendency:.1f} (0=independent, 1=conformist)",
            "",
            "Now, considering ALL of these environmental and social factors, respond to the following scenario as this persona would, taking into account how your environment shapes your behavior:",
            "",
            scenario_description
        ])
        
        return "\n".join(prompt_parts)

    def get_environmental_prompt_context(self, secret_key: str = None) -> str:
        """
        Return the complete environmental prompt context (sensitive information).
        Requires secret key for security.
        """
        # Security check
        expected_key = os.getenv("PERSONA_SOURCE_SECRET", "persona_debug_2024")
        if secret_key != expected_key:
            return "❌ Access denied: Invalid secret key required for environmental prompt access"
        
        # Return a sample prompt context for demonstration
        return self.generate_llm_prompt_context(
            "Sample scenario for environmental context demonstration", 
            "general"
        )

    # ========================================
    # SELF-IDENTIFICATION CAPABILITIES
    # ========================================

    def describe_environmental_capabilities(self) -> Dict[str, str]:
        """
        Describe my environmental awareness functions.
        Public method - no security key required.
        """
        return {
            "calculate_social_pressures": "Analyze social pressures affecting my behavior based on environment",
            "identify_reference_groups": "Find groups I look to for behavioral cues", 
            "calculate_conformity_tendency": "Determine my tendency to conform vs resist social pressure",
            "calculate_similarity": "Compare myself to other personas demographically",
            "get_behavioral_adjustment_context": "Get environmental behavior modifications for scenarios",
            "add_nearby_persona": "Add another persona to my social environment",
            "generate_llm_prompt_context": "Create environmentally-aware persona prompt",
            "calculate_minority_status": "Assess how much of a minority I am in this environment",
            "estimate_political_lean": "Predict my political orientation from demographics",
            "get_environmental_summary": "Get complete environmental context description"
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

    def describe_environmental_state(self) -> Dict[str, Any]:
        """
        Describe my environmental context and social pressures.
        """
        return {
            "location": f"{self.environment.location_name}, {self.environment.state}",
            "location_type": self.environment.location_type,
            "demographic_fit": self._calculate_similar_demographic_percentage(),
            "minority_status": self._calculate_minority_status(),
            "conformity_tendency": self.conformity_tendency,
            "social_pressures": [
                {
                    "type": p.pressure_type.value,
                    "strength": p.strength,
                    "direction": p.direction,
                    "description": p.description
                } for p in self.social_pressures
            ],
            "reference_groups": [{
                "name": g.group_name,
                "influence_strength": g.influence_strength,
                "demographic_profile": g.demographic_profile
            } for g in self.reference_groups],
            "nearby_personas_count": len(self.nearby_personas),
            "social_network_influence": self.social_network_influence,
            "environmental_context": {
                "political_lean": self.environment.political_lean,
                "political_strength": self.environment.political_strength,
                "social_cohesion": self.environment.social_cohesion,
                "cultural_diversity": self.environment.cultural_diversity,
                "economic_trend": self.environment.economic_trend
            }
        }

    def get_demographics(self) -> Dict[str, Any]:
        """
        Return my base demographic configuration.
        """
        return {
            "name": self.base_persona.name,
            "age": self.base_persona.age,
            "race_ethnicity": self.base_persona.race_ethnicity,
            "gender": self.base_persona.gender,
            "education": self.base_persona.education,
            "location_type": self.base_persona.location_type,
            "income": self.base_persona.income,
            "religion": getattr(self.base_persona, 'religion', None),
            "marital_status": getattr(self.base_persona, 'marital_status', None),
            "occupation": getattr(self.base_persona, 'occupation', None),
            "state": getattr(self.base_persona, 'state', None)
        }

    def get_behavioral_characteristics(self) -> Dict[str, str]:
        """
        Return behavioral traits for other agents to understand.
        """
        return self.base_persona.get_behavioral_characteristics()

    def describe_self(self) -> Dict[str, Any]:
        """
        Complete self-description for other agents.
        This is the main method other agents should call to understand me.
        """
        return {
            "agent_type": "EnvironmentallyAwarePersona",
            "class_name": self.__class__.__name__,
            "persona_identity": {
                "name": self.base_persona.name,
                "demographics": self.get_demographics(),
                "behavioral_characteristics": self.get_behavioral_characteristics()
            },
            "environmental_capabilities": self.describe_environmental_capabilities(),
            "environmental_state": self.describe_environmental_state(),
            "available_methods": self.get_available_methods(),
            "social_analysis": {
                "conformity_tendency": self.conformity_tendency,
                "estimated_political_lean": self._estimate_political_lean(),
                "minority_status": self._calculate_minority_status(),
                "similar_demographic_percentage": self._calculate_similar_demographic_percentage()
            },
            "interaction_capabilities": {
                "can_interact_with": ["other_personas", "llm_engines", "simulation_engines"],
                "supports_multi_agent_awareness": True,
                "environmental_context_generation": True
            }
        }

    def can_perform(self, capability: str) -> bool:
        """
        Can I perform this environmental capability?
        """
        return capability in self.describe_environmental_capabilities()

    def share_capabilities_with_agent(self, requesting_agent_id: str = None) -> Dict[str, Any]:
        """
        Structured response when another agent asks 'what can you do?'
        This is the standardized interface for inter-agent communication.
        """
        return {
            "response_type": "environmental_capability_sharing",
            "responding_agent": {
                "type": "EnvironmentallyAwarePersona",
                "name": self.base_persona.name,
                "location": f"{self.environment.location_name}, {self.environment.state}"
            },
            "requesting_agent_id": requesting_agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "environmental_capabilities": self.describe_environmental_capabilities(),
            "demographic_profile": self.get_demographics(),
            "environmental_context": self.describe_environmental_state(),
            "social_analysis_summary": {
                "conformity_tendency": self.conformity_tendency,
                "primary_social_pressures": [p.description for p in self.social_pressures[:3]],
                "primary_reference_groups": [g.group_name for g in self.reference_groups[:3]],
                "environmental_fit": "high" if self._calculate_similar_demographic_percentage() > 0.6 else "low"
            },
            "interaction_interface": {
                "add_to_social_network": "add_nearby_persona(other_persona)",
                "get_environmental_context": "get_behavioral_adjustment_context(scenario_type)",
                "generate_llm_prompt": "generate_llm_prompt_context(scenario, scenario_type)",
                "compare_similarity": "_calculate_persona_similarity(other_persona)"
            },
            "security_note": "Some methods require PERSONA_SOURCE_SECRET environment variable"
        }

    def get_environmental_summary(self) -> Dict[str, Any]:
        """
        Get complete environmental context description for other agents.
        """
        return {
            "location_details": {
                "name": self.environment.location_name,
                "state": self.environment.state,
                "type": self.environment.location_type,
                "region": self.environment.region
            },
            "demographic_composition": {
                "racial_composition": self.environment.racial_composition,
                "age_distribution": self.environment.age_distribution,
                "education_levels": self.environment.education_levels,
                "income_distribution": self.environment.income_distribution
            },
            "social_dynamics": {
                "political_lean": self.environment.political_lean,
                "political_strength": self.environment.political_strength,
                "social_cohesion": self.environment.social_cohesion,
                "cultural_diversity": self.environment.cultural_diversity,
                "change_rate": self.environment.change_rate
            },
            "economic_context": {
                "unemployment_rate": self.environment.unemployment_rate,
                "median_income": self.environment.median_income,
                "economic_trend": self.environment.economic_trend
            },
            "persona_fit_analysis": {
                "demographic_similarity": self._calculate_similar_demographic_percentage(),
                "minority_status": self._calculate_minority_status(),
                "estimated_political_alignment": self._estimate_political_lean() == self.environment.political_lean
            }
        }


# Example usage and testing functions

def create_sample_environments() -> Dict[str, EnvironmentalContext]:
    """Create sample environmental contexts for testing"""
    
    environments = {}
    
    # Dallas, TX - diverse urban area
    environments["dallas_tx"] = EnvironmentalContext(
        location_name="Dallas",
        location_type="urban",
        state="Texas",
        region="south",
        racial_composition={"white": 0.29, "hispanic": 0.42, "black": 0.24, "asian": 0.04},
        age_distribution={"18_29": 0.22, "30_44": 0.28, "45_64": 0.32, "65_plus": 0.18},
        education_levels={"high_school": 0.35, "bachelors": 0.30, "graduate": 0.15, "some_college": 0.20},
        income_distribution={"under_50k": 0.45, "50k_100k": 0.35, "over_100k": 0.20},
        political_lean="moderate",
        political_strength=0.6,
        religious_composition={"christian": 0.78, "other": 0.22},
        unemployment_rate=0.06,
        median_income=65000,
        economic_trend="growing",
        social_cohesion=0.4,
        cultural_diversity=0.8,
        change_rate=0.7
    )
    
    # Detroit, MI - majority Black urban area
    environments["detroit_mi"] = EnvironmentalContext(
        location_name="Detroit",
        location_type="urban",
        state="Michigan",
        region="midwest",
        racial_composition={"white": 0.14, "hispanic": 0.07, "black": 0.79, "asian": 0.01},
        age_distribution={"18_29": 0.20, "30_44": 0.25, "45_64": 0.35, "65_plus": 0.20},
        education_levels={"high_school": 0.45, "bachelors": 0.20, "graduate": 0.10, "some_college": 0.25},
        income_distribution={"under_50k": 0.65, "50k_100k": 0.25, "over_100k": 0.10},
        political_lean="liberal",
        political_strength=0.8,
        religious_composition={"christian": 0.85, "other": 0.15},
        unemployment_rate=0.12,
        median_income=45000,
        economic_trend="stable",
        social_cohesion=0.7,
        cultural_diversity=0.3,
        change_rate=0.2
    )
    
    # Suburban Minneapolis, MN - predominantly white, educated
    environments["minneapolis_suburbs"] = EnvironmentalContext(
        location_name="Bloomington",
        location_type="suburban",
        state="Minnesota",
        region="midwest",
        racial_composition={"white": 0.75, "hispanic": 0.08, "black": 0.06, "asian": 0.08},
        age_distribution={"18_29": 0.15, "30_44": 0.30, "45_64": 0.35, "65_plus": 0.20},
        education_levels={"high_school": 0.25, "bachelors": 0.40, "graduate": 0.25, "some_college": 0.10},
        income_distribution={"under_50k": 0.25, "50k_100k": 0.45, "over_100k": 0.30},
        political_lean="moderate",
        political_strength=0.5,
        religious_composition={"christian": 0.65, "other": 0.35},
        unemployment_rate=0.04,
        median_income=75000,
        economic_trend="stable",
        social_cohesion=0.6,
        cultural_diversity=0.4,
        change_rate=0.3
    )
    
    return environments


def demonstrate_environmental_awareness():
    """Demonstrate how same persona behaves differently in different environments"""
    
    # Create base persona - Hispanic teacher
    base_persona = PersonaConfig(
        name="Maria Rodriguez",
        age=35,
        race_ethnicity="Hispanic",
        gender="Female",
        education="Bachelor's degree",
        location_type="urban",
        income="50k_75k",
        media_consumption="moderate",
        risk_tolerance="low",
        spending_style="practical",
        civic_engagement="high",
        trust_in_institutions="moderate"
    )
    
    environments = create_sample_environments()
    
    print("🌍 ENVIRONMENTAL AWARENESS DEMONSTRATION")
    print("=" * 80)
    print(f"Base Persona: {base_persona.name} - {base_persona.age}yo {base_persona.race_ethnicity} {base_persona.gender} Teacher")
    print()
    
    # Create environmentally aware personas for different locations
    personas_by_location = {}
    
    for location, env_context in environments.items():
        personas_by_location[location] = EnvironmentallyAwarePersona(base_persona, env_context)
    
    # Show how behavior differs by location
    scenario = "A new school policy proposes requiring all students to take a standardized cultural competency test. What is your opinion on this policy?"
    
    for location, aware_persona in personas_by_location.items():
        print(f"📍 {aware_persona.environment.location_name}, {aware_persona.environment.state}")
        print("-" * 60)
        
        # Show environmental context
        context = aware_persona.get_behavioral_adjustment_context("political")
        
        print(f"Demographic Fit: {context['environmental_summary']['demographic_fit']:.1%}")
        print(f"Minority Status: {context['environmental_summary']['minority_status']:.1%}")
        print(f"Conformity Tendency: {aware_persona.conformity_tendency:.1f}")
        
        print("\nKey Social Pressures:")
        for pressure in context['social_pressures']['all_pressures'][:2]:  # Top 2
            print(f"  • {pressure['description']} (strength: {pressure['strength']:.1f})")
        
        print("\nBehavioral Guidance:")
        for key, guidance in context['behavioral_guidance'].items():
            print(f"  • {key}: {guidance}")
        
        print("\n" + "="*80 + "\n")
    
    return personas_by_location


if __name__ == "__main__":
    demonstrate_environmental_awareness()
