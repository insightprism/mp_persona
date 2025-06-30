"""
Census-Proportional Persona Generation

This module generates demographically representative persona populations
based on US Census data for statistically valid behavioral predictions.
"""

import random
import statistics
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import json
from collections import defaultdict

from persona_config import PersonaConfig


@dataclass
class CensusData:
    """US Census demographic distributions"""
    
    # Age distribution (approximate US Census 2022)
    age_distribution = {
        (18, 24): 0.09,   # 9%
        (25, 34): 0.14,   # 14%
        (35, 44): 0.13,   # 13%
        (45, 54): 0.13,   # 13%
        (55, 64): 0.14,   # 14%
        (65, 85): 0.17    # 17%
    }
    
    # Race/ethnicity distribution
    race_distribution = {
        "white": 0.601,
        "hispanic": 0.187,
        "black": 0.134,
        "asian": 0.061,
        "mixed": 0.017
    }
    
    # Gender distribution
    gender_distribution = {
        "female": 0.507,
        "male": 0.493
    }
    
    # Education distribution (adults 25+)
    education_distribution = {
        "no_hs": 0.11,
        "high_school": 0.28,
        "some_college": 0.21,
        "college": 0.25,
        "graduate": 0.15
    }
    
    # Location type distribution
    location_distribution = {
        "urban": 0.82,
        "suburban": 0.12,
        "rural": 0.06
    }
    
    # Income distribution (household)
    income_distribution = {
        "under_30k": 0.19,
        "30k_50k": 0.17,
        "50k_75k": 0.20,
        "75k_100k": 0.17,
        "over_100k": 0.27
    }
    
    # Marital status distribution
    marital_distribution = {
        "single": 0.34,
        "married": 0.48,
        "divorced": 0.11,
        "widowed": 0.07
    }
    
    # Behavioral characteristic distributions (estimated from polling data)
    behavioral_distributions = {
        "media_consumption": {
            "social_media": 0.35,
            "local_news": 0.25,
            "cable_news": 0.20,
            "npr": 0.12,
            "none": 0.08
        },
        "risk_tolerance": {
            "risk_averse": 0.45,
            "moderate": 0.40,
            "risk_taking": 0.15
        },
        "spending_style": {
            "saver": 0.30,
            "budgeter": 0.35,
            "spender": 0.25,
            "investor": 0.10
        },
        "civic_engagement": {
            "highly_engaged": 0.25,
            "occasional_voter": 0.50,
            "politically_disengaged": 0.25
        },
        "trust_in_institutions": {
            "high_trust": 0.20,
            "skeptical": 0.55,
            "distrustful": 0.25
        }
    }


@dataclass
class PopulationValidation:
    """Validation results for generated population"""
    target_size: int
    actual_size: int
    demographic_accuracy: Dict[str, float]  # How close to census targets
    representation_gaps: List[str]  # Underrepresented groups
    validation_score: float  # Overall accuracy score
    recommendations: List[str]


