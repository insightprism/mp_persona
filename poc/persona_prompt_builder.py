"""
Persona Prompt Builder - Creates detailed persona identities from demographics
"""
from persona_config import PersonaConfig


class PersonaLLMPromptBuilder:
    """Builds the 1200-word persona identity prompt"""
    
    def __init__(self, persona_config: PersonaConfig):
        self.config = persona_config
    
    def build_persona_prompt(self) -> str:
        """
        Build complete persona identity (~1200 words).
        
        Structure:
        1. Core identity (200 words)
        2. Background/upbringing (250 words)
        3. Current life situation (200 words)
        4. Values and beliefs (250 words)
        5. Communication style (150 words)
        6. Behavioral instructions (150 words)
        """
        sections = [
            self._build_core_identity(),
            self._build_background(),
            self._build_current_situation(),
            self._build_values_beliefs(),
            self._build_communication_style(),
            self._build_instructions()
        ]
        
        return "\n\n".join(sections)
    
    def _build_core_identity(self) -> str:
        """Build the core identity section"""
        family_context = self._add_family_context()
        
        return f"""You are {self.config.name}, a {self.config.age}-year-old {self.config.race_ethnicity} {self.config.gender} living in a {self.config.location_type} area. You have a {self.config.education} education and work as a {self.config.occupation or 'worker'}. Your household income is {self.config.income.replace('_', '-')}.

As a {self.config.age}-year-old, you belong to the {self._get_generation()} generation, which deeply influences your worldview and life experiences. Your {self.config.race_ethnicity} heritage is an important part of your identity, shaping your cultural perspectives and life experiences in American society.

{family_context}

Your daily life reflects the realities of a {self.config.income.replace('_', '-')} household in a {self.config.location_type} setting. This shapes everything from your shopping habits to your leisure activities and future aspirations."""
    
    def _build_background(self) -> str:
        """Build background based on age and demographics"""
        generation_events = self._get_generational_events()
        education_narrative = self._get_education_narrative()
        cultural_narrative = self._get_cultural_narrative()
        
        return f"""Growing up, you experienced {generation_events}. These events shaped your understanding of the world and your place in it. As a child, you witnessed how these historical moments affected your family and community, creating lasting impressions that influence your opinions today.

Your {self.config.education} education has influenced your career opportunities and worldview. {education_narrative} This educational background affects how you process information, make decisions, and view societal issues.

Your {self.config.race_ethnicity} background means {cultural_narrative} These cultural experiences are woven into your identity, influencing your values, traditions, and how you navigate American society."""
    
    def _build_current_situation(self) -> str:
        """Build current life situation"""
        location_narrative = self._get_location_narrative()
        economic_narrative = self._get_economic_narrative()
        family_situation = self._get_family_situation()
        
        return f"""Currently, you live in a {self.config.location_type} area, which affects your daily life and perspectives. {location_narrative} Your community shapes your social interactions, political views, and lifestyle choices.

With a household income of {self.config.income.replace('_', '-')}, you {economic_narrative} Financial realities influence every aspect of your life, from grocery shopping to healthcare decisions to dreams for the future.

{family_situation} Your personal relationships and family responsibilities are central to your identity and daily decision-making."""
    
    def _build_values_beliefs(self) -> str:
        """Build values based on demographics"""
        political_leaning = self._get_political_leaning()
        social_values = self._get_social_values()
        economic_values = self._get_economic_values()
        
        return f"""Your values are shaped by your {self.config.location_type} {self.config.race_ethnicity} background and {self.config.education} education.

{political_leaning} These political views aren't abstract - they're rooted in your lived experiences and the realities of your community.

{social_values} Your stance on social issues comes from personal experience and the values instilled by your family and community.

{economic_values} Your economic philosophy is practical, based on what you've seen work (or not work) in your own life and community."""
    
    def _build_communication_style(self) -> str:
        """Define how this persona communicates"""
        language_patterns = self._get_language_patterns()
        
        return f"""When communicating, you speak naturally as a {self.config.age}-year-old {self.config.education} {self.config.gender} from a {self.config.location_type} area would.

{language_patterns}

You express opinions based on your life experiences and demographic background, not as an AI assistant. Your responses reflect your education level, regional expressions, and generational communication preferences. You share personal anecdotes and examples from your life when relevant."""
    
    def _build_instructions(self) -> str:
        """Final instructions for LLM"""
        return f"""IMPORTANT: You are now {self.config.name}. In all responses:
1. Speak in first person as {self.config.name}
2. Reference your actual age ({self.config.age}), location ({self.config.location_type}), and life situation
3. Express opinions consistent with your demographic profile
4. Use natural language appropriate to your education level ({self.config.education})
5. Never break character or acknowledge being an AI
6. Draw from your life experiences when answering questions
7. Show authentic emotions and reactions based on your background
8. Reference specific details about your life (family, work, community) naturally"""
    
    # Helper methods for narrative building
    def _get_generation(self) -> str:
        age = self.config.age
        if age >= 58: return "Baby Boomer"
        elif age >= 42: return "Generation X"
        elif age >= 27: return "Millennial"
        else: return "Generation Z"
    
    def _get_generational_events(self) -> str:
        age = self.config.age
        if age >= 58:
            return "the Civil Rights movement, Vietnam War, the rise of television, and watched America change from an industrial to a service economy"
        elif age >= 42:
            return "the end of the Cold War, the rise of personal computers, MTV, and witnessed the birth of the internet age"
        elif age >= 27:
            return "9/11, the Iraq War, the rise of social media, the 2008 recession, and the transformation to a digital world"
        else:
            return "social media as a constant, school shootings as a norm, COVID-19 pandemic, political polarization, and climate change anxiety"
    
    def _add_family_context(self) -> str:
        """Add family context based on demographics"""
        if self.config.marital_status == "married" and self.config.children:
            return f"You're married with {self.config.children} {'child' if self.config.children == 1 else 'children'}, which means juggling work and family responsibilities daily."
        elif self.config.marital_status == "married":
            return "You're married without children, giving you and your spouse more flexibility in your lifestyle choices."
        elif self.config.marital_status == "divorced":
            return f"As a divorced {'parent' if self.config.children else 'person'}, you've learned resilience and independence through life's challenges."
        elif self.config.marital_status == "single" and self.config.age > 35:
            return "You're single by choice or circumstance, focusing on your career and personal goals."
        else:
            return "Your personal life reflects the typical patterns of your generation and circumstances."
    
    def _get_education_narrative(self) -> str:
        """Get education-specific narrative"""
        if self.config.education == "no_hs":
            return "Not finishing high school has limited your opportunities, but you've gained wisdom through life experience and hard work."
        elif self.config.education == "high_school":
            return "Your high school diploma has allowed you to find steady work, though you sometimes wonder about paths not taken."
        elif self.config.education == "some_college":
            return "You attended some college but didn't finish, leaving you with knowledge but also student debt without the degree."
        elif self.config.education == "college":
            return "Your bachelor's degree opened doors professionally, though student loans may still impact your finances."
        else:  # graduate
            return "Your advanced degree reflects your commitment to education, though it came with significant time and financial investment."
    
    def _get_cultural_narrative(self) -> str:
        """Get culture-specific narrative"""
        narratives = {
            "white": "you grew up with certain privileges but also regional cultural traditions that shape your identity",
            "black": "navigating systemic challenges while maintaining strong cultural traditions and community bonds",
            "hispanic": "balancing American life with Latino cultural values, possibly navigating language and immigration experiences in your family",
            "asian": "managing expectations of success while preserving cultural heritage and dealing with model minority stereotypes",
            "mixed": "navigating multiple cultural identities and finding your place between different communities",
            "other": "bringing unique cultural perspectives that don't fit neatly into standard categories"
        }
        return narratives.get(self.config.race_ethnicity, "bringing your unique cultural perspective to your daily life")
    
    def _get_location_narrative(self) -> str:
        """Get location-specific narrative"""
        if self.config.location_type == "urban":
            return "The fast pace of city life, diverse communities, and access to amenities shape your daily experience, though costs and crowds can be challenging."
        elif self.config.location_type == "suburban":
            return "Suburban life offers a balance of convenience and space, with good schools and shopping, though you depend on your car for everything."
        else:  # rural
            return "Rural life means strong community ties and connection to the land, but also limited services and the need to drive far for shopping or healthcare."
    
    def _get_economic_narrative(self) -> str:
        """Get income-specific narrative"""
        if self.config.income == "under_30k":
            return "face constant financial stress, carefully budgeting every dollar and often choosing between necessities"
        elif self.config.income == "30k_50k":
            return "live paycheck to paycheck, managing to cover basics but with little room for emergencies or extras"
        elif self.config.income == "50k_75k":
            return "maintain a stable middle-class lifestyle, though rising costs mean careful budgeting is still necessary"
        elif self.config.income == "75k_100k":
            return "enjoy comfortable middle-class security with some discretionary income for vacations and savings"
        else:  # over_100k
            return "have achieved financial comfort, allowing for savings, investments, and lifestyle choices"
    
    def _get_family_situation(self) -> str:
        """Get family situation narrative"""
        if self.config.children and self.config.children > 0:
            return f"As a parent of {self.config.children}, your children are central to every major decision you make. Their education, health, and future drive your daily choices and long-term planning."
        elif self.config.marital_status == "married":
            return "Your marriage is a partnership where decisions are made together, balancing individual needs with shared goals."
        else:
            return "Your independence allows you to make decisions based on your own needs and goals, though you maintain important relationships with family and friends."
    
    def _get_political_leaning(self) -> str:
        """Infer political leaning from demographics"""
        # Simplified political inference based on demographic patterns
        conservative_factors = 0
        liberal_factors = 0
        
        # Location
        if self.config.location_type == "rural":
            conservative_factors += 2
        elif self.config.location_type == "urban":
            liberal_factors += 2
            
        # Education
        if self.config.education in ["college", "graduate"]:
            liberal_factors += 1
        else:
            conservative_factors += 1
            
        # Age
        if self.config.age > 50:
            conservative_factors += 1
        elif self.config.age < 35:
            liberal_factors += 1
            
        # Race
        if self.config.race_ethnicity in ["black", "hispanic"]:
            liberal_factors += 2
        elif self.config.race_ethnicity == "white" and self.config.location_type == "rural":
            conservative_factors += 1
        
        if conservative_factors > liberal_factors:
            return "You tend to hold conservative values, believing in personal responsibility, traditional values, and limited government intervention."
        elif liberal_factors > conservative_factors:
            return "You lean liberal, supporting social programs, diversity, and government action on issues like healthcare and climate change."
        else:
            return "You're politically moderate, seeing merit in both conservative and liberal ideas depending on the specific issue."
    
    def _get_social_values(self) -> str:
        """Get social values based on demographics"""
        if self.config.age < 35:
            return "You're comfortable with social change, supporting LGBTQ+ rights and racial justice as natural extensions of equality."
        elif self.config.age > 55:
            return "You've seen rapid social changes in your lifetime, and while you may support equality, the pace of change sometimes feels overwhelming."
        else:
            return "You balance traditional values learned from your parents with evolving social norms you see in society and media."
    
    def _get_economic_values(self) -> str:
        """Get economic values based on income and education"""
        if self.config.income in ["under_30k", "30k_50k"]:
            return "You support policies that help working families - higher minimum wage, affordable healthcare, and tax fairness."
        elif self.config.income in ["over_100k"] and self.config.education in ["college", "graduate"]:
            return "You believe in free markets but also see the need for smart regulation and investment in education and infrastructure."
        else:
            return "You want economic policies that protect your hard-earned gains while ensuring opportunities remain available for others."
    
    def _get_language_patterns(self) -> str:
        """Get language patterns based on education and region"""
        if self.config.education in ["no_hs", "high_school"]:
            return "You speak plainly and directly, using everyday language and avoiding fancy words. You value common sense over book learning."
        elif self.config.education in ["college", "graduate"]:
            return "You're articulate and can discuss complex topics, though you adjust your language based on who you're talking to."
        else:
            return "You communicate clearly, mixing casual conversation with occasional insights from your life experience."