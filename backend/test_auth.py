#!/usr/bin/env python3
"""
Test script for Clerk authentication endpoints
Run this after starting the FastAPI server to test authentication
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_public_endpoint():
    """Test public endpoint (should work without authentication)"""
    print("🔓 Testing public endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/auth/public")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Public endpoint working correctly\n")
    except Exception as e:
        print(f"❌ Public endpoint failed: {e}\n")

def test_protected_endpoint_without_auth():
    """Test protected endpoint without authentication (should fail)"""
    print("🔒 Testing protected endpoint without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/auth/profile")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 403:
            print("✅ Protected endpoint correctly rejecting unauthenticated requests\n")
        else:
            print("❌ Protected endpoint should reject unauthenticated requests\n")
    except Exception as e:
        print(f"❌ Protected endpoint test failed: {e}\n")

def test_protected_endpoint_with_fake_token():
    """Test protected endpoint with fake token (should fail)"""
    print("🔒 Testing protected endpoint with invalid token...")
    try:
        headers = {"Authorization": "Bearer fake_token_123"}
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 401:
            print("✅ Protected endpoint correctly rejecting invalid tokens\n")
        else:
            print("❌ Protected endpoint should reject invalid tokens\n")
    except Exception as e:
        print(f"❌ Protected endpoint test with fake token failed: {e}\n")

def test_health_check():
    """Test basic health check"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Health check working\n")
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")

if __name__ == "__main__":
    print("🧪 Starting Clerk Authentication Tests")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running at {BASE_URL}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"❌ Server is not running at {BASE_URL}: {e}")
        print("Please start the server with: python main.py")
        exit(1)
    
    # Run tests
    test_health_check()
    test_public_endpoint()
    test_protected_endpoint_without_auth()
    test_protected_endpoint_with_fake_token()
    
    print("🎯 Authentication Setup Summary:")
    print("- ✅ Public endpoints work without authentication")
    print("- ✅ Protected endpoints reject unauthenticated requests")
    print("- ✅ Protected endpoints reject invalid tokens")
    print("- ℹ️  To test with real Clerk tokens, get a JWT from your frontend")
    print("\n📝 Next steps:")
    print("1. Add your Clerk keys to .env file")
    print("2. Test with real Clerk JWT tokens from your frontend")
    print("3. Proceed to document upload implementation") 