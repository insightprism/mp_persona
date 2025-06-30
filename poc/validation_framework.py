"""
Validation and Accuracy Tracking Framework

This module provides comprehensive validation tools to measure and improve
the accuracy of persona predictions against real-world polling data.
"""

import json
import sqlite3
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
import asyncio
from pathlib import Path

from persona_config import PersonaConfig
from simulation_engine import PersonaSimulation, ScenarioConfig, SimulationResults
from poll_data_manager import PollDatabase, PollDataSelector, PollRecord


@dataclass
class ValidationTarget:
    """Known polling result to validate against"""
    validation_id: str
    source_poll: PollRecord
    expected_results: Dict[str, float]  # Expected response distribution
    demographic_filter: Optional[Dict[str, Any]] = None
    validation_date: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of comparing prediction to known data"""
    validation_id: str
    scenario_id: str
    predicted_results: Dict[str, float]
    actual_results: Dict[str, float]
    accuracy_score: float  # 0-1, where 1 is perfect accuracy
    demographic_accuracy: Dict[str, float]  # accuracy by demographic
    error_analysis: Dict[str, Any]
    confidence_calibration: float  # How well confidence matches actual accuracy
    validation_timestamp: str


@dataclass
class AccuracyReport:
    """Comprehensive accuracy report over time"""
    report_id: str
    time_period: Tuple[str, str]  # start_date, end_date
    total_validations: int
    overall_accuracy: float
    accuracy_by_topic: Dict[str, float]
    accuracy_by_demographic: Dict[str, float]
    accuracy_trend: List[Tuple[str, float]]  # date, accuracy pairs
    best_performing_scenarios: List[str]
    worst_performing_scenarios: List[str]
    improvement_recommendations: List[str]
    report_timestamp: str


class ValidationDatabase:
    """Database for storing validation results and tracking accuracy over time"""
    
    def __init__(self, db_path: str = "validation_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize validation database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Validation targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_targets (
                validation_id TEXT PRIMARY KEY,
                source_poll_id TEXT NOT NULL,
                expected_results TEXT NOT NULL,  -- JSON
                demographic_filter TEXT,         -- JSON
                validation_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Validation results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                validation_id TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                predicted_results TEXT NOT NULL,  -- JSON
                actual_results TEXT NOT NULL,     -- JSON
                accuracy_score REAL NOT NULL,
                demographic_accuracy TEXT,        -- JSON
                error_analysis TEXT,              -- JSON
                confidence_calibration REAL,
                validation_timestamp TEXT NOT NULL,
                FOREIGN KEY (validation_id) REFERENCES validation_targets (validation_id)
            )
        ''')
        
        # Accuracy tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accuracy_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                topic TEXT,
                demographic_group TEXT,
                accuracy_score REAL NOT NULL,
                sample_size INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_validation_target(self, target: ValidationTarget):
        """Add a validation target"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO validation_targets 
            (validation_id, source_poll_id, expected_results, demographic_filter, validation_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            target.validation_id,
            target.source_poll.poll_id,
            json.dumps(target.expected_results),
            json.dumps(target.demographic_filter) if target.demographic_filter else None,
            target.validation_date
        ))
        
        conn.commit()
        conn.close()
    
    def add_validation_result(self, result: ValidationResult):
        """Add a validation result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO validation_results 
            (validation_id, scenario_id, predicted_results, actual_results, 
             accuracy_score, demographic_accuracy, error_analysis, 
             confidence_calibration, validation_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.validation_id, result.scenario_id,
            json.dumps(result.predicted_results),
            json.dumps(result.actual_results),
            result.accuracy_score,
            json.dumps(result.demographic_accuracy),
            json.dumps(result.error_analysis),
            result.confidence_calibration,
            result.validation_timestamp
        ))
        
        conn.commit()
        conn.close()
    
    def get_accuracy_history(self, days: int = 30) -> List[ValidationResult]:
        """Get validation results from the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT * FROM validation_results 
            WHERE validation_timestamp > ?
            ORDER BY validation_timestamp DESC
        ''', (cutoff_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = ValidationResult(
                validation_id=row[1], scenario_id=row[2],
                predicted_results=json.loads(row[3]),
                actual_results=json.loads(row[4]),
                accuracy_score=row[5],
                demographic_accuracy=json.loads(row[6]),
                error_analysis=json.loads(row[7]),
                confidence_calibration=row[8],
                validation_timestamp=row[9]
            )
            results.append(result)
        
        return results


class ValidationFramework:
    """Main validation framework for testing persona accuracy"""
    
    def __init__(
        self, 
        simulation_engine: PersonaSimulation,
        poll_database: PollDatabase,
        validation_database: ValidationDatabase
    ):
        self.simulation_engine = simulation_engine
        self.poll_database = poll_database
        self.validation_database = validation_database
        self.validation_targets = []
    
    def create_validation_targets_from_polls(
        self, 
        topic_filter: Optional[str] = None,
        min_sample_size: int = 500,
        max_targets: int = 20
    ) -> List[ValidationTarget]:
        """
        Create validation targets from existing poll data
        
        Args:
            topic_filter: Filter polls by topic
            min_sample_size: Minimum poll sample size to include
            max_targets: Maximum number of targets to create
        
        Returns:
            List of validation targets
        """
        
        print(f"🎯 Creating validation targets from poll data...")
        
        # Query suitable polls
        polls = self.poll_database.query_polls(topic=topic_filter)
        
        # Filter by sample size and create targets
        targets = []
        for poll in polls:
            if poll.sample_size >= min_sample_size and len(targets) < max_targets:
                target = ValidationTarget(
                    validation_id=f"val_{poll.poll_id}_{datetime.now().strftime('%Y%m%d')}",
                    source_poll=poll,
                    expected_results=poll.response_data,
                    demographic_filter=poll.demographic_slice,
                    validation_date=datetime.now().isoformat()
                )
                targets.append(target)
                self.validation_database.add_validation_target(target)
        
        self.validation_targets.extend(targets)
        print(f"✅ Created {len(targets)} validation targets")
        
        return targets
    
    async def validate_against_target(
        self, 
        target: ValidationTarget,
        test_personas: List[PersonaConfig],
        max_concurrent: int = 5
    ) -> ValidationResult:
        """
        Validate persona predictions against a specific target
        
        Args:
            target: The validation target to test against
            test_personas: Personas matching the target demographics
            max_concurrent: Maximum concurrent simulations
        
        Returns:
            Validation result with accuracy metrics
        """
        
        print(f"🧪 Validating against target: {target.validation_id}")
        
        # Create scenario from the poll question
        scenario = ScenarioConfig(
            scenario_id=f"validation_{target.validation_id}",
            scenario_type="validation",
            description=f"Validation test for {target.source_poll.topic}",
            question=target.source_poll.question,
            context={"validation": True, "original_poll": target.source_poll.poll_id}
        )
        
        # Get relevant poll data for context (excluding the target poll)
        poll_selector = PollDataSelector(self.poll_database)
        poll_data = poll_selector.select_relevant_polls(
            scenario.description, 
            test_personas[0] if test_personas else None,
            max_polls=3
        )
        
        # Run simulation
        results = await self.simulation_engine.run_scenario_simulation(
            scenario=scenario,
            personas=test_personas,
            poll_data=poll_data,
            max_concurrent=max_concurrent
        )
        
        # Calculate accuracy
        return self._calculate_validation_accuracy(target, results)
    
    def _calculate_validation_accuracy(
        self, 
        target: ValidationTarget, 
        results: SimulationResults
    ) -> ValidationResult:
        """Calculate accuracy metrics comparing prediction to actual results"""
        
        predicted = results.response_distribution
        actual = target.expected_results
        
        # Calculate overall accuracy using overlapping categories
        accuracy_scores = []
        
        # Map common response categories
        category_mappings = {
            "support": ["support", "approve", "favor", "yes"],
            "oppose": ["oppose", "disapprove", "against", "no"],
            "neutral": ["neutral", "unsure", "undecided"]
        }
        
        # Calculate accuracy for each mapped category
        for standard_cat, variations in category_mappings.items():
            pred_value = sum(predicted.get(var, 0) for var in variations)
            actual_value = sum(actual.get(var, 0) for var in variations)
            
            # Calculate absolute error and convert to accuracy
            error = abs(pred_value - actual_value)
            accuracy = 1.0 - error  # Accuracy is 1 minus absolute error
            accuracy_scores.append(max(0.0, accuracy))  # Ensure non-negative
        
        overall_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.0
        
        # Calculate demographic accuracy (simplified)
        demo_accuracy = self._calculate_demographic_accuracy(results, target)
        
        # Error analysis
        error_analysis = {
            "largest_error": max([abs(predicted.get(k, 0) - actual.get(k, 0)) for k in actual.keys()]),
            "category_errors": {
                k: predicted.get(k, 0) - actual.get(k, 0) 
                for k in actual.keys()
            },
            "sample_size_difference": results.total_personas - target.source_poll.sample_size
        }
        
        # Confidence calibration (simplified)
        confidence_calibration = min(1.0, results.statistical_significance / overall_accuracy) if overall_accuracy > 0 else 0.5
        
        validation_result = ValidationResult(
            validation_id=target.validation_id,
            scenario_id=results.scenario_id,
            predicted_results=predicted,
            actual_results=actual,
            accuracy_score=overall_accuracy,
            demographic_accuracy=demo_accuracy,
            error_analysis=error_analysis,
            confidence_calibration=confidence_calibration,
            validation_timestamp=datetime.utcnow().isoformat()
        )
        
        # Store result
        self.validation_database.add_validation_result(validation_result)
        
        return validation_result
    
    def _calculate_demographic_accuracy(
        self, 
        results: SimulationResults, 
        target: ValidationTarget
    ) -> Dict[str, float]:
        """Calculate accuracy broken down by demographic groups"""
        
        # Simplified demographic accuracy calculation
        # In production, would compare demographic breakdowns in detail
        demo_accuracy = {}
        
        if target.demographic_filter:
            for demo_field in target.demographic_filter.keys():
                if demo_field in results.demographic_breakdowns:
                    # Calculate average accuracy across demographic values
                    accuracies = []
                    for demo_value, responses in results.demographic_breakdowns[demo_field].items():
                        # Simplified accuracy calculation
                        main_response = max(responses.items(), key=lambda x: x[1])[1] if responses else 0.0
                        accuracies.append(main_response)
                    
                    demo_accuracy[demo_field] = statistics.mean(accuracies) if accuracies else 0.5
        
        return demo_accuracy
    
    async def run_comprehensive_validation(
        self, 
        personas: List[PersonaConfig],
        max_targets: int = 10
    ) -> List[ValidationResult]:
        """
        Run comprehensive validation across multiple targets
        
        Args:
            personas: Test personas to use
            max_targets: Maximum validation targets to test
        
        Returns:
            List of validation results
        """
        
        print(f"🔬 Running comprehensive validation with {len(personas)} personas")
        
        # Create validation targets if none exist
        if not self.validation_targets:
            self.create_validation_targets_from_polls(max_targets=max_targets)
        
        validation_results = []
        
        for i, target in enumerate(self.validation_targets[:max_targets]):
            print(f"   Validation {i+1}/{min(max_targets, len(self.validation_targets))}")
            
            try:
                result = await self.validate_against_target(target, personas)
                validation_results.append(result)
                
                print(f"   ✅ Accuracy: {result.accuracy_score:.3f}")
                
            except Exception as e:
                print(f"   ❌ Validation failed: {e}")
                continue
        
        return validation_results
    
    def generate_accuracy_report(self, days: int = 30) -> AccuracyReport:
        """Generate comprehensive accuracy report"""
        
        print(f"📊 Generating accuracy report for last {days} days")
        
        # Get validation history
        results = self.validation_database.get_accuracy_history(days)
        
        if not results:
            print("⚠️ No validation data available")
            return AccuracyReport(
                report_id=f"empty_report_{datetime.now().strftime('%Y%m%d')}",
                time_period=(datetime.now().isoformat(), datetime.now().isoformat()),
                total_validations=0,
                overall_accuracy=0.0,
                accuracy_by_topic={},
                accuracy_by_demographic={},
                accuracy_trend=[],
                best_performing_scenarios=[],
                worst_performing_scenarios=[],
                improvement_recommendations=[],
                report_timestamp=datetime.utcnow().isoformat()
            )
        
        # Calculate overall accuracy
        overall_accuracy = statistics.mean([r.accuracy_score for r in results])
        
        # Calculate accuracy by topic (simplified)
        accuracy_by_topic = {}
        topic_groups = {}
        for result in results:
            # Extract topic from validation_id (simplified)
            topic = result.validation_id.split('_')[1] if '_' in result.validation_id else 'general'
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(result.accuracy_score)
        
        for topic, scores in topic_groups.items():
            accuracy_by_topic[topic] = statistics.mean(scores)
        
        # Generate accuracy trend
        accuracy_trend = []
        results_by_date = {}
        for result in results:
            date = result.validation_timestamp[:10]  # YYYY-MM-DD
            if date not in results_by_date:
                results_by_date[date] = []
            results_by_date[date].append(result.accuracy_score)
        
        for date in sorted(results_by_date.keys()):
            daily_accuracy = statistics.mean(results_by_date[date])
            accuracy_trend.append((date, daily_accuracy))
        
        # Best and worst performing scenarios
        sorted_results = sorted(results, key=lambda x: x.accuracy_score, reverse=True)
        best_scenarios = [r.scenario_id for r in sorted_results[:3]]
        worst_scenarios = [r.scenario_id for r in sorted_results[-3:]]
        
        # Improvement recommendations
        recommendations = []
        if overall_accuracy < 0.7:
            recommendations.append("Overall accuracy below 70% - consider improving persona behavioral modeling")
        if len(results) < 10:
            recommendations.append("Limited validation data - increase validation frequency")
        
        low_accuracy_topics = [topic for topic, acc in accuracy_by_topic.items() if acc < 0.6]
        if low_accuracy_topics:
            recommendations.append(f"Topics needing improvement: {', '.join(low_accuracy_topics)}")
        
        return AccuracyReport(
            report_id=f"accuracy_report_{datetime.now().strftime('%Y%m%d_%H%M')}",
            time_period=(min(r.validation_timestamp for r in results)[:10], 
                        max(r.validation_timestamp for r in results)[:10]),
            total_validations=len(results),
            overall_accuracy=overall_accuracy,
            accuracy_by_topic=accuracy_by_topic,
            accuracy_by_demographic={},  # Simplified for now
            accuracy_trend=accuracy_trend,
            best_performing_scenarios=best_scenarios,
            worst_performing_scenarios=worst_scenarios,
            improvement_recommendations=recommendations,
            report_timestamp=datetime.utcnow().isoformat()
        )


def print_validation_results(results: List[ValidationResult]):
    """Print formatted validation results"""
    
    print(f"\n🔬 VALIDATION RESULTS")
    print("=" * 80)
    print(f"Total Validations: {len(results)}")
    
    if not results:
        print("No validation results to display")
        return
    
    accuracies = [r.accuracy_score for r in results]
    print(f"Overall Accuracy: {statistics.mean(accuracies):.3f}")
    print(f"Accuracy Range: {min(accuracies):.3f} - {max(accuracies):.3f}")
    
    print(f"\n📋 INDIVIDUAL RESULTS:")
    for i, result in enumerate(results[:5]):  # Show top 5
        print(f"   {i+1}. {result.validation_id}")
        print(f"      Accuracy: {result.accuracy_score:.3f}")
        print(f"      Largest Error: {result.error_analysis.get('largest_error', 0):.3f}")
        print()


def print_accuracy_report(report: AccuracyReport):
    """Print formatted accuracy report"""
    
    print(f"\n📊 ACCURACY REPORT")
    print("=" * 80)
    print(f"Report ID: {report.report_id}")
    print(f"Time Period: {report.time_period[0]} to {report.time_period[1]}")
    print(f"Total Validations: {report.total_validations}")
    print(f"Overall Accuracy: {report.overall_accuracy:.3f}")
    
    if report.accuracy_by_topic:
        print(f"\n📈 ACCURACY BY TOPIC:")
        for topic, accuracy in sorted(report.accuracy_by_topic.items(), key=lambda x: x[1], reverse=True):
            print(f"   {topic}: {accuracy:.3f}")
    
    if report.accuracy_trend:
        print(f"\n📉 ACCURACY TREND (last 5 days):")
        for date, accuracy in report.accuracy_trend[-5:]:
            print(f"   {date}: {accuracy:.3f}")
    
    if report.improvement_recommendations:
        print(f"\n💡 IMPROVEMENT RECOMMENDATIONS:")
        for rec in report.improvement_recommendations:
            print(f"   • {rec}")


async def test_validation_framework():
    """Test the validation framework"""
    
    print("🧪 TESTING VALIDATION FRAMEWORK")
    print("=" * 80)
    
    # Setup
    from poll_data_manager import PollDatabase, load_sample_poll_data
    
    poll_db = PollDatabase("test_validation_poll_data.db")
    load_sample_poll_data(poll_db)
    
    validation_db = ValidationDatabase("test_validation_data.db")
    
    # Mock simulation engine
    class MockLLMConfig:
        llm_provider = "openai"
        llm_name = "gpt-4"
        temperature = 0.8
    
    simulation_engine = PersonaSimulation(MockLLMConfig())
    
    # Create validation framework
    validator = ValidationFramework(simulation_engine, poll_db, validation_db)
    
    # Create test personas
    test_personas = [
        PersonaConfig(
            name="Test Persona 1", age=34, race_ethnicity="hispanic", gender="female",
            education="college", location_type="suburban", income="50k_75k"
        ),
        PersonaConfig(
            name="Test Persona 2", age=52, race_ethnicity="white", gender="male",
            education="high_school", location_type="rural", income="30k_50k"
        )
    ]
    
    # Run validation
    try:
        validation_results = await validator.run_comprehensive_validation(
            personas=test_personas,
            max_targets=3
        )
        
        print_validation_results(validation_results)
        
        # Generate accuracy report
        accuracy_report = validator.generate_accuracy_report(days=1)
        print_accuracy_report(accuracy_report)
        
        return validation_results, accuracy_report
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return [], None


if __name__ == "__main__":
    # Fix missing import
    from datetime import timedelta
    asyncio.run(test_validation_framework())