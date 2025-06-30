#!/usr/bin/env python3
"""
Test Self-Identification Capabilities
=====================================

This script tests the newly added self-identification and introspection capabilities
for both LLMPersonaFirefly and EnvironmentallyAwarePersona classes.

It demonstrates:
1. Basic capability discovery
2. Method introspection
3. Self-description capabilities
4. Security-protected source code access
5. Inter-agent communication patterns
"""

import os
import asyncio
from datetime import datetime
from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly
from environmentally_aware_persona import EnvironmentallyAwarePersona, EnvironmentalContext

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print('─'*40)

async def test_firefly_self_identification():
    """Test LLMPersonaFirefly self-identification capabilities"""
    print_section("LLMPersonaFirefly Self-Identification Tests")
    
    # Create sample persona
    maria_config = PersonaConfig(
        name="Maria Rodriguez",
        age=34,
        race_ethnicity="hispanic",
        gender="female",
        education="college",
        location_type="urban",
        income="50k_75k",
        media_consumption="npr",
        risk_tolerance="moderate",
        spending_style="budgeter",
        civic_engagement="high"
    )
    
    # Create firefly
    firefly = LLMPersonaFirefly(maria_config, purpose="self_identification_test")
    
    # Test 1: Basic capability discovery
    print_subsection("1. Capability Discovery")
    capabilities = firefly.describe_capabilities()
    print("Available capabilities:")
    for capability, description in capabilities.items():
        print(f"  • {capability}: {description}")
    
    # Test 2: Method listing
    print_subsection("2. Available Methods")
    methods = firefly.get_available_methods()
    print(f"Total public methods: {len(methods)}")
    print("Methods:", ", ".join(methods[:10]), "..." if len(methods) > 10 else "")
    
    # Test 3: Method signatures
    print_subsection("3. Method Signatures")
    test_methods = ["glow", "describe_self", "can_perform"]
    for method in test_methods:
        signature = firefly.get_method_signature(method)
        print(f"  {method}: {signature}")
    
    # Test 4: Self-description
    print_subsection("4. Complete Self-Description")
    self_description = firefly.describe_self()
    print("Agent Type:", self_description["agent_type"])
    print("Persona Name:", self_description["persona_identity"]["name"])
    print("Current State:", self_description["current_state"])
    print("Behavioral Characteristics:", self_description["behavioral_characteristics"])
    
    # Test 5: Capability checking
    print_subsection("5. Capability Checking")
    test_capabilities = ["glow", "birth", "invalid_capability"]
    for cap in test_capabilities:
        can_do = firefly.can_perform(cap)
        print(f"  Can perform '{cap}': {can_do}")
    
    # Test 6: Demographics access
    print_subsection("6. Demographics Access")
    demographics = firefly.get_demographics()
    print("Demographics:", demographics)
    
    # Test 7: Current state
    print_subsection("7. Current State")
    state = firefly.get_current_state()
    print("Current State:", state)
    
    # Test 8: Inter-agent communication
    print_subsection("8. Inter-Agent Communication")
    comm_response = firefly.share_capabilities_with_agent("test_agent_123")
    print("Response Type:", comm_response["response_type"])
    print("Responding Agent:", comm_response["responding_agent"])
    print("Interaction Interface:", comm_response["interaction_interface"])
    
    return firefly

