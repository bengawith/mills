"""
Comprehensive test runner for the entire backend.
Runs all tests and generates a detailed report.
"""

import unittest
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path so we can import modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(backend_dir))

# Import test modules
from tests.test_analytics_optimized import TestAnalyticsOptimized
from tests.test_performance_benchmark import EndpointPerformanceBenchmark

class TestSuiteRunner:
    """Comprehensive test suite runner with reporting."""
    
    def __init__(self):
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            },
            "test_suites": {},
            "performance_report": {}
        }
    
    def run_all_tests(self):
        """Run all test suites and collect results."""
        print("=" * 80)
        print("MILL DASH BACKEND COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        
        self.results["start_time"] = datetime.now()
        start_time = time.time()
        
        # Define test suites
        test_suites = [
            ("Analytics Optimized", TestAnalyticsOptimized),
            ("Performance Benchmark", EndpointPerformanceBenchmark),
        ]
        
        for suite_name, test_class in test_suites:
            print(f"\n{'-' * 60}")
            print(f"Running {suite_name} Tests")
            print(f"{'-' * 60}")
            
            suite_result = self.run_test_suite(test_class)
            self.results["test_suites"][suite_name] = suite_result
            
            # Update summary
            self.results["summary"]["total_tests"] += suite_result["total"]
            self.results["summary"]["passed"] += suite_result["passed"]
            self.results["summary"]["failed"] += suite_result["failed"]
            self.results["summary"]["errors"] += suite_result["errors"]
            self.results["summary"]["skipped"] += suite_result["skipped"]
        
        end_time = time.time()
        self.results["end_time"] = datetime.now()
        self.results["total_duration"] = end_time - start_time
        
        self.print_final_report()
        return self.results
    
    def run_test_suite(self, test_class) -> Dict[str, Any]:
        """Run a single test suite and return results."""
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        
        result = runner.run(suite)
        
        return {
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
            "failures_details": [str(failure) for failure in result.failures],
            "errors_details": [str(error) for error in result.errors]
        }
    
    def print_final_report(self):
        """Print comprehensive final report."""
        print("\n" + "=" * 80)
        print("FINAL TEST REPORT")
        print("=" * 80)
        
        # Summary
        summary = self.results["summary"]
        print(f"Total Tests Run: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Skipped: {summary['skipped']}")
        
        success_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {self.results['total_duration']:.2f} seconds")
        
        # Per-suite breakdown
        print(f"\n{'-' * 40}")
        print("Per-Suite Breakdown:")
        print(f"{'-' * 40}")
        
        for suite_name, suite_result in self.results["test_suites"].items():
            suite_success_rate = (suite_result['passed'] / suite_result['total'] * 100) if suite_result['total'] > 0 else 0
            print(f"{suite_name}:")
            print(f"  Tests: {suite_result['total']}, "
                  f"Passed: {suite_result['passed']}, "
                  f"Failed: {suite_result['failed']}, "
                  f"Errors: {suite_result['errors']}")
            print(f"  Success Rate: {suite_success_rate:.1f}%")
        
        # Failures and errors
        if summary['failed'] > 0 or summary['errors'] > 0:
            print(f"\n{'-' * 40}")
            print("Failures and Errors:")
            print(f"{'-' * 40}")
            
            for suite_name, suite_result in self.results["test_suites"].items():
                if suite_result['failures_details'] or suite_result['errors_details']:
                    print(f"\n{suite_name}:")
                    for failure in suite_result['failures_details']:
                        print(f"  FAILURE: {failure}")
                    for error in suite_result['errors_details']:
                        print(f"  ERROR: {error}")
        
        # Performance insights
        print(f"\n{'-' * 40}")
        print("Performance Insights:")
        print(f"{'-' * 40}")
        print("✓ All optimized endpoints should be faster than original endpoints")
        print("✓ Real-time endpoints should respond under 100ms")
        print("✓ Analytics endpoints should respond under 500ms")
        print("✓ Complex insights endpoints should respond under 2000ms")
        
        # Recommendations
        print(f"\n{'-' * 40}")
        print("Recommendations:")
        print(f"{'-' * 40}")
        
        if success_rate >= 95:
            print("✅ Excellent! All systems are performing optimally.")
        elif success_rate >= 80:
            print("⚠️  Good performance with some issues to address.")
        else:
            print("❌ Significant issues detected. Review failed tests.")
        
        if summary['total_tests'] < 20:
            print("💡 Consider adding more test cases for better coverage.")
        
        print("💡 Regularly run performance benchmarks to catch regressions.")
        print("💡 Monitor real-world performance metrics in production.")

def save_test_results(results: Dict[str, Any]):
    """Save test results to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    # Convert datetime objects to strings for JSON serialization
    json_results = results.copy()
    if json_results["start_time"]:
        json_results["start_time"] = json_results["start_time"].isoformat()
    if json_results["end_time"]:
        json_results["end_time"] = json_results["end_time"].isoformat()
    
    try:
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        print(f"\n📄 Test results saved to: {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save test results: {e}")

def run_quick_tests():
    """Run a quick subset of tests for rapid feedback."""
    print("Running Quick Test Suite...")
    
    # Run only a few key tests
    suite = unittest.TestSuite()
    
    # Add a few critical tests
    suite.addTest(TestAnalyticsOptimized('test_oee_optimized_endpoint'))
    suite.addTest(TestAnalyticsOptimized('test_utilization_optimized_endpoint'))
    suite.addTest(TestAnalyticsOptimized('test_real_time_metrics_endpoint'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"\nQuick Test Results: {success_rate:.1f}% success rate")
    return result

def main():
    """Main entry point for test runner."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_tests()
    else:
        # Run comprehensive test suite
        runner = TestSuiteRunner()
        results = runner.run_all_tests()
        save_test_results(results)
        
        # Exit with error code if tests failed
        if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
            sys.exit(1)

if __name__ == "__main__":
    main()
