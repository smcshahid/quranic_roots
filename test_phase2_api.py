"""
Phase 2 API Test Script
Quick verification that the FastAPI backend is working correctly
"""

import json
import time
from typing import Dict, Any

# Try to import optional dependencies
try:
    import asyncio
    import aiohttp
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# API Base URL
BASE_URL = "http://localhost:8000"

async def test_endpoint(session, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            async with session.get(url) as response:
                result = await response.json()
                status = response.status
        elif method == "POST":
            async with session.post(url, json=data) as response:
                result = await response.json()
                status = response.status
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        return {
            "endpoint": endpoint,
            "status": status,
            "response_time_ms": response_time,
            "success": status == 200,
            "data": result
        }
    
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": "ERROR",
            "response_time_ms": 0,
            "success": False,
            "error": str(e)
        }

async def run_api_tests():
    """Run comprehensive API tests"""
    if not ASYNC_AVAILABLE:
        print("❌ aiohttp not available. Install with: pip install aiohttp")
        return
        
    print("🧪 Testing Phase 2 API...")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test basic endpoints
        tests = [
            ("Root endpoint", "/"),
            ("Health check", "/health"),
            ("API docs", "/docs"),
            ("Roots list", "/api/v1/roots/?limit=5"),
            ("Frequency analysis", "/api/v1/analytics/frequency"),
            ("Statistics", "/api/v1/analytics/statistics"),
            ("Suras list", "/api/v1/suras/?limit=5"),
        ]
        
        results = []
        
        for test_name, endpoint in tests:
            print(f"Testing {test_name}...")
            result = await test_endpoint(session, endpoint)
            results.append((test_name, result))
            
            if result["success"]:
                print(f"  ✅ {result['status']} ({result['response_time_ms']}ms)")
            else:
                print(f"  ❌ {result.get('status', 'ERROR')} - {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print("=" * 50)
        
        successful = sum(1 for _, result in results if result["success"])
        total = len(results)
        success_rate = (successful / total) * 100
        
        print(f"Tests passed: {successful}/{total} ({success_rate:.1f}%)")
        
        if successful == total:
            print("🎉 All tests passed! API is working correctly.")
            
            # Show sample data
            print("\n📈 Sample API Response:")
            print("-" * 30)
            
            # Get frequency analysis sample
            freq_result = next((r[1] for r in results if "frequency" in r[0]), None)
            if freq_result and freq_result["success"]:
                data = freq_result["data"]
                if "data" in data:
                    freq_data = data["data"]
                    print(f"Total unique roots: {freq_data.get('total_unique_roots', 'N/A')}")
                    print(f"Hapax legomena: {freq_data.get('hapax_legomena_count', 'N/A')}")
                    
                    if "top_frequent_roots" in freq_data:
                        print("\nTop 3 most frequent roots:")
                        for i, root in enumerate(freq_data["top_frequent_roots"][:3], 1):
                            print(f"  {i}. {root.get('root', 'N/A')} ({root.get('total_frequency', 0)} occurrences)")
        
        else:
            print("❌ Some tests failed. Check the API server status.")
            print("\nFailed tests:")
            for test_name, result in results:
                if not result["success"]:
                    print(f"  - {test_name}: {result.get('error', 'Unknown error')}")

def run_synchronous_tests():
    """Run basic tests without async/await"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library not available. Install with: pip install requests")
        return
    
    print("🧪 Testing Phase 2 API (Synchronous)...")
    print("=" * 50)
    
    import requests
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API is responding")
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"❌ API returned status {response.status_code}")
            return
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            health = response.json()
            data_status = health.get('data_status', {})
            print(f"   Enhanced dataset: {data_status.get('enhanced_dataset', 0):,} entries")
            print(f"   Frequency analysis: {data_status.get('frequency_analysis', 0):,} roots")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test a simple API endpoint
        response = requests.get(f"{BASE_URL}/api/v1/analytics/statistics", timeout=10)
        if response.status_code == 200:
            print("✅ Analytics API working")
            stats = response.json()
            if "data" in stats and "dataset_info" in stats["data"]:
                info = stats["data"]["dataset_info"]
                print(f"   Total entries: {info.get('total_entries', 0):,}")
                print(f"   Unique roots: {info.get('total_unique_roots', 0):,}")
        else:
            print(f"❌ Analytics API failed: {response.status_code}")
        
        print("\n🎉 Basic API test completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Visit http://localhost:8000/docs for interactive API documentation")
        print("   2. Try the advanced async tests: python -c 'import test_phase2_api; import asyncio; asyncio.run(test_phase2_api.run_api_tests())'")
        print("   3. Start Phase 3 frontend development")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure the server is running:")
        print("   cd backend")
        print("   python startup.py --mode dev")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import sys
    
    print("Quranic Roots Analysis - Phase 2 API Test")
    print("="*50)
    
    # Check if we can use async
    try:
        # Try synchronous tests first (more reliable)
        run_synchronous_tests()
        
        # Offer async tests
        print(f"\n🔄 For more comprehensive tests, run:")
        print(f"python -c \"import asyncio; import {__name__.replace('.py', '')}; asyncio.run({__name__.replace('.py', '')}.run_api_tests())\"")
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        sys.exit(1) 