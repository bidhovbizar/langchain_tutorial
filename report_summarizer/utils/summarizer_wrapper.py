"""
Summarizer Wrapper - Wraps circuit_langchain_summarizer.py functionality
"""

import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from circuit_langchain_summarizer import (
        get_oauth_token,
        initialize_llm,
        read_report_file,
        analyze_report,
        quick_summarize_report,
        compare_reports,
        chat_with_report,
        chat_with_comparison,
        test_token_validity,
        CLIENT_ID,
        CLIENT_SECRET
    )
    SUMMARIZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import circuit_langchain_summarizer: {e}")
    SUMMARIZER_AVAILABLE = False


class SummarizerWrapper:
    """Wrapper for circuit_langchain_summarizer.py functionality"""
    
    def __init__(self):
        """Initialize the summarizer wrapper"""
        self.llm = None
        self.last_analysis = None
        self.access_token = None
    
    def initialize(self, force_refresh=False) -> Tuple[bool, Optional[str]]:
        """
        Initialize the LLM with authentication and intelligent token management.
        
        Args:
            force_refresh: Force getting a new token even if cached one exists
            
        Returns:
            Tuple of (success, error_message)
        """
        if not SUMMARIZER_AVAILABLE:
            return False, "Summarizer module not available"
        
        try:
            # Get access token with intelligent caching
            if CLIENT_ID and CLIENT_SECRET:
                self.access_token = get_oauth_token(CLIENT_ID, CLIENT_SECRET, force_refresh=force_refresh)
            else:
                return False, "CLIENT_ID and CLIENT_SECRET not configured"
            
            # Test if token is valid before initializing LLM
            if not force_refresh and self.access_token:
                print("Testing token validity...")
                if not test_token_validity(self.access_token):
                    print("Token is expired, getting new one...")
                    self.access_token = get_oauth_token(CLIENT_ID, CLIENT_SECRET, force_refresh=True)
            
            # Initialize LLM
            self.llm = initialize_llm(self.access_token)
            
            return True, None
            
        except Exception as e:
            return False, f"Failed to initialize summarizer: {str(e)}"
    
    def analyze_full(
        self,
        report_path: str,
        callback=None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Perform full analysis of the report using AI with automatic token refresh on expiry.
        
        Args:
            report_path: Path to the error report file
            callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (success, result_dict, error_message)
        """
        if not SUMMARIZER_AVAILABLE:
            return False, None, "Summarizer module not available"
        
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Initialize if not already done
                if self.llm is None or retry_count > 0:
                    if callback:
                        callback("Initializing AI model...")
                    
                    force_refresh = (retry_count > 0)  # Force refresh on retry
                    success, error = self.initialize(force_refresh=force_refresh)
                    if not success:
                        return False, None, error
                
                # Read report
                if callback:
                    callback("Reading report file...")
                report_content = read_report_file(report_path)
                
                # Analyze with AI (callback will be used for chunk progress)
                if callback:
                    callback("Analyzing with AI...")
                analysis_result = analyze_report(self.llm, report_content, callback=callback)
                
                self.last_analysis = analysis_result
                
                # Format result
                result_dict = {
                    'content': analysis_result['content'],
                    'metadata': analysis_result.get('metadata', {}),
                    'message_id': analysis_result.get('message_id', 'N/A'),
                    'usage': analysis_result.get('usage', {}),
                    'report_size': len(report_content)
                }
                
                return True, result_dict, None
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's an authentication error (token expired)
                if ("401" in error_str or "Expired" in error_str or "AuthenticationError" in error_str) and retry_count < max_retries - 1:
                    print(f"\n⚠️  Token expired, getting new token (attempt {retry_count + 1}/{max_retries})...")
                    if callback:
                        callback("Token expired, refreshing authentication...")
                    
                    # Reset LLM to force reinitialization with new token
                    self.llm = None
                    retry_count += 1
                    continue
                else:
                    # Not an auth error or out of retries
                    import traceback
                    traceback.print_exc()
                    return False, None, f"Analysis failed: {str(e)}"
        
        return False, None, "Failed after retrying with fresh token"
    
    def analyze_quick(
        self,
        report_path: str,
        callback=None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Perform quick AI-powered summary of the report using a simpler prompt.
        Uses the same full report as Full mode, but with a concise summarization prompt.
        
        Args:
            report_path: Path to the error report file
            callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (success, result_dict, error_message)
        """
        if not SUMMARIZER_AVAILABLE:
            return False, None, "Summarizer module not available"
        
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Initialize if not already done
                if self.llm is None or retry_count > 0:
                    if callback:
                        callback("Initializing AI model...")
                    
                    force_refresh = (retry_count > 0)  # Force refresh on retry
                    success, error = self.initialize(force_refresh=force_refresh)
                    if not success:
                        return False, None, error
                
                # Read report
                if callback:
                    callback("Reading report file...")
                report_content = read_report_file(report_path)
                
                # Quick summarize with AI (callback will be used for chunk progress)
                if callback:
                    callback("Generating quick AI summary...")
                summary_result = quick_summarize_report(self.llm, report_content, callback=callback)
                
                self.last_analysis = summary_result
                
                # Format result
                result_dict = {
                    'content': summary_result['content'],
                    'metadata': summary_result.get('metadata', {}),
                    'message_id': summary_result.get('message_id', 'N/A'),
                    'usage': summary_result.get('usage', {}),
                    'report_size': len(report_content)
                }
                
                return True, result_dict, None
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's an authentication error (token expired)
                if ("401" in error_str or "Expired" in error_str or "AuthenticationError" in error_str) and retry_count < max_retries - 1:
                    print(f"\n⚠️  Token expired, getting new token (attempt {retry_count + 1}/{max_retries})...")
                    if callback:
                        callback("Token expired, refreshing authentication...")
                    
                    # Reset LLM to force reinitialization with new token
                    self.llm = None
                    retry_count += 1
                    continue
                else:
                    # Not an auth error or out of retries
                    import traceback
                    traceback.print_exc()
                    return False, None, f"Quick analysis failed: {str(e)}"
        
        return False, None, "Failed after retrying with fresh token"
    
    def compare_multiple(
        self,
        report_paths: List[Tuple[str, str]],
        callback=None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Compare multiple test reports using AI analysis.
        
        Args:
            report_paths: List of tuples [(report_path, build_name), ...]
            callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (success, result_dict, error_message)
        """
        if not SUMMARIZER_AVAILABLE:
            return False, None, "Summarizer module not available"
        
        if len(report_paths) < 2:
            return False, None, "Need at least 2 reports to compare"
        
        # For now, compare first two reports
        # Can be extended to support more than 2 in the future
        report1_path, build1_name = report_paths[0]
        report2_path, build2_name = report_paths[1]
        
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Initialize if not already done
                if self.llm is None or retry_count > 0:
                    if callback:
                        callback("Initializing AI model...")
                    
                    force_refresh = (retry_count > 0)
                    success, error = self.initialize(force_refresh=force_refresh)
                    if not success:
                        return False, None, error
                
                # Read both reports
                if callback:
                    callback(f"Reading reports for {build1_name} and {build2_name}...")
                
                report1_content = read_report_file(report1_path)
                report2_content = read_report_file(report2_path)
                
                # Compare with AI
                if callback:
                    callback("Analyzing differences and similarities (this may take 30-60 seconds)...")
                
                comparison_result = compare_reports(
                    self.llm,
                    report1_content,
                    report2_content,
                    build1_name,
                    build2_name,
                    callback=callback  # Pass callback for chunking progress
                )
                
                self.last_analysis = comparison_result
                
                # Format result
                result_dict = {
                    'content': comparison_result['content'],
                    'metadata': comparison_result.get('metadata', {}),
                    'message_id': comparison_result.get('message_id', 'N/A'),
                    'usage': comparison_result.get('usage', {}),
                    'builds_compared': [build1_name, build2_name]
                }
                
                return True, result_dict, None
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's an authentication error (token expired)
                if ("401" in error_str or "Expired" in error_str or "AuthenticationError" in error_str) and retry_count < max_retries - 1:
                    print(f"\n⚠️  Token expired, getting new token (attempt {retry_count + 1}/{max_retries})...")
                    if callback:
                        callback("Token expired, refreshing authentication...")
                    
                    # Reset LLM to force reinitialization with new token
                    self.llm = None
                    retry_count += 1
                    continue
                else:
                    # Not an auth error or out of retries
                    import traceback
                    traceback.print_exc()
                    return False, None, f"Comparison failed: {str(e)}"
        
        return False, None, "Failed after retrying with fresh token"
    
    def chat(
        self,
        report_content: str,
        ai_summary: str,
        chat_history: List[Dict],
        user_question: str,
        callback=None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Chat with AI about a test report.
        
        Args:
            report_content: The full test report content
            ai_summary: The AI-generated summary
            chat_history: List of previous chat messages [{"role": "user/assistant", "content": "..."}]
            user_question: The user's current question
            callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (success, ai_response, error_message)
        """
        if not SUMMARIZER_AVAILABLE:
            return False, None, "Summarizer module not available"
        
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Initialize if not already done
                if self.llm is None or retry_count > 0:
                    if callback:
                        callback("Initializing AI model...")
                    
                    force_refresh = (retry_count > 0)
                    success, error = self.initialize(force_refresh=force_refresh)
                    if not success:
                        return False, None, error
                
                # Get AI response
                if callback:
                    callback("Getting AI response...")
                
                chat_result = chat_with_report(
                    self.llm,
                    report_content,
                    ai_summary,
                    chat_history,
                    user_question
                )
                
                return True, chat_result['content'], None
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's an authentication error (token expired)
                if ("401" in error_str or "Expired" in error_str or "AuthenticationError" in error_str) and retry_count < max_retries - 1:
                    print(f"\n⚠️  Token expired, getting new token (attempt {retry_count + 1}/{max_retries})...")
                    if callback:
                        callback("Token expired, refreshing authentication...")
                    
                    # Reset LLM to force reinitialization with new token
                    self.llm = None
                    retry_count += 1
                    continue
                else:
                    # Not an auth error or out of retries
                    import traceback
                    traceback.print_exc()
                    return False, None, f"Chat failed: {str(e)}"
        
        return False, None, "Failed after retrying with fresh token"
    
    def chat_comparison(
        self,
        report1_content: str,
        report2_content: str,
        comparison_summary: str,
        build1_name: str,
        build2_name: str,
        chat_history: List[Dict],
        user_question: str,
        callback=None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Chat with AI about a comparison of two test reports.
        
        Args:
            report1_content: Content of the first test report
            report2_content: Content of the second test report
            comparison_summary: The AI-generated comparison summary
            build1_name: Name of the first build
            build2_name: Name of the second build
            chat_history: List of previous chat messages
            user_question: The user's current question
            callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (success, ai_response, error_message)
        """
        if not SUMMARIZER_AVAILABLE:
            return False, None, "Summarizer module not available"
        
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Initialize if not already done
                if self.llm is None or retry_count > 0:
                    if callback:
                        callback("Initializing AI model...")
                    
                    force_refresh = (retry_count > 0)
                    success, error = self.initialize(force_refresh=force_refresh)
                    if not success:
                        return False, None, error
                
                # Get AI response
                if callback:
                    callback("Getting AI response...")
                
                chat_result = chat_with_comparison(
                    self.llm,
                    report1_content,
                    report2_content,
                    comparison_summary,
                    build1_name,
                    build2_name,
                    chat_history,
                    user_question
                )
                
                return True, chat_result['content'], None
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's an authentication error (token expired)
                if ("401" in error_str or "Expired" in error_str or "AuthenticationError" in error_str) and retry_count < max_retries - 1:
                    print(f"\n⚠️  Token expired, getting new token (attempt {retry_count + 1}/{max_retries})...")
                    if callback:
                        callback("Token expired, refreshing authentication...")
                    
                    # Reset LLM to force reinitialization with new token
                    self.llm = None
                    retry_count += 1
                    continue
                else:
                    # Not an auth error or out of retries
                    import traceback
                    traceback.print_exc()
                    return False, None, f"Comparison chat failed: {str(e)}"
        
        return False, None, "Failed after retrying with fresh token"
    
    def get_token_usage(self) -> Optional[Dict]:
        """
        Get token usage from last analysis.
        
        Returns:
            Dict with token usage info or None
        """
        if self.last_analysis and 'usage' in self.last_analysis:
            return self.last_analysis['usage']
        return None

