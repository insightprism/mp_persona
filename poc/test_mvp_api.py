#!/usr/bin/env python3
"""
MVP API Test Script
==================

Test the FastAPI backend without the React frontend.
Demonstrates all core API functionality.
"""

import asyncio
import requests
import json
import time
from datetime import datetime

class MVPTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session_id = None
        self.personas = []
    
    def test_health_check(self):
        """Test basic health endpoint"""
        print("🔍 Testing Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server healthy - {data['status']}")
                print(f"   Services: {data['services']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def test_available_models(self):
        """Test available models endpoint"""
        print("\n🤖 Testing Available Models...")
        try:
            response = requests.get(f"{self.base_url}/api/models/available")
            if response.status_code == 200:
                data = response.json()
                print("✅ Available providers:")
                for provider, config in data["providers"].items():
                    status = "✓" if config["available"] else "✗"
                    print(f"   {status} {provider}: {config['models']}")
                return data
            else:
                print(f"❌ Models check failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Models check error: {e}")
            return None
    
    def test_create_session(self):
        """Test session creation"""
        print("\n📋 Testing Session Creation...")
        try:
            response = requests.post(f"{self.base_url}/api/sessions/")
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"✅ Session created: {self.session_id[:8]}...")
                return True
            else:
                print(f"❌ Session creation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return False
    
    def test_create_persona(self, provider="mock"):
        """Test persona creation"""
        print(f"\n🎭 Testing Persona Creation ({provider})...")
        
        persona_data = {
            "name": "Test Maria Rodriguez",
            "age": 34,
            "race_ethnicity": "hispanic",
            "gender": "female", 
            "education": "college",
            "location_type": "urban",
            "income": "50k_75k",
            "llm_provider": provider
        }
        
        # Add API key if needed
        if provider == "openai":
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                persona_data["llm_api_key"] = api_key
                persona_data["llm_model"] = "gpt-4"
            else:
                print("⚠️  No OpenAI key - using mock")
                persona_data["llm_provider"] = "mock"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/sessions/{self.session_id}/personas/",
                json=persona_data
            )
            if response.status_code == 200:
                data = response.json()
                self.personas.append(data)
                print(f"✅ Persona created: {data['name']}")
                print(f"   Provider: {data['llm_provider']} - {data['llm_model']}")
                return data
            else:
                print(f"❌ Persona creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Persona creation error: {e}")
            return None
    
    def test_chat_with_persona(self, persona_id, message):
        """Test chat functionality"""
        print(f"\n💬 Testing Chat...")
        print(f"   Question: {message}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/personas/{persona_id}/chat",
                json={"message": message}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat successful ({(end_time - start_time)*1000:.0f}ms)")
                print(f"   Response: {data['persona_response'][:100]}...")
                if data.get("usage"):
                    print(f"   Usage: {data['usage']}")
                return data
            else:
                print(f"❌ Chat failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return None
    
    def test_get_session(self):
        """Test session retrieval"""
        print(f"\n📊 Testing Session Retrieval...")
        try:
            response = requests.get(f"{self.base_url}/api/sessions/{self.session_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Session retrieved")
                print(f"   Personas: {len(data['personas'])}")
                for persona in data["personas"]:
                    print(f"   - {persona['name']} ({persona['llm_provider']})")
                return data
            else:
                print(f"❌ Session retrieval failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Session retrieval error: {e}")
            return None
    
    def test_comparison_scenario(self):
        """Test comparison across multiple personas"""
        print(f"\n📈 Testing Comparison Scenario...")
        
        # Create multiple personas with different providers
        providers = ["mock"]  # Start with mock
        
        # Add real providers if available
        import os
        if os.getenv("OPENAI_API_KEY"):
            providers.append("openai")
        
        if len(providers) == 1:
            print("ℹ️  Only mock provider available - creating multiple mock personas")
            providers = ["mock", "mock"]  # Create 2 mock personas for comparison
        
        comparison_personas = []
        for i, provider in enumerate(providers):
            name_suffix = f" {i+1}" if provider == "mock" and len([p for p in providers if p == "mock"]) > 1 else ""
            persona_data = {
                "name": f"Comparison Test{name_suffix}",
                "age": 30 + i,
                "race_ethnicity": "white",
                "gender": "female",
                "education": "college", 
                "location_type": "urban",
                "income": "50k_75k",
                "llm_provider": provider
            }
            
            if provider == "openai":
                persona_data["llm_api_key"] = os.getenv("OPENAI_API_KEY")
                persona_data["llm_model"] = "gpt-4"
            
            persona = self.test_create_persona_direct(persona_data)
            if persona:
                comparison_personas.append(persona)
        
        if len(comparison_personas) < 2:
            print("⚠️  Need at least 2 personas for comparison")
            return
        
        # Ask same question to all personas
        test_question = "What's your opinion on remote work and its impact on work-life balance?"
        print(f"\n❓ Asking all personas: {test_question}")
        
        results = []
        for persona in comparison_personas:
            result = self.test_chat_with_persona(persona["persona_id"], test_question)
            if result:
                results.append({
                    "persona": persona["name"],
                    "provider": persona["llm_provider"],
                    "response": result["persona_response"],
                    "usage": result.get("usage", {})
                })
        
        # Display comparison
        if len(results) > 1:
            print(f"\n📊 Comparison Results:")
            print("=" * 60)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['persona']} ({result['provider']}):")
                print(f"   {result['response'][:120]}...")
                if result['usage']:
                    print(f"   Usage: {result['usage']}")
                print()
    
    def test_create_persona_direct(self, persona_data):
        """Helper method to create persona directly"""
        try:
            response = requests.post(
                f"{self.base_url}/api/sessions/{self.session_id}/personas/",
                json=persona_data
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

def main():
    print("🚀 MVP Backend API Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = MVPTester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("Available Models", tester.test_available_models),
        ("Create Session", tester.test_create_session),
        ("Create Persona", lambda: tester.test_create_persona("mock")),
        ("Chat Test", lambda: tester.test_chat_with_persona(
            tester.personas[0]["persona_id"] if tester.personas else None,
            "Tell me about your background and what's important to you."
        ) if tester.personas else print("⚠️  No personas to test")),
        ("Session Retrieval", tester.test_get_session),
        ("Comparison Test", tester.test_comparison_scenario)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            if result is not False and result is not None:
                passed += 1
            elif result is False:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎯 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MVP backend is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start the frontend: ./start_frontend.sh")
        print("   2. Open http://localhost:3000")
        print("   3. Create personas and start chatting!")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure backend is running: ./start_backend.sh")
        print("   2. Check API keys are set correctly")
        print("   3. Verify Ollama is running (optional)")
    
    print(f"\n📖 Full documentation: MVP_README.md")

if __name__ == "__main__":
    main()