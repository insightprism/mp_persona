"""
Environmental Integration Demonstration

This demonstrates the complete environmentally-aware persona system showing how
people with identical demographics behave differently based on their social environment.

Key Demonstrations:
1. Same persona in different cities shows different behavioral patterns
2. Social pressure calculations affect responses
3. Reference group influence varies by environment
4. Multi-agent awareness creates realistic social dynamics
"""

import asyncio
from typing import Dict, List, Any
from persona_config import PersonaConfig
from environmentally_aware_persona import EnvironmentallyAwarePersona, demonstrate_environmental_awareness
from environmental_data_manager import EnvironmentalDataManager, demonstrate_environmental_data_integration
from simulation_engine import PersonaSimulation, ScenarioConfig, MockLLMConfig


class EnvironmentalPersonaSimulation:
    """Enhanced simulation engine that considers environmental context"""
    
    def __init__(self, data_manager: EnvironmentalDataManager, llm_config=None):
        self.data_manager = data_manager
        self.llm_config = llm_config or MockLLMConfig()
        self.base_simulation = PersonaSimulation(self.llm_config)
    
    async def simulate_environmental_scenario(
        self,
        base_persona: PersonaConfig,
        area_ids: List[str],
        scenario_description: str,
        scenario_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Simulate same persona in different environments to show behavioral differences
        """
        
        results = {}
        
        for area_id in area_ids:
            # Get environmental context
            env_context = self.data_manager.get_environmental_context(area_id)
            if not env_context:
                continue
            
            # Create environmentally aware persona
            env_persona = EnvironmentallyAwarePersona(base_persona, env_context)
            
            # Generate LLM prompt with environmental context
            enhanced_prompt = env_persona.generate_llm_prompt_context(scenario_description, scenario_type)
            
            # Simulate response (using mock for demo)
            response = await self._simulate_environmental_response(
                env_persona, 
                enhanced_prompt, 
                scenario_type
            )
            
            results[area_id] = {
                "location": f"{env_context.location_name}, {env_context.state}",
                "environmental_context": env_persona.get_behavioral_adjustment_context(scenario_type),
                "response": response,
                "social_pressures": len(env_persona.social_pressures),
                "conformity_tendency": env_persona.conformity_tendency,
                "demographic_fit": env_persona._calculate_similar_demographic_percentage()
            }
        
        return results
    
    async def _simulate_environmental_response(
        self, 
        env_persona: EnvironmentallyAwarePersona, 
        prompt: str, 
        scenario_type: str
    ) -> str:
        """
        Simulate how environmental context affects persona response
        (In production, this would call actual LLM)
        """
        
        context = env_persona.get_behavioral_adjustment_context(scenario_type)
        env_summary = context["environmental_summary"]
        pressures = context["social_pressures"]
        
        # Mock different responses based on environmental factors
        base_response = f"As {env_persona.base_persona.name}, I think..."
        
        # Adjust response based on minority status
        if env_summary["minority_status"] > 0.7:  # Strong minority
            if env_persona.conformity_tendency > 0.6:
                response_modifier = " I try to be cautious about this topic since I want to fit in with my community."
            else:
                response_modifier = " As someone from a minority background, I have a unique perspective on this."
        elif env_summary["minority_status"] < 0.3:  # Majority
            response_modifier = " I feel comfortable expressing my views since most people here share similar backgrounds."
        else:
            response_modifier = " I think this is something that affects different people in different ways."
        
        # Adjust based on dominant social pressure
        if pressures["dominant_pressure"]:
            pressure_type = pressures["dominant_pressure"]["type"]
            if pressure_type == "conformity":
                response_modifier += " I generally try to go along with what most people think is best."
            elif pressure_type == "minority_solidarity":
                response_modifier += " I think it's important to stand up for what people like me believe in."
            elif pressure_type == "political_climate":
                if not env_summary["political_alignment"]:
                    response_modifier += " I'm careful about how I express political opinions around here."
        
        # Add location-specific context
        location_modifier = f" Living in {env_persona.environment.location_name}, I see how this affects our community."
        
        return base_response + response_modifier + location_modifier
    
    async def demonstrate_multi_agent_awareness(
        self, 
        personas: List[PersonaConfig], 
        environment_area_id: str,
        scenario: str
    ) -> Dict[str, Any]:
        """Demonstrate how personas affect each other in shared environment"""
        
        env_context = self.data_manager.get_environmental_context(environment_area_id)
        if not env_context:
            return {"error": "Environment not found"}
        
        # Create environmentally aware personas
        env_personas = []
        for persona in personas:
            env_persona = EnvironmentallyAwarePersona(persona, env_context)
            env_personas.append(env_persona)
        
        # Add multi-agent awareness (each persona knows about others)
        for i, persona_a in enumerate(env_personas):
            for j, persona_b in enumerate(env_personas):
                if i != j:
                    persona_a.add_nearby_persona(persona_b)
        
        # Simulate group dynamics
        results = {}
        for i, env_persona in enumerate(env_personas):
            # Calculate social network influence
            network_influence = env_persona.social_network_influence
            similarity_scores = [
                env_persona._calculate_persona_similarity(other) 
                for other in env_persona.nearby_personas
            ]
            
            # Generate response considering group dynamics
            prompt = env_persona.generate_llm_prompt_context(scenario, "social")
            response = await self._simulate_group_influenced_response(
                env_persona, prompt, network_influence, similarity_scores
            )
            
            results[f"persona_{i+1}"] = {
                "name": env_persona.base_persona.name,
                "demographics": f"{env_persona.base_persona.age}yo {env_persona.base_persona.race_ethnicity} {env_persona.base_persona.gender}",
                "social_network_influence": network_influence,
                "similar_personas_nearby": sum(1 for s in similarity_scores if s > 0.5),
                "response": response,
                "conformity_tendency": env_persona.conformity_tendency
            }
        
        return {
            "environment": f"{env_context.location_name}, {env_context.state}",
            "group_size": len(env_personas),
            "group_diversity": self._calculate_group_diversity(env_personas),
            "individual_responses": results
        }
    
    async def _simulate_group_influenced_response(
        self, 
        env_persona: EnvironmentallyAwarePersona, 
        prompt: str, 
        network_influence: float,
        similarity_scores: List[float]
    ) -> str:
        """Simulate how group presence affects individual response"""
        
        base_response = f"I think this is an important issue to consider."
        
        # Higher network influence = more conformist response
        if network_influence > 0.6:
            modifier = " I agree with what others here are saying about this."
        elif network_influence > 0.3:
            modifier = " I think most of us would agree on this topic."
        else:
            modifier = " I have my own perspective on this."
        
        # If surrounded by similar people, more confident
        similar_count = sum(1 for s in similarity_scores if s > 0.5)
        if similar_count > len(similarity_scores) * 0.7:
            confidence = " I'm confident this is the right approach."
        elif similar_count < len(similarity_scores) * 0.3:
            confidence = " I want to be respectful of different viewpoints here."
        else:
            confidence = " I think there are valid points on different sides."
        
        return base_response + modifier + confidence
    
    def _calculate_group_diversity(self, env_personas: List[EnvironmentallyAwarePersona]) -> float:
        """Calculate diversity score for group of personas"""
        if len(env_personas) < 2:
            return 0.0
        
        # Calculate average similarity between all pairs
        total_similarity = 0
        pair_count = 0
        
        for i in range(len(env_personas)):
            for j in range(i+1, len(env_personas)):
                similarity = env_personas[i]._calculate_persona_similarity(env_personas[j])
                total_similarity += similarity
                pair_count += 1
        
        avg_similarity = total_similarity / pair_count if pair_count > 0 else 0
        diversity = 1.0 - avg_similarity  # Higher diversity = lower average similarity
        
        return diversity


async def run_environmental_integration_demo():
    """Run comprehensive environmental integration demonstration"""
    
    print("🌍 ENVIRONMENTAL INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print("Showing how identical personas behave differently in different environments")
    print()
    
    # Initialize data manager with realistic data
    print("1️⃣ Loading environmental data...")
    data_manager = EnvironmentalDataManager("integration_demo.db")
    data_manager.load_sample_environmental_data()
    
    # Initialize environmental simulation
    env_simulation = EnvironmentalPersonaSimulation(data_manager)
    
    # Create base persona - Hispanic teacher (same as user's example)
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
    
    print(f"📍 Base Persona: {base_persona.name} - {base_persona.age}yo {base_persona.race_ethnicity} {base_persona.gender} Teacher")
    print()
    
    # Demo 1: Same persona in different cities
    print("DEMO 1: Same Persona, Different Cities")
    print("-" * 60)
    
    cities = ["dallas_tx_city", "detroit_mi_city", "minneapolis_mn_city"]
    scenario = "A new school policy proposes requiring all students to take a standardized cultural competency test. What is your opinion on this policy?"
    
    city_results = await env_simulation.simulate_environmental_scenario(
        base_persona, cities, scenario, "political"
    )
    
    for area_id, result in city_results.items():
        print(f"\n📍 {result['location']}")
        print(f"   Demographic Fit: {result['demographic_fit']:.1%}")
        print(f"   Social Pressures: {result['social_pressures']} active")
        print(f"   Conformity Tendency: {result['conformity_tendency']:.1f}")
        print(f"   Response: {result['response']}")
    
    # Demo 2: Multi-agent awareness
    print("\n\nDEMO 2: Multi-Agent Social Dynamics")
    print("-" * 60)
    
    # Create diverse group of personas
    group_personas = [
        PersonaConfig(
            name="Maria Rodriguez", age=35, race_ethnicity="Hispanic", gender="Female",
            education="Bachelor's degree", location_type="urban", income="50k_75k"
        ),
        PersonaConfig(
            name="James Washington", age=42, race_ethnicity="Black", gender="Male",
            education="Graduate degree", location_type="urban", income="75k_100k"
        ),
        PersonaConfig(
            name="Sarah Miller", age=29, race_ethnicity="White", gender="Female",
            education="Bachelor's degree", location_type="urban", income="50k_75k"
        ),
        PersonaConfig(
            name="David Chen", age=38, race_ethnicity="Asian", gender="Male",
            education="Graduate degree", location_type="urban", income="over_100k"
        )
    ]
    
    group_scenario = "Should the city increase property taxes to fund better public schools?"
    
    # Test in Dallas (diverse) vs Detroit (majority Black)
    for test_city in ["dallas_tx_city", "detroit_mi_city"]:
        print(f"\n🏙️ Group Dynamics in {test_city.replace('_', ' ').title()}")
        
        group_results = await env_simulation.demonstrate_multi_agent_awareness(
            group_personas, test_city, group_scenario
        )
        
        print(f"   Environment: {group_results['environment']}")
        print(f"   Group Diversity: {group_results['group_diversity']:.1f}")
        print("   Individual Responses:")
        
        for persona_id, response_data in group_results["individual_responses"].items():
            print(f"     • {response_data['name']} ({response_data['demographics']})")
            print(f"       Network Influence: {response_data['social_network_influence']:.1f}")
            print(f"       Response: {response_data['response']}")
    
    # Demo 3: Environmental pressure analysis
    print("\n\nDEMO 3: Environmental Pressure Analysis")
    print("-" * 60)
    
    # Show detailed pressure analysis for different environments
    for area_id in cities:
        env_context = data_manager.get_environmental_context(area_id)
        if env_context:
            env_persona = EnvironmentallyAwarePersona(base_persona, env_context)
            context = env_persona.get_behavioral_adjustment_context("political")
            
            print(f"\n📊 {env_context.location_name}, {env_context.state}")
            print(f"   Political Climate: {env_context.political_lean} (strength: {env_context.political_strength:.1f})")
            print(f"   Cultural Diversity: {env_context.cultural_diversity:.1f}")
            print(f"   Minority Status: {context['environmental_summary']['minority_status']:.1%}")
            
            print("   Active Social Pressures:")
            for pressure in context['social_pressures']['all_pressures'][:2]:  # Top 2
                print(f"     • {pressure['type']}: {pressure['description']} (strength: {pressure['strength']:.1f})")
    
    print("\n\n🎯 KEY INSIGHTS:")
    print("=" * 80)
    print("✅ Same demographic profile produces different behaviors in different environments")
    print("✅ Social pressure calculations capture minority/majority dynamics")
    print("✅ Multi-agent awareness creates realistic group conformity effects")
    print("✅ Environmental context provides rich behavioral adjustment factors")
    print("✅ System uses realistic demographic data from US Census and elections")
    
    print("\n💡 BUSINESS IMPLICATIONS:")
    print("• Political polling must account for local social pressures")
    print("• Product marketing needs environment-specific messaging")
    print("• Policy analysis requires understanding of social conformity dynamics")
    print("• Traditional demographic targeting misses environmental effects")
    
    return env_simulation, data_manager


async def run_business_scenario_with_environment():
    """Run business scenarios showing environmental impact"""
    
    print("\n💼 BUSINESS SCENARIO: Environmental Marketing Impact")
    print("=" * 80)
    
    # Initialize system
    data_manager = EnvironmentalDataManager("business_scenario.db")
    data_manager.load_sample_environmental_data()
    env_simulation = EnvironmentalPersonaSimulation(data_manager)
    
    # Business scenario: Electric vehicle marketing
    base_consumer = PersonaConfig(
        name="Jennifer Kim",
        age=34,
        race_ethnicity="Asian",
        gender="Female",
        education="Bachelor's degree",
        location_type="suburban",
        income="75k_100k",
        media_consumption="high",
        risk_tolerance="moderate",
        spending_style="research_driven",
        civic_engagement="moderate",
        trust_in_institutions="high"
    )
    
    scenario = "A new electric vehicle costs $45,000 and promises 300-mile range with fast charging. Would you consider purchasing this vehicle?"
    
    # Test in different markets
    markets = ["dallas_tx_city", "detroit_mi_city", "phoenix_az_city"]
    
    print(f"Consumer Profile: {base_consumer.name} - {base_consumer.age}yo {base_consumer.race_ethnicity} Professional")
    print(f"Product: Electric Vehicle ($45,000, 300-mile range)")
    print()
    
    market_responses = await env_simulation.simulate_environmental_scenario(
        base_consumer, markets, scenario, "consumer"
    )
    
    for area_id, result in market_responses.items():
        print(f"📍 {result['location']}")
        print(f"   Environmental Fit: {result['demographic_fit']:.1%}")
        print(f"   Consumer Response: {result['response']}")
        
        # Extract purchase intent (mock analysis)
        if "interested" in result['response'].lower() or "consider" in result['response'].lower():
            purchase_intent = "High"
        elif "maybe" in result['response'].lower() or "depends" in result['response'].lower():
            purchase_intent = "Medium"
        else:
            purchase_intent = "Low"
        
        print(f"   Purchase Intent: {purchase_intent}")
        print()
    
    print("🎯 Marketing Insights:")
    print("• Environmental context significantly affects product receptivity")
    print("• Social conformity pressures influence purchase decisions")
    print("• Local economic conditions shape value perceptions")
    print("• Reference group influence varies by community composition")


if __name__ == "__main__":
    # Run main demonstration
    asyncio.run(run_environmental_integration_demo())
    
    # Run business scenario
    asyncio.run(run_business_scenario_with_environment())