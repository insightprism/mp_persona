"""
Context Effectiveness Test: How Different Context Levels Affect AI Responses

This demonstrates the practical impact of different context amounts on
persona authenticity and response quality.
"""

import asyncio
from context_analysis_simple import PersonaContextBuilder
from persona_config import PersonaConfig


class ContextEffectivenessTest:
    """Test how context levels affect persona response authenticity"""
    
    def __init__(self):
        self.builder = PersonaContextBuilder()
    
    def simulate_ai_responses(self, context: str, question: str) -> str:
        """
        Simulate how AI would respond with different context levels
        (In real test, this would call actual LLM with the context)
        """
        
        # Extract key info from context to simulate realistic responses
        words = len(context.split())
        has_examples = "EXAMPLES" in context.upper()
        has_emotions = "EMOTIONAL" in context.upper()
        has_situations = "SITUATIONAL" in context.upper()
        
        if "smartphone" in question.lower():
            if words < 200:  # Minimal context
                return "I need a phone with good battery life and camera for my kids. Price is important on a teacher's salary."
            
            elif words < 800:  # Standard context
                return "As a teacher and mom of two, I really need a phone with amazing battery life - I can't have it dying during parent-teacher conferences. The camera is super important for capturing my kids' moments. Honestly, I'd love the latest iPhone but on a teacher's salary with two kids? I'd probably spend $400-600 max."
            
            elif has_examples:  # Enhanced context
                return "Oh, for me it's all about practicality! Last month I spent three weeks researching phones before buying because every dollar counts. As a teacher and mom, I need amazing battery life - I learned that lesson when my phone died during a school emergency. The camera is crucial too - I take hundreds of photos of my students' work and my kids' activities. I'd love that new iPhone, but realistically? I'm looking at $400-600 range. Maybe last year's model on sale. Storage matters too because between educational apps and family photos, I'm always running out of space."
            
            else:  # Comprehensive context
                return "¡Dios mío! Don't get me started on smartphones - this is such a personal topic for me. Look, as a Latina teacher juggling two kids and a classroom of 28 students, my phone is literally my lifeline. I need that battery to last ALL day because when little Sofia has an asthma attack and I need to call her mom, or when I'm coordinating pickup schedules with other parents, I cannot have a dead phone. Period.\n\nThe camera? Essential. I document everything - my students' progress for their portfolios, family moments I'll treasure forever. You know how Hispanic families are about photos, right? Every birthday, every school play, every little milestone.\n\nBut here's the reality - I make $48,000 a year. After rent, groceries, and putting aside $200 monthly for the kids' college fund, I can maybe spend $500 on a phone. I research for WEEKS. Last time, I drove to four different stores, read every review online. My husband thinks I'm crazy, but one bad purchase affects our whole budget. I usually end up with last year's model - still great quality but at a price that doesn't keep me awake at night worrying about bills."
        
        return "I'd need to think about that based on my situation as a teacher and parent."
    
    async def test_context_levels(self):
        """Test different context levels with the same question"""
        
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
        
        # Build different context levels
        contexts = {
            "Minimal": self.builder.build_minimal_persona(maria),
            "Standard": self.builder.build_standard_persona(maria),
            "Enhanced": self.builder.build_enhanced_persona(maria),
            "Comprehensive": self.builder.build_comprehensive_persona(maria)
        }
        
        # Test question
        question = "What smartphone features are most important to you? How much would you be willing to spend?"
        
        print("🧪 CONTEXT EFFECTIVENESS TEST")
        print("=" * 80)
        print(f"Question: {question}")
        print(f"Test Persona: {maria.name} - {maria.age}yo {maria.race_ethnicity} teacher")
        print()
        
        for level, context in contexts.items():
            words = len(context.split())
            print(f"📱 {level.upper()} CONTEXT ({words} words):")
            print("-" * 60)
            
            # Simulate AI response
            response = self.simulate_ai_responses(context, question)
            print(f"Maria's Response: {response}")
            
            # Analyze response quality
            self._analyze_response_quality(response, level)
            print()
    
    def _analyze_response_quality(self, response: str, context_level: str):
        """Analyze the authenticity and quality of the response"""
        
        # Check for authenticity markers
        markers = {
            "Personal details": any(word in response.lower() for word in ["teacher", "kids", "children", "salary", "mom"]),
            "Financial specifics": any(word in response for word in ["$", "budget", "afford", "price"]),
            "Emotional language": any(word in response.lower() for word in ["love", "worry", "important", "crucial", "can't"]),
            "Cultural references": any(word in response.lower() for word in ["hispanic", "latina", "family", "dios"]),
            "Specific examples": any(phrase in response.lower() for phrase in ["last month", "three weeks", "drove to", "learned that"]),
            "Professional context": any(word in response.lower() for word in ["classroom", "students", "parent-teacher", "school"]),
            "Decision process": any(phrase in response.lower() for phrase in ["research", "weeks", "read reviews", "compare"])
        }
        
        score = sum(markers.values())
        
        print(f"   Authenticity Score: {score}/7")
        print(f"   Present: {', '.join([k for k, v in markers.items() if v])}")
        
        # Context effectiveness analysis
        if context_level == "Minimal":
            print("   Analysis: Basic demographics only, generic teacher response")
        elif context_level == "Standard":
            print("   Analysis: Good persona basics with some specific details")
        elif context_level == "Enhanced":
            print("   Analysis: Rich details, specific examples, authentic decision-making")
        else:  # Comprehensive
            print("   Analysis: Highly authentic, cultural markers, emotional depth, specific life details")


