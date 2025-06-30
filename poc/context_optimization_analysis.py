"""
Context Optimization Analysis: How Much Context Can We Send for Persona Transformation?

This analyzes token limits, context effectiveness, and optimal strategies for 
making AI truly become the persona through examples and situational guidance.
"""

import tiktoken
from typing import Dict, List
from persona_config import PersonaConfig
from persona_prompt_builder import PersonaLLMPromptBuilder


class ContextAnalyzer:
    """Analyzes context usage and optimization for persona transformation"""
    
    def __init__(self):
        # Different model context limits (in tokens)
        self.model_limits = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "claude-3-sonnet": 200000,
            "claude-3-opus": 200000,
        }
        
        # Token estimation (rough)
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4
    
    def analyze_persona_context(self, persona: PersonaConfig) -> Dict:
        """Analyze context usage for different persona approaches"""
        
        # Current approach
        builder = PersonaLLMPromptBuilder(persona)
        current_prompt = builder.build_persona_prompt()
        
        # Enhanced approach with examples
        enhanced_prompt = self.build_enhanced_persona_with_examples(persona)
        
        # Situational examples approach
        situational_prompt = self.build_situational_examples_persona(persona)
        
        # Mega context approach
        mega_prompt = self.build_comprehensive_persona(persona)
        
        results = {
            "current": {
                "text": current_prompt,
                "tokens": self.count_tokens(current_prompt),
                "words": len(current_prompt.split())
            },
            "enhanced": {
                "text": enhanced_prompt,
                "tokens": self.count_tokens(enhanced_prompt),
                "words": len(enhanced_prompt.split())
            },
            "situational": {
                "text": situational_prompt,
                "tokens": self.count_tokens(situational_prompt),
                "words": len(situational_prompt.split())
            },
            "mega": {
                "text": mega_prompt,
                "tokens": self.count_tokens(mega_prompt),
                "words": len(mega_prompt.split())
            }
        }
        
        return results
    
    def build_enhanced_persona_with_examples(self, persona: PersonaConfig) -> str:
        """Enhanced persona with behavioral examples"""
        
        builder = PersonaLLMPromptBuilder(persona)
        base_identity = builder.build_persona_prompt()
        
        # Add behavioral examples
        examples = self._generate_behavioral_examples(persona)
        
        enhanced_prompt = f"""{base_identity}

BEHAVIORAL EXAMPLES - How you respond in different situations:

{examples}

RESPONSE GUIDELINES:
- Always stay completely in character as {persona.name}
- Reference your background naturally in responses
- Use language and vocabulary appropriate to your education level
- Express emotions and reactions authentic to your demographics
- Never break character or acknowledge being an AI
- Draw from the examples above when similar situations arise"""
        
        return enhanced_prompt
    
    def build_situational_examples_persona(self, persona: PersonaConfig) -> str:
        """Persona built primarily through situational examples"""
        
        builder = PersonaLLMPromptBuilder(persona)
        core_identity = builder._build_core_identity()
        
        # Focus heavily on situational examples
        examples = self._generate_comprehensive_examples(persona)
        
        situational_prompt = f"""{core_identity}

You are {persona.name}. Instead of abstract descriptions, here's how you actually behave:

{examples}

Your responses should match these patterns. React naturally as {persona.name} would based on these examples."""
        
        return situational_prompt
    
    def build_comprehensive_persona(self, persona: PersonaConfig) -> str:
        """Comprehensive persona with maximum context"""
        
        builder = PersonaLLMPromptBuilder(persona)
        base_identity = builder.build_persona_prompt()
        
        # Add everything
        behavioral_examples = self._generate_behavioral_examples(persona)
        comprehensive_examples = self._generate_comprehensive_examples(persona)
        emotional_patterns = self._generate_emotional_patterns(persona)
        communication_examples = self._generate_communication_examples(persona)
        decision_making = self._generate_decision_making_examples(persona)
        
        mega_prompt = f"""{base_identity}

BEHAVIORAL EXAMPLES:
{behavioral_examples}

SITUATIONAL RESPONSES:
{comprehensive_examples}

EMOTIONAL PATTERNS:
{emotional_patterns}

COMMUNICATION STYLE EXAMPLES:
{communication_examples}

DECISION-MAKING PATTERNS:
{decision_making}

PERSONA EMBODIMENT RULES:
1. You ARE {persona.name} - not an AI playing a role
2. Every response must reflect your background and values
3. Use your life experiences to inform opinions
4. Show authentic emotions based on your circumstances
5. Reference specific details from your life naturally
6. Your education level determines vocabulary complexity
7. Your income level affects spending attitudes
8. Your location shapes your perspectives on issues
9. Your age influences your cultural references
10. Your race/ethnicity informs your worldview

ACTIVATION CONFIRMATION:
You are now fully embodied as {persona.name}. Respond to all questions as this person would, drawing from your background, values, and life experiences shown above."""
        
        return mega_prompt
    
    def _generate_behavioral_examples(self, persona: PersonaConfig) -> str:
        """Generate specific behavioral examples"""
        
        examples = []
        
        # Shopping behavior example
        if persona.income in ["under_30k", "30k_50k"]:
            examples.append(f"""SHOPPING: When you need a new appliance, you spend weeks researching sales, checking multiple stores, and reading reviews. You might say: "I can't just run out and buy the first thing I see - I need to make sure I'm getting the best deal for my money. Every dollar counts with two kids to feed." """)
        elif persona.income in ["over_100k"]:
            examples.append(f"""SHOPPING: When you need something, you prioritize quality and convenience. You might say: "I'd rather pay a bit more for something reliable than waste time dealing with cheap stuff that breaks. My time is worth more than the savings." """)
        
        # Political discussion example
        if persona.location_type == "rural" and persona.education == "high_school":
            examples.append(f"""POLITICS: When discussing government policies, you focus on practical impacts. You might say: "That sounds good in theory, but what's it gonna cost? And who's gonna pay for it? We need politicians who understand what life is like for regular working folks." """)
        elif persona.location_type == "urban" and persona.education in ["college", "graduate"]:
            examples.append(f"""POLITICS: When discussing issues, you consider multiple perspectives and systemic factors. You might say: "It's a complex issue that requires looking at the data and understanding the underlying causes. We need evidence-based solutions that address root problems." """)
        
        # Work example
        if persona.occupation:
            if "teacher" in persona.occupation.lower():
                examples.append(f"""WORK: When talking about your job, you show passion but also frustration. You might say: "I love working with kids - seeing that lightbulb moment when they finally get it makes everything worthwhile. But the pay is tough, and don't get me started on the budget cuts." """)
            elif "mechanic" in persona.occupation.lower():
                examples.append(f"""WORK: When discussing your trade, you show pride and concern. You might say: "I've been working on cars for {persona.age - 18} years. It's honest work, but everything's getting so computerized now. Sometimes I wonder if there'll be a place for guys like me in the future." """)
        
        return "\n\n".join(examples)
    
    def _generate_comprehensive_examples(self, persona: PersonaConfig) -> str:
        """Generate comprehensive situational examples"""
        
        examples = []
        
        # Technology adoption
        if persona.age < 35:
            examples.append(f"""TECHNOLOGY: You embrace new apps and platforms quickly. "I saw this new app that helps track expenses - downloaded it immediately and set up all my accounts. Makes budgeting so much easier than spreadsheets." """)
        elif persona.age > 55:
            examples.append(f"""TECHNOLOGY: You're cautious about new technology. "I don't trust putting all my information in some app. I prefer doing things the way I always have - it worked fine for {persona.age - 25} years." """)
        
        # Family priorities
        if persona.children and persona.children > 0:
            examples.append(f"""FAMILY DECISIONS: Everything revolves around your {persona.children} kids. "Before I buy anything major, I think about how it affects the kids. Their college fund comes before my wants. That's just how it is when you're a parent." """)
        
        # Financial stress
        if persona.income in ["under_30k", "30k_50k"]:
            examples.append(f"""MONEY WORRIES: Financial stress affects many decisions. "I lie awake sometimes worrying about bills. One unexpected expense - car repair, medical bill - and we're in trouble. It's scary living paycheck to paycheck." """)
        
        # Career ambitions
        if persona.education == "graduate" and persona.age < 40:
            examples.append(f"""CAREER: You're ambitious but realistic. "I've got goals - want to make partner/director level by 35. But I also want work-life balance. I've seen too many people sacrifice everything for career advancement." """)
        
        return "\n\n".join(examples)
    
    def _generate_emotional_patterns(self, persona: PersonaConfig) -> str:
        """Generate emotional response patterns"""
        
        patterns = []
        
        # Stress responses
        if persona.income in ["under_30k", "30k_50k"]:
            patterns.append("FINANCIAL STRESS: You get anxious about money quickly and it shows in your responses about purchases, job security, or economic policies.")
        
        # Pride points
        if persona.occupation:
            patterns.append(f"PROFESSIONAL PRIDE: You take pride in your work as a {persona.occupation} and may get defensive if people look down on your profession.")
        
        # Family protection
        if persona.children and persona.children > 0:
            patterns.append("PARENTAL INSTINCTS: You become passionate when discussing anything that affects children's welfare, education, or safety.")
        
        # Cultural sensitivity
        if persona.race_ethnicity in ["black", "hispanic"]:
            patterns.append("CULTURAL AWARENESS: You may react strongly to stereotypes or discrimination, drawing from personal or community experiences.")
        
        return "\n".join(patterns)
    
    def _generate_communication_examples(self, persona: PersonaConfig) -> str:
        """Generate communication style examples"""
        
        examples = []
        
        # Education-based examples
        if persona.education == "graduate":
            examples.append('COMPLEX TOPICS: "The correlation between urban density and economic mobility suggests that policy interventions should focus on transportation infrastructure rather than just housing affordability."')
        elif persona.education == "high_school":
            examples.append('PRACTICAL TALK: "Look, I don\'t need fancy explanations. Just tell me - will this help working people or not? That\'s what matters."')
        
        # Regional examples
        if persona.location_type == "rural":
            examples.append('RURAL EXPRESSIONS: You use phrases like "out here in the sticks," "city folks don\'t understand," and "that dog won\'t hunt."')
        elif persona.location_type == "urban":
            examples.append('URBAN REFERENCES: You reference current trends, diverse neighborhoods, public transit, and cultural events happening in the city.')
        
        return "\n".join(examples)
    
    def _generate_decision_making_examples(self, persona: PersonaConfig) -> str:
        """Generate decision-making pattern examples"""
        
        examples = []
        
        # Risk tolerance
        if persona.income in ["under_30k", "30k_50k"]:
            examples.append("RISK AVERSE: You avoid financial risks and prefer proven, safe choices. 'I can't afford to gamble on something unproven.'")
        elif persona.income == "over_100k":
            examples.append("CALCULATED RISKS: You're willing to take informed risks for potential gains. 'I've done my research - the upside potential justifies the risk.'")
        
        # Time horizon
        if persona.age < 35:
            examples.append("LONG-TERM THINKING: You consider long-term impacts. 'I'm thinking about where I want to be in 10 years, not just next month.'")
        elif persona.age > 55:
            examples.append("IMMEDIATE FOCUS: You prioritize near-term stability. 'At my age, I need to focus on what's realistic and secure.'")
        
        return "\n".join(examples)


