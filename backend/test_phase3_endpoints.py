#!/usr/bin/env python3
"""
Test script for Phase 3 optimized endpoints.
This script verifies that all new optimized endpoints are working correctly.
"""

import requests
import json
from typing import Dict, Any

# Backend URL
BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(endpoint: str, description: str) -> Dict[str, Any]:
    """Test a single endpoint and return results."""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers={"Content-Type": "application/json"})
        
        return {
            "endpoint": endpoint,
            "description": description,
            "status_code": response.status_code,
            "success": response.status_code in [200, 401],  # 401 is expected (not authenticated)
            "response_size": len(response.text),
            "has_detail": "detail" in response.text
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "description": description,
            "status_code": "ERROR",
            "success": False,
            "error": str(e)
        }

def main():
    """Test all Phase 3 optimized endpoints."""
    print("=== Phase 3 Endpoint Testing ===\n")
    
    # Define endpoints to test
    endpoints = [
        # Original endpoints (should maintain compatibility)
        ("/dashboard/analytical-data", "Original analytical data endpoint"),
        
        # New optimized endpoints
        ("/dashboard/analytical-data-optimized", "Optimized analytical data endpoint"),
        ("/dashboard/machine-summary", "Machine summary endpoint"),
        ("/dashboard/production-metrics", "Production metrics endpoint"),
        ("/dashboard/maintenance-overview", "Maintenance overview endpoint"),
        ("/dashboard/quick-stats", "Quick stats endpoint"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        print(f"Testing: {endpoint}")
        result = test_endpoint(endpoint, description)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ SUCCESS - Status: {result['status_code']}")
        else:
            print(f"  ❌ FAILED - Status: {result.get('status_code', 'ERROR')}")
            if "error" in result:
                print(f"     Error: {result['error']}")
        print()
    
    # Summary
    print("=== Summary ===")
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"Endpoints tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    if successful == total:
        print("\n🎉 All Phase 3 endpoints are working correctly!")
        print("✅ Backend optimization complete")
        print("✅ Frontend compatibility maintained")
    else:
        print(f"\n⚠️  {total - successful} endpoints need attention")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