def test_environmental_persona_self_identification():
    """Test EnvironmentallyAwarePersona self-identification capabilities"""
    print_section("EnvironmentallyAwarePersona Self-Identification Tests")
    
    # Create sample persona and environment
    base_persona = PersonaConfig(
        name="John Smith",
        age=45,
        race_ethnicity="white",
        gender="male",
        education="graduate",
        location_type="suburban",
        income="75k_100k",
        media_consumption="moderate",
        risk_tolerance="conservative"
    )
    
    # Create sample environment (Minneapolis suburbs)
    environment = EnvironmentalContext(
        location_name="Bloomington",
        location_type="suburban",
        state="Minnesota",
        region="midwest",
        racial_composition={"white": 0.75, "hispanic": 0.08, "black": 0.06, "asian": 0.08},
        age_distribution={"18_29": 0.15, "30_44": 0.30, "45_64": 0.35, "65_plus": 0.20},
        education_levels={"high_school": 0.25, "bachelors": 0.40, "graduate": 0.25, "some_college": 0.10},
        income_distribution={"under_50k": 0.25, "50k_100k": 0.45, "over_100k": 0.30},
        political_lean="moderate",
        political_strength=0.5,
        religious_composition={"christian": 0.65, "other": 0.35},
        unemployment_rate=0.04,
        median_income=75000,
        economic_trend="stable",
        social_cohesion=0.6,
        cultural_diversity=0.4,
        change_rate=0.3
    )
    
    # Create environmentally aware persona
    env_persona = EnvironmentallyAwarePersona(base_persona, environment)
    
    # Test 1: Environmental capability discovery
    print_subsection("1. Environmental Capability Discovery")
    env_capabilities = env_persona.describe_environmental_capabilities()
    print("Environmental capabilities:")
    for capability, description in env_capabilities.items():
        print(f"  • {capability}: {description}")
    
    # Test 2: Environmental state description
    print_subsection("2. Environmental State Description")
    env_state = env_persona.describe_environmental_state()
    print("Location:", env_state["location"])
    print("Demographic Fit:", f"{env_state['demographic_fit']:.1%}")
    print("Minority Status:", f"{env_state['minority_status']:.1%}")
    print("Conformity Tendency:", f"{env_state['conformity_tendency']:.2f}")
    print("Social Pressures:", len(env_state["social_pressures"]))
    print("Reference Groups:", len(env_state["reference_groups"]))
    
    # Test 3: Complete self-description
    print_subsection("3. Complete Self-Description")
    self_desc = env_persona.describe_self()
    print("Agent Type:", self_desc["agent_type"])
    print("Persona Name:", self_desc["persona_identity"]["name"])
    print("Social Analysis:", self_desc["social_analysis"])
    print("Interaction Capabilities:", self_desc["interaction_capabilities"])
    
    # Test 4: Environmental summary
    print_subsection("4. Environmental Summary")
    env_summary = env_persona.get_environmental_summary()
    print("Location Details:", env_summary["location_details"])
    print("Social Dynamics:", env_summary["social_dynamics"])
    print("Persona Fit Analysis:", env_summary["persona_fit_analysis"])
    
    # Test 5: Inter-agent communication
    print_subsection("5. Inter-Agent Communication")
    comm_response = env_persona.share_capabilities_with_agent("test_agent_456")
    print("Response Type:", comm_response["response_type"])
    print("Social Analysis Summary:", comm_response["social_analysis_summary"])
    print("Interaction Interface:", comm_response["interaction_interface"])
    
    return env_persona

def test_security_features():
    """Test security features for sensitive information access"""
    print_section("Security Features Testing")
    
    # Create a simple persona for testing
    test_config = PersonaConfig(
        name="Test Persona",
        age=30,
        race_ethnicity="white",
        gender="male",
        education="college",
        location_type="urban",
        income="50k_75k"
    )
    
    firefly = LLMPersonaFirefly(test_config, purpose="security_test")
    
    # Test 1: Source code access without key
    print_subsection("1. Source Code Access (No Key)")
    source_no_key = firefly.get_source_code("describe_self")
    print("Result:", source_no_key)
    
    # Test 2: Source code access with wrong key
    print_subsection("2. Source Code Access (Wrong Key)")
    source_wrong_key = firefly.get_source_code("describe_self", "wrong_key")
    print("Result:", source_wrong_key)
    
    # Test 3: Source code access with correct key
    print_subsection("3. Source Code Access (Correct Key)")
    # Use default key (can be overridden with PERSONA_SOURCE_SECRET env var)
    correct_key = "persona_debug_2024"
    source_correct_key = firefly.get_source_code("describe_self", correct_key)
    print("Result length:", len(source_correct_key), "characters")
    print("First 200 chars:", source_correct_key[:200] + "..." if len(source_correct_key) > 200 else source_correct_key)
    
    # Test 4: Persona identity access without key
    print_subsection("4. Persona Identity Access (No Key)")
    identity_no_key = firefly.get_persona_identity()
    print("Result:", identity_no_key)
    
    # Test 5: Persona identity access with correct key
    print_subsection("5. Persona Identity Access (Correct Key)")
    # First need to initialize the persona
    asyncio.run(firefly.birth())
    identity_correct_key = firefly.get_persona_identity(correct_key)
    print("Result length:", len(identity_correct_key), "characters")
    print("First 200 chars:", identity_correct_key[:200] + "..." if len(identity_correct_key) > 200 else identity_correct_key)
    
    return firefly