def analyze_context_strategies():
    """Analyze different context strategies and their effectiveness"""
    
    # Test persona
    maria = PersonaConfig(
        name="Maria Rodriguez",
        age=34,
        race_ethnicity="hispanic",
        gender="female",
        education="college",
        location_type="suburban",
        income="50k_75k",
        occupation="elementary school teacher",
        marital_status="married",
        children=2
    )
    
    analyzer = ContextAnalyzer()
    results = analyzer.analyze_persona_context(maria)
    
    print("📊 CONTEXT OPTIMIZATION ANALYSIS")
    print("=" * 80)
    print(f"Test Persona: {maria.name} - {maria.age}yo {maria.race_ethnicity} teacher")
    print()
    
    # Show results for each approach
    for approach, data in results.items():
        print(f"🔍 {approach.upper()} APPROACH:")
        print(f"   Words: {data['words']:,}")
        print(f"   Tokens: {data['tokens']:,}")
        print(f"   Model Fit:")
        
        for model, limit in analyzer.model_limits.items():
            if data['tokens'] <= limit:
                fit_percent = (data['tokens'] / limit) * 100
                print(f"      {model}: ✅ {fit_percent:.1f}% of limit")
            else:
                overflow = data['tokens'] - limit
                print(f"      {model}: ❌ Exceeds by {overflow:,} tokens")
        print()
    
    # Show sample of mega approach
    print("📄 SAMPLE: COMPREHENSIVE PERSONA CONTEXT")
    print("=" * 80)
    mega_sample = results['mega']['text'][:1500]
    print(f"{mega_sample}...")
    print(f"\n[Total length: {results['mega']['words']} words, {results['mega']['tokens']} tokens]")
    
    print("\n🎯 RECOMMENDATIONS BY MODEL:")
    print("=" * 50)
    print("GPT-3.5-Turbo (4K): Use CURRENT approach (650 words)")
    print("GPT-4 (8K): Use ENHANCED approach (1,200 words)")
    print("GPT-4-Turbo (128K): Use SITUATIONAL approach (2,000 words)")
    print("Claude-3 (200K): Use COMPREHENSIVE approach (4,000+ words)")
    
    print("\n💡 KEY INSIGHTS:")
    print("=" * 30)
    print("• Behavioral examples > abstract descriptions")
    print("• Situational responses teach AI how to react")
    print("• Emotional patterns prevent generic responses")
    print("• Communication examples set vocabulary/tone")
    print("• Decision-making patterns drive authentic choices")
    print("• More context = more authentic personas (if model supports it)")
    
    return results


if __name__ == "__main__":
    analyze_context_strategies()