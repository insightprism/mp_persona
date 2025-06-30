"""
Persona Configuration Data Classes
"""
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class PersonaConfig:
    """Demographics and characteristics for persona"""
    # Required demographics
    name: str                    # e.g., "Maria Rodriguez"
    age: int                     # 18-85
    race_ethnicity: str          # "white", "black", "hispanic", "asian", "mixed", "other"
    gender: str                  # "male", "female", "non_binary"
    education: str               # "no_hs", "high_school", "some_college", "college", "graduate"
    location_type: str           # "urban", "suburban", "rural"
    income: str                  # "under_30k", "30k_50k", "50k_75k", "75k_100k", "over_100k"
    
    # Optional demographics
    religion: Optional[str] = None
    marital_status: Optional[str] = None
    children: Optional[int] = 0
    occupation: Optional[str] = None
    state: Optional[str] = None
    
    # Behavioral characteristics (for enhanced prediction accuracy)
    media_consumption: Optional[str] = None        # "fox_news", "npr", "social_media", "local_news", "none"
    social_circle: Optional[str] = None            # "tight_family", "diverse_friends", "professional_network", "online_community"
    risk_tolerance: Optional[str] = None           # "risk_averse", "moderate", "risk_taking"
    change_orientation: Optional[str] = None       # "traditional", "adaptive", "early_adopter"
    spending_style: Optional[str] = None           # "saver", "budgeter", "spender", "investor"
    brand_loyalty: Optional[str] = None            # "loyal", "price_focused", "variety_seeker", "quality_focused"
    civic_engagement: Optional[str] = None         # "highly_engaged", "occasional_voter", "politically_disengaged"
    trust_in_institutions: Optional[str] = None   # "high_trust", "skeptical", "distrustful"
    decision_making: Optional[str] = None          # "analytical", "intuitive", "consensus_seeking", "quick_decisive"
    information_processing: Optional[str] = None  # "detail_oriented", "big_picture", "emotional", "data_driven"
    
    # Generated fields
    persona_prompt: Optional[str] = None  # The complete persona identity
    
    def get_behavioral_characteristics(self) -> Dict[str, str]:
        """Get all non-None behavioral characteristics as a dictionary"""
        behavioral_fields = [
            'media_consumption', 'social_circle', 'risk_tolerance', 'change_orientation',
            'spending_style', 'brand_loyalty', 'civic_engagement', 'trust_in_institutions',
            'decision_making', 'information_processing'
        ]
        
        return {
            field: getattr(self, field) 
            for field in behavioral_fields 
            if getattr(self, field) is not None
        }


@dataclass
class StimulusConfig:
    """Standardized stimulus for persona testing"""
    
    stimulus_type: str              # "product_evaluation", "political_survey", "general_question"
    stimulus_id: str               # Unique identifier
    
    # Primary prompt content (this becomes the LLM prompt)
    prompt: str                    # Main question/request for the persona to respond to
    
    # Context and metadata
    title: Optional[str] = None                     # Brief title/description
    description: Optional[str] = None               # Additional context
    
    # Type-specific fields for building enhanced prompts
    product_name: Optional[str] = None
    price: Optional[str] = None
    features: Optional[List[str]] = None
    
    political_issue: Optional[str] = None
    proposal: Optional[str] = None
    
    # Legacy support
    question: Optional[str] = None   # Alias for prompt for backwards compatibility
    
    def get_prompt(self) -> str:
        """Get the main prompt, with fallbacks for backwards compatibility"""
        return self.prompt or self.question or self.description