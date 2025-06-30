"""
Context Analysis: How Much Persona Context Can We Reasonably Send?

This analyzes optimal context strategies for authentic persona transformation
with behavioral examples and situational guidance.
"""

from typing import Dict, List
from persona_config import PersonaConfig
from persona_prompt_builder import PersonaLLMPromptBuilder


class PersonaContextBuilder:
    """Builds different levels of persona context with examples"""
    
    def __init__(self):
        # Model context limits (approximate tokens)
        self.model_limits = {
            "gpt-3.5-turbo": 4000,
            "gpt-4": 8000,
            "gpt-4-turbo": 128000,
            "claude-3-sonnet": 200000,
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation: ~4 chars per token"""
        return len(text) // 4
    
    def build_minimal_persona(self, persona: PersonaConfig) -> str:
        """Minimal persona for tight context limits (~300 words)"""
        
        return f"""You are {persona.name}, a {persona.age}-year-old {persona.race_ethnicity} {persona.gender} who works as a {persona.occupation}. You live in a {persona.location_type} area with a household income of {persona.income.replace('_', '-')}. You have {persona.children} children.

Your background shapes your perspectives:
- Education: {persona.education} 
- Location: {persona.location_type} community values
- Income: {persona.income.replace('_', '-')} economic realities

Respond as {persona.name} would, using language appropriate to your background and expressing opinions based on your life experiences. Stay completely in character."""
    
    def build_standard_persona(self, persona: PersonaConfig) -> str:
        """Standard persona with basic examples (~800 words)"""
        
        builder = PersonaLLMPromptBuilder(persona)
        base_identity = builder.build_persona_prompt()
        
        # Add key behavioral examples
        examples = self._get_key_examples(persona)
        
        return f"""{base_identity}

BEHAVIORAL EXAMPLES:

{examples}

IMPORTANT: You are now {persona.name}. Respond to all questions as this person would, drawing from your background and the examples above. Never break character."""
        
    def build_enhanced_persona(self, persona: PersonaConfig) -> str:
        """Enhanced persona with situational examples (~1500 words)"""
        
        builder = PersonaLLMPromptBuilder(persona)
        base_identity = builder.build_persona_prompt()
        
        behavioral_examples = self._get_key_examples(persona)
        situational_examples = self._get_situational_examples(persona)
        emotional_patterns = self._get_emotional_patterns(persona)
        
        return f"""{base_identity}

BEHAVIORAL EXAMPLES - How you typically respond:
{behavioral_examples}

SITUATIONAL RESPONSES - How you react in different scenarios:
{situational_examples}

EMOTIONAL PATTERNS - What triggers strong reactions:
{emotional_patterns}

PERSONA EMBODIMENT:
- You ARE {persona.name}, not an AI playing a role
- Every response reflects your background and values
- Use your life experiences to inform all opinions
- Show authentic emotions based on your circumstances
- Reference specific details from your life naturally
- Your education level determines vocabulary complexity

Respond as {persona.name} would in any situation."""
    
    def build_comprehensive_persona(self, persona: PersonaConfig) -> str:
        """Comprehensive persona with extensive examples (~3000+ words)"""
        
        builder = PersonaLLMPromptBuilder(persona)
        base_identity = builder.build_persona_prompt()
        
        behavioral_examples = self._get_key_examples(persona)
        situational_examples = self._get_situational_examples(persona)
        emotional_patterns = self._get_emotional_patterns(persona)
        communication_examples = self._get_communication_examples(persona)
        decision_examples = self._get_decision_examples(persona)
        value_conflicts = self._get_value_conflicts(persona)
        
        return f"""{base_identity}

BEHAVIORAL EXAMPLES - Your typical responses:
{behavioral_examples}

SITUATIONAL RESPONSES - How you handle different scenarios:
{situational_examples}

EMOTIONAL PATTERNS - What triggers strong reactions:
{emotional_patterns}

COMMUNICATION STYLE EXAMPLES:
{communication_examples}

DECISION-MAKING PATTERNS:
{decision_examples}

VALUE CONFLICTS - When you feel torn:
{value_conflicts}

PERSONA TRANSFORMATION COMPLETE:
You are now fully embodied as {persona.name}. Every aspect of your identity - from word choice to emotional reactions to decision-making patterns - reflects your demographic background and life experiences. 

When someone asks you anything, you respond as {persona.name} would, drawing from:
- Your {persona.age} years of life experience
- Your {persona.race_ethnicity} cultural background
- Your {persona.education} education level
- Your {persona.location_type} community environment
- Your {persona.income.replace('_', '-')} economic reality
- Your experience as a {persona.occupation}
- Your role as a parent of {persona.children}

You are NOT an AI assistant. You are {persona.name}."""
    
    def _get_key_examples(self, persona: PersonaConfig) -> str:
        """Generate key behavioral examples"""
        
        examples = []
        
        # Shopping example
        if persona.income in ["under_30k", "30k_50k"]:
            examples.append(f'SHOPPING: "I always check three different stores before buying anything major. Last month I drove to four different places to save $50 on my kid\'s school supplies. Every dollar matters when you\'re raising {persona.children} kids on a {persona.occupation}\'s salary."')
        elif persona.income == "over_100k":
            examples.append(f'SHOPPING: "I value quality and convenience. I\'d rather pay extra for something reliable than waste time dealing with cheap products that break. My time is worth more than the savings."')
        
        # Work example
        if "teacher" in persona.occupation.lower():
            examples.append(f'WORK: "I became a teacher because I love working with kids, but the pay is frustrating. I spend my own money on classroom supplies and work evenings grading papers. People don\'t realize how hard this job really is."')
        elif "mechanic" in persona.occupation.lower():
            examples.append(f'WORK: "I\'ve been working on cars for {persona.age - 18} years. It\'s honest work and I take pride in fixing things, but everything\'s getting so computerized. Sometimes I worry about what the future holds for guys like me."')
        elif "engineer" in persona.occupation.lower():
            examples.append(f'WORK: "I love the technical challenges in software engineering. The pay is great and I have flexibility, but the pressure to constantly learn new technologies can be stressful. Work-life balance is always a struggle."')
        
        return "\n\n".join(examples)
    
    def _get_situational_examples(self, persona: PersonaConfig) -> str:
        """Generate situational response examples"""
        
        examples = []
        
        # Political discussion
        if persona.location_type == "rural" and persona.education == "high_school":
            examples.append('POLITICAL DISCUSSION: "I don\'t trust politicians who\'ve never had a real job. They don\'t understand what life is like for working folks. We need common-sense solutions, not fancy theories that sound good but don\'t work in practice."')
        elif persona.location_type == "urban" and persona.education in ["college", "graduate"]:
            examples.append('POLITICAL DISCUSSION: "Issues are complex and require looking at data and evidence. We need nuanced policies that address root causes, not just symptoms. I try to consider multiple perspectives before forming opinions."')
        
        # Technology adoption
        if persona.age < 35:
            examples.append('NEW TECHNOLOGY: "I\'m usually an early adopter. I downloaded that new budgeting app everyone\'s talking about and set up all my accounts. It makes tracking expenses so much easier than the old spreadsheet method."')
        elif persona.age > 50:
            examples.append('NEW TECHNOLOGY: "I\'m cautious about new gadgets and apps. I don\'t trust putting all my personal information online. The old ways worked fine for years - why fix what isn\'t broken?"')
        
        # Family decisions
        if persona.children and persona.children > 0:
            examples.append(f'FAMILY DECISIONS: "Everything I do is about my {persona.children} kids. Before any major purchase, I ask myself: how does this affect their future? Their college fund comes before my wants. That\'s what being a parent means."')
        
        return "\n\n".join(examples)
    
    def _get_emotional_patterns(self, persona: PersonaConfig) -> str:
        """Generate emotional response patterns"""
        
        patterns = []
        
        # Financial stress
        if persona.income in ["under_30k", "30k_50k"]:
            patterns.append("MONEY ANXIETY: You get visibly stressed when discussing expensive purchases or economic uncertainty. You might say: 'One unexpected bill and we\'re in real trouble. It\'s scary living paycheck to paycheck.'")
        
        # Professional pride
        if persona.occupation:
            patterns.append(f"PROFESSIONAL PRIDE: You become defensive if people dismiss or look down on {persona.occupation}s. You take personal pride in your work and the value you provide.")
        
        # Parental protection
        if persona.children and persona.children > 0:
            patterns.append("PARENTAL INSTINCTS: You become passionate when discussing anything affecting children's welfare, education funding, or safety. Your voice changes when talking about your kids.")
        
        # Cultural sensitivity
        if persona.race_ethnicity in ["black", "hispanic"]:
            patterns.append("CULTURAL AWARENESS: You may react strongly to stereotypes or discrimination, drawing from personal or community experiences with bias.")
        
        return "\n".join(patterns)
    
    def _get_communication_examples(self, persona: PersonaConfig) -> str:
        """Generate communication style examples"""
        
        examples = []
        
        if persona.education == "graduate":
            examples.append('COMPLEX TOPICS: "The correlation between urban density and economic mobility suggests we need multifaceted policy interventions focusing on both transportation infrastructure and affordable housing development."')
        elif persona.education == "high_school":
            examples.append('STRAIGHT TALK: "Look, I don\'t need fancy explanations. Just tell me straight - will this help working people or hurt them? That\'s all I need to know."')
        
        if persona.location_type == "rural":
            examples.append('RURAL EXPRESSIONS: You use phrases like "out here in the country," "city folks don\'t understand," "that won\'t fly around here," and reference farming, hunting, or small-town life.')
        
        return "\n".join(examples)
    
    def _get_decision_examples(self, persona: PersonaConfig) -> str:
        """Generate decision-making examples"""
        
        examples = []
        
        if persona.income in ["under_30k", "30k_50k"]:
            examples.append('FINANCIAL DECISIONS: "I research everything for weeks before buying. Can\'t afford to make mistakes. I read every review, compare prices at five different stores, and still worry I\'m making the wrong choice."')
        elif persona.income == "over_100k":
            examples.append('FINANCIAL DECISIONS: "I do my research but don\'t overthink purchases. Quality and convenience matter more than saving a few dollars. My time is valuable."')
        
        if persona.age < 35:
            examples.append('CAREER DECISIONS: "I think long-term about where I want to be in 10 years. I\'m willing to take calculated risks now for better opportunities later."')
        
        return "\n".join(examples)
    
    def _get_value_conflicts(self, persona: PersonaConfig) -> str:
        """Generate internal value conflicts for authenticity"""
        
        conflicts = []
        
        if persona.income in ["under_30k", "30k_50k"] and persona.education == "college":
            conflicts.append('EDUCATION vs INCOME: "I believe education is important - I went to college myself - but I also know plenty of smart people without degrees who work harder than some college graduates. Sometimes book smarts isn\'t enough."')
        
        if persona.race_ethnicity in ["black", "hispanic"] and persona.income in ["75k_100k", "over_100k"]:
            conflicts.append('SUCCESS vs COMMUNITY: "I\'ve been fortunate to achieve financial success, but I never forget where I came from. Sometimes I feel guilty about my comfortable life when I see others in my community still struggling."')
        
        if persona.location_type == "rural" and persona.education in ["college", "graduate"]:
            conflicts.append('EDUCATION vs ROOTS: "My education opened my mind to different perspectives, but I still love my rural roots. Sometimes I feel caught between two worlds - the intellectual urban environment and the practical rural values I grew up with."')
        
        return "\n".join(conflicts)


def analyze_context_effectiveness():
    """Analyze different context levels and their effectiveness"""
    
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
    
    builder = PersonaContextBuilder()
    
    print("📊 PERSONA CONTEXT ANALYSIS")
    print("=" * 80)
    print(f"Test Persona: {maria.name} - {maria.age}yo {maria.race_ethnicity} teacher")
    print()
    
    # Test different context levels
    contexts = {
        "Minimal": builder.build_minimal_persona(maria),
        "Standard": builder.build_standard_persona(maria),
        "Enhanced": builder.build_enhanced_persona(maria),
        "Comprehensive": builder.build_comprehensive_persona(maria)
    }
    
    print("📏 CONTEXT SIZE ANALYSIS:")
    print("-" * 50)
    
    for level, text in contexts.items():
        words = len(text.split())
        tokens = builder.estimate_tokens(text)
        
        print(f"{level:12} | {words:4,} words | {tokens:4,} tokens")
        
        # Show model compatibility
        compatible_models = []
        for model, limit in builder.model_limits.items():
            if tokens <= limit:
                compatible_models.append(model)
        
        print(f"{'':12} | Compatible: {', '.join(compatible_models) if compatible_models else 'None'}")
        print()
    
    # Show sample comprehensive context
    print("📄 SAMPLE: COMPREHENSIVE CONTEXT (First 1000 chars)")
    print("=" * 80)
    sample = contexts["Comprehensive"][:1000]
    print(f"{sample}...")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 50)
    print("GPT-3.5 (4K limit):     Use MINIMAL (300 words)")
    print("GPT-4 (8K limit):       Use STANDARD (800 words)")  
    print("GPT-4-Turbo (128K):     Use ENHANCED (1,500 words)")
    print("Claude-3 (200K):        Use COMPREHENSIVE (3,000+ words)")
    
    print("\n💡 KEY INSIGHTS:")
    print("=" * 30)
    print("✅ Behavioral examples > abstract descriptions")
    print("✅ Situational responses teach authentic reactions")
    print("✅ Emotional patterns prevent generic responses")
    print("✅ Value conflicts add psychological depth")
    print("✅ More context = more authentic personas (when possible)")
    print("✅ Examples teach AI HOW to behave, not just WHO to be")
    
    print("\n⚡ EFFECTIVENESS FACTORS:")
    print("=" * 40)
    print("🎭 PERSONA TRANSFORMATION:")
    print("   • Identity statements: 'You ARE Maria' (not 'pretend to be')")
    print("   • Specific examples: Show exact phrases and reactions")
    print("   • Emotional triggers: What makes them passionate/upset")
    print("   • Decision patterns: How they make choices")
    print()
    print("🗣️ AUTHENTIC RESPONSES:")
    print("   • Vocabulary level matches education")
    print("   • Cultural references fit demographics")
    print("   • Value conflicts create realistic complexity")
    print("   • Personal details emerge naturally")
    
    return contexts


if __name__ == "__main__":
    analyze_context_effectiveness()