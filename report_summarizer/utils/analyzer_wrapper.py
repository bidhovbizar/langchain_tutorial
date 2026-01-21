"""
Analyzer Wrapper - Wraps test_results_analyzer_full_error.py functionality
"""

import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime

# Add parent directory to path to import test_results_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from test_results_analyzer_full_error import TestResultsAnalyzer
except ImportError as e:
    print(f"Error importing TestResultsAnalyzer: {e}")
    TestResultsAnalyzer = None


class AnalyzerWrapper:
    """Wrapper for test_results_analyzer_full_error.py functionality"""
    
    def __init__(self):
        """Initialize the analyzer wrapper"""
        self.analyzer = None
        self.report_path = None
        self.results = None
    
    def analyze(
        self,
        index_html_path: Path,
        fetch_logs: bool = False,
        verbose: bool = False
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Analyze test results from index.html file.
        
        Args:
            index_html_path: Path to index.html file (NOT detail.html)
            fetch_logs: Whether to fetch detailed logs (slower)
            verbose: Enable verbose output
            
        Returns:
            Tuple of (success, report_path, results_dict)
            - success: bool indicating if analysis was successful
            - report_path: Path to generated report file
            - results_dict: Dictionary containing analysis results
        """
        if TestResultsAnalyzer is None:
            return False, None, {"error": "TestResultsAnalyzer module not available"}
        
        try:
            # Verify we have index.html
            if not str(index_html_path).endswith('index.html'):
                return False, None, {"error": f"Expected index.html but got: {index_html_path.name}"}
            
            # Create analyzer instance
            self.analyzer = TestResultsAnalyzer(
                html_file=str(index_html_path),
                base_url=None,
                verbose=verbose
            )
            
            # Run analysis with fetch_logs parameter
            success = self.analyzer.run(fetch_logs=fetch_logs)
            
            if not success:
                return False, None, {"error": "Analysis failed"}
            
            # Generate report in temp directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Extract build name from path (e.g., staging_sars_sanity_build_7449)
            build_name = index_html_path.parts[-4] if len(index_html_path.parts) >= 4 else "unknown"
            report_filename = f"test_report_{build_name}_{timestamp}.txt"
            report_path = Path(tempfile.gettempdir()) / report_filename
            
            # Save report to the specified path
            if not self.analyzer.save_report(str(report_path)):
                return False, None, {"error": "Failed to save report"}
            
            self.report_path = report_path
            self.results = self.analyzer.results
            
            # Return results dictionary
            results_dict = {
                'report_path': str(report_path),
                'summary': self.analyzer.results.get('summary', {}),
                'total_tests': self.analyzer.results.get('total_tests', 0),
                'failed_tests': self.analyzer.results.get('failed_tests', 0),
                'failures': self.analyzer.results.get('failures', []),
                'test_suites': self.analyzer.results.get('test_suites', [])
            }
            
            return True, str(report_path), results_dict
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, None, {"error": str(e)}
    
    def get_quick_summary(self) -> Optional[str]:
        """
        Get a quick summary of the analysis results.
        
        Returns:
            str: Quick summary text or None if no results
        """
        if not self.results:
            return None
        
        summary = self.results.get('summary', {})
        failures = self.results.get('failures', [])
        
        lines = []
        lines.append("=" * 80)
        lines.append("QUICK SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        
        # Overall stats
        if summary:
            lines.append("Test Results:")
            for key, value in summary.items():
                if isinstance(value, (int, float, str)):
                    lines.append(f"  {key}: {value}")
        
        lines.append("")
        lines.append(f"Total Tests: {self.results.get('total_tests', 0)}")
        lines.append(f"Failed Tests: {self.results.get('failed_tests', 0)}")
        
        if self.results.get('total_tests', 0) > 0:
            pass_rate = (1 - self.results.get('failed_tests', 0) / self.results.get('total_tests', 1)) * 100
            lines.append(f"Pass Rate: {pass_rate:.1f}%")
        
        lines.append("")
        lines.append("=" * 80)
        
        # List failures
        if failures:
            lines.append("FAILURES:")
            lines.append("=" * 80)
            for i, failure in enumerate(failures[:10], 1):  # Show first 10
                lines.append(f"\n{i}. {failure.get('test_name', 'Unknown Test')}")
                lines.append(f"   Suite: {failure.get('suite_name', 'Unknown Suite')}")
                lines.append(f"   Status: {failure.get('status', 'Unknown')}")
                
                # Show brief error message
                error_msg = failure.get('error_message', '')
                if error_msg:
                    # Truncate long error messages
                    if len(error_msg) > 200:
                        error_msg = error_msg[:200] + "..."
                    lines.append(f"   Error: {error_msg}")
            
            if len(failures) > 10:
                lines.append(f"\n... and {len(failures) - 10} more failures")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def cleanup(self):
        """Cleanup temporary files if needed"""
        # Report files in /tmp will be cleaned up by the system
        # But we can implement explicit cleanup if needed
        pass

