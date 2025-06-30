#!/usr/bin/env python3
"""
Simple Vector Image Matcher - MVP Implementation
===============================================

Simple vector-based image matching for pre-generated persona images.
Uses basic similarity scoring without external vector database dependencies.
"""

import json
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from persona_config import PersonaConfig

@dataclass
class PersonaImageRecord:
    """A pre-generated image record with characteristics"""
    image_id: str
    image_url: str
    age: int
    gender: str
    race_ethnicity: str
    education: str
    location_type: str
    income: str
    tags: List[str]
    description: str

class SimplePersonaImageMatcher:
    """
    Simple vector matching using weighted similarity scoring.
    No external dependencies - pure Python implementation.
    """
    
    def __init__(self, image_database_path: str = None):
        self.image_records: List[PersonaImageRecord] = []
        self.similarity_weights = {
            "age": 0.15,
            "gender": 0.25,
            "race_ethnicity": 0.30,
            "education": 0.10,
            "location_type": 0.10,
            "income": 0.10
        }
        
        # Load or create sample database
        if image_database_path and os.path.exists(image_database_path):
            self.load_database(image_database_path)
        else:
            self._create_sample_database()
    
    def _create_sample_database(self):
        """Create sample pre-generated images for MVP testing"""
        sample_images = [
            {
                "image_id": "img_001",
                "image_url": "https://example.com/personas/young_hispanic_female_urban.jpg",
                "age": 25,
                "gender": "female",
                "race_ethnicity": "hispanic",
                "education": "college",
                "location_type": "urban",
                "income": "40k_50k",
                "tags": ["professional", "young", "city"],
                "description": "Young Hispanic professional woman in urban setting"
            },
            {
                "image_id": "img_002", 
                "image_url": "https://example.com/personas/middle_white_male_suburban.jpg",
                "age": 45,
                "gender": "male",
                "race_ethnicity": "white",
                "education": "graduate",
                "location_type": "suburban",
                "income": "75k_100k",
                "tags": ["executive", "family", "suburban"],
                "description": "Middle-aged white male executive in suburban environment"
            },
            {
                "image_id": "img_003",
                "image_url": "https://example.com/personas/young_black_female_urban.jpg", 
                "age": 28,
                "gender": "female",
                "race_ethnicity": "black",
                "education": "college",
                "location_type": "urban",
                "income": "50k_75k",
                "tags": ["creative", "urban", "professional"],
                "description": "Young Black professional woman in creative field"
            },
            {
                "image_id": "img_004",
                "image_url": "https://example.com/personas/senior_white_female_rural.jpg",
                "age": 62,
                "gender": "female", 
                "race_ethnicity": "white",
                "education": "high_school",
                "location_type": "rural",
                "income": "25k_40k",
                "tags": ["retired", "rural", "traditional"],
                "description": "Senior white woman in rural community setting"
            },
            {
                "image_id": "img_005",
                "image_url": "https://example.com/personas/young_asian_male_urban.jpg",
                "age": 30,
                "gender": "male",
                "race_ethnicity": "asian", 
                "education": "graduate",
                "location_type": "urban",
                "income": "over_100k",
                "tags": ["tech", "professional", "urban"],
                "description": "Young Asian male tech professional in urban setting"
            },
            {
                "image_id": "img_006",
                "image_url": "https://example.com/personas/middle_hispanic_male_suburban.jpg",
                "age": 38,
                "gender": "male",
                "race_ethnicity": "hispanic",
                "education": "college", 
                "location_type": "suburban",
                "income": "50k_75k",
                "tags": ["family", "blue_collar", "suburban"],
                "description": "Middle-aged Hispanic male with family in suburbs"
            },
            {
                "image_id": "img_007",
                "image_url": "https://example.com/personas/young_white_female_rural.jpg",
                "age": 24,
                "gender": "female",
                "race_ethnicity": "white",
                "education": "high_school",
                "location_type": "rural", 
                "income": "under_25k",
                "tags": ["student", "rural", "working"],
                "description": "Young white woman in rural area, working/studying"
            },
            {
                "image_id": "img_008",
                "image_url": "https://example.com/personas/middle_black_male_urban.jpg",
                "age": 42,
                "gender": "male",
                "race_ethnicity": "black",
                "education": "college",
                "location_type": "urban",
                "income": "75k_100k", 
                "tags": ["management", "urban", "professional"],
                "description": "Middle-aged Black male in management role"
            }
        ]
        
        # Convert to PersonaImageRecord objects
        for img_data in sample_images:
            record = PersonaImageRecord(**img_data)
            self.image_records.append(record)
        
        print(f"📸 Created sample database with {len(self.image_records)} pre-generated persona images")
    
    def calculate_similarity(self, persona_config: PersonaConfig, image_record: PersonaImageRecord) -> float:
        """
        Calculate similarity score between persona and image record.
        Returns score from 0.0 (no match) to 1.0 (perfect match).
        """
        total_score = 0.0
        
        # Age similarity (within 10 years = good match)
        age_diff = abs(persona_config.age - image_record.age)
        age_score = max(0, 1.0 - (age_diff / 20.0))  # Linear falloff over 20 years
        total_score += age_score * self.similarity_weights["age"]
        
        # Exact matches for categorical features
        if persona_config.gender.lower() == image_record.gender.lower():
            total_score += self.similarity_weights["gender"]
        
        if persona_config.race_ethnicity.lower() == image_record.race_ethnicity.lower():
            total_score += self.similarity_weights["race_ethnicity"]
        
        if persona_config.education.lower() == image_record.education.lower():
            total_score += self.similarity_weights["education"]
            
        if persona_config.location_type.lower() == image_record.location_type.lower():
            total_score += self.similarity_weights["location_type"]
            
        if persona_config.income.lower() == image_record.income.lower():
            total_score += self.similarity_weights["income"]
        
        return min(1.0, total_score)  # Cap at 1.0
    
    def find_best_match(self, persona_config: PersonaConfig, min_similarity: float = 0.5) -> Dict[str, Any]:
        """
        Find the best matching pre-generated image for a persona.
        
        Args:
            persona_config: The persona to match
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            Dict with match results or None if no good match
        """
        if not self.image_records:
            return {
                "success": False,
                "reason": "No images in database"
            }
        
        # Calculate similarity for all images
        matches = []
        for record in self.image_records:
            similarity = self.calculate_similarity(persona_config, record)
            matches.append((similarity, record))
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x[0], reverse=True)
        
        best_similarity, best_record = matches[0]
        
        if best_similarity < min_similarity:
            return {
                "success": False,
                "reason": f"Best match similarity {best_similarity:.2f} below threshold {min_similarity}",
                "best_similarity": best_similarity,
                "alternatives": [
                    {"similarity": sim, "description": rec.description} 
                    for sim, rec in matches[:3]
                ]
            }
        
        return {
            "success": True,
            "image_url": best_record.image_url,
            "image_id": best_record.image_id,
            "similarity_score": best_similarity,
            "description": best_record.description,
            "method": "pre_generated_vector_match",
            "cost": 0.0,
            "time_taken": 0.05,  # Nearly instant
            "match_details": {
                "age_match": abs(persona_config.age - best_record.age) <= 10,
                "gender_match": persona_config.gender.lower() == best_record.gender.lower(),
                "race_match": persona_config.race_ethnicity.lower() == best_record.race_ethnicity.lower(),
                "education_match": persona_config.education.lower() == best_record.education.lower()
            }
        }
    
    def get_top_matches(self, persona_config: PersonaConfig, top_k: int = 3) -> List[Dict[str, Any]]:
        """Get top K matching images with similarity scores"""
        matches = []
        for record in self.image_records:
            similarity = self.calculate_similarity(persona_config, record)
            matches.append({
                "similarity_score": similarity,
                "image_url": record.image_url,
                "image_id": record.image_id,
                "description": record.description,
                "demographics": {
                    "age": record.age,
                    "gender": record.gender,
                    "race_ethnicity": record.race_ethnicity,
                    "education": record.education,
                    "location_type": record.location_type,
                    "income": record.income
                }
            })
        
        # Sort and return top K
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:top_k]
    
    def add_image_record(self, record: PersonaImageRecord):
        """Add a new pre-generated image to the database"""
        self.image_records.append(record)
    
    def save_database(self, file_path: str):
        """Save image database to JSON file"""
        data = []
        for record in self.image_records:
            data.append({
                "image_id": record.image_id,
                "image_url": record.image_url,
                "age": record.age,
                "gender": record.gender,
                "race_ethnicity": record.race_ethnicity,
                "education": record.education,
                "location_type": record.location_type,
                "income": record.income,
                "tags": record.tags,
                "description": record.description
            })
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(data)} image records to {file_path}")
    
    def load_database(self, file_path: str):
        """Load image database from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.image_records = []
        for item in data:
            record = PersonaImageRecord(**item)
            self.image_records.append(record)
        
        print(f"📁 Loaded {len(self.image_records)} image records from {file_path}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the image database"""
        if not self.image_records:
            return {"total_images": 0}
        
        stats = {
            "total_images": len(self.image_records),
            "age_range": {
                "min": min(r.age for r in self.image_records),
                "max": max(r.age for r in self.image_records),
                "avg": sum(r.age for r in self.image_records) / len(self.image_records)
            },
            "gender_distribution": {},
            "race_distribution": {},
            "education_distribution": {},
            "location_distribution": {}
        }
        
        # Count distributions
        for record in self.image_records:
            # Gender
            gender = record.gender
            stats["gender_distribution"][gender] = stats["gender_distribution"].get(gender, 0) + 1
            
            # Race
            race = record.race_ethnicity
            stats["race_distribution"][race] = stats["race_distribution"].get(race, 0) + 1
            
            # Education
            edu = record.education
            stats["education_distribution"][edu] = stats["education_distribution"].get(edu, 0) + 1
            
            # Location
            loc = record.location_type
            stats["location_distribution"][loc] = stats["location_distribution"].get(loc, 0) + 1
        
        return stats