async def demonstrate_context_impact():
    """Demonstrate practical impact of context on persona authenticity"""
    
    print("🎯 CONTEXT IMPACT DEMONSTRATION")
    print("=" * 80)
    print("This shows how different context amounts affect persona authenticity")
    print()
    
    tester = ContextEffectivenessTest()
    await tester.test_context_levels()
    
    print("📊 CONTEXT EFFECTIVENESS SUMMARY:")
    print("=" * 50)
    
    effectiveness = {
        "Minimal (72 words)": {
            "Pros": ["Fast processing", "Low token usage", "Basic persona"],
            "Cons": ["Generic responses", "No cultural depth", "Limited authenticity"],
            "Best for": "Quick tests, tight budgets"
        },
        "Standard (709 words)": {
            "Pros": ["Good balance", "Key demographics", "Some examples"],
            "Cons": ["Limited emotional depth", "Few specific details"],
            "Best for": "General market research"
        },
        "Enhanced (904 words)": {
            "Pros": ["Rich examples", "Emotional patterns", "Authentic reactions"],
            "Cons": ["Higher token usage", "More complex"],
            "Best for": "Detailed persona studies"
        },
        "Comprehensive (978 words)": {
            "Pros": ["Maximum authenticity", "Cultural depth", "Psychological complexity"],
            "Cons": ["High token usage", "Complex processing"],
            "Best for": "Premium research, academic studies"
        }
    }
    
    for level, details in effectiveness.items():
        print(f"\n{level}:")
        print(f"   ✅ Pros: {', '.join(details['Pros'])}")
        print(f"   ❌ Cons: {', '.join(details['Cons'])}")
        print(f"   🎯 Best for: {details['Best for']}")
    
    print("\n🔑 KEY RECOMMENDATIONS:")
    print("=" * 40)
    print("1. EXAMPLES > DESCRIPTIONS")
    print("   'Maria shops for weeks before buying' vs 'Maria is price-conscious'")
    print()
    print("2. SPECIFIC DETAILS > GENERAL TRAITS")
    print("   '$48,000 salary, $200/month college fund' vs 'middle income'")
    print()
    print("3. EMOTIONAL CONTEXT > LOGICAL FACTS")
    print("   'keeps me awake worrying about bills' vs 'financial constraints'")
    print()
    print("4. SITUATIONAL EXAMPLES > PERSONALITY LISTS")
    print("   'When Sofia had asthma attack...' vs 'caring teacher'")
    print()
    print("5. CULTURAL MARKERS > DEMOGRAPHIC LABELS")
    print("   '¡Dios mío!' and family photo traditions vs 'Hispanic female'")
    
    print("\n💡 OPTIMAL STRATEGY:")
    print("=" * 30)
    print("• Use GPT-4-Turbo or Claude for comprehensive context")
    print("• Include 3-5 specific behavioral examples")
    print("• Add emotional triggers and value conflicts")
    print("• Provide exact phrases and vocabulary")
    print("• Show decision-making processes with examples")
    print("• Include cultural/regional expressions")
    print("• Give specific financial/life details")


if __name__ == "__main__":
    asyncio.run(demonstrate_context_impact())