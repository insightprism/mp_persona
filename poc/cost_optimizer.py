#!/usr/bin/env python3
"""
Persona System Cost Optimizer
============================

Smart cost management for persona asset generation.
Provides recommendations and usage tracking.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CostEstimate:
    """Cost estimate for persona operations"""
    image_cost: float = 0.02  # DALL-E 2 256x256
    voice_cost: float = 0.003  # ~200 char script
    llm_cost_per_1k: Dict[str, float] = None
    
    def __post_init__(self):
        if self.llm_cost_per_1k is None:
            self.llm_cost_per_1k = {
                "openai_input": 0.03,
                "openai_output": 0.06,
                "claude_input": 0.003,
                "claude_output": 0.015,
                "ollama": 0.0
            }

class PersonaCostOptimizer:
    """Optimize costs for persona asset generation"""
    
    def __init__(self):
        self.usage_history = {}
        self.cost_estimates = CostEstimate()
        self.cost_thresholds = {
            "image_warning": 0.50,  # Warn at $0.50 in images
            "voice_warning": 0.20,  # Warn at $0.20 in voice
            "session_limit": 2.00   # Alert at $2.00 total
        }
    
    def should_generate_image(self, persona_id: str, force: bool = False, vector_match_available: bool = True) -> Dict[str, Any]:
        """
        Determine if image generation is cost-effective
        
        Args:
            persona_id: Unique persona identifier
            force: Override cost recommendations
            vector_match_available: Whether pre-generated images are available
            
        Returns:
            Dict with recommendation and reasoning
        """
        if force:
            return {
                "recommend": True,
                "reason": "User explicitly requested (force=True)",
                "cost": self.cost_estimates.image_cost,
                "warnings": []
            }
        
        # ALWAYS prefer vector matching if available
        if vector_match_available:
            return {
                "recommend": False,
                "reason": "Pre-generated images available - use vector matching instead (free + instant)",
                "cost_savings": self.cost_estimates.image_cost,
                "time_savings": "3-5 seconds",
                "alternatives": [
                    "Use vector matching for instant, free images",
                    "Try lower similarity threshold if no match found",
                    "Use force_generate=True only if vector match is insufficient"
                ],
                "vector_match_benefits": {
                    "cost": "$0.000 vs $0.020",
                    "time": "0.05s vs 3-5s", 
                    "reliability": "No API failures or rate limits"
                }
            }
        
        # Check persona usage patterns
        usage = self.get_persona_usage(persona_id)
        warnings = []
        
        # Cost-benefit analysis
        if usage["total_interactions"] == 0:
            return {
                "recommend": False,
                "reason": "Persona has no usage history - consider testing first",
                "cost": self.cost_estimates.image_cost,
                "warnings": ["No interaction history", "Consider chat testing first"],
                "alternatives": ["Use text-only persona", "Generate after first conversation"]
            }
        
        if usage["total_interactions"] < 5:
            warnings.append(f"Low usage ({usage['total_interactions']} interactions)")
        
        if usage["session_duration"] < 300:  # Less than 5 minutes
            warnings.append(f"Short session duration ({usage['session_duration']}s)")
        
        # Check total session costs
        session_cost = self.calculate_session_cost(persona_id)
        if session_cost > self.cost_thresholds["session_limit"]:
            warnings.append(f"High session cost (${session_cost:.2f})")
        
        # Make recommendation
        if len(warnings) == 0:
            recommend = True
            reason = "Good usage pattern - image generation recommended"
        elif len(warnings) == 1:
            recommend = True
            reason = f"Acceptable usage with minor concern: {warnings[0]}"
        else:
            recommend = False
            reason = f"Multiple cost concerns: {', '.join(warnings)}"
        
        return {
            "recommend": recommend,
            "reason": reason,
            "cost": self.cost_estimates.image_cost,
            "warnings": warnings,
            "usage_stats": usage,
            "alternatives": self._get_alternatives() if not recommend else []
        }
    
    def should_generate_voice(self, persona_id: str, custom_text: str = None) -> Dict[str, Any]:
        """
        Determine if voice generation is cost-effective
        
        Args:
            persona_id: Unique persona identifier  
            custom_text: Custom text to speak (affects cost)
            
        Returns:
            Dict with recommendation and cost
        """
        usage = self.get_persona_usage(persona_id)
        text_length = len(custom_text) if custom_text else 200  # Default script length
        voice_cost = (text_length / 1000) * 0.015  # TTS cost per 1k chars
        
        warnings = []
        
        # Voice is cheaper than images, but still check usage
        if usage["total_interactions"] == 0:
            warnings.append("No interaction history")
        
        if text_length > 1000:
            warnings.append(f"Long text ({text_length} chars = ${voice_cost:.3f})")
        
        # Voice is generally more cost-effective
        recommend = len(warnings) <= 1
        
        return {
            "recommend": recommend,
            "reason": "Voice generation is cost-effective" if recommend else f"Concerns: {', '.join(warnings)}",
            "cost": voice_cost,
            "warnings": warnings,
            "text_length": text_length
        }
    
    def track_asset_generation(self, persona_id: str, asset_type: str, cost: float):
        """Track asset generation for cost monitoring"""
        if persona_id not in self.usage_history:
            self.usage_history[persona_id] = {
                "created_at": datetime.utcnow(),
                "total_interactions": 0,
                "session_duration": 0,
                "assets_generated": [],
                "total_cost": 0
            }
        
        self.usage_history[persona_id]["assets_generated"].append({
            "type": asset_type,
            "cost": cost,
            "timestamp": datetime.utcnow()
        })
        self.usage_history[persona_id]["total_cost"] += cost
    
    def track_interaction(self, persona_id: str, tokens_used: Dict[str, int] = None):
        """Track persona interaction for usage analysis"""
        if persona_id not in self.usage_history:
            self.usage_history[persona_id] = {
                "created_at": datetime.utcnow(),
                "total_interactions": 0,
                "session_duration": 0,
                "assets_generated": [],
                "total_cost": 0
            }
        
        usage = self.usage_history[persona_id]
        usage["total_interactions"] += 1
        usage["session_duration"] = (datetime.utcnow() - usage["created_at"]).total_seconds()
        
        # Track LLM costs if provided
        if tokens_used:
            llm_cost = self._calculate_llm_cost(tokens_used)
            usage["total_cost"] += llm_cost
    
    def get_persona_usage(self, persona_id: str) -> Dict[str, Any]:
        """Get usage statistics for a persona"""
        if persona_id not in self.usage_history:
            return {
                "total_interactions": 0,
                "session_duration": 0,
                "assets_generated": 0,
                "total_cost": 0.0,
                "created_at": None
            }
        
        usage = self.usage_history[persona_id]
        return {
            "total_interactions": usage["total_interactions"],
            "session_duration": usage["session_duration"],
            "assets_generated": len(usage["assets_generated"]),
            "total_cost": usage["total_cost"],
            "created_at": usage["created_at"],
            "cost_per_interaction": usage["total_cost"] / max(usage["total_interactions"], 1)
        }
    
    def calculate_session_cost(self, persona_id: str) -> float:
        """Calculate total cost for a persona session"""
        if persona_id not in self.usage_history:
            return 0.0
        return self.usage_history[persona_id]["total_cost"]
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get overall cost summary across all personas"""
        total_personas = len(self.usage_history)
        total_cost = sum(p["total_cost"] for p in self.usage_history.values())
        total_interactions = sum(p["total_interactions"] for p in self.usage_history.values())
        total_assets = sum(len(p["assets_generated"]) for p in self.usage_history.values())
        
        return {
            "total_personas": total_personas,
            "total_cost": total_cost,
            "total_interactions": total_interactions,
            "total_assets": total_assets,
            "avg_cost_per_persona": total_cost / max(total_personas, 1),
            "avg_cost_per_interaction": total_cost / max(total_interactions, 1),
            "most_expensive_persona": self._get_most_expensive_persona()
        }
    
    def _calculate_llm_cost(self, tokens_used: Dict[str, int]) -> float:
        """Calculate LLM usage cost"""
        input_tokens = tokens_used.get("input_tokens", 0)
        output_tokens = tokens_used.get("output_tokens", 0)
        provider = tokens_used.get("provider", "openai")
        
        costs = self.cost_estimates.llm_cost_per_1k
        input_cost = (input_tokens / 1000) * costs.get(f"{provider}_input", 0.03)
        output_cost = (output_tokens / 1000) * costs.get(f"{provider}_output", 0.06)
        
        return input_cost + output_cost
    
    def _get_most_expensive_persona(self) -> Optional[str]:
        """Get the persona with highest cost"""
        if not self.usage_history:
            return None
        
        return max(self.usage_history.keys(), 
                  key=lambda p: self.usage_history[p]["total_cost"])
    
    def _get_alternatives(self) -> list:
        """Get cost-saving alternatives"""
        return [
            "Use text-only persona for testing",
            "Generate image after confirming usage pattern",
            "Use placeholder avatar instead",
            "Consider batch generation for multiple personas"
        ]
    
    def generate_cost_report(self, persona_id: str) -> str:
        """Generate human-readable cost report"""
        usage = self.get_persona_usage(persona_id)
        
        report = f"""
Cost Report for Persona {persona_id}
{'='*50}
💰 Total Cost: ${usage['total_cost']:.3f}
💬 Interactions: {usage['total_interactions']}
🎨 Assets: {usage['assets_generated']}
⏱️  Duration: {usage['session_duration']:.0f}s
📊 Cost/Interaction: ${usage['cost_per_interaction']:.3f}

Recommendations:
"""
        
        image_rec = self.should_generate_image(persona_id)
        voice_rec = self.should_generate_voice(persona_id)
        
        report += f"🖼️  Image: {'✅ Recommended' if image_rec['recommend'] else '⚠️  Not recommended'}\n"
        report += f"   Reason: {image_rec['reason']}\n"
        
        report += f"🎤 Voice: {'✅ Recommended' if voice_rec['recommend'] else '⚠️  Consider carefully'}\n"
        report += f"   Reason: {voice_rec['reason']}\n"
        
        return report


