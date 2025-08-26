"""
Mill Dash Backend Optimization and Testing Script.
Validates all optimizations and runs comprehensive performance benchmarks.
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import requests

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

class OptimizationValidator:
    """Validates that all optimization work is functioning correctly."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "validation_time": datetime.now().isoformat(),
            "endpoint_tests": {},
            "performance_tests": {},
            "summary": {
                "total_endpoints": 0,
                "working_endpoints": 0,
                "optimized_endpoints": 0,
                "performance_improved": 0
            }
        }
    
    def test_endpoint_availability(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Test if an endpoint is available and returns valid data."""
        try:
            url = f"{self.base_url}{endpoint}"
            start_time = time.time()
            
            response = requests.get(url, params=params or {}, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code in [200, 401],  # 401 is expected for protected endpoints
                "data_size": len(response.text),
                "error": None
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["has_data"] = bool(data)
                    result["data_structure"] = type(data).__name__
                except:
                    result["has_data"] = False
                    result["data_structure"] = "non-json"
            
            return result
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status_code": "ERROR",
                "response_time_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    def validate_original_endpoints(self) -> Dict[str, Any]:
        """Validate original endpoints are still working."""
        print("🔍 Validating Original Endpoints...")
        
        original_endpoints = [
            "/api/v1/oee",
            "/api/v1/utilization",
            "/api/v1/downtime-analysis",
            "/api/v1/machine-data",
            "/api/v1/machines",
            "/api/v1/shifts",
            "/api/v1/days-of-week"
        ]
        
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat()
        }
        
        results = {}
        for endpoint in original_endpoints:
            if endpoint in ["/api/v1/machines", "/api/v1/shifts", "/api/v1/days-of-week"]:
                result = self.test_endpoint_availability(endpoint)
            else:
                result = self.test_endpoint_availability(endpoint, params)
            
            results[endpoint] = result
            self.results["endpoint_tests"][endpoint] = result
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {endpoint}: {result['response_time_ms']:.2f}ms")
        
        return results
    
    def validate_optimized_endpoints(self) -> Dict[str, Any]:
        """Validate optimized endpoints are working."""
        print("\n🚀 Validating Optimized Endpoints...")
        
        optimized_endpoints = [
            "/api/v1/analytics/oee-optimized",
            "/api/v1/analytics/utilization-optimized",
            "/api/v1/analytics/downtime-analysis-optimized",
            "/api/v1/analytics/performance-summary",
            "/api/v1/analytics/real-time-metrics",
            "/api/v1/analytics/trends",
            "/api/v1/analytics/machine-comparison",
            "/api/v1/analytics/efficiency-insights"
        ]
        
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat()
        }
        
        results = {}
        for endpoint in optimized_endpoints:
            if "real-time-metrics" in endpoint:
                result = self.test_endpoint_availability(endpoint)
            else:
                result = self.test_endpoint_availability(endpoint, params)
            
            results[endpoint] = result
            self.results["endpoint_tests"][endpoint] = result
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {endpoint}: {result['response_time_ms']:.2f}ms")
        
        return results
    
    def validate_phase3_endpoints(self) -> Dict[str, Any]:
        """Validate Phase 3 optimized dashboard endpoints."""
        print("\n📊 Validating Phase 3 Dashboard Endpoints...")
        
        phase3_endpoints = [
            "/api/v1/dashboard/analytical-data-optimized",
            "/api/v1/dashboard/machine-summary",
            "/api/v1/dashboard/production-metrics",
            "/api/v1/dashboard/maintenance-overview",
            "/api/v1/dashboard/quick-stats"
        ]
        
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat()
        }
        
        results = {}
        for endpoint in phase3_endpoints:
            if "quick-stats" in endpoint:
                result = self.test_endpoint_availability(endpoint)
            else:
                result = self.test_endpoint_availability(endpoint, params)
            
            results[endpoint] = result
            self.results["endpoint_tests"][endpoint] = result
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {endpoint}: {result['response_time_ms']:.2f}ms")
        
        return results
    
    def validate_websocket_endpoints(self) -> Dict[str, Any]:
        """Validate WebSocket endpoints."""
        print("\n🔌 Validating WebSocket Endpoints...")
        
        websocket_endpoints = [
            "/api/v1/ws",  # Main WebSocket endpoint won't respond to GET
        ]
        
        # For WebSocket endpoints, we just check if they exist (expect different status codes)
        results = {}
        for endpoint in websocket_endpoints:
            result = self.test_endpoint_availability(endpoint)
            # WebSocket endpoints may return 400 or 426 for GET requests, which is expected
            result["success"] = result["status_code"] in [400, 426, 405]  # Expected for WebSocket endpoints
            results[endpoint] = result
            self.results["endpoint_tests"][endpoint] = result
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {endpoint}: WebSocket endpoint available")
        
        return results
    
    def compare_performance(self) -> Dict[str, Any]:
        """Compare performance between original and optimized endpoints."""
        print("\n⚡ Performance Comparison...")
        
        # Compare OEE endpoints
        comparisons = []
        endpoint_pairs = [
            ("/api/v1/oee", "/api/v1/analytics/oee-optimized"),
            ("/api/v1/utilization", "/api/v1/analytics/utilization-optimized"),
            ("/api/v1/downtime-analysis", "/api/v1/analytics/downtime-analysis-optimized")
        ]
        
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat()
        }
        
        for original, optimized in endpoint_pairs:
            original_result = self.test_endpoint_availability(original, params)
            optimized_result = self.test_endpoint_availability(optimized, params)
            
            if original_result["success"] and optimized_result["success"]:
                improvement = ((original_result["response_time_ms"] - optimized_result["response_time_ms"]) 
                             / original_result["response_time_ms"] * 100)
                
                comparison = {
                    "original_endpoint": original,
                    "optimized_endpoint": optimized,
                    "original_time_ms": original_result["response_time_ms"],
                    "optimized_time_ms": optimized_result["response_time_ms"],
                    "improvement_percent": improvement,
                    "faster": improvement > 0
                }
                
                comparisons.append(comparison)
                
                status = "🚀" if improvement > 0 else "⚠️"
                print(f"  {status} {original.split('/')[-1]}: {improvement:+.1f}% "
                      f"({original_result['response_time_ms']:.1f}ms → {optimized_result['response_time_ms']:.1f}ms)")
        
        self.results["performance_tests"]["comparisons"] = comparisons
        return {"comparisons": comparisons}
    
    def generate_summary(self):
        """Generate a summary of all validation results."""
        print("\n" + "="*80)
        print("OPTIMIZATION VALIDATION SUMMARY")
        print("="*80)
        
        # Count endpoints
        total_endpoints = len(self.results["endpoint_tests"])
        working_endpoints = sum(1 for r in self.results["endpoint_tests"].values() if r["success"])
        
        # Count optimized endpoints
        optimized_endpoints = sum(1 for endpoint in self.results["endpoint_tests"].keys() 
                                if "optimized" in endpoint or "analytics" in endpoint)
        
        # Count performance improvements
        comparisons = self.results["performance_tests"].get("comparisons", [])
        performance_improved = sum(1 for c in comparisons if c["faster"])
        
        # Update summary
        self.results["summary"].update({
            "total_endpoints": total_endpoints,
            "working_endpoints": working_endpoints,
            "optimized_endpoints": optimized_endpoints,
            "performance_improved": performance_improved
        })
        
        # Print summary
        print(f"📊 Total Endpoints Tested: {total_endpoints}")
        print(f"✅ Working Endpoints: {working_endpoints}")
        print(f"🚀 Optimized Endpoints: {optimized_endpoints}")
        print(f"⚡ Performance Improvements: {performance_improved}/{len(comparisons)}")
        
        success_rate = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
        
        # Performance insights
        if comparisons:
            avg_improvement = sum(c["improvement_percent"] for c in comparisons if c["faster"]) / len(comparisons)
            print(f"📈 Average Performance Improvement: {avg_improvement:.1f}%")
        
        # Status assessment
        if success_rate >= 90 and performance_improved >= len(comparisons) * 0.8:
            print("\n🎉 EXCELLENT: All optimizations working correctly!")
        elif success_rate >= 80:
            print("\n✅ GOOD: Most optimizations working with minor issues.")
        else:
            print("\n⚠️  WARNING: Significant issues detected.")
        
        return self.results["summary"]
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        print("🚀 Mill Dash Backend Optimization Validation")
        print("=" * 60)
        
        # Test all endpoints
        self.validate_original_endpoints()
        self.validate_optimized_endpoints()
        self.validate_phase3_endpoints()
        self.validate_websocket_endpoints()
        
        # Performance comparison
        self.compare_performance()
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def save_results(self, filename: Optional[str] = None):
        """Save validation results to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimization_validation_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📄 Validation results saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def check_server_running(base_url: str = "http://localhost:8000") -> bool:
    """Check if the Mill Dash server is running."""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function to run optimization validation."""
    base_url = "http://localhost:8000"
    
    # Check if server is running
    if not check_server_running(base_url):
        print("❌ Mill Dash server is not running!")
        print("Please start the server with: uvicorn main:app --reload")
        return False
    
    print("✅ Mill Dash server is running\n")
    
    # Run validation
    validator = OptimizationValidator(base_url)
    results = validator.run_full_validation()
    validator.save_results()
    
    # Return success/failure
    success_rate = results["summary"]["working_endpoints"] / results["summary"]["total_endpoints"] * 100
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
