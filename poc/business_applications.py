"""
Business Applications Layer

This module provides high-level business analysis tools built on top of the
persona simulation engine for political analysis and market research applications.
"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import statistics

from persona_config import PersonaConfig
from simulation_engine import PersonaSimulation, ScenarioConfig, SimulationResults
from poll_data_manager import PollDatabase, PollDataSelector


@dataclass
class PoliticalPrediction:
    """Results from political analysis"""
    scenario_id: str
    policy_topic: str
    overall_support: float
    overall_opposition: float
    demographic_support: Dict[str, float]  # support by demographic group
    key_insights: List[str]
    swing_demographics: List[str]  # demographics that could be persuaded
    confidence_level: float
    sample_size: int
    prediction_timestamp: str


@dataclass
class MessageOptimization:
    """Results from message testing analysis"""
    scenario_id: str
    messages_tested: List[str]
    best_message: str
    message_performance: Dict[str, float]  # message -> effectiveness score
    demographic_preferences: Dict[str, str]  # demographic -> preferred message
    optimization_insights: List[str]
    confidence_level: float


@dataclass
class MarketPrediction:
    """Results from market research analysis"""
    scenario_id: str
    product_name: str
    price_points_tested: List[float]
    optimal_price: float
    purchase_intent_by_price: Dict[float, float]
    target_market_size: float
    demographic_segments: Dict[str, float]  # segment -> purchase intent
    market_insights: List[str]
    revenue_projections: Dict[float, float]  # price -> projected revenue
    confidence_level: float


@dataclass
class FeatureAnalysis:
    """Results from product feature analysis"""
    scenario_id: str
    features_tested: List[str]
    feature_rankings: Dict[str, float]  # feature -> importance score
    demographic_preferences: Dict[str, List[str]]  # demographic -> ranked features
    must_have_features: List[str]
    nice_to_have_features: List[str]
    deal_breaker_features: List[str]
    insights: List[str]


class PoliticalAnalyzer:
    """High-level political analysis using persona simulations"""
    
    def __init__(self, simulation_engine: PersonaSimulation, poll_selector: PollDataSelector):
        self.simulation_engine = simulation_engine
        self.poll_selector = poll_selector
        self.analysis_history = []
    
    async def test_policy_support(
        self, 
        policy_description: str,
        policy_topic: str,
        personas: List[PersonaConfig],
        include_historical_context: bool = True
    ) -> PoliticalPrediction:
        """
        Test public support for a policy proposal
        
        Args:
            policy_description: Detailed description of the policy
            policy_topic: Category (healthcare, economy, education, etc.)
            personas: List of personas to survey
            include_historical_context: Whether to include relevant historical polling
        
        Returns:
            Political prediction with support levels and insights
        """
        
        print(f"🗳️ Analyzing policy support: {policy_topic}")
        
        # Create scenario
        scenario = ScenarioConfig(
            scenario_id=f"policy_{policy_topic}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            scenario_type="policy",
            description=policy_description,
            question=f"Do you support or oppose this policy proposal: {policy_description}",
            context={"policy_topic": policy_topic}
        )
        
        # Get relevant historical polling data
        poll_data = {}
        if include_historical_context and personas:
            # Use first persona as representative for poll selection
            representative_persona = personas[0]
            poll_data = self.poll_selector.select_relevant_polls(
                policy_description, representative_persona, max_polls=3
            )
        
        # Run simulation
        results = await self.simulation_engine.run_scenario_simulation(
            scenario=scenario,
            personas=personas,
            poll_data=poll_data
        )
        
        # Analyze political implications
        return self._analyze_political_results(results, policy_topic)
    
    def _analyze_political_results(self, results: SimulationResults, policy_topic: str) -> PoliticalPrediction:
        """Analyze simulation results for political insights"""
        
        # Calculate overall support/opposition
        support_categories = ["support", "strong_support", "approve"]
        opposition_categories = ["oppose", "strong_oppose", "disapprove"]
        
        overall_support = sum(results.response_distribution.get(cat, 0) for cat in support_categories)
        overall_opposition = sum(results.response_distribution.get(cat, 0) for cat in opposition_categories)
        
        # Analyze demographic breakdowns for support
        demographic_support = {}
        for demo_field, breakdowns in results.demographic_breakdowns.items():
            for demo_value, responses in breakdowns.items():
                demo_support = sum(responses.get(cat, 0) for cat in support_categories)
                demographic_support[f"{demo_field}_{demo_value}"] = demo_support
        
        # Identify swing demographics (moderate support levels)
        swing_demographics = [
            demo for demo, support in demographic_support.items()
            if 0.4 <= support <= 0.6
        ]
        
        # Generate insights
        insights = self._generate_political_insights(results, overall_support, demographic_support)
        
        return PoliticalPrediction(
            scenario_id=results.scenario_id,
            policy_topic=policy_topic,
            overall_support=overall_support,
            overall_opposition=overall_opposition,
            demographic_support=demographic_support,
            key_insights=insights,
            swing_demographics=swing_demographics,
            confidence_level=results.statistical_significance,
            sample_size=results.total_personas,
            prediction_timestamp=datetime.utcnow().isoformat()
        )
    
    def _generate_political_insights(
        self, 
        results: SimulationResults, 
        overall_support: float,
        demographic_support: Dict[str, float]
    ) -> List[str]:
        """Generate actionable political insights"""
        
        insights = []
        
        # Overall support insight
        if overall_support > 0.6:
            insights.append(f"Strong public support ({overall_support:.1%}) - likely to succeed if brought to vote")
        elif overall_support < 0.4:
            insights.append(f"Weak public support ({overall_support:.1%}) - significant opposition expected")
        else:
            insights.append(f"Moderate support ({overall_support:.1%}) - outcome uncertain, messaging crucial")
        
        # Demographic insights
        highest_support = max(demographic_support.items(), key=lambda x: x[1])
        lowest_support = min(demographic_support.items(), key=lambda x: x[1])
        
        insights.append(f"Strongest support from {highest_support[0]} ({highest_support[1]:.1%})")
        insights.append(f"Weakest support from {lowest_support[0]} ({lowest_support[1]:.1%})")
        
        # Sample size validation
        if results.total_personas < 100:
            insights.append("⚠️ Small sample size - results should be validated with larger population")
        
        return insights
    
    async def optimize_messaging(
        self, 
        messages: List[str],
        target_demographics: List[str],
        personas: List[PersonaConfig],
        policy_context: str
    ) -> MessageOptimization:
        """
        Test different messages to find most effective framing
        
        Args:
            messages: List of message variations to test
            target_demographics: Demographics to focus analysis on
            personas: Personas to test with
            policy_context: Background context for the messages
        
        Returns:
            Message optimization results with best performing message
        """
        
        print(f"📢 Testing {len(messages)} message variations")
        
        message_results = {}
        
        for i, message in enumerate(messages):
            print(f"   Testing message {i+1}/{len(messages)}")
            
            scenario = ScenarioConfig(
                scenario_id=f"message_test_{i}_{datetime.now().strftime('%H%M%S')}",
                scenario_type="policy",
                description=policy_context,
                question=f"How do you respond to this message: '{message}'",
                context={"message_testing": True}
            )
            
            results = await self.simulation_engine.run_scenario_simulation(
                scenario=scenario,
                personas=personas,
                max_concurrent=5  # Faster for message testing
            )
            
            # Calculate message effectiveness
            positive_responses = sum(
                results.response_distribution.get(cat, 0) 
                for cat in ["support", "strong_support", "positive", "agree"]
            )
            
            message_results[message] = positive_responses
        
        # Find best message
        best_message = max(message_results.items(), key=lambda x: x[1])[0]
        
        return MessageOptimization(
            scenario_id=f"message_optimization_{datetime.now().strftime('%Y%m%d_%H%M')}",
            messages_tested=messages,
            best_message=best_message,
            message_performance=message_results,
            demographic_preferences={},  # Would require more detailed analysis
            optimization_insights=[
                f"Best performing message: '{best_message}' ({message_results[best_message]:.1%} positive response)",
                f"Message effectiveness range: {min(message_results.values()):.1%} - {max(message_results.values()):.1%}"
            ],
            confidence_level=0.8  # Simplified
        )


class MarketResearcher:
    """High-level market research using persona simulations"""
    
    def __init__(self, simulation_engine: PersonaSimulation, poll_selector: PollDataSelector):
        self.simulation_engine = simulation_engine
        self.poll_selector = poll_selector
        self.research_history = []
    
    async def test_product_reception(
        self, 
        product_name: str,
        product_description: str,
        price_points: List[float],
        personas: List[PersonaConfig],
        target_market: Optional[str] = None
    ) -> MarketPrediction:
        """
        Test market reception for a product at different price points
        
        Args:
            product_name: Name of the product
            product_description: Detailed product description
            price_points: List of prices to test
            personas: Market personas to survey
            target_market: Optional target market specification
        
        Returns:
            Market prediction with optimal pricing and purchase intent
        """
        
        print(f"🛍️ Testing market reception for {product_name}")
        
        price_results = {}
        
        for price in price_points:
            print(f"   Testing price point: ${price}")
            
            scenario = ScenarioConfig(
                scenario_id=f"product_test_{product_name}_{price}",
                scenario_type="product",
                description=f"Product: {product_name} - {product_description}",
                question=f"Would you purchase {product_name} for ${price}? {product_description}",
                context={"product_name": product_name, "price": price}
            )
            
            # Get relevant consumer behavior polling data
            poll_data = self.poll_selector.select_relevant_polls(
                f"consumer spending technology product purchase", 
                personas[0] if personas else None,
                max_polls=2
            )
            
            results = await self.simulation_engine.run_scenario_simulation(
                scenario=scenario,
                personas=personas,
                poll_data=poll_data,
                max_concurrent=8
            )
            
            # Calculate purchase intent
            purchase_intent = sum(
                results.response_distribution.get(cat, 0)
                for cat in ["purchase_intent", "would_buy", "interested", "support"]
            )
            
            price_results[price] = purchase_intent
        
        # Analyze results
        return self._analyze_market_results(
            product_name, price_points, price_results, personas
        )
    
    def _analyze_market_results(
        self,
        product_name: str,
        price_points: List[float],
        price_results: Dict[float, float],
        personas: List[PersonaConfig]
    ) -> MarketPrediction:
        """Analyze market research results"""
        
        # Find optimal price (balance of price and demand)
        revenue_projections = {}
        for price, intent in price_results.items():
            # Simplified revenue calculation
            estimated_sales = intent * len(personas) * 100  # Scale factor
            revenue_projections[price] = price * estimated_sales
        
        optimal_price = max(revenue_projections.items(), key=lambda x: x[1])[0]
        
        # Calculate target market size
        target_market_size = price_results[optimal_price]
        
        # Generate insights
        insights = [
            f"Optimal price point: ${optimal_price} (maximizes revenue)",
            f"Purchase intent at optimal price: {price_results[optimal_price]:.1%}",
            f"Price sensitivity: {self._calculate_price_sensitivity(price_results)}"
        ]
        
        return MarketPrediction(
            scenario_id=f"market_analysis_{product_name}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            product_name=product_name,
            price_points_tested=price_points,
            optimal_price=optimal_price,
            purchase_intent_by_price=price_results,
            target_market_size=target_market_size,
            demographic_segments={},  # Would require demographic analysis
            market_insights=insights,
            revenue_projections=revenue_projections,
            confidence_level=0.8
        )
    
    def _calculate_price_sensitivity(self, price_results: Dict[float, float]) -> str:
        """Calculate price sensitivity description"""
        prices = sorted(price_results.keys())
        intents = [price_results[p] for p in prices]
        
        # Calculate correlation between price and intent
        if len(prices) > 1:
            price_range = max(prices) - min(prices)
            intent_range = max(intents) - min(intents)
            
            if intent_range / price_range > 0.1:
                return "High price sensitivity - demand decreases significantly with price"
            elif intent_range / price_range > 0.05:
                return "Moderate price sensitivity - some demand elasticity"
            else:
                return "Low price sensitivity - stable demand across price range"
        
        return "Insufficient data to determine price sensitivity"
    
    async def analyze_feature_preferences(
        self,
        product_name: str,
        features: List[str],
        personas: List[PersonaConfig],
        base_description: str
    ) -> FeatureAnalysis:
        """
        Analyze which product features are most important to different demographics
        
        Args:
            product_name: Name of the product
            features: List of features to test
            personas: Personas to survey
            base_description: Base product description
        
        Returns:
            Feature analysis with rankings and demographic preferences
        """
        
        print(f"🔍 Analyzing feature preferences for {product_name}")
        
        feature_scores = {}
        
        for feature in features:
            print(f"   Testing feature: {feature}")
            
            scenario = ScenarioConfig(
                scenario_id=f"feature_test_{feature}",
                scenario_type="product",
                description=f"{base_description} with {feature}",
                question=f"How important is this feature to you: {feature}? Would this influence your purchase decision for {product_name}?",
                context={"feature": feature, "product": product_name}
            )
            
            results = await self.simulation_engine.run_scenario_simulation(
                scenario=scenario,
                personas=personas,
                max_concurrent=8
            )
            
            # Calculate feature importance
            importance = sum(
                results.response_distribution.get(cat, 0)
                for cat in ["important", "very_important", "essential", "positive", "support"]
            )
            
            feature_scores[feature] = importance
        
        # Rank features
        ranked_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize features
        must_have = [f for f, score in ranked_features if score > 0.7]
        nice_to_have = [f for f, score in ranked_features if 0.4 <= score <= 0.7]
        deal_breaker = [f for f, score in ranked_features if score < 0.2]
        
        return FeatureAnalysis(
            scenario_id=f"feature_analysis_{product_name}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            features_tested=features,
            feature_rankings=feature_scores,
            demographic_preferences={},  # Would require demographic breakdown
            must_have_features=must_have,
            nice_to_have_features=nice_to_have,
            deal_breaker_features=deal_breaker,
            insights=[
                f"Most important feature: {ranked_features[0][0]} ({ranked_features[0][1]:.1%} importance)",
                f"Least important feature: {ranked_features[-1][0]} ({ranked_features[-1][1]:.1%} importance)",
                f"Must-have features: {len(must_have)}, Nice-to-have: {len(nice_to_have)}"
            ]
        )


def print_political_results(prediction: PoliticalPrediction):
    """Print formatted political analysis results"""
    
    print(f"\n🗳️ POLITICAL ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Policy Topic: {prediction.policy_topic}")
    print(f"Overall Support: {prediction.overall_support:.1%}")
    print(f"Overall Opposition: {prediction.overall_opposition:.1%}")
    print(f"Sample Size: {prediction.sample_size}")
    print(f"Confidence Level: {prediction.confidence_level:.3f}")
    
    print(f"\n💡 KEY INSIGHTS:")
    for insight in prediction.key_insights:
        print(f"   • {insight}")
    
    if prediction.swing_demographics:
        print(f"\n🎯 SWING DEMOGRAPHICS:")
        for demo in prediction.swing_demographics[:5]:  # Top 5
            print(f"   • {demo}")


def print_market_results(prediction: MarketPrediction):
    """Print formatted market research results"""
    
    print(f"\n🛍️ MARKET RESEARCH RESULTS")
    print("=" * 80)
    print(f"Product: {prediction.product_name}")
    print(f"Optimal Price: ${prediction.optimal_price}")
    print(f"Purchase Intent at Optimal Price: {prediction.target_market_size:.1%}")
    
    print(f"\n💰 PRICE ANALYSIS:")
    for price in sorted(prediction.price_points_tested):
        intent = prediction.purchase_intent_by_price[price]
        revenue = prediction.revenue_projections[price]
        print(f"   ${price}: {intent:.1%} intent, ${revenue:,.0f} projected revenue")
    
    print(f"\n💡 MARKET INSIGHTS:")
    for insight in prediction.market_insights:
        print(f"   • {insight}")


async def test_business_applications():
    """Test the business application layer"""
    
    print("🧪 TESTING BUSINESS APPLICATIONS")
    print("=" * 80)
    
    # Setup
    from poll_data_manager import PollDatabase, load_sample_poll_data
    
    poll_db = PollDatabase("test_business_poll_data.db")
    load_sample_poll_data(poll_db)
    poll_selector = PollDataSelector(poll_db)
    
    # Mock LLM config
    class MockLLMConfig:
        llm_provider = "openai"
        llm_name = "gpt-4"
        temperature = 0.8
    
    simulation_engine = PersonaSimulation(MockLLMConfig())
    
    # Create test personas
    test_personas = [
        PersonaConfig(
            name="Maria Rodriguez", age=34, race_ethnicity="hispanic", gender="female",
            education="college", location_type="suburban", income="50k_75k", occupation="teacher"
        ),
        PersonaConfig(
            name="Bob Johnson", age=52, race_ethnicity="white", gender="male",
            education="high_school", location_type="rural", income="30k_50k", occupation="mechanic"
        ),
        PersonaConfig(
            name="Ashley Chen", age=28, race_ethnicity="asian", gender="female",
            education="graduate", location_type="urban", income="over_100k", occupation="software engineer"
        )
    ]
    
    # Test political analysis
    political_analyzer = PoliticalAnalyzer(simulation_engine, poll_selector)
    
    political_result = await political_analyzer.test_policy_support(
        policy_description="Universal healthcare system providing coverage for all citizens",
        policy_topic="healthcare",
        personas=test_personas
    )
    
    print_political_results(political_result)
    
    # Test market research
    market_researcher = MarketResearcher(simulation_engine, poll_selector)
    
    market_result = await market_researcher.test_product_reception(
        product_name="Smart Home Assistant",
        product_description="AI-powered device that controls home automation and answers questions",
        price_points=[99.99, 149.99, 199.99],
        personas=test_personas
    )
    
    print_market_results(market_result)


if __name__ == "__main__":
    asyncio.run(test_business_applications())