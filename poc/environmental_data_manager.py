"""
Environmental Data Manager

Manages collection and integration of realistic demographic and environmental data
for environmentally-aware persona modeling. Uses available public data sources
like US Census, American Community Survey, and other demographic databases.

Key Data Sources:
1. US Census Bureau - demographic composition by geographic area
2. American Community Survey (ACS) - detailed demographic and economic data
3. Bureau of Labor Statistics - unemployment and economic indicators
4. Pew Research - political and religious composition data
5. FBI Crime Statistics - safety and social cohesion indicators
"""

import sqlite3
import json
import csv
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import os
import time
from environmentally_aware_persona import EnvironmentalContext


@dataclass
class GeographicArea:
    """Represents a geographic area with unique identifiers"""
    area_id: str
    name: str
    area_type: str  # city, county, state, msa, zip
    state: str
    region: str
    parent_area_id: Optional[str] = None
    population: Optional[int] = None
    area_sq_miles: Optional[float] = None


@dataclass
class DemographicDataPoint:
    """Single demographic data point"""
    area_id: str
    data_source: str
    data_type: str  # race, age, education, income, etc.
    category: str
    value: float
    value_type: str  # percentage, count, median, etc.
    year: int
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class PoliticalDataPoint:
    """Political/voting data for an area"""
    area_id: str
    election_year: int
    election_type: str  # presidential, gubernatorial, local
    candidate_party: str
    vote_percentage: float
    turnout_rate: float
    data_source: str