class BehavioralCharacteristicEngine:
    """Assigns behavioral characteristics based on demographic correlations"""
    
    def __init__(self):
        # Correlation rules between demographics and behavior
        self.correlation_rules = {
            # Media consumption correlations
            "media_consumption": {
                ("education", "graduate"): {"npr": 0.4, "social_media": 0.3},
                ("education", "no_hs"): {"local_news": 0.5, "none": 0.3},
                ("age", "under_35"): {"social_media": 0.6},
                ("age", "over_55"): {"cable_news": 0.4, "local_news": 0.3},
                ("location_type", "rural"): {"local_news": 0.4, "cable_news": 0.3},
                ("location_type", "urban"): {"social_media": 0.4, "npr": 0.2}
            },
            
            # Risk tolerance correlations
            "risk_tolerance": {
                ("age", "under_35"): {"risk_taking": 0.3, "moderate": 0.5},
                ("age", "over_55"): {"risk_averse": 0.6},
                ("income", "over_100k"): {"risk_taking": 0.4, "moderate": 0.4},
                ("income", "under_30k"): {"risk_averse": 0.7},
                ("education", "graduate"): {"moderate": 0.5, "risk_taking": 0.3}
            },
            
            # Spending style correlations
            "spending_style": {
                ("income", "over_100k"): {"investor": 0.3, "spender": 0.4},
                ("income", "under_30k"): {"saver": 0.5, "budgeter": 0.4},
                ("age", "under_35"): {"spender": 0.4},
                ("age", "over_55"): {"saver": 0.5, "investor": 0.2},
                ("education", "graduate"): {"investor": 0.3, "budgeter": 0.4}
            },
            
            # Civic engagement correlations
            "civic_engagement": {
                ("education", "graduate"): {"highly_engaged": 0.5},
                ("education", "no_hs"): {"politically_disengaged": 0.5},
                ("age", "over_55"): {"highly_engaged": 0.4},
                ("age", "under_35"): {"occasional_voter": 0.6},
                ("income", "over_100k"): {"highly_engaged": 0.4}
            },
            
            # Trust in institutions correlations
            "trust_in_institutions": {
                ("education", "graduate"): {"skeptical": 0.5, "high_trust": 0.3},
                ("education", "no_hs"): {"distrustful": 0.4, "skeptical": 0.4},
                ("age", "over_55"): {"high_trust": 0.3, "skeptical": 0.5},
                ("location_type", "rural"): {"distrustful": 0.4, "skeptical": 0.4},
                ("location_type", "urban"): {"skeptical": 0.5, "high_trust": 0.3}
            }
        }
    
    def assign_behavioral_characteristics(self, persona: PersonaConfig) -> PersonaConfig:
        """Assign behavioral characteristics based on demographic correlations"""
        
        # Get demographic context
        demo_context = self._get_demographic_context(persona)
        
        # Assign each behavioral characteristic
        for behavior_type, rules in self.correlation_rules.items():
            if getattr(persona, behavior_type) is None:  # Only assign if not already set
                characteristic = self._select_characteristic(behavior_type, demo_context, rules)
                setattr(persona, behavior_type, characteristic)
        
        return persona
    
    def _get_demographic_context(self, persona: PersonaConfig) -> List[Tuple[str, str]]:
        """Extract demographic context for correlation matching"""
        
        context = []
        
        # Age categories
        if persona.age < 35:
            context.append(("age", "under_35"))
        elif persona.age > 55:
            context.append(("age", "over_55"))
        
        # Education
        context.append(("education", persona.education))
        
        # Income
        context.append(("income", persona.income))
        
        # Location
        context.append(("location_type", persona.location_type))
        
        # Race/ethnicity
        context.append(("race_ethnicity", persona.race_ethnicity))
        
        return context
    
    def _select_characteristic(
        self, 
        behavior_type: str, 
        demo_context: List[Tuple[str, str]], 
        rules: Dict[Tuple[str, str], Dict[str, float]]
    ) -> str:
        """Select behavioral characteristic based on demographic correlations"""
        
        # Start with base distribution
        base_dist = CensusData.behavioral_distributions.get(behavior_type, {})
        adjusted_dist = base_dist.copy()
        
        # Apply correlation adjustments
        for demo_key in demo_context:
            if demo_key in rules:
                correlation_adjustments = rules[demo_key]
                
                # Increase probabilities for correlated characteristics
                for char, boost in correlation_adjustments.items():
                    if char in adjusted_dist:
                        adjusted_dist[char] = min(1.0, adjusted_dist[char] + boost)
        
        # Normalize probabilities
        total = sum(adjusted_dist.values())
        if total > 0:
            normalized_dist = {k: v/total for k, v in adjusted_dist.items()}
        else:
            normalized_dist = base_dist
        
        # Select based on weighted random choice
        return self._weighted_random_choice(normalized_dist)
    
    def _weighted_random_choice(self, distribution: Dict[str, float]) -> str:
        """Make weighted random selection from distribution"""
        
        if not distribution:
            return "unknown"
        
        rand_val = random.random()
        cumulative = 0.0
        
        for option, probability in distribution.items():
            cumulative += probability
            if rand_val <= cumulative:
                return option
        
        # Fallback to first option
        return list(distribution.keys())[0]


