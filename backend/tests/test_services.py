"""
Test suite for services layer.
Tests all service classes for functionality, performance, and reliability.
"""

import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from tests.conftest import (
    get_test_engine, get_test_db, TestDataFactory, PerformanceTimer, TestConfig
)
from services.analytics_service import AnalyticsService
from services.maintenance_service import MaintenanceService
from services.machine_service import MachineDataService

class TestAnalyticsService(unittest.TestCase):
    """Test cases for AnalyticsService."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        self.service = AnalyticsService()
        
        # Create test data
        self.test_data = TestDataFactory.create_comprehensive_test_data(
            self.db, "test_machine_1"
        )
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def test_get_optimized_oee(self):
        """Test optimized OEE calculation."""
        start_time = datetime.now(timezone.utc) - timedelta(days=2)
        end_time = datetime.now(timezone.utc)
        
        with PerformanceTimer() as timer:
            result = self.service.get_optimized_oee(
                self.db, 
                machine_ids=["test_machine_1"],
                start_time=start_time,
                end_time=end_time
            )
        
        # Verify structure
        self.assertIn("oee", result)
        self.assertIn("availability", result)
        self.assertIn("performance", result)
        self.assertIn("quality", result)
        
        # Verify values are reasonable
        for key, value in result.items():
            self.assertIsInstance(value, (int, float))
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 100)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"OEE calculation: {timer.elapsed_ms:.2f}ms")
    
    def test_get_optimized_utilization(self):
        """Test optimized utilization calculation."""
        start_time = datetime.now(timezone.utc) - timedelta(days=2)
        end_time = datetime.now(timezone.utc)
        
        with PerformanceTimer() as timer:
            result = self.service.get_optimized_utilization(
                self.db,
                machine_ids=["test_machine_1"],
                start_time=start_time,
                end_time=end_time
            )
        
        # Verify structure
        expected_fields = [
            "total_time_seconds", "productive_uptime_seconds",
            "unproductive_downtime_seconds", "productive_downtime_seconds",
            "utilization_percentage"
        ]
        for field in expected_fields:
            self.assertIn(field, result)
        
        # Verify values are reasonable
        total_time = result["total_time_seconds"]
        if total_time > 0:
            utilization = result["utilization_percentage"]
            self.assertGreaterEqual(utilization, 0)
            self.assertLessEqual(utilization, 100)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Utilization calculation: {timer.elapsed_ms:.2f}ms")
    
    def test_get_optimized_downtime_analysis(self):
        """Test optimized downtime analysis."""
        start_time = datetime.now(timezone.utc) - timedelta(days=2)
        end_time = datetime.now(timezone.utc)
        
        with PerformanceTimer() as timer:
            result = self.service.get_optimized_downtime_analysis(
                self.db,
                machine_ids=["test_machine_1"],
                start_time=start_time,
                end_time=end_time,
                excessive_threshold=1000
            )
        
        # Verify structure
        self.assertIn("excessive_downtimes", result)
        self.assertIn("recurring_downtime_reasons", result)
        self.assertIsInstance(result["excessive_downtimes"], list)
        self.assertIsInstance(result["recurring_downtime_reasons"], dict)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD)
        print(f"Downtime analysis: {timer.elapsed_ms:.2f}ms")
    
    def test_get_machine_performance_summary(self):
        """Test machine performance summary."""
        with PerformanceTimer() as timer:
            result = self.service.get_machine_performance_summary(
                self.db,
                machine_ids=["test_machine_1"],
                hours_back=24
            )
        
        # Verify structure
        self.assertIsInstance(result, list)
        if result:
            machine = result[0]
            expected_fields = [
                "machine_id", "machine_name", "utilization_percentage",
                "total_cuts", "total_time_hours", "uptime_hours",
                "downtime_events", "current_status"
            ]
            for field in expected_fields:
                self.assertIn(field, machine)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD)
        print(f"Performance summary: {timer.elapsed_ms:.2f}ms")
    
    def test_get_real_time_metrics(self):
        """Test real-time metrics calculation."""
        with PerformanceTimer() as timer:
            result = self.service.get_real_time_metrics(self.db)
        
        # Verify structure
        expected_fields = [
            "total_machines", "active_machines", "today_total_cuts",
            "open_tickets", "high_priority_tickets", "overall_utilization",
            "last_updated"
        ]
        for field in expected_fields:
            self.assertIn(field, result)
        
        # Verify performance (should be very fast)
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Real-time metrics: {timer.elapsed_ms:.2f}ms")
    
    def test_get_trend_data(self):
        """Test trend data calculation."""
        with PerformanceTimer() as timer:
            result = self.service.get_trend_data(
                self.db,
                machine_ids=["test_machine_1"],
                days_back=7,
                interval="daily"
            )
        
        # Verify structure
        self.assertIsInstance(result, list)
        for trend in result:
            expected_fields = [
                "timestamp", "utilization_percentage", "total_events",
                "uptime_hours", "total_time_hours"
            ]
            for field in expected_fields:
                self.assertIn(field, trend)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD)
        print(f"Trend data: {timer.elapsed_ms:.2f}ms")



class TestMaintenanceService(unittest.TestCase):
    """Test cases for MaintenanceService."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        self.service = MaintenanceService()
        
        # Create test data
        TestDataFactory.create_maintenance_ticket(self.db, "test_machine", "Open", "High")
        TestDataFactory.create_maintenance_ticket(self.db, "test_machine", "Closed", "Medium")
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def test_get_ticket_statistics(self):
        """Test ticket statistics calculation."""
        with PerformanceTimer() as timer:
            result = self.service.get_ticket_statistics(self.db)
        
        # Verify we get some statistics back
        self.assertIsInstance(result, dict)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Ticket statistics: {timer.elapsed_ms:.2f}ms")
    
    def test_get_tickets_by_machine(self):
        """Test getting tickets by machine."""
        with PerformanceTimer() as timer:
            result = self.service.get_tickets_by_machine(self.db, "test_machine")
        
        # Verify we get a list back
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Tickets by machine: {timer.elapsed_ms:.2f}ms")

class TestMachineService(unittest.TestCase):
    """Test cases for MachineService."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        self.service = MachineDataService()
        
        # Create test data
        TestDataFactory.create_cut_event(
            self.db, "test_machine", datetime.now(timezone.utc) - timedelta(minutes=5)
        )
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def test_get_machine_status(self):
        """Test machine status retrieval."""
        with PerformanceTimer() as timer:
            result = self.service.get_machine_status(self.db, "test_machine")
        
        # Verify we get a dictionary back
        self.assertIsInstance(result, dict)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Machine status: {timer.elapsed_ms:.2f}ms")



def run_service_tests():
    """Run all service tests."""
    test_classes = [
        TestAnalyticsService,
        TestMaintenanceService,
        TestMachineService,
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    run_service_tests()
