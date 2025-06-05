"""
Test script for document upload API
This script tests the document upload functionality with validation
"""

import requests
import os
import json
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "your_test_jwt_token_here"  # Replace with actual JWT token from Clerk

# Headers for authenticated requests
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def test_file_type_validation():
    """Test supported file types validation endpoint"""
    print("🧪 Testing file type validation endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/validate/file-types")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_test_pdf():
    """Create a simple test PDF file"""
    # Simple PDF content (minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
    return pdf_content

def test_document_upload_valid():
    """Test uploading a valid PDF document"""
    print("\n🧪 Testing valid document upload...")
    
    # Create test file
    pdf_content = create_test_pdf()
    
    files = {
        'file': ('test_document.pdf', BytesIO(pdf_content), 'application/pdf')
    }
    
    # Remove Content-Type from headers for multipart upload
    upload_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            files=files,
            headers=upload_headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return response.json().get('id')
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_document_upload_invalid_type():
    """Test uploading an invalid file type"""
    print("\n🧪 Testing invalid file type upload...")
    
    # Create test file with invalid type
    text_content = b"This is a text file, not a supported document type."
    
    files = {
        'file': ('test_file.txt', BytesIO(text_content), 'text/plain')
    }
    
    upload_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            files=files,
            headers=upload_headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_document_upload_large_file():
    """Test uploading a file that exceeds size limit"""
    print("\n🧪 Testing large file upload...")
    
    # Create a file larger than 50MB (simulated)
    large_content = b"x" * (51 * 1024 * 1024)  # 51MB
    
    files = {
        'file': ('large_file.pdf', BytesIO(large_content), 'application/pdf')
    }
    
    upload_headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            files=files,
            headers=upload_headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_list_documents():
    """Test listing user documents"""
    print("\n🧪 Testing document listing...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_document_stats():
    """Test document statistics"""
    print("\n🧪 Testing document statistics...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/stats/summary",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_document(document_id):
    """Test getting a specific document"""
    if not document_id:
        print("\n⏭️  Skipping get document test (no document ID)")
        return True
        
    print(f"\n🧪 Testing get document {document_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_delete_document(document_id):
    """Test deleting a document"""
    if not document_id:
        print("\n⏭️  Skipping delete document test (no document ID)")
        return True
        
    print(f"\n🧪 Testing delete document {document_id}...")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/documents/{document_id}",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all document upload tests"""
    print("🚀 Starting Document Upload API Tests")
    print("=" * 50)
    
    # Test configuration
    if AUTH_TOKEN == "your_test_jwt_token_here":
        print("⚠️  Warning: Please update AUTH_TOKEN with a valid JWT token from Clerk")
        print("   You can get this from your browser's developer tools after logging in")
        print()
    
    results = []
    
    # Test 1: File type validation
    results.append(("File Type Validation", test_file_type_validation()))
    
    # Test 2: Valid document upload
    document_id = test_document_upload_valid()
    results.append(("Valid Document Upload", document_id is not None))
    
    # Test 3: Invalid file type
    results.append(("Invalid File Type", test_document_upload_invalid_type()))
    
    # Test 4: Large file upload
    results.append(("Large File Upload", test_document_upload_large_file()))
    
    # Test 5: List documents
    results.append(("List Documents", test_list_documents()))
    
    # Test 6: Document statistics
    results.append(("Document Statistics", test_document_stats()))
    
    # Test 7: Get specific document
    results.append(("Get Document", test_get_document(document_id)))
    
    # Test 8: Delete document
    results.append(("Delete Document", test_delete_document(document_id)))
    
    # Print results
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Document upload API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")

if __name__ == "__main__":
    run_all_tests() 