class CensusPersonaGenerator:
    """Generates census-proportional persona populations"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.behavioral_engine = BehavioralCharacteristicEngine()
        self.generation_history = []
    
    def generate_representative_population(
        self, 
        size: int = 1000,
        include_behavioral_characteristics: bool = True,
        demographic_constraints: Optional[Dict[str, Any]] = None
    ) -> List[PersonaConfig]:
        """
        Generate a demographically representative population
        
        Args:
            size: Target population size
            include_behavioral_characteristics: Whether to assign behavioral traits
            demographic_constraints: Optional constraints (e.g., {"age_min": 25, "education": ["college", "graduate"]})
        
        Returns:
            List of representative personas
        """
        
        print(f"👥 Generating {size} census-proportional personas...")
        
        personas = []
        
        for i in range(size):
            if i % 100 == 0:
                print(f"   Generated {i}/{size} personas")
            
            persona = self._generate_single_persona(demographic_constraints)
            
            if include_behavioral_characteristics:
                persona = self.behavioral_engine.assign_behavioral_characteristics(persona)
            
            personas.append(persona)
        
        print(f"✅ Generated {len(personas)} personas")
        
        # Store generation record
        self.generation_history.append({
            "timestamp": random.randint(1000000000, 9999999999),  # Mock timestamp
            "size": len(personas),
            "constraints": demographic_constraints,
            "behavioral_included": include_behavioral_characteristics
        })
        
        return personas
    
    def _generate_single_persona(self, constraints: Optional[Dict[str, Any]] = None) -> PersonaConfig:
        """Generate a single persona following census distributions"""
        
        # Sample age
        age = self._sample_age(constraints)
        
        # Sample other demographics
        race_ethnicity = self._weighted_sample(CensusData.race_distribution, constraints, "race_ethnicity")
        gender = self._weighted_sample(CensusData.gender_distribution, constraints, "gender")
        education = self._weighted_sample(CensusData.education_distribution, constraints, "education")
        location_type = self._weighted_sample(CensusData.location_distribution, constraints, "location_type")
        income = self._weighted_sample(CensusData.income_distribution, constraints, "income")
        marital_status = self._weighted_sample(CensusData.marital_distribution, constraints, "marital_status")
        
        # Generate name based on demographics
        name = self._generate_name(race_ethnicity, gender)
        
        # Generate occupation based on education and age
        occupation = self._generate_occupation(education, age)
        
        # Generate children based on age and marital status
        children = self._generate_children(age, marital_status)
        
        return PersonaConfig(
            name=name,
            age=age,
            race_ethnicity=race_ethnicity,
            gender=gender,
            education=education,
            location_type=location_type,
            income=income,
            marital_status=marital_status,
            children=children,
            occupation=occupation
        )
    
    def _sample_age(self, constraints: Optional[Dict[str, Any]] = None) -> int:
        """Sample age from census distribution with optional constraints"""
        
        # Apply age constraints if provided
        if constraints:
            age_min = constraints.get("age_min", 18)
            age_max = constraints.get("age_max", 85)
        else:
            age_min, age_max = 18, 85
        
        # Filter age ranges by constraints
        valid_ranges = []
        for (range_min, range_max), probability in CensusData.age_distribution.items():
            if range_max >= age_min and range_min <= age_max:
                # Adjust range to fit constraints
                adjusted_min = max(range_min, age_min)
                adjusted_max = min(range_max, age_max)
                valid_ranges.append(((adjusted_min, adjusted_max), probability))
        
        if not valid_ranges:
            return random.randint(age_min, age_max)
        
        # Select age range
        range_probs = {r: p for r, p in valid_ranges}
        selected_range = self._weighted_random_choice(range_probs)
        
        # Select specific age within range
        return random.randint(selected_range[0], selected_range[1])
    
    def _weighted_sample(
        self, 
        distribution: Dict[str, float], 
        constraints: Optional[Dict[str, Any]], 
        field_name: str
    ) -> str:
        """Sample from distribution with optional constraints"""
        
        if constraints and field_name in constraints:
            constraint_values = constraints[field_name]
            if isinstance(constraint_values, list):
                # Filter distribution to only allowed values
                filtered_dist = {k: v for k, v in distribution.items() if k in constraint_values}
                if filtered_dist:
                    # Normalize
                    total = sum(filtered_dist.values())
                    normalized_dist = {k: v/total for k, v in filtered_dist.items()}
                    return self._weighted_random_choice(normalized_dist)
                else:
                    return random.choice(constraint_values)
            else:
                return constraint_values  # Single value constraint
        
        return self._weighted_random_choice(distribution)
    
    def _weighted_random_choice(self, distribution: Dict[str, float]) -> str:
        """Make weighted random selection"""
        
        rand_val = random.random()
        cumulative = 0.0
        
        for option, probability in distribution.items():
            cumulative += probability
            if rand_val <= cumulative:
                return option
        
        # Fallback
        return list(distribution.keys())[0]
    
    def _generate_name(self, race_ethnicity: str, gender: str) -> str:
        """Generate culturally appropriate names"""
        
        # Simplified name generation - in production would use comprehensive name databases
        first_names = {
            ("hispanic", "female"): ["Maria", "Ana", "Sofia", "Carmen", "Elena", "Isabel"],
            ("hispanic", "male"): ["Carlos", "Miguel", "Jose", "Luis", "Diego", "Antonio"],
            ("black", "female"): ["Keisha", "Tanya", "Nicole", "Jasmine", "Alicia", "Denise"],
            ("black", "male"): ["Marcus", "Damon", "Jerome", "Kevin", "Tyrone", "Andre"],
            ("asian", "female"): ["Ashley", "Jennifer", "Michelle", "Lisa", "Amy", "Catherine"],
            ("asian", "male"): ["David", "Michael", "Kevin", "Daniel", "Steven", "Andrew"],
            ("white", "female"): ["Sarah", "Jennifer", "Emily", "Jessica", "Ashley", "Amanda"],
            ("white", "male"): ["Michael", "David", "James", "Robert", "John", "William"]
        }
        
        last_names = {
            "hispanic": ["Rodriguez", "Garcia", "Martinez", "Lopez", "Hernandez", "Perez"],
            "black": ["Johnson", "Williams", "Brown", "Jones", "Davis", "Miller"],
            "asian": ["Chen", "Wang", "Kim", "Lee", "Liu", "Park"],
            "white": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
        }
        
        first_name_key = (race_ethnicity, gender)
        if first_name_key in first_names:
            first_name = random.choice(first_names[first_name_key])
        else:
            first_name = random.choice(first_names[("white", gender)])
        
        last_name = random.choice(last_names.get(race_ethnicity, last_names["white"]))
        
        return f"{first_name} {last_name}"
    
    def _generate_occupation(self, education: str, age: int) -> str:
        """Generate occupation based on education and age"""
        
        occupations_by_education = {
            "no_hs": ["retail worker", "food service worker", "warehouse worker", "cleaner", "security guard"],
            "high_school": ["mechanic", "administrative assistant", "sales associate", "truck driver", "factory worker"],
            "some_college": ["technician", "customer service rep", "bank teller", "police officer", "paramedic"],
            "college": ["teacher", "accountant", "marketing coordinator", "nurse", "social worker"],
            "graduate": ["lawyer", "doctor", "professor", "engineer", "consultant"]
        }
        
        base_occupations = occupations_by_education.get(education, occupations_by_education["high_school"])
        
        # Add "retired" for older people
        if age >= 65:
            return "retired"
        elif age >= 60 and random.random() < 0.3:
            return "retired"
        
        return random.choice(base_occupations)
    
    def _generate_children(self, age: int, marital_status: str) -> int:
        """Generate number of children based on age and marital status"""
        
        if age < 25:
            return 0 if random.random() < 0.8 else random.randint(0, 1)
        elif age < 35:
            if marital_status == "married":
                return random.choices([0, 1, 2], weights=[0.3, 0.4, 0.3])[0]
            else:
                return random.choices([0, 1], weights=[0.7, 0.3])[0]
        elif age < 50:
            if marital_status == "married":
                return random.choices([0, 1, 2, 3], weights=[0.2, 0.3, 0.4, 0.1])[0]
            else:
                return random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
        else:
            # Older adults, children likely grown
            if marital_status == "married":
                return random.choices([0, 1, 2, 3], weights=[0.3, 0.2, 0.3, 0.2])[0]
            else:
                return random.choices([0, 1, 2], weights=[0.4, 0.3, 0.3])[0]
    
    def validate_population_accuracy(self, personas: List[PersonaConfig]) -> PopulationValidation:
        """Validate how well the generated population matches census targets"""
        
        print(f"📊 Validating population of {len(personas)} personas against census targets...")
        
        # Calculate actual distributions
        actual_distributions = self._calculate_actual_distributions(personas)
        
        # Compare to census targets
        accuracy_scores = {}
        
        for field, target_dist in [
            ("age_range", self._convert_age_to_ranges(personas)),
            ("race_ethnicity", self._count_field(personas, "race_ethnicity")),
            ("gender", self._count_field(personas, "gender")),
            ("education", self._count_field(personas, "education")),
            ("location_type", self._count_field(personas, "location_type")),
            ("income", self._count_field(personas, "income"))
        ]:
            
            if field == "age_range":
                census_target = CensusData.age_distribution
                actual_dist = target_dist
            else:
                census_target = getattr(CensusData, f"{field}_distribution", {})
                actual_dist = target_dist
            
            # Calculate accuracy for this field
            field_accuracy = self._calculate_field_accuracy(actual_dist, census_target)
            accuracy_scores[field] = field_accuracy
        
        # Overall accuracy
        overall_accuracy = statistics.mean(accuracy_scores.values())
        
        # Identify representation gaps
        gaps = []
        for field, accuracy in accuracy_scores.items():
            if accuracy < 0.8:  # Less than 80% accurate
                gaps.append(f"{field} representation: {accuracy:.1%} accuracy")
        
        # Generate recommendations
        recommendations = []
        if overall_accuracy < 0.9:
            recommendations.append("Consider increasing sample size for better representation")
        if gaps:
            recommendations.append("Review demographic sampling weights for underrepresented groups")
        
        return PopulationValidation(
            target_size=len(personas),
            actual_size=len(personas),
            demographic_accuracy=accuracy_scores,
            representation_gaps=gaps,
            validation_score=overall_accuracy,
            recommendations=recommendations
        )
    
    def _calculate_actual_distributions(self, personas: List[PersonaConfig]) -> Dict[str, Dict[str, float]]:
        """Calculate actual demographic distributions from generated personas"""
        
        distributions = {}
        total = len(personas)
        
        if total == 0:
            return distributions
        
        # Count each demographic field
        for field in ["race_ethnicity", "gender", "education", "location_type", "income"]:
            field_counts = defaultdict(int)
            for persona in personas:
                value = getattr(persona, field, "unknown")
                field_counts[value] += 1
            
            # Convert to percentages
            distributions[field] = {k: v/total for k, v in field_counts.items()}
        
        return distributions
    
    def _convert_age_to_ranges(self, personas: List[PersonaConfig]) -> Dict[Tuple[int, int], float]:
        """Convert ages to ranges for comparison with census data"""
        
        range_counts = defaultdict(int)
        total = len(personas)
        
        for persona in personas:
            age = persona.age
            for age_range in CensusData.age_distribution.keys():
                if age_range[0] <= age <= age_range[1]:
                    range_counts[age_range] += 1
                    break
        
        return {k: v/total for k, v in range_counts.items()}
    
    def _count_field(self, personas: List[PersonaConfig], field: str) -> Dict[str, float]:
        """Count field values and convert to percentages"""
        
        counts = defaultdict(int)
        total = len(personas)
        
        for persona in personas:
            value = getattr(persona, field, "unknown")
            counts[value] += 1
        
        return {k: v/total for k, v in counts.items()}
    
    def _calculate_field_accuracy(
        self, 
        actual_dist: Dict[Any, float], 
        target_dist: Dict[Any, float]
    ) -> float:
        """Calculate accuracy between actual and target distributions"""
        
        if not target_dist:
            return 1.0
        
        errors = []
        for key, target_pct in target_dist.items():
            actual_pct = actual_dist.get(key, 0.0)
            error = abs(actual_pct - target_pct)
            errors.append(error)
        
        # Accuracy is 1 minus average absolute error
        avg_error = statistics.mean(errors) if errors else 0.0
        return max(0.0, 1.0 - avg_error)


def print_population_summary(personas: List[PersonaConfig], validation: PopulationValidation):
    """Print summary of generated population"""
    
    print(f"\n👥 POPULATION SUMMARY")
    print("=" * 80)
    print(f"Generated: {len(personas)} personas")
    print(f"Validation Score: {validation.validation_score:.3f}")
    
    print(f"\n📊 DEMOGRAPHIC ACCURACY:")
    for field, accuracy in validation.demographic_accuracy.items():
        status = "✅" if accuracy > 0.9 else "⚠️" if accuracy > 0.8 else "❌"
        print(f"   {status} {field}: {accuracy:.1%}")
    
    if validation.representation_gaps:
        print(f"\n⚠️ REPRESENTATION GAPS:")
        for gap in validation.representation_gaps:
            print(f"   • {gap}")
    
    if validation.recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in validation.recommendations:
            print(f"   • {rec}")
    
    # Show sample personas
    print(f"\n🎭 SAMPLE PERSONAS:")
    for i, persona in enumerate(personas[:3]):
        print(f"   {i+1}. {persona.name} ({persona.age}yo {persona.race_ethnicity} {persona.gender})")
        print(f"      {persona.education}, {persona.location_type}, {persona.income}, {persona.occupation}")
        behavioral = persona.get_behavioral_characteristics()
        if behavioral:
            print(f"      Behavioral: {', '.join([f'{k}={v}' for k, v in list(behavioral.items())[:3]])}")
        print()


def test_census_persona_generator():
    """Test the census persona generator"""
    
    print("🧪 TESTING CENSUS PERSONA GENERATOR")
    print("=" * 80)
    
    # Test basic generation
    generator = CensusPersonaGenerator(seed=42)  # For reproducible results
    
    personas = generator.generate_representative_population(
        size=100,  # Small test size
        include_behavioral_characteristics=True
    )
    
    # Validate population
    validation = generator.validate_population_accuracy(personas)
    
    # Print results
    print_population_summary(personas, validation)
    
    # Test constrained generation
    print(f"\n🎯 TESTING CONSTRAINED GENERATION")
    print("-" * 50)
    
    constrained_personas = generator.generate_representative_population(
        size=50,
        demographic_constraints={
            "age_min": 25,
            "age_max": 45,
            "education": ["college", "graduate"],
            "income": ["75k_100k", "over_100k"]
        }
    )
    
    print(f"Generated {len(constrained_personas)} constrained personas")
    print("Sample constrained personas:")
    for persona in constrained_personas[:3]:
        print(f"   • {persona.name}: {persona.age}yo, {persona.education}, {persona.income}")
    
    return personas, validation


if __name__ == "__main__":
    test_census_persona_generator()