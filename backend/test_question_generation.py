"""
Test script for question generation functionality with Ollama
"""

import asyncio
import logging
import json
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama_service():
    """Test Ollama service functionality"""
    print("\n" + "="*60)
    print("🔧 TESTING OLLAMA SERVICE")
    print("="*60)
    
    try:
        from app.services.ollama_service import ollama_service
        
        # Test 1: Health check
        print("\n1️⃣ Testing Ollama health check...")
        health = ollama_service.health_check()
        print(f"   Health status: {'✅ Healthy' if health else '❌ Unhealthy'}")
        
        if not health:
            print("   ⚠️  Ollama not available. Make sure it's running: `ollama serve`")
            return False
        
        # Test 2: Available models
        print("\n2️⃣ Testing available models...")
        models = ollama_service.get_recommended_models()
        print(f"   Available models: {models.get('available', [])}")
        print(f"   Default model: {models.get('current_default')}")
        
        # Test 3: Simple generation
        print("\n3️⃣ Testing simple text generation...")
        result = ollama_service.generate_response(
            prompt="What is machine learning?",
            temperature=0.5,
            max_tokens=100
        )
        
        if result["success"]:
            print(f"   ✅ Generation successful!")
            print(f"   Model: {result.get('model')}")
            print(f"   Time: {result.get('generation_time', 0):.2f}s")
            print(f"   Tokens: {result.get('total_tokens', 0)}")
            print(f"   Response preview: {result.get('content', '')[:200]}...")
        else:
            print(f"   ❌ Generation failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama service test failed: {e}")
        return False

def test_question_generation_service():
    """Test question generation service"""
    print("\n" + "="*60)
    print("📚 TESTING QUESTION GENERATION SERVICE")
    print("="*60)
    
    try:
        from app.services.question_generation_service import question_generation_service
        
        # Test 1: Service initialization
        print("\n1️⃣ Testing service initialization...")
        supported_types = question_generation_service.get_question_types()
        bloom_levels = question_generation_service.get_bloom_levels()
        
        print(f"   Supported question types: {supported_types}")
        print(f"   Supported Bloom levels: {bloom_levels}")
        
        # Test 2: Sample content for testing
        print("\n2️⃣ Testing question generation with sample content...")
        
        sample_chunks = [
            {
                "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It involves algorithms that can identify patterns in data and make predictions or classifications based on those patterns.",
                "metadata": {
                    "filename": "ml_basics.pdf",
                    "page_number": 1,
                    "document_id": "test-doc-1"
                }
            },
            {
                "text": "There are three main types of machine learning: supervised learning, where the algorithm learns from labeled training data; unsupervised learning, where the algorithm finds patterns in unlabeled data; and reinforcement learning, where the algorithm learns through trial and error by receiving rewards or penalties.",
                "metadata": {
                    "filename": "ml_basics.pdf", 
                    "page_number": 2,
                    "document_id": "test-doc-1"
                }
            }
        ]
        
        # Test different question types
        test_cases = [
            {
                "type": "multiple_choice",
                "bloom": "understand",
                "difficulty": "intermediate",
                "num": 2
            },
            {
                "type": "mixed",
                "bloom": "remember",
                "difficulty": "basic",
                "num": 3
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test Case {i}: {test_case['type']} questions")
            
            result = question_generation_service.generate_questions(
                content_chunks=sample_chunks,
                question_type=test_case["type"],
                bloom_level=test_case["bloom"],
                difficulty=test_case["difficulty"],
                num_questions=test_case["num"],
                user_id="test-user"
            )
            
            if result["success"]:
                questions = result["questions"]
                metadata = result["metadata"]
                
                print(f"   ✅ Generated {len(questions)} questions")
                print(f"   Model: {metadata.get('model')}")
                print(f"   Generation time: {metadata.get('generation_time', 0):.2f}s")
                
                # Show first question as example
                if questions:
                    first_q = questions[0]
                    print(f"   Example question: {first_q.get('question', '')[:100]}...")
                    print(f"   Type: {first_q.get('type')}")
                    print(f"   Bloom level: {first_q.get('bloom_level')}")
                    
                    # Show options for MCQ
                    options = first_q.get('options')
                    if options:
                        if isinstance(options, dict):
                            print(f"   Options: {list(options.keys())}")
                        elif isinstance(options, list):
                            print(f"   Options: {options}")
                        else:
                            print(f"   Options: {options}")
            else:
                print(f"   ❌ Generation failed: {result.get('error')}")
                
        return True
        
    except Exception as e:
        print(f"❌ Question generation service test failed: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions for Ollama"""
    print("\n" + "="*60)
    print("📋 OLLAMA SETUP INSTRUCTIONS")
    print("="*60)
    
    print("""
To use this question generation system, you need to set up Ollama:

1️⃣ Install Ollama:
   • Visit: https://ollama.ai/
   • Download and install for your platform

2️⃣ Start Ollama service:
   • Run: `ollama serve` (in terminal)
   • Should start on http://localhost:11434

3️⃣ Pull recommended models:
   • DeepSeek R1 1.5B: `ollama pull deepseek-r1:1.5b`
   • DeepSeek R1 7B: `ollama pull deepseek-r1:7b`
   • Llama 3.2 3B: `ollama pull llama3.2:3b`
   • Llama 3.2 1B: `ollama pull llama3.2:1b`

4️⃣ Verify installation:
   • Run: `ollama list`
   • Should show installed models

💡 Model Recommendations:
   • For speed: deepseek-r1:1.5b or llama3.2:1b
   • For quality: deepseek-r1:7b or llama3.2:3b
   • For balance: llama3.2:3b (recommended default)

🚀 Start small with 1B-3B models, then upgrade as needed!
""")

async def main():
    """Run all tests"""
    print("🚀 QUESTION GENERATION SYSTEM TESTS")
    print("="*60)
    
    # Print setup instructions first
    print_setup_instructions()
    
    tests = [
        ("Ollama Service", test_ollama_service),
        ("Question Generation Service", test_question_generation_service)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} tests...")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Question generation system is ready!")
    else:
        print("\n⚠️  Some tests failed. Check setup and try again.")
        print("\n💡 Most common issues:")
        print("   • Ollama not running: `ollama serve`")
        print("   • Models not downloaded: `ollama pull <model>`")

if __name__ == "__main__":
    asyncio.run(main()) 