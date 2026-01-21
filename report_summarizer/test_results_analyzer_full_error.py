#!/usr/bin/env python3
"""
Test Results Analyzer - Extracts and summarizes issues from test result HTML files
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, parse_qs, unquote
import gzip
from bs4 import BeautifulSoup

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it using: pip install requests beautifulsoup4")
    sys.exit(1)


class TestResultsAnalyzer:
    """Analyzes test results from HTML files and extracts failure information"""

    # Test result statuses that indicate failures
    FAILURE_STATUSES = {'FAIL', 'ERROR', 'NOT RUN', 'SETUP ERROR', 'CLEANUP ERROR', 'PLUGIN ERROR', 'SKIP'}

    def __init__(self, html_file: str, base_url: Optional[str] = None, verbose: bool = False):
        """
        Initialize the analyzer

        Args:
            html_file: Path to the test results HTML file
            base_url: Optional base URL for resolving relative links
            verbose: Enable verbose output
        """
        self.html_file = Path(html_file)
        self.base_url = base_url
        self.verbose = verbose
        self.soup = None
        self.results = {
            'summary': {},
            'test_suites': [],
            'failures': [],
            'total_tests': 0,
            'failed_tests': 0
        }
        self.session = requests.Session()
        self.session.timeout = 10

    def load_html(self) -> bool:
        """Load and parse the HTML file"""
        try:
            if not self.html_file.exists():
                print(f"Error: File not found: {self.html_file}")
                return False

            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            self.soup = BeautifulSoup(html_content, 'html.parser')
            if self.verbose:
                print(f"✓ Successfully loaded HTML file: {self.html_file}")
            return True

        except Exception as e:
            print(f"Error loading HTML file: {e}")
            return False

    def extract_summary(self) -> Dict:
        """Extract the test summary from the header"""
        summary = {}
        try:
            subheader = self.soup.find('div', class_='subheader')
            if subheader:
                h4 = subheader.find('h4')
                if h4:
                    text = h4.get_text()
                    # Parse the summary text
                    matches = re.findall(r'(\w+):\s*(\d+)', text)
                    for key, value in matches:
                        summary[key] = int(value)

            # Extract configuration table
            config_table = self.soup.find('table', class_='config-summary')
            if config_table:
                for row in config_table.find_all('tr'):
                    cell = row.find('td')
                    if cell:
                        text = cell.get_text().strip()
                        if ':' in text:
                            key, value = text.split(':', 1)
                            summary[key.strip()] = value.strip()

            self.results['summary'] = summary
            if self.verbose:
                print(f"✓ Extracted summary: {len(summary)} fields")
            return summary

        except Exception as e:
            print(f"Warning: Error extracting summary: {e}")
            return summary

    def extract_test_results(self) -> List[Dict]:
        """Extract all test results from the HTML"""
        test_data = []
        try:
            # Find all test result tables
            test_tables = self.soup.find_all('table', class_='test-results')

            current_suite = None
            for table in test_tables:
                # Get the suite name from the h3 before the table
                h3 = table.find_previous('h3')
                if h3:
                    current_suite = h3.get_text().replace('SUITE: ', '').strip()

                # Process each row in the table
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        test_name_cell = cells[0]
                        status_cell = cells[1]
                        failure_msg_cell = cells[2]

                        test_name = test_name_cell.get_text().strip()
                        status = status_cell.get_text().strip()
                        failure_msg = failure_msg_cell.get_text().strip()

                        # Extract log link if available
                        log_link = None
                        link_elem = test_name_cell.find('a')
                        if link_elem and link_elem.get('href'):
                            log_link = link_elem.get('href')

                        test_result = {
                            'suite': current_suite,
                            'name': test_name,
                            'status': status,
                            'failure_message': failure_msg,
                            'log_link': log_link,
                            'detailed_info': None
                        }

                        test_data.append(test_result)

                        # Count results
                        self.results['total_tests'] += 1
                        if status in self.FAILURE_STATUSES:
                            self.results['failed_tests'] += 1
                            self.results['failures'].append(test_result)

            self.results['test_suites'] = test_data
            if self.verbose:
                print(f"✓ Extracted {len(test_data)} test results")
                print(f"  - Failed/Error tests: {len(self.results['failures'])}")
            return test_data

        except Exception as e:
            print(f"Warning: Error extracting test results: {e}")
            return test_data

    def _extract_local_path_from_url(self, url_string: str) -> Optional[str]:
        """Extract local file path from a URL string by matching against the HTML file location"""
        try:
            # Decode the URL-encoded string
            decoded_url = unquote(url_string)

            # Get the parent directories of the HTML file
            html_parent = self.html_file.parent

            # Look for the build folder (e.g., qatest_sars_sanity_build_7307)
            # This is typically the folder that contains test_results
            if 'test_results' in str(html_parent):
                parts = html_parent.parts

                # Find the index of 'test_results' in the path
                test_results_idx = None
                for i, part in enumerate(parts):
                    if part == 'test_results':
                        test_results_idx = i
                        break

                if test_results_idx is not None and test_results_idx > 0:
                    # The build folder is the parent of test_results
                    build_folder_path = Path(*parts[:test_results_idx])
                    test_results_path = build_folder_path / 'test_results'

                    # Approach 1: Look for exact build folder name (if build folders have matching names)
                    build_folder_name = build_folder_path.name
                    if build_folder_name in decoded_url:
                        idx = decoded_url.find(build_folder_name)
                        if idx != -1:
                            relative_path = decoded_url[idx:]
                            local_path = build_folder_path / relative_path
                            if os.path.exists(local_path):
                                return str(local_path)

                    # Approach 2: Extract path after /test_results/ in the URL
                    # The URL might have a different build folder name, so we look for /test_results/
                    if '/test_results/' in decoded_url:
                        # Find the test_results portion
                        idx = decoded_url.find('/test_results/')
                        if idx != -1:
                            # Extract the relative path from /test_results/ onwards
                            relative_path_from_test_results = decoded_url[idx + len('/test_results/'):]
                            # Construct the full local path
                            local_path = test_results_path / relative_path_from_test_results

                            # Check if this file exists
                            if os.path.exists(local_path):
                                return str(local_path)

            return None
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Error extracting local path from URL: {e}")
            return None

    def fetch_log_content(self, log_link: str) -> Optional[str]:
        """Fetch the content from a log link, prioritizing local file access"""
        try:
            if not log_link:
                return None

            # Handle local file paths with file:// protocol
            if log_link.startswith('file://'):
                file_path = log_link.replace('file://', '')
                if os.path.exists(file_path):
                    if file_path.endswith('.gz'):
                        with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                            return f.read()
                    else:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            return f.read()
                return None

            # Handle URLs with log_view.html (extract the actual log URL from page parameter)
            if log_link.startswith('http'):
                try:
                    # Check if it's a log_view.html link with a page parameter
                    if 'log_view.html' in log_link and 'page=' in log_link:
                        # Extract the actual log file URL from the page parameter
                        parsed_url = urlparse(log_link)
                        query_params = parse_qs(parsed_url.query)
                        if 'page' in query_params:
                            actual_log_url = query_params['page'][0]

                            # First, try to extract and access local file path
                            local_path = self._extract_local_path_from_url(actual_log_url)
                            if local_path and os.path.exists(local_path):
                                if self.verbose:
                                    print(f"      └─ Using local file: {local_path}")
                                if local_path.endswith('.gz'):
                                    with gzip.open(local_path, 'rt', encoding='utf-8', errors='ignore') as f:
                                        return f.read()
                                else:
                                    with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        return f.read()

                            # Fallback to URL fetch if local path not found
                            if self.verbose and local_path:
                                print(f"      └─ Local path not found at {local_path[:80]}, trying URL fetch")

                            try:
                                # Try to fetch the actual log file from URL
                                response = self.session.get(actual_log_url, timeout=10, verify=False, stream=True)
                                if response.status_code == 200:
                                    # If it's gzipped content, decompress it
                                    if actual_log_url.endswith('.gz') or response.headers.get('Content-Encoding') == 'gzip':
                                        try:
                                            return gzip.decompress(response.content).decode('utf-8', errors='ignore')
                                        except Exception:
                                            # If decompression fails, try treating as plain text
                                            return response.text
                                    return response.text
                            except requests.exceptions.Timeout:
                                if self.verbose:
                                    print(f"  Warning: Timeout fetching URL {actual_log_url}")
                                return None
                            except Exception as e:
                                if self.verbose:
                                    print(f"  Warning: Could not fetch URL: {type(e).__name__}")
                                return None
                    else:
                        # Direct URL fetch (non-log_view.html links)
                        try:
                            response = self.session.get(log_link, timeout=10, verify=False, stream=True)
                            if response.status_code == 200:
                                if log_link.endswith('.gz') or response.headers.get('Content-Encoding') == 'gzip':
                                    try:
                                        return gzip.decompress(response.content).decode('utf-8', errors='ignore')
                                    except Exception:
                                        return response.text
                                return response.text
                        except requests.exceptions.Timeout:
                            if self.verbose:
                                print(f"  Warning: Timeout fetching URL {log_link}")
                            return None
                        except Exception as e:
                            if self.verbose:
                                print(f"  Warning: Could not fetch URL: {type(e).__name__}")
                            return None

                except Exception as e:
                    if self.verbose:
                        print(f"  Warning: Error processing log link: {e}")
                    return None

            return None

        except Exception as e:
            if self.verbose:
                print(f"  Warning: Error fetching log content: {e}")
            return None

    def extract_error_details(self, log_content: str) -> str:
        """Extract error details from log content"""
        if not log_content:
            return ""

        try:
            # Try to parse as HTML if it's an HTML log
            if '<html' in log_content.lower() or '<body' in log_content.lower():
                soup = BeautifulSoup(log_content, 'html.parser')
                # Remove script and style elements
                for script in soup(['script', 'style']):
                    script.decompose()
                text = soup.get_text()
            else:
                text = log_content

            # Extract error/failure lines with context
            lines = text.split('\n')
            error_lines = []
            exception_started = False

            for idx, line in enumerate(lines):
                line_lower = line.lower()
                line_stripped = line.strip()

                # Look for error keywords
                if any(keyword in line_lower for keyword in ['error:', 'failed:', 'exception:', 'traceback', 'assert']):
                    # Add the line and some context around it
                    error_lines.append(line_stripped)
                    exception_started = True

                    # Add next few lines for context (usually contain error details)
                    for j in range(idx + 1, min(idx + 4, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not any(k in next_line.lower() for k in ['at line', 'file']):
                            error_lines.append(next_line)
                        if 'at line' in lines[j].lower() or 'traceback' in lines[j].lower():
                            break

            # If no specific errors found, look for important keywords
            if not error_lines:
                important_keywords = ['failure', 'fail:', 'error', 'invalid', 'cannot', 'not found', 'missing']
                for line in lines:
                    if any(keyword in line.lower() for keyword in important_keywords):
                        error_lines.append(line.strip())

            # Clean up and deduplicate
            error_lines = [line for line in error_lines if line]
            error_lines = list(dict.fromkeys(error_lines))  # Remove duplicates while preserving order

            # Limit to first 15 lines
            return '\n'.join(error_lines) if error_lines else "No specific error details found in log"

        except Exception as e:
            return f"Error parsing log content: {e}"

    def analyze_failures(self, fetch_logs: bool = False) -> List[Dict]:
        """Analyze failed tests and extract details"""
        try:
            if self.verbose:
                print(f"\nAnalyzing {len(self.results['failures'])} failed/error tests...")

            for idx, failure in enumerate(self.results['failures'], 1):
                if self.verbose:
                    print(f"  [{idx}/{len(self.results['failures'])}] {failure['suite']} > {failure['name']} ({failure['status']})")

                # Fetch and extract error details if requested
                if fetch_logs and failure['log_link']:
                    log_content = self.fetch_log_content(failure['log_link'])
                    if log_content:
                        error_details = self.extract_error_details(log_content)
                        failure['detailed_info'] = error_details
                        if self.verbose and error_details:
                            print(f"      └─ Error details extracted")

            return self.results['failures']

        except Exception as e:
            print(f"Warning: Error analyzing failures: {e}")
            return self.results['failures']

    def generate_report(self) -> str:
        """Generate a summary report of test results and failures"""
        report = []
        report.append("=" * 80)
        report.append("TEST RESULTS SUMMARY REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary section
        report.append("OVERALL SUMMARY:")
        report.append("-" * 80)
        summary = self.results['summary']
        if summary:
            for key in ['PASS', 'FAIL', 'ERROR', 'NOT RUN', 'SETUP ERROR', 'CLEANUP ERROR']:
                if key in summary:
                    report.append(f"  {key}: {summary[key]}")

        report.append(f"\n  Total Tests: {self.results['total_tests']}")
        report.append(f"  Failed/Error Tests: {self.results['failed_tests']}")
        if self.results['total_tests'] > 0:
            pass_rate = ((self.results['total_tests'] - self.results['failed_tests']) / self.results['total_tests']) * 100
            report.append(f"  Pass Rate: {pass_rate:.1f}%")
        report.append("")

        # Test configuration info
        if 'Qali_id' in summary:
            report.append("TEST CONFIGURATION:")
            report.append("-" * 80)
            config_keys = ['Qali_id', 'Comment', 'Test_bed', 'Start_time', 'Stop_time', 'Test_duration']
            for key in config_keys:
                if key in summary:
                    report.append(f"  {key}: {summary[key]}")
            report.append("")

        # Failures section
        if self.results['failures']:
            report.append("FAILURES & ERRORS:")
            report.append("=" * 80)

            # Group by suite
            by_suite = {}
            for failure in self.results['failures']:
                suite = failure['suite'] or 'Unknown'
                if suite not in by_suite:
                    by_suite[suite] = []
                by_suite[suite].append(failure)

            for suite_name in sorted(by_suite.keys()):
                failures_in_suite = by_suite[suite_name]
                report.append(f"\nSUITE: {suite_name}")
                report.append("-" * 80)

                for failure in failures_in_suite:
                    report.append(f"\n  Test: {failure['name']}")
                    report.append(f"  Status: {failure['status']}")

                    if failure['failure_message']:
                        report.append(f"  Failure Message: {failure['failure_message']}")

                    if failure['detailed_info']:
                        report.append(f"  Detailed Info:")
                        for line in failure['detailed_info'].split('\n'):
                            if line.strip():
                                report.append(f"    {line}")

                    if failure['log_link']:
                        report.append(f"  Log Link: {failure['log_link']}")
        else:
            report.append("\n✓ ALL TESTS PASSED - NO FAILURES DETECTED!")

        report.append("\n" + "=" * 80)
        return "\n".join(report)

    def run(self, fetch_logs: bool = False) -> bool:
        """Run the complete analysis"""
        print("Starting Test Results Analysis...\n")

        # Load HTML
        if not self.load_html():
            return False

        # Extract data
        self.extract_summary()
        self.extract_test_results()

        # Analyze failures
        self.analyze_failures(fetch_logs=fetch_logs)

        return True

    def print_report(self):
        """Print the generated report"""
        print(self.generate_report())

    def save_report(self, output_file: str) -> bool:
        """Save the report to a file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_report())
            print(f"\n✓ Report saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze test results from HTML files and extract failure information'
    )
    parser.add_argument(
        'html_file',
        help='Path to the test results HTML file (index.html)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save report to output file',
        default=None
    )
    parser.add_argument(
        '-l', '--fetch-logs',
        action='store_true',
        help='Fetch and analyze detailed log files (may be slow)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-b', '--base-url',
        help='Base URL for resolving relative links',
        default=None
    )

    args = parser.parse_args()

    # Create analyzer
    analyzer = TestResultsAnalyzer(
        html_file=args.html_file,
        base_url=args.base_url,
        verbose=args.verbose
    )

    # Run analysis
    if analyzer.run(fetch_logs=args.fetch_logs):
        # Print report
        analyzer.print_report()

        # Save report if requested
        if args.output:
            analyzer.save_report(args.output)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

