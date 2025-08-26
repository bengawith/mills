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
from services.production_service import ProductionService
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

class TestProductionService(unittest.TestCase):
    """Test cases for ProductionService."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        self.service = ProductionService()
        
        # Create test data
        for i in range(5):
            TestDataFactory.create_cut_event(
                self.db, "test_machine", 
                datetime.now(timezone.utc) - timedelta(hours=i), 10
            )
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def test_get_production_summary(self):
        """Test production summary calculation."""
        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc)
        
        with PerformanceTimer() as timer:
            result = self.service.get_production_summary(
                self.db, "test_machine", start_date, end_date
            )
        
        # Verify structure
        expected_fields = ["total_cuts", "total_events", "cut_frequency"]
        for field in expected_fields:
            self.assertIn(field, result)
        
        # Verify values
        self.assertGreaterEqual(result["total_cuts"], 0)
        self.assertGreaterEqual(result["total_events"], 0)
        self.assertGreaterEqual(result["cut_frequency"], 0)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Production summary: {timer.elapsed_ms:.2f}ms")
    
    def test_get_daily_production(self):
        """Test daily production data."""
        date = datetime.now(timezone.utc)
        
        with PerformanceTimer() as timer:
            result = self.service.get_daily_production(self.db, date, "test_machine")
        
        # Verify structure
        expected_fields = ["total_cuts", "total_events", "cut_frequency"]
        for field in expected_fields:
            self.assertIn(field, result)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Daily production: {timer.elapsed_ms:.2f}ms")
    
    def test_get_machine_utilization(self):
        """Test machine utilization calculation."""
        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc)
        
        with PerformanceTimer() as timer:
            result = self.service.get_machine_utilization(
                self.db, "test_machine", start_date, end_date
            )
        
        # Verify structure
        expected_fields = ["utilization_percentage", "total_cuts", "total_period_hours"]
        for field in expected_fields:
            self.assertIn(field, result)
        
        # Verify values
        self.assertGreaterEqual(result["utilization_percentage"], 0)
        self.assertLessEqual(result["utilization_percentage"], 100)
        
        # Verify performance
        self.assertLess(timer.elapsed_ms, TestConfig.FAST_ENDPOINT_THRESHOLD)
        print(f"Machine utilization: {timer.elapsed_ms:.2f}ms")

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

class TestServiceIntegration(unittest.TestCase):
    """Integration tests across multiple services."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = get_test_engine()
        self.db_gen = get_test_db(self.engine)
        self.db = next(self.db_gen)
        
        # Initialize all services
        self.analytics_service = AnalyticsService()
        self.production_service = ProductionService()
        self.maintenance_service = MaintenanceService()
        self.machine_service = MachineDataService()
        
        # Create comprehensive test data
        TestDataFactory.create_comprehensive_test_data(self.db, "test_machine_1")
        TestDataFactory.create_comprehensive_test_data(self.db, "test_machine_2")
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            next(self.db_gen)
        except StopIteration:
            pass
    
    def test_cross_service_data_consistency(self):
        """Test data consistency across different services."""
        machine_ids = ["test_machine_1", "test_machine_2"]
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
        end_time = datetime.now(timezone.utc)
        
        # Get data from different services
        analytics_summary = self.analytics_service.get_machine_performance_summary(
            self.db, machine_ids, 24
        )
        
        for machine_id in machine_ids:
            production_summary = self.production_service.get_production_summary(
                self.db, machine_id, start_time, end_time
            )
            
            machine_status = self.machine_service.get_machine_status(self.db, machine_id)
            
            # Find corresponding analytics data
            analytics_data = next(
                (m for m in analytics_summary if m["machine_id"] == machine_id), 
                None
            )
            
            if analytics_data:
                # Verify cut count consistency (within reasonable tolerance)
                analytics_cuts = analytics_data["total_cuts"]
                production_cuts = production_summary["total_cuts"]
                
                # Allow for some difference due to time window variations
                cut_difference = abs(analytics_cuts - production_cuts)
                cut_tolerance = max(analytics_cuts, production_cuts) * 0.1  # 10% tolerance
                
                self.assertLessEqual(cut_difference, cut_tolerance,
                    f"Cut count mismatch for {machine_id}: analytics={analytics_cuts}, production={production_cuts}")
    
    def test_service_performance_under_load(self):
        """Test service performance with larger datasets."""
        # Create larger dataset
        machine_id = "load_test_machine"
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Create 100 historical data points
        for i in range(100):
            TestDataFactory.create_historical_machine_data(
                self.db, machine_id, 
                base_time + timedelta(hours=i),
                3600,
                "UPTIME" if i % 3 != 0 else "DOWNTIME",
                "productive" if i % 4 != 0 else "unproductive"
            )
        
        # Create 50 cut events
        for i in range(50):
            TestDataFactory.create_cut_event(
                self.db, machine_id,
                base_time + timedelta(hours=i), 10
            )
        
        # Test analytics performance
        with PerformanceTimer() as timer:
            result = self.analytics_service.get_optimized_oee(
                self.db, [machine_id],
                base_time, datetime.now(timezone.utc)
            )
        
        # Should still be fast even with larger dataset
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD)
        print(f"OEE with large dataset: {timer.elapsed_ms:.2f}ms")
        
        # Test utilization performance
        with PerformanceTimer() as timer:
            result = self.analytics_service.get_optimized_utilization(
                self.db, [machine_id],
                base_time, datetime.now(timezone.utc)
            )
        
        self.assertLess(timer.elapsed_ms, TestConfig.MEDIUM_ENDPOINT_THRESHOLD)
        print(f"Utilization with large dataset: {timer.elapsed_ms:.2f}ms")

def run_service_tests():
    """Run all service tests."""
    test_classes = [
        TestAnalyticsService,
        TestProductionService,
        TestMaintenanceService,
        TestMachineService,
        TestServiceIntegration
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    run_service_tests()
