"""
Performance benchmark suite for endpoints.
Tests and compares performance between old and optimized endpoints.
"""

import unittest
import time
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi.testclient import TestClient

from tests.conftest import (
    get_test_engine, get_test_db, get_test_client, get_auth_headers,
    TestDataFactory, PerformanceTimer, TestConfig
)

class BenchmarkResult:
    """Container for benchmark results."""
    
    def __init__(self, name: str):
        self.name = name
        self.times = []
        self.success_count = 0
        self.error_count = 0
    
    def add_result(self, elapsed_ms: float, success: bool = True):
        """Add a benchmark result."""
        self.times.append(elapsed_ms)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    @property
    def avg_time(self) -> float:
        """Average response time."""
        return statistics.mean(self.times) if self.times else 0
    
    @property
    def median_time(self) -> float:
        """Median response time."""
        return statistics.median(self.times) if self.times else 0
    
    @property
    def min_time(self) -> float:
        """Minimum response time."""
        return min(self.times) if self.times else 0
    
    @property
    def max_time(self) -> float:
        """Maximum response time."""
        return max(self.times) if self.times else 0
    
    @property
    def success_rate(self) -> float:
        """Success rate percentage."""
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0

class EndpointPerformanceBenchmark(unittest.TestCase):
    """Performance benchmark tests for endpoints."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        self.client = get_test_client(self.db)
        self.auth_headers = get_auth_headers(self.client)
        
        # Create substantial test data for meaningful benchmarks
        self.create_benchmark_data()
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def create_benchmark_data(self):
        """Create realistic test data for benchmarking."""
        base_time = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Create data for 3 machines over 30 days
        machines = ["machine_1", "machine_2", "machine_3"]
        
        for machine_id in machines:
            # Create historical machine data (simulate 4 events per hour)
            for day in range(30):
                for hour in range(24):
                    for event in range(4):
                        timestamp = base_time + timedelta(days=day, hours=hour, minutes=event*15)
                        
                        # Mix of uptime and downtime
                        if event % 5 == 0:  # 20% downtime
                            classification = "DOWNTIME"
                            productivity = "unproductive"
                            duration = 900  # 15 minutes
                        else:
                            classification = "UPTIME"
                            productivity = "productive"
                            duration = 900  # 15 minutes
                        
                        TestDataFactory.create_historical_machine_data(
                            self.db, machine_id, timestamp, duration,
                            classification, productivity
                        )
            
            # Create cut events (simulate cuts every 30 minutes during uptime)
            for day in range(30):
                for hour in range(24):
                    timestamp = base_time + timedelta(days=day, hours=hour)
                    TestDataFactory.create_cut_event(
                        self.db, machine_id, timestamp, 30
                    )
            
            # Create some maintenance tickets
            for i in range(5):
                TestDataFactory.create_maintenance_ticket(
                    self.db, machine_id,
                    "Open" if i < 2 else "Closed",
                    "High" if i == 0 else "Medium"
                )
    
    def benchmark_endpoint(self, endpoint: str, params: Optional[dict] = None, 
                          iterations: int = 10) -> BenchmarkResult:
        """Benchmark a single endpoint."""
        result = BenchmarkResult(endpoint)
        
        for i in range(iterations):
            try:
                start_time = time.perf_counter()
                response = self.client.get(
                    endpoint,
                    headers=self.auth_headers,
                    params=params or {}
                )
                end_time = time.perf_counter()
                
                elapsed_ms = (end_time - start_time) * 1000
                success = response.status_code == 200
                
                result.add_result(elapsed_ms, success)
                
            except Exception as e:
                result.add_result(0, False)
        
        return result
    
    def test_oee_endpoint_performance(self):
        """Benchmark OEE endpoints."""
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
            "machine_ids": ["machine_1", "machine_2"]
        }
        
        # Test original endpoint
        original_result = self.benchmark_endpoint("/api/v1/oee", params)
        
        # Test optimized endpoint
        optimized_result = self.benchmark_endpoint("/api/v1/analytics/oee-optimized", params)
        
        # Print results
        print(f"\n=== OEE Endpoint Performance ===")
        print(f"Original - Avg: {original_result.avg_time:.2f}ms, "
              f"Median: {original_result.median_time:.2f}ms, "
              f"Success: {original_result.success_rate:.1f}%")
        print(f"Optimized - Avg: {optimized_result.avg_time:.2f}ms, "
              f"Median: {optimized_result.median_time:.2f}ms, "
              f"Success: {optimized_result.success_rate:.1f}%")
        
        if original_result.avg_time > 0 and optimized_result.avg_time > 0:
            improvement = (original_result.avg_time - optimized_result.avg_time) / original_result.avg_time * 100
            print(f"Performance improvement: {improvement:.1f}%")
        
        # Verify optimized version is faster (if both work)
        if original_result.success_rate > 50 and optimized_result.success_rate > 50:
            self.assertLess(optimized_result.avg_time, original_result.avg_time,
                           "Optimized endpoint should be faster")
    
    def test_utilization_endpoint_performance(self):
        """Benchmark utilization endpoints."""
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
            "machine_ids": ["machine_1", "machine_2"]
        }
        
        # Test original endpoint
        original_result = self.benchmark_endpoint("/api/v1/utilization", params)
        
        # Test optimized endpoint
        optimized_result = self.benchmark_endpoint("/api/v1/analytics/utilization-optimized", params)
        
        # Print results
        print(f"\n=== Utilization Endpoint Performance ===")
        print(f"Original - Avg: {original_result.avg_time:.2f}ms, "
              f"Median: {original_result.median_time:.2f}ms, "
              f"Success: {original_result.success_rate:.1f}%")
        print(f"Optimized - Avg: {optimized_result.avg_time:.2f}ms, "
              f"Median: {optimized_result.median_time:.2f}ms, "
              f"Success: {optimized_result.success_rate:.1f}%")
        
        if original_result.avg_time > 0 and optimized_result.avg_time > 0:
            improvement = (original_result.avg_time - optimized_result.avg_time) / original_result.avg_time * 100
            print(f"Performance improvement: {improvement:.1f}%")
    
    def test_downtime_analysis_endpoint_performance(self):
        """Benchmark downtime analysis endpoints."""
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
            "machine_ids": ["machine_1", "machine_2"],
            "excessive_downtime_threshold_seconds": 3600
        }
        
        # Test original endpoint
        original_result = self.benchmark_endpoint("/api/v1/downtime-analysis", params)
        
        # Test optimized endpoint
        optimized_result = self.benchmark_endpoint("/api/v1/analytics/downtime-analysis-optimized", params)
        
        # Print results
        print(f"\n=== Downtime Analysis Endpoint Performance ===")
        print(f"Original - Avg: {original_result.avg_time:.2f}ms, "
              f"Median: {original_result.median_time:.2f}ms, "
              f"Success: {original_result.success_rate:.1f}%")
        print(f"Optimized - Avg: {optimized_result.avg_time:.2f}ms, "
              f"Median: {optimized_result.median_time:.2f}ms, "
              f"Success: {optimized_result.success_rate:.1f}%")
        
        if original_result.avg_time > 0 and optimized_result.avg_time > 0:
            improvement = (original_result.avg_time - optimized_result.avg_time) / original_result.avg_time * 100
            print(f"Performance improvement: {improvement:.1f}%")
    
    def test_dashboard_endpoints_performance(self):
        """Benchmark dashboard endpoints."""
        params = {
            "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
            "machine_ids": ["machine_1", "machine_2", "machine_3"]
        }
        
        # Test Phase 3 optimized endpoints
        endpoints = [
            "/api/v1/dashboard/analytical-data-optimized",
            "/api/v1/dashboard/machine-summary",
            "/api/v1/dashboard/production-metrics",
            "/api/v1/dashboard/maintenance-overview",
            "/api/v1/dashboard/quick-stats"
        ]
        
        print(f"\n=== Dashboard Endpoints Performance ===")
        
        for endpoint in endpoints:
            if "quick-stats" in endpoint:
                # Quick stats doesn't need params
                result = self.benchmark_endpoint(endpoint)
            else:
                result = self.benchmark_endpoint(endpoint, params)
            
            print(f"{endpoint}")
            print(f"  Avg: {result.avg_time:.2f}ms, "
                  f"Median: {result.median_time:.2f}ms, "
                  f"Min: {result.min_time:.2f}ms, "
                  f"Max: {result.max_time:.2f}ms")
            print(f"  Success Rate: {result.success_rate:.1f}%")
            
            # Verify performance meets thresholds
            if "quick-stats" in endpoint:
                threshold = TestConfig.FAST_ENDPOINT_THRESHOLD
            else:
                threshold = TestConfig.MEDIUM_ENDPOINT_THRESHOLD
            
            self.assertLess(result.median_time, threshold,
                           f"{endpoint} median time {result.median_time:.2f}ms exceeds threshold {threshold}ms")
    
    def test_new_analytics_endpoints_performance(self):
        """Benchmark new analytics endpoints."""
        params = {
            "machine_ids": ["machine_1", "machine_2"],
            "hours_back": 24
        }
        
        # Test new analytics endpoints
        endpoints = [
            ("/api/v1/analytics/real-time-metrics", {}),
            ("/api/v1/analytics/performance-summary", params),
            ("/api/v1/analytics/trends", {"days_back": 7, "interval": "daily"}),
            ("/api/v1/analytics/machine-comparison", {"metric": "utilization"}),
            ("/api/v1/analytics/efficiency-insights", {"hours_back": 48})
        ]
        
        print(f"\n=== New Analytics Endpoints Performance ===")
        
        for endpoint, endpoint_params in endpoints:
            result = self.benchmark_endpoint(endpoint, endpoint_params)
            
            print(f"{endpoint}")
            print(f"  Avg: {result.avg_time:.2f}ms, "
                  f"Median: {result.median_time:.2f}ms, "
                  f"Min: {result.min_time:.2f}ms, "
                  f"Max: {result.max_time:.2f}ms")
            print(f"  Success Rate: {result.success_rate:.1f}%")
            
            # Verify performance meets thresholds
            if "real-time-metrics" in endpoint:
                threshold = TestConfig.FAST_ENDPOINT_THRESHOLD
            elif "efficiency-insights" in endpoint:
                threshold = TestConfig.SLOW_ENDPOINT_THRESHOLD
            else:
                threshold = TestConfig.MEDIUM_ENDPOINT_THRESHOLD
            
            self.assertLess(result.median_time, threshold,
                           f"{endpoint} median time {result.median_time:.2f}ms exceeds threshold {threshold}ms")
    
    def test_load_testing(self):
        """Test endpoint performance under concurrent load simulation."""
        # Simulate load by running multiple requests quickly
        endpoint = "/api/v1/analytics/real-time-metrics"
        
        print(f"\n=== Load Testing {endpoint} ===")
        
        # Test with increasing load
        for load_level in [1, 5, 10, 20]:
            times = []
            
            start_time = time.perf_counter()
            
            for i in range(load_level):
                with PerformanceTimer() as timer:
                    response = self.client.get(endpoint, headers=self.auth_headers)
                    if response.status_code == 200:
                        times.append(timer.elapsed_ms)
            
            total_time = time.perf_counter() - start_time
            
            if times:
                avg_response_time = statistics.mean(times)
                throughput = len(times) / total_time  # requests per second
                
                print(f"Load {load_level:2d}: Avg response {avg_response_time:6.2f}ms, "
                      f"Throughput {throughput:6.2f} req/s")
                
                # Verify performance doesn't degrade too much under load
                self.assertLess(avg_response_time, TestConfig.FAST_ENDPOINT_THRESHOLD * 2,
                               f"Response time under load too slow: {avg_response_time:.2f}ms")

def run_performance_benchmarks():
    """Run all performance benchmarks."""
    unittest.main(argv=[''], exit=False, verbosity=2)

if __name__ == "__main__":
    run_performance_benchmarks()