# Convenience functions
def should_generate_image(persona_id: str, interactions: int = 0, duration: int = 0) -> bool:
    """Quick check if image generation is recommended"""
    optimizer = PersonaCostOptimizer()
    
    # Simulate usage for decision
    if interactions > 0:
        optimizer.usage_history[persona_id] = {
            "created_at": datetime.utcnow() - timedelta(seconds=duration),
            "total_interactions": interactions,
            "session_duration": duration,
            "assets_generated": [],
            "total_cost": 0
        }
    
    recommendation = optimizer.should_generate_image(persona_id)
    return recommendation["recommend"]

def get_asset_cost_estimate() -> Dict[str, float]:
    """Get current cost estimates for all assets"""
    costs = CostEstimate()
    return {
        "image": costs.image_cost,
        "voice_200_chars": costs.voice_cost,
        "voice_per_1k_chars": 0.015,
        "gpt4_per_1k_input": costs.llm_cost_per_1k["openai_input"],
        "gpt4_per_1k_output": costs.llm_cost_per_1k["openai_output"],
        "claude_per_1k_input": costs.llm_cost_per_1k["claude_input"],
        "claude_per_1k_output": costs.llm_cost_per_1k["claude_output"]
    }


if __name__ == "__main__":
    # Demo the cost optimizer
    optimizer = PersonaCostOptimizer()
    
    print("🎯 Persona Cost Optimizer Demo")
    print("=" * 40)
    
    # Test scenarios
    scenarios = [
        ("new_persona", 0, 0, "New persona - no usage"),
        ("light_user", 2, 60, "Light usage - 2 interactions, 1 min"),
        ("active_user", 15, 600, "Active usage - 15 interactions, 10 min"),
        ("heavy_user", 50, 1800, "Heavy usage - 50 interactions, 30 min")
    ]
    
    for persona_id, interactions, duration, description in scenarios:
        print(f"\n📊 Scenario: {description}")
        
        # Simulate usage
        for _ in range(interactions):
            optimizer.track_interaction(persona_id, {"input_tokens": 100, "output_tokens": 200, "provider": "openai"})
        
        # Check recommendations
        image_rec = optimizer.should_generate_image(persona_id)
        voice_rec = optimizer.should_generate_voice(persona_id)
        
        print(f"   🖼️  Image: {'✅' if image_rec['recommend'] else '❌'} - {image_rec['reason']}")
        print(f"   🎤 Voice: {'✅' if voice_rec['recommend'] else '❌'} - {voice_rec['reason']}")
        print(f"   💰 Current cost: ${optimizer.calculate_session_cost(persona_id):.3f}")
    
    print(f"\n📈 Overall Summary:")
    summary = optimizer.get_cost_summary()
    print(f"   Total cost: ${summary['total_cost']:.3f}")
    print(f"   Avg per persona: ${summary['avg_cost_per_persona']:.3f}")
    print(f"   Avg per interaction: ${summary['avg_cost_per_interaction']:.3f}")