class EnvironmentalDataManager:
    """Manages collection and storage of environmental context data"""
    
    def __init__(self, db_path: str = "environmental_data.db"):
        self.db_path = db_path
        self.init_database()
        
        # API endpoints (would need API keys for production)
        self.census_api_base = "https://api.census.gov/data"
        self.bls_api_base = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        
        # Standard geographic mappings
        self.state_codes = self._load_state_codes()
        self.region_mapping = self._load_region_mapping()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Geographic areas table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS geographic_areas (
                    area_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    area_type TEXT NOT NULL,
                    state TEXT NOT NULL,
                    region TEXT NOT NULL,
                    parent_area_id TEXT,
                    population INTEGER,
                    area_sq_miles REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Demographic data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS demographic_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_id TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value REAL NOT NULL,
                    value_type TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    confidence_low REAL,
                    confidence_high REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (area_id) REFERENCES geographic_areas (area_id)
                )
            ''')
            
            # Political data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS political_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_id TEXT NOT NULL,
                    election_year INTEGER NOT NULL,
                    election_type TEXT NOT NULL,
                    candidate_party TEXT NOT NULL,
                    vote_percentage REAL NOT NULL,
                    turnout_rate REAL,
                    data_source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (area_id) REFERENCES geographic_areas (area_id)
                )
            ''')
            
            # Economic indicators table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS economic_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_id TEXT NOT NULL,
                    indicator_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    data_source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (area_id) REFERENCES geographic_areas (area_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_demo_area_type ON demographic_data (area_id, data_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_political_area_year ON political_data (area_id, election_year)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_economic_area_type ON economic_data (area_id, indicator_type)')
            
            conn.commit()
    
    def add_geographic_area(self, area: GeographicArea):
        """Add a geographic area to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO geographic_areas 
                (area_id, name, area_type, state, region, parent_area_id, population, area_sq_miles)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (area.area_id, area.name, area.area_type, area.state, area.region,
                  area.parent_area_id, area.population, area.area_sq_miles))
            conn.commit()
    
    def add_demographic_data(self, data_point: DemographicDataPoint):
        """Add demographic data point"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            confidence_low = data_point.confidence_interval[0] if data_point.confidence_interval else None
            confidence_high = data_point.confidence_interval[1] if data_point.confidence_interval else None
            
            cursor.execute('''
                INSERT INTO demographic_data 
                (area_id, data_source, data_type, category, value, value_type, year, confidence_low, confidence_high)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data_point.area_id, data_point.data_source, data_point.data_type,
                  data_point.category, data_point.value, data_point.value_type,
                  data_point.year, confidence_low, confidence_high))
            conn.commit()
    
    def load_sample_environmental_data(self):
        """Load sample environmental data for major US cities"""
        
        print("Loading sample environmental data for major US cities...")
        
        # Major cities with realistic demographic data
        cities_data = [
            {
                "area": GeographicArea(
                    area_id="dallas_tx_city",
                    name="Dallas",
                    area_type="city",
                    state="TX",
                    region="South",
                    population=1304379
                ),
                "demographics": {
                    "race": {"White": 29.1, "Hispanic": 41.7, "Black": 24.3, "Asian": 3.8, "Other": 1.1},
                    "age": {"18-29": 22.5, "30-44": 27.8, "45-64": 32.1, "65+": 17.6},
                    "education": {"High School": 35.2, "Some College": 23.1, "Bachelor's": 25.4, "Graduate": 16.3},
                    "income": {"Under 50k": 45.2, "50k-100k": 34.7, "Over 100k": 20.1}
                },
                "political": {"Republican": 35.2, "Democratic": 60.8, "Other": 4.0},
                "economic": {"unemployment_rate": 6.1, "median_income": 54747}
            },
            {
                "area": GeographicArea(
                    area_id="detroit_mi_city",
                    name="Detroit",
                    area_type="city",
                    state="MI",
                    region="Midwest",
                    population=670031
                ),
                "demographics": {
                    "race": {"White": 14.7, "Hispanic": 6.8, "Black": 78.3, "Asian": 1.1, "Other": 1.1},
                    "age": {"18-29": 19.8, "30-44": 24.7, "45-64": 35.2, "65+": 20.3},
                    "education": {"High School": 44.8, "Some College": 25.2, "Bachelor's": 20.1, "Graduate": 9.9},
                    "income": {"Under 50k": 64.7, "50k-100k": 25.3, "Over 100k": 10.0}
                },
                "political": {"Republican": 15.2, "Democratic": 82.1, "Other": 2.7},
                "economic": {"unemployment_rate": 11.8, "median_income": 34762}
            },
            {
                "area": GeographicArea(
                    area_id="minneapolis_mn_city",
                    name="Minneapolis",
                    area_type="city",
                    state="MN",
                    region="Midwest",
                    population=429954
                ),
                "demographics": {
                    "race": {"White": 63.8, "Hispanic": 10.5, "Black": 19.4, "Asian": 5.6, "Other": 0.7},
                    "age": {"18-29": 28.1, "30-44": 26.3, "45-64": 29.2, "65+": 16.4},
                    "education": {"High School": 22.1, "Some College": 20.3, "Bachelor's": 35.2, "Graduate": 22.4},
                    "income": {"Under 50k": 38.7, "50k-100k": 35.8, "Over 100k": 25.5}
                },
                "political": {"Republican": 25.8, "Democratic": 70.2, "Other": 4.0},
                "economic": {"unemployment_rate": 4.2, "median_income": 70099}
            },
            {
                "area": GeographicArea(
                    area_id="phoenix_az_city",
                    name="Phoenix",
                    area_type="city",
                    state="AZ",
                    region="West",
                    population=1680992
                ),
                "demographics": {
                    "race": {"White": 46.5, "Hispanic": 42.6, "Black": 6.5, "Asian": 3.2, "Other": 1.2},
                    "age": {"18-29": 23.4, "30-44": 26.8, "45-64": 32.5, "65+": 17.3},
                    "education": {"High School": 38.9, "Some College": 26.7, "Bachelor's": 23.1, "Graduate": 11.3},
                    "income": {"Under 50k": 42.1, "50k-100k": 36.2, "Over 100k": 21.7}
                },
                "political": {"Republican": 48.3, "Democratic": 47.2, "Other": 4.5},
                "economic": {"unemployment_rate": 5.8, "median_income": 62983}
            },
            {
                "area": GeographicArea(
                    area_id="atlanta_ga_city",
                    name="Atlanta",
                    area_type="city",
                    state="GA",
                    region="South",
                    population=498715
                ),
                "demographics": {
                    "race": {"White": 38.4, "Hispanic": 4.6, "Black": 51.0, "Asian": 4.4, "Other": 1.6},
                    "age": {"18-29": 27.3, "30-44": 30.1, "45-64": 28.9, "65+": 13.7},
                    "education": {"High School": 28.7, "Some College": 22.1, "Bachelor's": 30.8, "Graduate": 18.4},
                    "income": {"Under 50k": 49.2, "50k-100k": 28.7, "Over 100k": 22.1}
                },
                "political": {"Republican": 18.3, "Democratic": 79.2, "Other": 2.5},
                "economic": {"unemployment_rate": 7.3, "median_income": 55379}
            }
        ]
        
        # Load data into database
        for city_data in cities_data:
            # Add geographic area
            self.add_geographic_area(city_data["area"])
            
            # Add demographic data
            area_id = city_data["area"].area_id
            year = 2022  # Most recent available
            
            # Racial demographics
            for race, percentage in city_data["demographics"]["race"].items():
                self.add_demographic_data(DemographicDataPoint(
                    area_id=area_id,
                    data_source="US Census ACS",
                    data_type="race",
                    category=race.lower(),
                    value=percentage / 100,  # Convert to decimal
                    value_type="percentage",
                    year=year
                ))
            
            # Age demographics
            for age_group, percentage in city_data["demographics"]["age"].items():
                age_category = age_group.replace("-", "_").replace("+", "_plus").lower()
                self.add_demographic_data(DemographicDataPoint(
                    area_id=area_id,
                    data_source="US Census ACS",
                    data_type="age",
                    category=age_category,
                    value=percentage / 100,
                    value_type="percentage",
                    year=year
                ))
            
            # Education demographics
            for education, percentage in city_data["demographics"]["education"].items():
                edu_category = education.lower().replace(" ", "_").replace("'s", "s")
                self.add_demographic_data(DemographicDataPoint(
                    area_id=area_id,
                    data_source="US Census ACS",
                    data_type="education",
                    category=edu_category,
                    value=percentage / 100,
                    value_type="percentage",
                    year=year
                ))
            
            # Income demographics
            for income_bracket, percentage in city_data["demographics"]["income"].items():
                income_category = income_bracket.lower().replace(" ", "_").replace("-", "_")
                self.add_demographic_data(DemographicDataPoint(
                    area_id=area_id,
                    data_source="US Census ACS",
                    data_type="income",
                    category=income_category,
                    value=percentage / 100,
                    value_type="percentage",
                    year=year
                ))
            
            # Political data (from recent elections)
            for party, percentage in city_data["political"].items():
                self.add_political_data(PoliticalDataPoint(
                    area_id=area_id,
                    election_year=2020,
                    election_type="presidential",
                    candidate_party=party.lower(),
                    vote_percentage=percentage / 100,
                    turnout_rate=0.73,  # Average turnout
                    data_source="Election Results"
                ))
            
            # Economic data
            economic = city_data["economic"]
            self.add_economic_data(area_id, "unemployment_rate", economic["unemployment_rate"], year, "BLS")
            self.add_economic_data(area_id, "median_income", economic["median_income"], year, "US Census ACS")
        
        print(f"✅ Loaded environmental data for {len(cities_data)} cities")
    
    def add_political_data(self, data_point: PoliticalDataPoint):
        """Add political data point"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO political_data 
                (area_id, election_year, election_type, candidate_party, vote_percentage, turnout_rate, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data_point.area_id, data_point.election_year, data_point.election_type,
                  data_point.candidate_party, data_point.vote_percentage,
                  data_point.turnout_rate, data_point.data_source))
            conn.commit()
    
    def add_economic_data(self, area_id: str, indicator_type: str, value: float, year: int, data_source: str, month: int = None):
        """Add economic indicator data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO economic_data 
                (area_id, indicator_type, value, year, month, data_source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (area_id, indicator_type, value, year, month, data_source))
            conn.commit()
    
    def get_environmental_context(self, area_id: str) -> Optional[EnvironmentalContext]:
        """Build EnvironmentalContext from database data"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get geographic info
            cursor.execute('SELECT * FROM geographic_areas WHERE area_id = ?', (area_id,))
            area_row = cursor.fetchone()
            if not area_row:
                return None
            
            area_cols = [desc[0] for desc in cursor.description]
            area_data = dict(zip(area_cols, area_row))
            
            # Get demographic data
            cursor.execute('''
                SELECT data_type, category, value FROM demographic_data 
                WHERE area_id = ? AND year = (SELECT MAX(year) FROM demographic_data WHERE area_id = ?)
            ''', (area_id, area_id))
            
            demographic_rows = cursor.fetchall()
            
            # Organize demographic data
            racial_composition = {}
            age_distribution = {}
            education_levels = {}
            income_distribution = {}
            
            for data_type, category, value in demographic_rows:
                if data_type == "race":
                    racial_composition[category] = value
                elif data_type == "age":
                    age_distribution[category] = value
                elif data_type == "education":
                    education_levels[category] = value
                elif data_type == "income":
                    income_distribution[category] = value
            
            # Get political data
            cursor.execute('''
                SELECT candidate_party, vote_percentage FROM political_data 
                WHERE area_id = ? AND election_year = (SELECT MAX(election_year) FROM political_data WHERE area_id = ?)
            ''', (area_id, area_id))
            
            political_rows = cursor.fetchall()
            political_lean = "moderate"  # Default
            political_strength = 0.5
            
            if political_rows:
                # Determine political lean from vote percentages
                party_votes = {party: percentage for party, percentage in political_rows}
                if "democratic" in party_votes and "republican" in party_votes:
                    dem_vote = party_votes.get("democratic", 0)
                    rep_vote = party_votes.get("republican", 0)
                    
                    if dem_vote > rep_vote + 0.15:
                        political_lean = "liberal"
                        political_strength = min(1.0, (dem_vote - rep_vote) * 2)
                    elif rep_vote > dem_vote + 0.15:
                        political_lean = "conservative"
                        political_strength = min(1.0, (rep_vote - dem_vote) * 2)
                    else:
                        political_lean = "moderate"
                        political_strength = 0.3  # Less political intensity in swing areas
            
            # Get economic data
            cursor.execute('''
                SELECT indicator_type, value FROM economic_data 
                WHERE area_id = ? AND year = (SELECT MAX(year) FROM economic_data WHERE area_id = ?)
            ''', (area_id, area_id))
            
            economic_rows = cursor.fetchall()
            economic_data = {indicator: value for indicator, value in economic_rows}
            
            # Calculate derived metrics
            cultural_diversity = 1.0 - max(racial_composition.values()) if racial_composition else 0.5
            social_cohesion = 0.7 - (cultural_diversity * 0.3)  # Simplified heuristic
            
            # Determine economic trend (simplified)
            unemployment_rate = economic_data.get("unemployment_rate", 5.0)
            if unemployment_rate < 4.0:
                economic_trend = "growing"
            elif unemployment_rate > 8.0:
                economic_trend = "declining"
            else:
                economic_trend = "stable"
            
            # Build EnvironmentalContext
            context = EnvironmentalContext(
                location_name=area_data["name"],
                location_type=area_data["area_type"],
                state=area_data["state"],
                region=area_data["region"],
                racial_composition=racial_composition,
                age_distribution=age_distribution,
                education_levels=education_levels,
                income_distribution=income_distribution,
                political_lean=political_lean,
                political_strength=political_strength,
                religious_composition={"christian": 0.7, "other": 0.3},  # Default values
                unemployment_rate=unemployment_rate / 100,  # Convert to decimal
                median_income=economic_data.get("median_income", 50000),
                economic_trend=economic_trend,
                social_cohesion=social_cohesion,
                cultural_diversity=cultural_diversity,
                change_rate=0.5  # Default moderate change rate
            )
            
            return context
    
    def list_available_areas(self) -> List[GeographicArea]:
        """Get list of all available geographic areas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM geographic_areas ORDER BY name')
            rows = cursor.fetchall()
            
            cols = [desc[0] for desc in cursor.description]
            areas = []
            for row in rows:
                area_data = dict(zip(cols, row))
                areas.append(GeographicArea(
                    area_id=area_data["area_id"],
                    name=area_data["name"],
                    area_type=area_data["area_type"],
                    state=area_data["state"],
                    region=area_data["region"],
                    parent_area_id=area_data["parent_area_id"],
                    population=area_data["population"],
                    area_sq_miles=area_data["area_sq_miles"]
                ))
            
            return areas
    
    def _load_state_codes(self) -> Dict[str, str]:
        """Load state name to code mappings"""
        return {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
            "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
            "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
            "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
            "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
            "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
            "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
            "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
            "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
            "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
            "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
            "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
            "Wisconsin": "WI", "Wyoming": "WY"
        }
    
    def _load_region_mapping(self) -> Dict[str, str]:
        """Load state to region mappings"""
        return {
            "CT": "Northeast", "ME": "Northeast", "MA": "Northeast", "NH": "Northeast",
            "RI": "Northeast", "VT": "Northeast", "NJ": "Northeast", "NY": "Northeast", "PA": "Northeast",
            "IL": "Midwest", "IN": "Midwest", "MI": "Midwest", "OH": "Midwest", "WI": "Midwest",
            "IA": "Midwest", "KS": "Midwest", "MN": "Midwest", "MO": "Midwest", "NE": "Midwest",
            "ND": "Midwest", "SD": "Midwest",
            "DE": "South", "FL": "South", "GA": "South", "MD": "South", "NC": "South",
            "SC": "South", "VA": "South", "WV": "South", "AL": "South", "KY": "South",
            "MS": "South", "TN": "South", "AR": "South", "LA": "South", "OK": "South", "TX": "South",
            "AZ": "West", "CO": "West", "ID": "West", "MT": "West", "NV": "West",
            "NM": "West", "UT": "West", "WY": "West", "AK": "West", "CA": "West",
            "HI": "West", "OR": "West", "WA": "West"
        }
    
    def generate_report(self) -> str:
        """Generate a report of available environmental data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count areas by type
            cursor.execute('SELECT area_type, COUNT(*) FROM geographic_areas GROUP BY area_type')
            area_counts = cursor.fetchall()
            
            # Count data points by source
            cursor.execute('SELECT data_source, COUNT(*) FROM demographic_data GROUP BY data_source')
            demo_counts = cursor.fetchall()
            
            # Get data coverage
            cursor.execute('SELECT COUNT(DISTINCT area_id) FROM demographic_data')
            areas_with_demo_data = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT area_id) FROM political_data')
            areas_with_political_data = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT area_id) FROM economic_data')
            areas_with_economic_data = cursor.fetchone()[0]
            
            report_lines = [
                "📊 ENVIRONMENTAL DATA MANAGER REPORT",
                "=" * 60,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "",
                "🗺️  GEOGRAPHIC COVERAGE:",
            ]
            
            for area_type, count in area_counts:
                report_lines.append(f"   • {area_type.title()}s: {count}")
            
            report_lines.extend([
                "",
                "📈 DATA COVERAGE:",
                f"   • Areas with demographic data: {areas_with_demo_data}",
                f"   • Areas with political data: {areas_with_political_data}",
                f"   • Areas with economic data: {areas_with_economic_data}",
                "",
                "📚 DATA SOURCES:"
            ])
            
            for source, count in demo_counts:
                report_lines.append(f"   • {source}: {count} data points")
            
            report_lines.extend([
                "",
                "🎯 CAPABILITIES:",
                "• Generate EnvironmentalContext for any loaded area",
                "• Support for demographic, political, and economic data",
                "• Realistic data based on US Census and election results",
                "• Extensible to add new data sources and metrics"
            ])
            
            return "\n".join(report_lines)


def demonstrate_environmental_data_integration():
    """Demonstrate environmental data integration with realistic data"""
    
    print("🗺️ ENVIRONMENTAL DATA INTEGRATION DEMONSTRATION")
    print("=" * 80)
    
    # Initialize data manager
    data_manager = EnvironmentalDataManager("demo_environmental_data.db")
    
    # Load sample data
    data_manager.load_sample_environmental_data()
    
    # List available areas
    areas = data_manager.list_available_areas()
    print(f"\n📍 Available Areas: {len(areas)}")
    for area in areas:
        print(f"   • {area.name}, {area.state} ({area.area_type}) - Pop: {area.population:,}")
    
    # Generate environmental contexts for sample areas
    print("\n🌍 ENVIRONMENTAL CONTEXTS:")
    print("-" * 60)
    
    sample_areas = ["dallas_tx_city", "detroit_mi_city", "minneapolis_mn_city"]
    
    for area_id in sample_areas:
        context = data_manager.get_environmental_context(area_id)
        if context:
            print(f"\n📍 {context.location_name}, {context.state}")
            print(f"   Political Lean: {context.political_lean} (strength: {context.political_strength:.1f})")
            print(f"   Cultural Diversity: {context.cultural_diversity:.1f}")
            print(f"   Social Cohesion: {context.social_cohesion:.1f}")
            print(f"   Unemployment: {context.unemployment_rate:.1%}")
            print(f"   Median Income: ${context.median_income:,}")
            
            # Show top demographics
            top_race = max(context.racial_composition.items(), key=lambda x: x[1])
            print(f"   Largest Racial Group: {top_race[0].title()} ({top_race[1]:.1%})")
            
            top_education = max(context.education_levels.items(), key=lambda x: x[1])
            print(f"   Most Common Education: {top_education[0].replace('_', ' ').title()} ({top_education[1]:.1%})")
    
    # Generate system report
    print("\n\n")
    print(data_manager.generate_report())
    
    print("\n✅ Environmental data integration demonstration complete!")
    print("The system can now provide realistic environmental context for persona modeling.")
    
    return data_manager


if __name__ == "__main__":
    demonstrate_environmental_data_integration()