"""
Test suite for optimized analytics endpoints.
Tests performance, accuracy, and reliability of the new analytics service.
"""

import unittest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from tests.conftest import (
    get_test_engine, get_test_db, get_test_client, get_auth_headers,
    TestDataFactory, PerformanceTimer, TestConfig
)

class TestAnalyticsOptimized(unittest.TestCase):
    """Test cases for optimized analytics endpoints."""
    
    def setUp(self):
        """Set up test environment for each test."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        self.client = get_test_client(self.db)
        self.auth_headers = get_auth_headers(self.client)
        
        # Create comprehensive test data
        self.test_data = TestDataFactory.create_comprehensive_test_data(
            self.db, "test_machine_1"
        )
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def test_oee_optimized_endpoint(self):
        """Test optimized OEE calculation endpoint."""
        endpoint = "/api/v1/analytics/oee-optimized"
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1"],
                    "start_time": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    "end_time": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        required_fields = ["oee", "availability", "performance", "quality"]
        for field in required_fields:
            self.assertIn(field, data)
            self.assertIsInstance(data[field], (int, float))
            self.assertGreaterEqual(data[field], 0)
            self.assertLessEqual(data[field], 100)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD,
                       f"OEE endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"OEE endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_utilization_optimized_endpoint(self):
        """Test optimized utilization calculation endpoint."""
        endpoint = "/api/v1/analytics/utilization-optimized"
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1"],
                    "start_time": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    "end_time": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        required_fields = [
            "total_time_seconds", "productive_uptime_seconds",
            "unproductive_downtime_seconds", "productive_downtime_seconds",
            "utilization_percentage"
        ]
        for field in required_fields:
            self.assertIn(field, data)
            self.assertIsInstance(data[field], (int, float))
            self.assertGreaterEqual(data[field], 0)
        
        # Verify logical consistency
        total_time = data["total_time_seconds"]
        if total_time > 0:
            component_sum = (
                data["productive_uptime_seconds"] + 
                data["unproductive_downtime_seconds"] + 
                data["productive_downtime_seconds"]
            )
            self.assertLessEqual(component_sum, total_time * 1.1)  # Allow 10% tolerance
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD,
                       f"Utilization endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Utilization endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_downtime_analysis_optimized_endpoint(self):
        """Test optimized downtime analysis endpoint."""
        endpoint = "/api/v1/analytics/downtime-analysis-optimized"
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1"],
                    "start_time": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    "end_time": datetime.now(timezone.utc).isoformat(),
                    "excessive_downtime_threshold_seconds": 1000
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        self.assertIn("excessive_downtimes", data)
        self.assertIn("recurring_downtime_reasons", data)
        self.assertIsInstance(data["excessive_downtimes"], list)
        self.assertIsInstance(data["recurring_downtime_reasons"], dict)
        
        # Verify excessive downtimes structure if present
        for downtime in data["excessive_downtimes"]:
            required_fields = [
                "name", "machine_id", "downtime_reason_name",
                "duration_seconds", "start_timestamp", "end_timestamp"
            ]
            for field in required_fields:
                self.assertIn(field, downtime)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD,
                       f"Downtime analysis endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Downtime analysis endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_performance_summary_endpoint(self):
        """Test machine performance summary endpoint."""
        endpoint = "/api/v1/analytics/performance-summary"
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1"],
                    "hours_back": 24
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        self.assertIn("machines", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["machines"], list)
        self.assertIsInstance(data["summary"], dict)
        
        # Verify summary structure
        summary_fields = ["total_machines", "avg_utilization", "total_cuts", "total_downtime_events"]
        for field in summary_fields:
            self.assertIn(field, data["summary"])
        
        # Verify machine data structure
        for machine in data["machines"]:
            machine_fields = [
                "machine_id", "machine_name", "utilization_percentage",
                "total_cuts", "total_time_hours", "uptime_hours",
                "downtime_events", "current_status"
            ]
            for field in machine_fields:
                self.assertIn(field, machine)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD,
                       f"Performance summary endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Performance summary endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_real_time_metrics_endpoint(self):
        """Test real-time metrics endpoint."""
        endpoint = "/api/v1/analytics/real-time-metrics"
        
        with PerformanceTimer() as timer:
            response = self.client.get(endpoint, headers=self.auth_headers)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        required_fields = [
            "total_machines", "active_machines", "today_total_cuts",
            "open_tickets", "high_priority_tickets", "overall_utilization",
            "last_updated"
        ]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Verify data types and ranges
        self.assertIsInstance(data["total_machines"], int)
        self.assertIsInstance(data["active_machines"], int)
        self.assertIsInstance(data["today_total_cuts"], int)
        self.assertIsInstance(data["open_tickets"], int)
        self.assertIsInstance(data["high_priority_tickets"], int)
        self.assertIsInstance(data["overall_utilization"], (int, float))
        
        # Verify ranges
        self.assertGreaterEqual(data["active_machines"], 0)
        self.assertLessEqual(data["active_machines"], data["total_machines"])
        self.assertGreaterEqual(data["overall_utilization"], 0)
        self.assertLessEqual(data["overall_utilization"], 100)
        
        # Verify performance (should be very fast)
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD,
                       f"Real-time metrics endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Real-time metrics endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_trend_data_endpoint(self):
        """Test trend data endpoint."""
        endpoint = "/api/v1/analytics/trends"
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1"],
                    "days_back": 7,
                    "interval": "daily"
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        self.assertIn("trends", data)
        self.assertIn("period", data)
        self.assertIsInstance(data["trends"], list)
        self.assertIsInstance(data["period"], dict)
        
        # Verify period information
        period_fields = ["days_back", "interval", "data_points"]
        for field in period_fields:
            self.assertIn(field, data["period"])
        
        # Verify trend data structure
        for trend in data["trends"]:
            trend_fields = [
                "timestamp", "utilization_percentage", "total_events",
                "uptime_hours", "total_time_hours"
            ]
            for field in trend_fields:
                self.assertIn(field, trend)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD,
                       f"Trend data endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Trend data endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_machine_comparison_endpoint(self):
        """Test machine comparison endpoint."""
        endpoint = "/api/v1/analytics/machine-comparison"
        
        # Create data for multiple machines
        TestDataFactory.create_comprehensive_test_data(self.db, "test_machine_2")
        TestDataFactory.create_comprehensive_test_data(self.db, "test_machine_3")
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1", "test_machine_2", "test_machine_3"],
                    "metric": "utilization"
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        self.assertIn("metric", data)
        self.assertIn("machines", data)
        self.assertIn("statistics", data)
        
        # Verify machines are ranked
        machines = data["machines"]
        self.assertGreater(len(machines), 0)
        
        for i, machine in enumerate(machines):
            self.assertEqual(machine["rank"], i + 1)
            self.assertIn("machine_id", machine)
            self.assertIn("machine_name", machine)
            self.assertIn("value", machine)
        
        # Verify statistics
        stats = data["statistics"]
        stat_fields = ["highest", "lowest", "average"]
        for field in stat_fields:
            self.assertIn(field, stats)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD,
                       f"Machine comparison endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Machine comparison endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_efficiency_insights_endpoint(self):
        """Test efficiency insights endpoint."""
        endpoint = "/api/v1/analytics/efficiency-insights"
        
        with PerformanceTimer() as timer:
            response = self.client.get(
                endpoint,
                headers=self.auth_headers,
                params={
                    "machine_ids": ["test_machine_1"],
                    "hours_back": 48
                }
            )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify structure
        self.assertIn("machine_insights", data)
        self.assertIn("fleet_insights", data)
        self.assertIn("summary", data)
        
        # Verify machine insights structure
        for machine_insight in data["machine_insights"]:
            required_fields = ["machine_id", "machine_name", "insights", "performance_score"]
            for field in required_fields:
                self.assertIn(field, machine_insight)
            
            # Verify performance score is reasonable
            score = machine_insight["performance_score"]
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
        
        # Verify summary structure
        summary_fields = ["period_hours", "machines_analyzed", "avg_performance_score"]
        for field in summary_fields:
            self.assertIn(field, data["summary"])
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.SLOW_ENDPOINT_THRESHOLD,
                       f"Efficiency insights endpoint too slow: {timer.elapsed_ms}ms")
        
        print(f"Efficiency insights endpoint performance: {timer.elapsed_ms:.2f}ms")
    
    def test_endpoint_with_filters(self):
        """Test endpoints with various filter combinations."""
        # Test shift filter
        response = self.client.get(
            "/api/v1/analytics/oee-optimized",
            headers=self.auth_headers,
            params={
                "shift": "DAY",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assertEqual(response.status_code, 200)
        
        # Test day of week filter
        response = self.client.get(
            "/api/v1/analytics/utilization-optimized",
            headers=self.auth_headers,
            params={
                "day_of_week": "MONDAY",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assertEqual(response.status_code, 200)
        
        # Test multiple machine filter
        response = self.client.get(
            "/api/v1/analytics/downtime-analysis-optimized",
            headers=self.auth_headers,
            params={
                "machine_ids": ["test_machine_1", "test_machine_2"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assertEqual(response.status_code, 200)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid date format
        response = self.client.get(
            "/api/v1/analytics/oee-optimized",
            headers=self.auth_headers,
            params={
                "start_time": "invalid-date",
                "end_time": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Test invalid metric for comparison
        response = self.client.get(
            "/api/v1/analytics/machine-comparison",
            headers=self.auth_headers,
            params={"metric": "invalid_metric"}
        )
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Test invalid interval for trends
        response = self.client.get(
            "/api/v1/analytics/trends",
            headers=self.auth_headers,
            params={"interval": "invalid_interval"}
        )
        self.assertEqual(response.status_code, 422)  # Validation error

def run_analytics_tests():
    """Run all analytics tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)

if __name__ == "__main__":
    run_analytics_tests()