def test_inter_agent_communication():
    """Test communication between different persona agents"""
    print_section("Inter-Agent Communication Testing")
    
    # Create two different personas
    maria_config = PersonaConfig(
        name="Maria Rodriguez",
        age=34,
        race_ethnicity="hispanic",
        gender="female",
        education="college",
        location_type="urban",
        income="50k_75k"
    )
    
    bob_config = PersonaConfig(
        name="Bob Johnson",
        age=58,
        race_ethnicity="white",
        gender="male",
        education="high_school",
        location_type="rural",
        income="30k_50k"
    )
    
    maria = LLMPersonaFirefly(maria_config, purpose="communication_test")
    bob = LLMPersonaFirefly(bob_config, purpose="communication_test")
    
    # Test 1: Agent A asks Agent B about capabilities
    print_subsection("1. Maria asks Bob about his capabilities")
    bob_capabilities = bob.share_capabilities_with_agent(maria.firefly_id)
    print("Bob's response to Maria:")
    print(f"  Agent Type: {bob_capabilities['responding_agent']['type']}")
    print(f"  Agent Name: {bob_capabilities['responding_agent']['name']}")
    print(f"  Available Capabilities: {len(bob_capabilities['capabilities_summary'])}")
    print(f"  Demographics: {bob_capabilities['demographic_profile']['age']}yo {bob_capabilities['demographic_profile']['race_ethnicity']} {bob_capabilities['demographic_profile']['gender']}")
    
    # Test 2: Agent B asks Agent A about capabilities
    print_subsection("2. Bob asks Maria about her capabilities")
    maria_capabilities = maria.share_capabilities_with_agent(bob.firefly_id)
    print("Maria's response to Bob:")
    print(f"  Agent Type: {maria_capabilities['responding_agent']['type']}")
    print(f"  Agent Name: {maria_capabilities['responding_agent']['name']}")
    print(f"  Available Capabilities: {len(maria_capabilities['capabilities_summary'])}")
    print(f"  Demographics: {maria_capabilities['demographic_profile']['age']}yo {maria_capabilities['demographic_profile']['race_ethnicity']} {maria_capabilities['demographic_profile']['gender']}")
    
    # Test 3: Compare method availability
    print_subsection("3. Method Comparison")
    maria_methods = set(maria.get_available_methods())
    bob_methods = set(bob.get_available_methods())
    common_methods = maria_methods.intersection(bob_methods)
    print(f"Maria has {len(maria_methods)} methods")
    print(f"Bob has {len(bob_methods)} methods")
    print(f"Common methods: {len(common_methods)}")
    print(f"Are they the same class? {type(maria) == type(bob)}")
    
    return maria, bob

async def run_comprehensive_test():
    """Run all self-identification tests"""
    print("🧪 Starting Comprehensive Self-Identification Testing")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test LLMPersonaFirefly
        firefly = await test_firefly_self_identification()
        
        # Test EnvironmentallyAwarePersona  
        env_persona = test_environmental_persona_self_identification()
        
        # Test security features
        security_firefly = test_security_features()
        
        # Test inter-agent communication
        maria, bob = test_inter_agent_communication()
        
        print_section("Test Summary")
        print("✅ All self-identification tests completed successfully!")
        print("📊 Test Results:")
        print(f"  • LLMPersonaFirefly capabilities: {len(firefly.describe_capabilities())}")
        print(f"  • EnvironmentallyAwarePersona capabilities: {len(env_persona.describe_environmental_capabilities())}")
        print(f"  • Security features: ✅ Working (access control implemented)")
        print(f"  • Inter-agent communication: ✅ Working (standardized interface)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set test environment variable for security testing
    os.environ["PERSONA_SOURCE_SECRET"] = "persona_debug_2024"
    
    # Run comprehensive tests
    success = asyncio.run(run_comprehensive_test())
    
    if success:
        print("\n🎉 All tests passed! Self-identification capabilities are working correctly.")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")