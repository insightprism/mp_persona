"""
Poll Data Management System

This module manages historical polling data, major events, and provides
intelligent selection of relevant polling information for persona simulations.
"""

import json
import sqlite3
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import re

from persona_config import PersonaConfig


@dataclass
class PollRecord:
    """Individual polling record"""
    poll_id: str
    source: str  # "Gallup", "Pew", "CNN", etc.
    date: str  # ISO format
    topic: str  # "healthcare", "economy", "politics", etc.
    question: str
    demographic_slice: Dict[str, Any]  # age, race, education, etc.
    response_data: Dict[str, float]  # response categories and percentages
    sample_size: int
    margin_of_error: Optional[float] = None
    confidence_level: Optional[float] = 0.95


@dataclass
class MajorEvent:
    """Major historical events that influenced public opinion"""
    event_id: str
    name: str
    date: str  # ISO format
    event_type: str  # "economic", "political", "social", "health", "international"
    description: str
    magnitude: str  # "local", "national", "global"
    duration_days: Optional[int] = None
    end_date: Optional[str] = None


@dataclass
class BehavioralPattern:
    """Identified patterns in how demographics respond to events"""
    pattern_id: str
    demographic_profile: Dict[str, Any]
    event_types: List[str]
    typical_response: str
    confidence: float
    supporting_polls: List[str]  # poll_ids
    examples: List[str]