def test_image_matching():
    """Test the image matching system"""
    print("🎯 Testing Simple Vector Image Matching")
    print("=" * 50)
    
    # Create matcher with sample database
    matcher = SimplePersonaImageMatcher()
    
    # Print database stats
    stats = matcher.get_database_stats()
    print(f"📊 Database: {stats['total_images']} images")
    print(f"   Age range: {stats['age_range']['min']}-{stats['age_range']['max']} (avg: {stats['age_range']['avg']:.1f})")
    print(f"   Genders: {list(stats['gender_distribution'].keys())}")
    print(f"   Races: {list(stats['race_distribution'].keys())}")
    print()
    
    # Test scenarios
    test_personas = [
        PersonaConfig(
            name="Maria Lopez",
            age=26,
            race_ethnicity="hispanic", 
            gender="female",
            education="college",
            location_type="urban",
            income="40k_50k"
        ),
        PersonaConfig(
            name="John Smith",
            age=44,
            race_ethnicity="white",
            gender="male", 
            education="graduate",
            location_type="suburban",
            income="75k_100k"
        ),
        PersonaConfig(
            name="Sarah Johnson",
            age=70,
            race_ethnicity="white",
            gender="female",
            education="high_school", 
            location_type="rural",
            income="under_25k"
        )
    ]
    
    for i, persona in enumerate(test_personas, 1):
        print(f"🔍 Test {i}: Matching {persona.name}")
        print(f"   Looking for: {persona.age}yo {persona.race_ethnicity} {persona.gender}, {persona.education}, {persona.location_type}")
        
        # Find best match
        result = matcher.find_best_match(persona, min_similarity=0.3)
        
        if result["success"]:
            print(f"   ✅ Found match: {result['description']}")
            print(f"   📸 Image: {result['image_id']}")
            print(f"   🎯 Similarity: {result['similarity_score']:.2f}")
            print(f"   💰 Cost: ${result['cost']:.3f} (vs $0.020 for generation)")
            print(f"   ⚡ Time: {result['time_taken']}s (vs 3-5s for generation)")
            
            details = result["match_details"]
            matches = []
            if details["age_match"]: matches.append("age")
            if details["gender_match"]: matches.append("gender") 
            if details["race_match"]: matches.append("race")
            if details["education_match"]: matches.append("education")
            print(f"   ✓ Exact matches: {', '.join(matches)}")
        else:
            print(f"   ❌ No suitable match: {result['reason']}")
            if "alternatives" in result:
                print(f"   💡 Best alternatives:")
                for alt in result["alternatives"]:
                    print(f"      - {alt['description']} (similarity: {alt['similarity']:.2f})")
        
        print()


if __name__ == "__main__":
    test_image_matching()