"""
Complete System Demonstration

This demonstrates the full LLM Persona Behavioral Prediction System with all components
integrated together for end-to-end behavioral analysis and validation.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Import all system components
from persona_config import PersonaConfig
from simulation_engine import PersonaSimulation, ScenarioConfig, MockLLMConfig
from poll_data_manager import PollDatabase, PollDataSelector, load_sample_poll_data
from business_applications import PoliticalAnalyzer, MarketResearcher, print_political_results, print_market_results
from validation_framework import ValidationFramework, ValidationDatabase, print_validation_results, print_accuracy_report
from census_persona_generator import CensusPersonaGenerator, print_population_summary


class CompleteLLMPersonaSystem:
    """Complete integrated LLM Persona System for behavioral prediction"""
    
    def __init__(self, llm_config=None):
        # Initialize all components
        self.llm_config = llm_config or MockLLMConfig()
        
        # Data management
        self.poll_database = PollDatabase("complete_system_poll_data.db")
        load_sample_poll_data(self.poll_database)
        self.poll_selector = PollDataSelector(self.poll_database)
        
        # Core simulation engine
        self.simulation_engine = PersonaSimulation(self.llm_config)
        
        # Business applications
        self.political_analyzer = PoliticalAnalyzer(self.simulation_engine, self.poll_selector)
        self.market_researcher = MarketResearcher(self.simulation_engine, self.poll_selector)
        
        # Validation system
        self.validation_database = ValidationDatabase("complete_system_validation.db")
        self.validation_framework = ValidationFramework(
            self.simulation_engine, 
            self.poll_database, 
            self.validation_database
        )
        
        # Persona generation
        self.persona_generator = CensusPersonaGenerator(seed=42)
        
        # System state
        self.generated_populations = {}
        self.analysis_history = []
    
    async def run_complete_political_analysis(
        self, 
        policy_description: str,
        policy_topic: str,
        population_size: int = 100
    ) -> Dict[str, Any]:
        """
        Run complete political analysis: generate population → analyze policy → validate
        
        Args:
            policy_description: The policy to analyze
            policy_topic: Policy category (healthcare, economy, etc.)
            population_size: Size of test population
        
        Returns:
            Complete analysis results with validation metrics
        """
        
        print(f"🗳️ COMPLETE POLITICAL ANALYSIS: {policy_topic}")
        print("=" * 80)
        
        # Step 1: Generate representative population
        print("1️⃣ Generating census-proportional population...")
        personas = self.persona_generator.generate_representative_population(
            size=population_size,
            include_behavioral_characteristics=True
        )
        
        population_validation = self.persona_generator.validate_population_accuracy(personas)
        self.generated_populations[f"political_{policy_topic}"] = personas
        
        print(f"   ✅ Generated {len(personas)} personas (accuracy: {population_validation.validation_score:.3f})")
        
        # Step 2: Run political analysis
        print("2️⃣ Running political support analysis...")
        political_prediction = await self.political_analyzer.test_policy_support(
            policy_description=policy_description,
            policy_topic=policy_topic,
            personas=personas
        )
        
        print(f"   ✅ Analysis complete: {political_prediction.overall_support:.1%} support")
        
        # Step 3: Validate against historical data (if available)
        print("3️⃣ Running validation against historical polling...")
        try:
            validation_results = await self.validation_framework.run_comprehensive_validation(
                personas=personas[:20],  # Use subset for validation
                max_targets=3
            )
            
            avg_accuracy = sum(r.accuracy_score for r in validation_results) / len(validation_results) if validation_results else 0.0
            print(f"   ✅ Validation complete: {avg_accuracy:.3f} average accuracy")
            
        except Exception as e:
            print(f"   ⚠️ Validation skipped: {e}")
            validation_results = []
        
        # Store analysis
        analysis_result = {
            "type": "political",
            "topic": policy_topic,
            "population_size": len(personas),
            "population_accuracy": population_validation.validation_score,
            "political_prediction": political_prediction,
            "validation_results": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.analysis_history.append(analysis_result)
        
        return analysis_result
    
    async def run_complete_market_analysis(
        self,
        product_name: str,
        product_description: str,
        price_points: List[float],
        population_size: int = 100,
        target_constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run complete market analysis: generate target population → test product → validate
        
        Args:
            product_name: Name of product to test
            product_description: Product description
            price_points: Prices to test
            population_size: Size of test population
            target_constraints: Demographic constraints for target market
        
        Returns:
            Complete market analysis results
        """
        
        print(f"🛍️ COMPLETE MARKET ANALYSIS: {product_name}")
        print("=" * 80)
        
        # Step 1: Generate target market population
        print("1️⃣ Generating target market population...")
        personas = self.persona_generator.generate_representative_population(
            size=population_size,
            include_behavioral_characteristics=True,
            demographic_constraints=target_constraints
        )
        
        population_validation = self.persona_generator.validate_population_accuracy(personas)
        self.generated_populations[f"market_{product_name}"] = personas
        
        print(f"   ✅ Generated {len(personas)} target market personas")
        
        # Step 2: Test product reception
        print("2️⃣ Testing product reception across price points...")
        market_prediction = await self.market_researcher.test_product_reception(
            product_name=product_name,
            product_description=product_description,
            price_points=price_points,
            personas=personas
        )
        
        print(f"   ✅ Market analysis complete: ${market_prediction.optimal_price} optimal price")
        
        # Step 3: Feature analysis
        print("3️⃣ Analyzing feature preferences...")
        sample_features = ["high quality", "affordable price", "innovative design", "brand reputation"]
        
        feature_analysis = await self.market_researcher.analyze_feature_preferences(
            product_name=product_name,
            features=sample_features,
            personas=personas[:50],  # Use subset for feature analysis
            base_description=product_description
        )
        
        print(f"   ✅ Feature analysis complete: {len(feature_analysis.must_have_features)} must-have features")
        
        # Store analysis
        analysis_result = {
            "type": "market",
            "product": product_name,
            "population_size": len(personas),
            "population_accuracy": population_validation.validation_score,
            "market_prediction": market_prediction,
            "feature_analysis": feature_analysis,
            "target_constraints": target_constraints,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.analysis_history.append(analysis_result)
        
        return analysis_result
    
    async def run_system_validation_study(self, validation_population_size: int = 200) -> Dict[str, Any]:
        """
        Run comprehensive system validation to measure overall accuracy
        
        Args:
            validation_population_size: Size of validation population
        
        Returns:
            System validation results
        """
        
        print(f"🔬 SYSTEM VALIDATION STUDY")
        print("=" * 80)
        
        # Generate validation population
        print("1️⃣ Generating validation population...")
        validation_personas = self.persona_generator.generate_representative_population(
            size=validation_population_size,
            include_behavioral_characteristics=True
        )
        
        # Run comprehensive validation
        print("2️⃣ Running validation against historical polls...")
        validation_results = await self.validation_framework.run_comprehensive_validation(
            personas=validation_personas,
            max_targets=10
        )
        
        # Generate accuracy report
        print("3️⃣ Generating accuracy report...")
        accuracy_report = self.validation_framework.generate_accuracy_report(days=1)
        
        return {
            "validation_population_size": len(validation_personas),
            "validation_results": validation_results,
            "accuracy_report": accuracy_report,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system report"""
        
        report_lines = [
            "📊 LLM PERSONA SYSTEM REPORT",
            "=" * 80,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "🏗️ SYSTEM COMPONENTS:",
            "✅ Persona Configuration with behavioral characteristics",
            "✅ Census-proportional population generation",
            "✅ Historical polling data management",
            "✅ Parallel simulation engine",
            "✅ Political analysis tools",
            "✅ Market research tools", 
            "✅ Validation and accuracy tracking",
            "",
            f"📈 ANALYSIS HISTORY: {len(self.analysis_history)} analyses completed",
        ]
        
        if self.analysis_history:
            political_analyses = [a for a in self.analysis_history if a["type"] == "political"]
            market_analyses = [a for a in self.analysis_history if a["type"] == "market"]
            
            report_lines.extend([
                f"   • Political analyses: {len(political_analyses)}",
                f"   • Market analyses: {len(market_analyses)}",
                ""
            ])
            
            if political_analyses:
                report_lines.extend([
                    "🗳️ POLITICAL ANALYSIS SUMMARY:",
                    f"   Latest: {political_analyses[-1]['topic']} policy",
                    f"   Support level: {political_analyses[-1]['political_prediction'].overall_support:.1%}",
                    f"   Population accuracy: {political_analyses[-1]['population_accuracy']:.3f}",
                    ""
                ])
            
            if market_analyses:
                report_lines.extend([
                    "🛍️ MARKET ANALYSIS SUMMARY:",
                    f"   Latest: {market_analyses[-1]['product']}",
                    f"   Optimal price: ${market_analyses[-1]['market_prediction'].optimal_price}",
                    f"   Population accuracy: {market_analyses[-1]['population_accuracy']:.3f}",
                    ""
                ])
        
        report_lines.extend([
            "👥 GENERATED POPULATIONS:",
            f"   Total populations: {len(self.generated_populations)}",
            f"   Total personas: {sum(len(p) for p in self.generated_populations.values())}",
            "",
            "🎯 SYSTEM CAPABILITIES:",
            "• Predict policy support with demographic breakdowns",
            "• Optimize product pricing and features",
            "• Generate statistically representative populations",
            "• Validate predictions against historical data",
            "• Track accuracy and improve over time",
            "",
            "💼 BUSINESS APPLICATIONS:",
            "• Political campaign strategy",
            "• Product launch optimization", 
            "• Market segmentation analysis",
            "• Policy impact assessment",
            "• Consumer behavior prediction"
        ])
        
        return "\n".join(report_lines)
    
    def print_system_status(self):
        """Print current system status"""
        print(self.generate_system_report())


async def run_complete_system_demonstration():
    """Run comprehensive demonstration of the complete system"""
    
    print("🚀 COMPLETE LLM PERSONA SYSTEM DEMONSTRATION")
    print("=" * 80)
    print("This demonstrates the full end-to-end system capabilities")
    print()
    
    # Initialize system
    system = CompleteLLMPersonaSystem()
    
    # Demo 1: Political Analysis
    print("DEMO 1: Political Policy Analysis")
    print("-" * 50)
    
    political_result = await system.run_complete_political_analysis(
        policy_description="Universal healthcare system providing coverage for all citizens funded through progressive taxation",
        policy_topic="healthcare",
        population_size=50  # Small for demo
    )
    
    print_political_results(political_result["political_prediction"])
    
    # Demo 2: Market Research
    print("\n\nDEMO 2: Market Research Analysis")
    print("-" * 50)
    
    market_result = await system.run_complete_market_analysis(
        product_name="AI Smart Home Assistant",
        product_description="Voice-controlled AI device that manages home automation, answers questions, and provides personalized recommendations",
        price_points=[99.99, 149.99, 199.99, 249.99],
        population_size=50,  # Small for demo
        target_constraints={
            "age_min": 25,
            "age_max": 55,
            "income": ["50k_75k", "75k_100k", "over_100k"]
        }
    )
    
    print_market_results(market_result["market_prediction"])
    
    # Demo 3: System Validation
    print("\n\nDEMO 3: System Validation")
    print("-" * 50)
    
    try:
        validation_study = await system.run_system_validation_study(validation_population_size=30)
        print_validation_results(validation_study["validation_results"])
        print_accuracy_report(validation_study["accuracy_report"])
    except Exception as e:
        print(f"Validation demo skipped: {e}")
    
    # System Report
    print("\n\n")
    system.print_system_status()
    
    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("The system successfully demonstrated:")
    print("✅ Census-proportional population generation")
    print("✅ Political policy analysis with demographic breakdowns")
    print("✅ Market research with pricing optimization")
    print("✅ Validation against historical polling data")
    print("✅ Comprehensive accuracy tracking")
    
    return system


async def run_business_case_scenarios():
    """Run specific business case scenarios"""
    
    print("💼 BUSINESS CASE SCENARIOS")
    print("=" * 80)
    
    system = CompleteLLMPersonaSystem()
    
    # Scenario 1: Political Campaign Strategy
    print("Scenario 1: Political Campaign - Climate Policy")
    print("-" * 60)
    
    climate_result = await system.run_complete_political_analysis(
        policy_description="Comprehensive climate action plan including carbon tax, green energy subsidies, and infrastructure investment",
        policy_topic="environment",
        population_size=200
    )
    
    print(f"📊 Campaign Insight: {climate_result['political_prediction'].overall_support:.1%} support")
    print(f"🎯 Key Demographics: {', '.join(climate_result['political_prediction'].swing_demographics[:3])}")
    
    # Scenario 2: Product Launch Strategy
    print("\n\nScenario 2: Tech Company - Electric Vehicle")
    print("-" * 60)
    
    ev_result = await system.run_complete_market_analysis(
        product_name="Affordable Electric Sedan",
        product_description="Mid-range electric vehicle with 300-mile range, advanced driver assistance, and competitive pricing",
        price_points=[35000, 40000, 45000, 50000],
        population_size=200,
        target_constraints={
            "age_min": 30,
            "age_max": 60,
            "income": ["50k_75k", "75k_100k", "over_100k"],
            "location_type": ["urban", "suburban"]
        }
    )
    
    print(f"💰 Optimal Price: ${ev_result['market_prediction'].optimal_price:,.0f}")
    print(f"📈 Purchase Intent: {ev_result['market_prediction'].target_market_size:.1%}")
    
    return system


if __name__ == "__main__":
    # Run the complete demonstration
    asyncio.run(run_complete_system_demonstration())
    
    print("\n" + "="*80)
    print("To run business case scenarios, uncomment the line below:")
    print("# asyncio.run(run_business_case_scenarios())")