class PollDatabase:
    """SQLite-based storage for polling data and events"""
    
    def __init__(self, db_path: str = "poll_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Polls table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                poll_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                demographic_slice TEXT NOT NULL,  -- JSON
                response_data TEXT NOT NULL,      -- JSON
                sample_size INTEGER NOT NULL,
                margin_of_error REAL,
                confidence_level REAL DEFAULT 0.95,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Major events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS major_events (
                event_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                magnitude TEXT NOT NULL,
                duration_days INTEGER,
                end_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Behavioral patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavioral_patterns (
                pattern_id TEXT PRIMARY KEY,
                demographic_profile TEXT NOT NULL,  -- JSON
                event_types TEXT NOT NULL,          -- JSON
                typical_response TEXT NOT NULL,
                confidence REAL NOT NULL,
                supporting_polls TEXT NOT NULL,     -- JSON
                examples TEXT NOT NULL,             -- JSON
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Event-poll relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_poll_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                poll_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,  -- "before", "during", "after"
                days_offset INTEGER,
                FOREIGN KEY (event_id) REFERENCES major_events (event_id),
                FOREIGN KEY (poll_id) REFERENCES polls (poll_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_poll(self, poll: PollRecord):
        """Add a poll record to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO polls 
            (poll_id, source, date, topic, question, demographic_slice, 
             response_data, sample_size, margin_of_error, confidence_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            poll.poll_id, poll.source, poll.date, poll.topic, poll.question,
            json.dumps(poll.demographic_slice), json.dumps(poll.response_data),
            poll.sample_size, poll.margin_of_error, poll.confidence_level
        ))
        
        conn.commit()
        conn.close()
    
    def add_event(self, event: MajorEvent):
        """Add a major event to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO major_events 
            (event_id, name, date, event_type, description, magnitude, duration_days, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_id, event.name, event.date, event.event_type,
            event.description, event.magnitude, event.duration_days, event.end_date
        ))
        
        conn.commit()
        conn.close()
    
    def query_polls(
        self, 
        topic: Optional[str] = None,
        demographic_filters: Optional[Dict[str, Any]] = None,
        date_range: Optional[Tuple[str, str]] = None,
        source: Optional[str] = None
    ) -> List[PollRecord]:
        """Query polls with various filters"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM polls WHERE 1=1"
        params = []
        
        if topic:
            query += " AND topic = ?"
            params.append(topic)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if date_range:
            query += " AND date BETWEEN ? AND ?"
            params.extend(date_range)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        polls = []
        for row in rows:
            poll = PollRecord(
                poll_id=row[0], source=row[1], date=row[2], topic=row[3],
                question=row[4], 
                demographic_slice=json.loads(row[5]),
                response_data=json.loads(row[6]),
                sample_size=row[7], margin_of_error=row[8], confidence_level=row[9]
            )
            
            # Apply demographic filters if provided
            if demographic_filters and not self._matches_demographic_filter(poll, demographic_filters):
                continue
                
            polls.append(poll)
        
        return polls
    
    def _matches_demographic_filter(self, poll: PollRecord, filters: Dict[str, Any]) -> bool:
        """Check if poll matches demographic filters"""
        demo_slice = poll.demographic_slice
        
        for key, value in filters.items():
            if key in demo_slice:
                poll_value = demo_slice[key]
                if isinstance(poll_value, list):
                    if value not in poll_value:
                        return False
                elif poll_value != value and poll_value != "any":
                    return False
        
        return True
    
    def find_events_by_timeframe(self, start_date: str, end_date: str) -> List[MajorEvent]:
        """Find events within a timeframe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM major_events 
            WHERE date BETWEEN ? AND ?
            ORDER BY date
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            MajorEvent(
                event_id=row[0], name=row[1], date=row[2], event_type=row[3],
                description=row[4], magnitude=row[5], duration_days=row[6], end_date=row[7]
            )
            for row in rows
        ]


class PollDataSelector:
    """Intelligent selection of relevant polling data for personas and scenarios"""
    
    def __init__(self, poll_db: PollDatabase):
        self.poll_db = poll_db
        self.topic_keywords = {
            "healthcare": ["health", "medical", "insurance", "medicare", "medicaid", "hospital"],
            "economy": ["economic", "job", "employment", "income", "wage", "inflation", "recession"],
            "politics": ["election", "vote", "candidate", "political", "government", "congress"],
            "education": ["school", "college", "university", "teacher", "student", "education"],
            "technology": ["tech", "digital", "internet", "smartphone", "computer", "AI"],
            "environment": ["climate", "environment", "green", "pollution", "energy", "carbon"],
            "social": ["social", "community", "diversity", "equality", "rights", "justice"]
        }
    
    def select_relevant_polls(
        self, 
        scenario_description: str, 
        persona: PersonaConfig,
        max_polls: int = 5,
        recency_weight: float = 0.3
    ) -> Dict[str, Any]:
        """
        Select most relevant polling data for a persona and scenario
        
        Args:
            scenario_description: Description of the scenario
            persona: The persona configuration
            max_polls: Maximum number of polls to return
            recency_weight: Weight given to more recent polls (0-1)
        
        Returns:
            Dictionary of relevant polling data structured for persona context
        """
        
        # Identify relevant topics
        relevant_topics = self._identify_topics(scenario_description)
        
        # Create demographic filter for persona
        demographic_filter = {
            "age_range": self._get_age_range(persona.age),
            "race_ethnicity": persona.race_ethnicity,
            "education": persona.education,
            "location_type": persona.location_type,
            "income": persona.income
        }
        
        # Find relevant polls
        relevant_polls = []
        for topic in relevant_topics:
            topic_polls = self.poll_db.query_polls(
                topic=topic,
                demographic_filters=demographic_filter
            )
            relevant_polls.extend(topic_polls)
        
        # Score and rank polls
        scored_polls = []
        for poll in relevant_polls:
            score = self._calculate_poll_relevance_score(
                poll, scenario_description, persona, recency_weight
            )
            scored_polls.append((poll, score))
        
        # Sort by score and take top polls
        scored_polls.sort(key=lambda x: x[1], reverse=True)
        top_polls = scored_polls[:max_polls]
        
        # Format for persona context
        return self._format_polls_for_context(top_polls)
    
    def _identify_topics(self, scenario_description: str) -> List[str]:
        """Identify relevant topics from scenario description"""
        description_lower = scenario_description.lower()
        relevant_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                relevant_topics.append(topic)
        
        # Default to politics if no specific topic identified
        if not relevant_topics:
            relevant_topics.append("politics")
        
        return relevant_topics
    
    def _get_age_range(self, age: int) -> str:
        """Convert age to standard demographic age range"""
        if age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 45:
            return "35-44"
        elif age < 55:
            return "45-54"
        elif age < 65:
            return "55-64"
        else:
            return "65+"
    
    def _calculate_poll_relevance_score(
        self, 
        poll: PollRecord, 
        scenario: str, 
        persona: PersonaConfig,
        recency_weight: float
    ) -> float:
        """Calculate relevance score for a poll"""
        
        score = 0.0
        
        # Topic relevance (0-1)
        topic_score = 1.0 if poll.topic in scenario.lower() else 0.5
        score += topic_score * 0.4
        
        # Demographic match (0-1)
        demo_score = self._calculate_demographic_match(poll, persona)
        score += demo_score * 0.4
        
        # Recency (0-1)
        recency_score = self._calculate_recency_score(poll.date)
        score += recency_score * recency_weight
        
        # Sample size quality (0-1)
        quality_score = min(1.0, poll.sample_size / 1000)
        score += quality_score * (1 - recency_weight - 0.8)
        
        return score
    
    def _calculate_demographic_match(self, poll: PollRecord, persona: PersonaConfig) -> float:
        """Calculate how well poll demographics match persona"""
        
        demo_slice = poll.demographic_slice
        matches = 0
        total_checked = 0
        
        persona_demo = {
            "age_range": self._get_age_range(persona.age),
            "race_ethnicity": persona.race_ethnicity,
            "education": persona.education,
            "location_type": persona.location_type,
            "income": persona.income
        }
        
        for key, persona_value in persona_demo.items():
            if key in demo_slice:
                total_checked += 1
                poll_value = demo_slice[key]
                
                if poll_value == "any" or poll_value == persona_value:
                    matches += 1
                elif isinstance(poll_value, list) and persona_value in poll_value:
                    matches += 1
        
        return matches / total_checked if total_checked > 0 else 0.5
    
    def _calculate_recency_score(self, poll_date: str) -> float:
        """Calculate recency score (1.0 = very recent, 0.0 = very old)"""
        try:
            poll_datetime = datetime.fromisoformat(poll_date.replace('Z', '+00:00'))
            now = datetime.now()
            days_old = (now - poll_datetime).days
            
            # Score decreases with age: 1.0 for today, 0.5 for 1 year, 0.0 for 5+ years
            max_age_days = 5 * 365  # 5 years
            score = max(0.0, 1.0 - (days_old / max_age_days))
            return score
            
        except ValueError:
            return 0.5  # Default for unparseable dates
    
    def _format_polls_for_context(self, scored_polls: List[Tuple[PollRecord, float]]) -> Dict[str, Any]:
        """Format selected polls for persona context"""
        
        formatted_data = {}
        
        for i, (poll, score) in enumerate(scored_polls):
            # Extract main response
            main_response = max(poll.response_data.items(), key=lambda x: x[1]) if poll.response_data else ("neutral", 0.5)
            
            poll_key = f"{poll.topic}_{i+1}" if len(scored_polls) > 1 else poll.topic
            
            formatted_data[poll_key] = {
                "position": main_response[0],
                "confidence": main_response[1],
                "source": f"{poll.source} ({poll.date[:4]})",
                "behavior_notes": f"Your demographic shows {main_response[1]:.0%} {main_response[0]} on {poll.topic} issues",
                "sample_size": poll.sample_size,
                "relevance_score": round(score, 2)
            }
        
        return formatted_data
    
    def get_historical_patterns(self, event_type: str, persona_demographics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find historical behavioral patterns for similar events and demographics"""
        
        # For now, return mock patterns - in production would query behavioral_patterns table
        patterns = [
            {
                "event_type": event_type,
                "typical_response": f"Demographic group typically shows increased concern during {event_type} events",
                "confidence": 0.75,
                "historical_examples": ["2008 financial crisis", "COVID-19 pandemic"]
            }
        ]
        
        return patterns


def load_sample_poll_data(poll_db: PollDatabase):
    """Load sample polling data for testing"""
    
    print("📊 Loading sample poll data...")
    
    # Sample major events
    events = [
        MajorEvent(
            event_id="covid_19_pandemic",
            name="COVID-19 Pandemic",
            date="2020-03-11",
            event_type="health",
            description="Global pandemic declaration by WHO",
            magnitude="global",
            duration_days=1095  # 3 years
        ),
        MajorEvent(
            event_id="2008_financial_crisis",
            name="2008 Financial Crisis",
            date="2008-09-15",
            event_type="economic",
            description="Lehman Brothers collapse triggering global financial crisis",
            magnitude="global",
            duration_days=730  # 2 years
        ),
        MajorEvent(
            event_id="2016_election",
            name="2016 Presidential Election",
            date="2016-11-08",
            event_type="political",
            description="Donald Trump elected President",
            magnitude="national"
        )
    ]
    
    for event in events:
        poll_db.add_event(event)
    
    # Sample polls
    polls = [
        PollRecord(
            poll_id="gallup_healthcare_2024_01",
            source="Gallup",
            date="2024-01-15",
            topic="healthcare",
            question="Do you support universal healthcare?",
            demographic_slice={"age_range": "25-34", "education": "college", "race_ethnicity": "hispanic"},
            response_data={"support": 0.73, "oppose": 0.19, "neutral": 0.08},
            sample_size=1200
        ),
        PollRecord(
            poll_id="pew_economy_2024_02",
            source="Pew Research",
            date="2024-02-01",
            topic="economy",
            question="How confident are you in the current economy?",
            demographic_slice={"age_range": "35-44", "education": "college", "location_type": "suburban"},
            response_data={"confident": 0.45, "concerned": 0.41, "neutral": 0.14},
            sample_size=2500
        ),
        PollRecord(
            poll_id="cnn_politics_2024_03",
            source="CNN",
            date="2024-03-01",
            topic="politics",
            question="Do you approve of the current administration?",
            demographic_slice={"age_range": "45-54", "race_ethnicity": "white", "location_type": "rural"},
            response_data={"approve": 0.38, "disapprove": 0.54, "neutral": 0.08},
            sample_size=1800
        )
    ]
    
    for poll in polls:
        poll_db.add_poll(poll)
    
    print(f"✅ Loaded {len(events)} events and {len(polls)} polls")


def test_poll_data_manager():
    """Test the poll data management system"""
    
    print("🧪 TESTING POLL DATA MANAGER")
    print("=" * 80)
    
    # Initialize database
    poll_db = PollDatabase("test_poll_data.db")
    load_sample_poll_data(poll_db)
    
    # Test poll selector
    selector = PollDataSelector(poll_db)
    
    # Test persona
    test_persona = PersonaConfig(
        name="Maria Rodriguez", age=34, race_ethnicity="hispanic", gender="female",
        education="college", location_type="suburban", income="50k_75k",
        occupation="teacher"
    )
    
    # Test scenario
    scenario_description = "Testing support for universal healthcare policy reform"
    
    # Select relevant polls
    relevant_polls = selector.select_relevant_polls(scenario_description, test_persona)
    
    print("🎯 RELEVANT POLLS SELECTED:")
    print("-" * 50)
    for topic, poll_data in relevant_polls.items():
        print(f"Topic: {topic}")
        print(f"   Position: {poll_data['position']}")
        print(f"   Confidence: {poll_data['confidence']:.1%}")
        print(f"   Source: {poll_data['source']}")
        print(f"   Relevance Score: {poll_data['relevance_score']}")
        print()
    
    # Test historical patterns
    patterns = selector.get_historical_patterns("health", {"age": 34, "education": "college"})
    
    print("📚 HISTORICAL PATTERNS:")
    print("-" * 50)
    for pattern in patterns:
        print(f"Event Type: {pattern['event_type']}")
        print(f"Typical Response: {pattern['typical_response']}")
        print(f"Confidence: {pattern['confidence']:.1%}")
        print()
    
    return poll_db, selector


if __name__ == "__main__":
    test_poll_data_manager()