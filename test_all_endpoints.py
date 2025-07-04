"""
Comprehensive API Endpoint Testing
Tests all endpoints including GET vs POST method compatibility
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method: str, endpoint: str, data: Dict = None, description: str = "") -> Dict[str, Any]:
    """Test a single endpoint with specified method"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": response.status_code,
            "success": response.status_code == 200,
            "description": description
        }
        
        if response.status_code == 200:
            try:
                result["data"] = response.json()
            except:
                result["data"] = "Non-JSON response"
        else:
            result["error"] = response.text[:200]  # First 200 chars of error
        
        return result
        
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": "ERROR",
            "success": False,
            "error": str(e),
            "description": description
        }

def main():
    """Run comprehensive endpoint tests"""
    print("🧪 Comprehensive API Endpoint Testing")
    print("=" * 60)
    
    # Define all endpoints to test
    tests = [
        # Basic endpoints
        ("GET", "/", "Root API information"),
        ("GET", "/health", "Health check"),
        ("GET", "/docs", "API documentation"),
        
        # Roots API
        ("GET", "/api/v1/roots/", "List all roots"),
        ("GET", "/api/v1/roots/?limit=5", "List 5 roots"),
        ("GET", "/api/v1/roots/?min_frequency=100", "High frequency roots"),
        ("GET", "/api/v1/roots/ktb", "Specific root details"),
        
        # Analytics API
        ("GET", "/api/v1/analytics/", "Analytics info"),
        ("GET", "/api/v1/analytics/frequency", "Frequency analysis"),
        ("GET", "/api/v1/analytics/statistics", "Dataset statistics"),
        ("GET", "/api/v1/analytics/cooccurrence", "Co-occurrence analysis"),
        ("GET", "/api/v1/analytics/thematic", "Thematic analysis"),
        
        # Suras API
        ("GET", "/api/v1/suras/", "List suras"),
        ("GET", "/api/v1/suras/?limit=5", "List 5 suras"),
        ("GET", "/api/v1/suras/1", "Al-Fatiha details"),
        
        # Export API - These should work now!
        ("GET", "/api/v1/export/", "Export info"),
        
        # Utils API
        ("GET", "/api/v1/utils/", "Utils info"),
        
        # POST endpoints
        ("POST", "/api/v1/utils/convert", {
            "text": "ktb",
            "from_format": "buckwalter", 
            "to_format": "arabic"
        }, "Text conversion"),
        
        ("POST", "/api/v1/export/", {
            "data_type": "roots",
            "format": "json",
            "filters": {"min_frequency": 50}
        }, "Export data"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_item in tests:
        if len(test_item) == 3:
            method, endpoint, description = test_item
            data = None
        elif len(test_item) == 4:
            method, endpoint, data, description = test_item
        else:
            continue  # Skip malformed test items
        
        print(f"Testing: {method} {endpoint}")
        result = test_endpoint(method, endpoint, data, description)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ {result['status']} - {description}")
            passed += 1
        else:
            print(f"  ❌ {result['status']} - {description}")
            if "error" in result:
                print(f"     Error: {result['error'][:100]}...")
            failed += 1
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Total tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! API is fully functional.")
        print("\n💡 Key endpoints to explore:")
        print("   • http://127.0.0.1:8000/docs - Interactive API docs")
        print("   • http://127.0.0.1:8000/api/v1/roots/ - Browse roots")
        print("   • http://127.0.0.1:8000/api/v1/analytics/ - Analytics info")
        print("   • http://127.0.0.1:8000/api/v1/export/ - Export options")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        print("\nFailed endpoints:")
        for result in results:
            if not result["success"]:
                print(f"   • {result['method']} {result['endpoint']} - {result.get('error', 'Unknown error')}")
    
    # Test the specific 405 issue mentioned
    print("\n🔍 Testing the specific 405 issue:")
    print("=" * 60)
    
    problematic_endpoints = [
        "/api/v1/export/",
        "/api/v1/analytics/",
        "/api/v1/utils/",
        "/api/v1/roots/"
    ]
    
    for endpoint in problematic_endpoints:
        result = test_endpoint("GET", endpoint, description="Browser access test")
        if result["success"]:
            print(f"✅ {endpoint} - Now accessible from browser!")
        else:
            print(f"❌ {endpoint} - Status: {result['status']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed: {e}") 