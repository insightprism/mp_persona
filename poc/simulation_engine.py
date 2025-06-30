"""
Simulation Engine: Statistical Analysis of Persona Responses

This module provides the core simulation and statistical analysis capabilities
for running scenarios across multiple personas and calculating behavioral probabilities.
"""

import asyncio
import statistics
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import Counter, defaultdict
import json
import re

from persona_config import PersonaConfig
from pm_persona_handler import pm_persona_transform_handler_async


@dataclass
class ScenarioConfig:
    """Configuration for a simulation scenario"""
    scenario_id: str
    scenario_type: str  # "policy", "product", "economic", "crisis"
    description: str
    question: str  # The actual question to ask personas
    context: Dict[str, Any]  # Additional context (timing, background, etc.)
    target_demographics: Optional[List[str]] = None
    expected_outcomes: Optional[List[str]] = None  # For validation


@dataclass
class PersonaResponse:
    """Individual persona response with metadata"""
    persona_id: str
    persona_name: str
    response_text: str
    demographics: Dict[str, Any]
    response_category: Optional[str] = None  # Classified response
    confidence_score: Optional[float] = None
    response_timestamp: Optional[str] = None


@dataclass
class SimulationResults:
    """Statistical results from persona simulation"""
    scenario_id: str
    total_personas: int
    response_distribution: Dict[str, float]  # {"support": 0.67, "oppose": 0.23}
    demographic_breakdowns: Dict[str, Dict[str, float]]  # Response by demo groups
    confidence_interval: Tuple[float, float]
    statistical_significance: float
    response_categories: List[str]
    raw_responses: List[PersonaResponse]
    simulation_metadata: Dict[str, Any]
    validation_accuracy: Optional[float] = None


class ResponseClassifier:
    """Classifies persona responses into standard categories"""
    
    def __init__(self):
        # Standard response categories for different scenario types
        self.category_keywords = {
            "support": ["support", "agree", "favor", "like", "positive", "yes", "approve"],
            "oppose": ["oppose", "disagree", "against", "dislike", "negative", "no", "disapprove"],
            "neutral": ["neutral", "unsure", "uncertain", "mixed", "depends", "maybe"],
            "strong_support": ["strongly support", "definitely", "absolutely", "enthusiastic"],
            "strong_oppose": ["strongly oppose", "absolutely not", "never", "terrible"],
            "purchase_intent": ["would buy", "interested", "purchase", "order"],
            "no_purchase": ["wouldn't buy", "not interested", "too expensive", "pass"],
            "concerned": ["worried", "concerned", "anxious", "scared", "nervous"],
            "confident": ["confident", "optimistic", "hopeful", "positive", "secure"]
        }
    
    def classify_response(self, response_text: str, scenario_type: str) -> str:
        """Classify a response into standard categories"""
        response_lower = response_text.lower()
        
        # Check for strong indicators first
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in response_lower:
                    return category
        
        # Default classification based on scenario type
        if scenario_type == "policy":
            return "neutral"
        elif scenario_type == "product":
            return "no_purchase"
        else:
            return "neutral"
    
    def calculate_sentiment_score(self, response_text: str) -> float:
        """Calculate sentiment score from -1.0 (negative) to 1.0 (positive)"""
        positive_words = ["good", "great", "excellent", "love", "like", "positive", "support"]
        negative_words = ["bad", "terrible", "hate", "dislike", "negative", "oppose", "worry"]
        
        words = response_text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_sentiment_words


