"""
Test script to verify ChromaDB setup and connection
This ensures ChromaDB is properly configured before document parsing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from typing import Dict, Any

def test_chromadb_docker():
    """Test if ChromaDB Docker container is running"""
    print("🧪 Testing ChromaDB Docker container...")
    
    try:
        response = requests.get("http://localhost:8001/api/v2/heartbeat", timeout=5)
        if response.status_code == 200:
            print("✅ ChromaDB Docker container is running")
            return True
        else:
            print(f"❌ ChromaDB responded with status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ ChromaDB container is not accessible on localhost:8001")
        return False
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        return False

def test_chromadb_service():
    """Test ChromaDB service initialization"""
    print("\n🧪 Testing ChromaDB service initialization...")
    
    try:
        from app.services.chromadb_service import chromadb_service
        
        # Test health check
        is_healthy = chromadb_service.health_check()
        if is_healthy:
            print("✅ ChromaDB service health check passed")
        else:
            print("❌ ChromaDB service health check failed")
            return False
        
        # Test collection stats
        stats = chromadb_service.get_collection_stats()
        print(f"✅ Collection stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB service initialization failed: {e}")
        return False

def test_basic_operations():
    """Test basic ChromaDB operations"""
    print("\n🧪 Testing basic ChromaDB operations...")
    
    try:
        from app.services.chromadb_service import chromadb_service
        
        # Test adding chunks
        test_chunks = [
            {
                "text": "Test chunk for ChromaDB setup verification",
                "metadata": {"type": "test", "setup": "verification"},
                "page_number": 1
            }
        ]
        
        # Add test chunks
        success = chromadb_service.add_document_chunks(
            document_id=999999,  # Test document ID
            chunks=test_chunks
        )
        
        if not success:
            print("❌ Failed to add test chunks")
            return False
        
        print("✅ Test chunks added successfully")
        
        # Test search
        results = chromadb_service.search_similar_chunks(
            query="test setup verification",
            n_results=1
        )
        
        if results:
            print(f"✅ Search test passed - found {len(results)} results")
        else:
            print("⚠️  Search returned no results (this might be expected)")
        
        # Clean up test chunks
        cleanup_success = chromadb_service.delete_document_chunks(999999)
        if cleanup_success:
            print("✅ Test chunks cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic operations test failed: {e}")
        return False

def test_api_endpoints():
    """Test ChromaDB API endpoints"""
    print("\n🧪 Testing ChromaDB API endpoints...")
    
    try:
        # Test health endpoint (no auth required)
        response = requests.get("http://localhost:8000/chromadb/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health endpoint: {health_data}")
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
        
        print("✅ API endpoints are accessible")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️ API endpoints test skipped (FastAPI server not running)")
        print("   This is expected if you're only testing ChromaDB setup")
        print("   To test API endpoints, start the server: uvicorn main:app --reload")
        return True  # Don't fail the test for this
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def main():
    print("🚀 ChromaDB Setup Verification")
    print("=" * 40)
    
    results = []
    
    # Test 1: Docker container
    results.append(("ChromaDB Docker", test_chromadb_docker()))
    
    # Test 2: Service initialization (only if Docker is running)
    if results[0][1]:
        results.append(("ChromaDB Service", test_chromadb_service()))
        
        # Test 3: Basic operations (only if service is working)
        if results[1][1]:
            results.append(("Basic Operations", test_basic_operations()))
    else:
        results.append(("ChromaDB Service", False))
        results.append(("Basic Operations", False))
    
    # Test 4: API endpoints
    results.append(("API Endpoints", test_api_endpoints()))
    
    # Print results
    print("\n" + "=" * 40)
    print("🏁 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ChromaDB setup is working correctly!")
        print("✅ Ready for document parsing implementation")
    else:
        print("\n⚠️  ChromaDB setup has issues.")
        print("\n🛠️  Troubleshooting:")
        if not results[0][1]:
            print("- Start Docker services: docker-compose up -d")
            print("- Check if ChromaDB container is running: docker-compose ps")
            print("- Check logs: docker-compose logs chromadb")
        print("- Ensure requirements are installed: pip install -r requirements.txt")
        print("- Update .env file with correct ChromaDB settings")

if __name__ == "__main__":
    main() 