class PersonaSimulation:
    """Core simulation engine for running scenarios across persona populations"""
    
    def __init__(self, llm_config):
        self.llm_config = llm_config
        self.classifier = ResponseClassifier()
        self.simulation_history = []
    
    async def run_scenario_simulation(
        self, 
        scenario: ScenarioConfig, 
        personas: List[PersonaConfig],
        poll_data: Dict[str, Any] = None,
        max_concurrent: int = 10
    ) -> SimulationResults:
        """
        Run a scenario across multiple personas and analyze results statistically
        
        Args:
            scenario: The scenario configuration
            personas: List of personas to simulate
            poll_data: Relevant polling data for behavioral context
            max_concurrent: Maximum concurrent persona requests
        
        Returns:
            Statistical analysis of all persona responses
        """
        print(f"🎯 Starting simulation: {scenario.scenario_id}")
        print(f"📊 Testing {len(personas)} personas with scenario: {scenario.description}")
        
        # Run personas in batches to avoid overwhelming the system
        all_responses = []
        
        for i in range(0, len(personas), max_concurrent):
            batch = personas[i:i + max_concurrent]
            print(f"🔄 Processing batch {i//max_concurrent + 1}/{(len(personas)-1)//max_concurrent + 1} ({len(batch)} personas)")
            
            # Create async tasks for this batch
            tasks = []
            for persona in batch:
                task = self._simulate_single_persona(scenario, persona, poll_data)
                tasks.append(task)
            
            # Execute batch concurrently
            batch_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and collect valid responses
            for response in batch_responses:
                if isinstance(response, PersonaResponse):
                    all_responses.append(response)
                else:
                    print(f"⚠️ Persona simulation failed: {response}")
        
        print(f"✅ Completed simulation with {len(all_responses)} valid responses")
        
        # Analyze results statistically
        return self._analyze_simulation_results(scenario, all_responses)
    
    async def _simulate_single_persona(
        self, 
        scenario: ScenarioConfig, 
        persona: PersonaConfig,
        poll_data: Dict[str, Any]
    ) -> PersonaResponse:
        """Simulate a single persona's response to the scenario"""
        
        try:
            # Prepare rag_data for the persona handler
            rag_data = {
                'persona': persona,
                'poll_data': poll_data or {}
            }
            
            # Call the persona handler
            result = await pm_persona_transform_handler_async(
                input_content=scenario.question,
                llm_config=self.llm_config,
                rag_data=rag_data
            )
            
            if result['success']:
                response_text = result['output_content']
                
                # Classify the response
                category = self.classifier.classify_response(response_text, scenario.scenario_type)
                confidence = self.classifier.calculate_sentiment_score(response_text)
                
                return PersonaResponse(
                    persona_id=f"{persona.name}_{persona.age}_{persona.race_ethnicity}",
                    persona_name=persona.name,
                    response_text=response_text,
                    demographics={
                        "age": persona.age,
                        "race_ethnicity": persona.race_ethnicity,
                        "gender": persona.gender,
                        "education": persona.education,
                        "location_type": persona.location_type,
                        "income": persona.income,
                        "occupation": persona.occupation
                    },
                    response_category=category,
                    confidence_score=confidence,
                    response_timestamp=datetime.utcnow().isoformat()
                )
            else:
                raise Exception(f"Persona handler failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error simulating {persona.name}: {e}")
            raise e
    
    def _analyze_simulation_results(self, scenario: ScenarioConfig, responses: List[PersonaResponse]) -> SimulationResults:
        """Analyze all persona responses and calculate statistical metrics"""
        
        if not responses:
            raise ValueError("No valid responses to analyze")
        
        print(f"📈 Analyzing {len(responses)} responses...")
        
        # Calculate response distribution
        categories = [r.response_category for r in responses if r.response_category]
        category_counts = Counter(categories)
        total_responses = len(responses)
        
        response_distribution = {
            category: count / total_responses 
            for category, count in category_counts.items()
        }
        
        # Calculate demographic breakdowns
        demographic_breakdowns = self._calculate_demographic_breakdowns(responses)
        
        # Calculate confidence interval for main result
        if response_distribution:
            main_category = max(response_distribution.keys(), key=lambda k: response_distribution[k])
            main_percentage = response_distribution[main_category]
            confidence_interval = self._calculate_confidence_interval(main_percentage, total_responses)
        else:
            confidence_interval = (0.0, 0.0)
        
        # Calculate statistical significance
        significance = self._calculate_statistical_significance(response_distribution, total_responses)
        
        return SimulationResults(
            scenario_id=scenario.scenario_id,
            total_personas=total_responses,
            response_distribution=response_distribution,
            demographic_breakdowns=demographic_breakdowns,
            confidence_interval=confidence_interval,
            statistical_significance=significance,
            response_categories=list(category_counts.keys()),
            raw_responses=responses,
            simulation_metadata={
                "scenario_type": scenario.scenario_type,
                "scenario_description": scenario.description,
                "simulation_timestamp": datetime.utcnow().isoformat(),
                "total_attempted": total_responses,
                "success_rate": 1.0  # All responses in this list are successful
            }
        )
    
    def _calculate_demographic_breakdowns(self, responses: List[PersonaResponse]) -> Dict[str, Dict[str, float]]:
        """Calculate response distributions by demographic groups"""
        
        breakdowns = {}
        
        # Group by different demographic dimensions
        demographic_fields = ["age", "race_ethnicity", "gender", "education", "location_type", "income"]
        
        for field in demographic_fields:
            field_breakdown = defaultdict(lambda: defaultdict(int))
            field_totals = defaultdict(int)
            
            for response in responses:
                demo_value = response.demographics.get(field, "unknown")
                category = response.response_category
                
                field_breakdown[demo_value][category] += 1
                field_totals[demo_value] += 1
            
            # Convert to percentages
            field_percentages = {}
            for demo_value, categories in field_breakdown.items():
                total = field_totals[demo_value]
                field_percentages[demo_value] = {
                    category: count / total 
                    for category, count in categories.items()
                }
            
            breakdowns[field] = field_percentages
        
        return breakdowns
    
    def _calculate_confidence_interval(self, percentage: float, sample_size: int, confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for a percentage"""
        
        if sample_size == 0:
            return (0.0, 0.0)
        
        # Using normal approximation for large samples
        z_score = 1.96 if confidence_level == 0.95 else 1.645  # 95% vs 90%
        
        margin_of_error = z_score * (percentage * (1 - percentage) / sample_size) ** 0.5
        
        lower_bound = max(0.0, percentage - margin_of_error)
        upper_bound = min(1.0, percentage + margin_of_error)
        
        return (round(lower_bound, 3), round(upper_bound, 3))
    
    def _calculate_statistical_significance(self, distribution: Dict[str, float], sample_size: int) -> float:
        """Calculate statistical significance of results"""
        
        if not distribution or sample_size < 30:
            return 0.0
        
        # Simple significance based on sample size and distribution spread
        max_percentage = max(distribution.values()) if distribution else 0
        min_percentage = min(distribution.values()) if distribution else 0
        spread = max_percentage - min_percentage
        
        # Higher significance for larger samples and clearer results
        size_factor = min(1.0, sample_size / 1000)  # Max factor of 1.0 at 1000+ samples
        spread_factor = spread  # 0-1 based on how clear the results are
        
        return round(size_factor * spread_factor, 3)
    
    def print_results_summary(self, results: SimulationResults):
        """Print a formatted summary of simulation results"""
        
        print(f"\n📊 SIMULATION RESULTS: {results.scenario_id}")
        print("=" * 80)
        
        print(f"Total Personas: {results.total_personas}")
        print(f"Statistical Significance: {results.statistical_significance:.3f}")
        print()
        
        print("📈 RESPONSE DISTRIBUTION:")
        for category, percentage in sorted(results.response_distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category.upper()}: {percentage:.1%}")
        
        print(f"\n🎯 CONFIDENCE INTERVAL (Main Result): {results.confidence_interval[0]:.1%} - {results.confidence_interval[1]:.1%}")
        
        print("\n👥 TOP DEMOGRAPHIC PATTERNS:")
        # Show most interesting demographic breakdowns
        for demo_field, breakdowns in list(results.demographic_breakdowns.items())[:3]:
            print(f"\n   {demo_field.upper()}:")
            for demo_value, categories in list(breakdowns.items())[:3]:
                main_response = max(categories.items(), key=lambda x: x[1]) if categories else ("none", 0)
                print(f"      {demo_value}: {main_response[1]:.1%} {main_response[0]}")


class MockLLMConfig:
    """Mock LLM configuration for testing"""
    def __init__(self):
        self.llm_provider = "openai"
        self.llm_name = "gpt-4"
        self.temperature = 0.8


async def test_simulation_engine():
    """Test the simulation engine with sample data"""
    
    print("🧪 TESTING SIMULATION ENGINE")
    print("=" * 80)
    
    # Create test scenario
    scenario = ScenarioConfig(
        scenario_id="healthcare_policy_test",
        scenario_type="policy",
        description="Testing support for universal healthcare policy",
        question="Do you support or oppose a universal healthcare system where the government provides healthcare coverage for all citizens?",
        context={"policy_type": "healthcare", "scope": "universal"},
        expected_outcomes=["support", "oppose", "neutral"]
    )
    
    # Create diverse test personas
    test_personas = [
        PersonaConfig(
            name="Maria Rodriguez", age=34, race_ethnicity="hispanic", gender="female",
            education="college", location_type="suburban", income="50k_75k",
            occupation="teacher"
        ),
        PersonaConfig(
            name="Bob Johnson", age=52, race_ethnicity="white", gender="male",
            education="high_school", location_type="rural", income="30k_50k",
            occupation="mechanic"
        ),
        PersonaConfig(
            name="Ashley Chen", age=28, race_ethnicity="asian", gender="female",
            education="graduate", location_type="urban", income="over_100k",
            occupation="software engineer"
        ),
        PersonaConfig(
            name="James Wilson", age=65, race_ethnicity="black", gender="male",
            education="some_college", location_type="urban", income="75k_100k",
            occupation="retired"
        ),
        PersonaConfig(
            name="Sarah Smith", age=42, race_ethnicity="white", gender="female",
            education="college", location_type="suburban", income="75k_100k",
            occupation="nurse"
        )
    ]
    
    # Sample poll data
    poll_data = {
        "healthcare": {
            "position": "mixed support based on implementation details",
            "confidence": 0.6,
            "source": "Kaiser Family Foundation 2024"
        }
    }
    
    # Run simulation
    llm_config = MockLLMConfig()
    simulator = PersonaSimulation(llm_config)
    
    try:
        results = await simulator.run_scenario_simulation(
            scenario=scenario,
            personas=test_personas,
            poll_data=poll_data,
            max_concurrent=3
        )
        
        # Print results
        simulator.print_results_summary(results)
        
        return results
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(test_simulation_engine())