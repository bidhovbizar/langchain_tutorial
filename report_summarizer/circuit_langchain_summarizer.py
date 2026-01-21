"""
Test Report Failure Analyzer using Cisco Azure OpenAI

This script analyzes test reports (like test_report_7499.txt) and generates
summaries highlighting the reasons for failures using Azure OpenAI through Cisco's chat-ai.

Prerequisites:
    - OPENAI_API_VERSION (optional)
    - AZURE_OPENAI_API_VERSION (access token)
    - AZURE_OPENAI_ENDPOINT="https://chat-ai.cisco.com/"
    - Valid client_id and client_secret for OAuth2

Usage:
    python circuit_langchain_summarizer.py <report_file_path>
    python circuit_langchain_summarizer.py  # Uses default test_report_7499.txt
"""

import os
import requests
import json
import sys
import base64
from pathlib import Path
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import dotenv

# Load environment variables
dotenv.load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = "Tutorial3"

# Configuration
DEFAULT_REPORT = "test_report_7499.txt"

# Cisco Brain configuration
CISCO_OPENAI_APP_KEY = 'egai-prd-networking-123120833-summarize-1768589443863'
CISCO_BRAIN_USER_ID = 'bbizar'

# OAuth2 credentials for Cisco identity service
CLIENT_ID = '0oasijtht0KJw99dW5d7'
CLIENT_SECRET = 'T3Pe7CWYpM2DSadIfVOYhQykxGG-Mz-fR_EKTGzTwBwFB1Fy0u_HaknaSudq9E5D'

# Token cache (stored globally to avoid regenerating)
_TOKEN_CACHE = {
    'access_token': None,
    'expires_at': 0  # Unix timestamp
}


def get_oauth_token(client_id, client_secret, force_refresh=False):
    """
    Get OAuth2 access token from Cisco identity service with intelligent caching.
    Token is cached for 1 hour and only refreshed when expired or forced.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        force_refresh: Force getting a new token even if cached one is valid
        
    Returns:
        str: Access token
    """
    import time
    
    # Check if we have a valid cached token
    if not force_refresh and _TOKEN_CACHE['access_token'] and _TOKEN_CACHE['expires_at'] > time.time():
        remaining = int(_TOKEN_CACHE['expires_at'] - time.time())
        print(f"Using cached token (valid for {remaining} more seconds)")
        return _TOKEN_CACHE['access_token']
    
    # Need to get a new token
    print("Fetching new OAuth token...")
    url = "https://id.cisco.com/oauth2/default/v1/token"
    payload = "grant_type=client_credentials"
    
    # Encode credentials
    credentials = f'{client_id}:{client_secret}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
        
        # Cache the token with expiration time (subtract 60 seconds as buffer)
        _TOKEN_CACHE['access_token'] = access_token
        _TOKEN_CACHE['expires_at'] = time.time() + expires_in - 60
        
        print(f"✅ New token obtained (valid for {expires_in} seconds)")
        return access_token
        
    except Exception as e:
        print(f"❌ Error: Could not get fresh token: {e}")
        raise


def test_token_validity(access_token):
    """
    Test if the access token is valid by sending a simple test message.
    
    Args:
        access_token: OAuth2 access token to test
        
    Returns:
        bool: True if token is valid, False if expired/invalid
    """
    try:
        # Initialize LLM with the token
        test_llm = AzureChatOpenAI(
            deployment_name="gpt-4.1",
            azure_endpoint='https://chat-ai.cisco.com',
            api_key=access_token,
            api_version="2023-08-01-preview",
            model_kwargs=dict(
                user=f'{{"appkey": "{CISCO_OPENAI_APP_KEY}", "user": "{CISCO_BRAIN_USER_ID}"}}'
            )
        )
        
        # Send a simple test message
        test_message = HumanMessage(content="Hi")
        response = test_llm.invoke([test_message])
        
        # If we get here, token is valid
        return True
        
    except Exception as e:
        error_str = str(e)
        # Check if it's an authentication error
        if "401" in error_str or "Expired" in error_str or "Authentication" in error_str:
            return False
        # For other errors, assume token might be valid but something else failed
        print(f"Warning: Token test failed with: {e}")
        return False


def initialize_llm(access_token):
    """
    Initialize Azure OpenAI LLM through Cisco's chat-ai.
    
    Args:
        access_token: OAuth2 access token
        
    Returns:
        AzureChatOpenAI: Initialized LLM instance
    """
    llm = AzureChatOpenAI(
        deployment_name="gpt-4.1",
        azure_endpoint='https://chat-ai.cisco.com',
        api_key=access_token,
        api_version="2023-08-01-preview",
        model_kwargs=dict(
            user=f'{{"appkey": "{CISCO_OPENAI_APP_KEY}", "user": "{CISCO_BRAIN_USER_ID}"}}'
        )
    )
    return llm


def read_report_file(file_path):
    """
    Read the content of a test report file.
    
    Args:
        file_path: Path to the test report file
        
    Returns:
        str: Content of the report file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Report file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")


def create_analysis_prompt(report_content):
    """
    Create a specialized prompt for analyzing test report failures.
    
    Args:
        report_content: Content of the test report
        
    Returns:
        list: List of messages for the LLM
    """
    system_message = SystemMessage(content="""You are an expert test automation engineer specializing in 
analyzing test failure reports. Your role is to:
1. Identify and categorize test failures
2. Extract root causes from error messages and stack traces
3. Provide concise, actionable summaries
4. Highlight patterns in failures
5. Suggest potential fixes or areas for investigation""")
    
    human_message = HumanMessage(content=f"""Please analyze this test report and provide a comprehensive summary 
focusing on the failures. For each failure, explain:
1. What test failed and in which suite
2. The root cause of the failure (based on error messages)
3. Any patterns or commonalities between failures
4. Recommendations for fixing the issues

Test Report:
{report_content}

Please provide a well-structured analysis with clear sections for:
- Overall Test Summary
- Failure Analysis (grouped by root cause if possible)
- Key Findings
- Recommendations""")
    
    return [system_message, human_message]


def create_quick_summary_prompt(report_content):
    """
    Create a simpler prompt for quick summarization.
    
    Args:
        report_content: Content of the test report
        
    Returns:
        list: List of messages for the LLM
    """
    system_message = SystemMessage(content="""You are an expert QA engineer who provides concise test summaries. 
Your role is to quickly summarize test results, highlighting:
1. Overall pass/fail statistics
2. Which tests failed
3. Brief description of failures
4. Any critical issues that need immediate attention""")
    
    human_message = HumanMessage(content=f"""Please provide a concise summary of this test report. 
Focus on:
- Overall test statistics
- List of failed tests
- Brief description of each failure
- Any patterns you notice

Keep the summary concise but informative.

Test Report:
{report_content}

Provide a clear, well-organized summary.""")
    
    return [system_message, human_message]


def analyze_report(llm, report_content):
    """
    Send the report to the LLM for detailed analysis.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_content: Content of the test report
        
    Returns:
        dict: Analysis results containing content, metadata, and usage info
    """
    messages = create_analysis_prompt(report_content)
    
    print("\n[Sending to Azure OpenAI for detailed analysis...]")
    response = llm.invoke(messages)
    
    return {
        'content': response.content,
        'metadata': response.response_metadata,
        'message_id': response.id,
        'usage': response.usage_metadata
    }


def quick_summarize_report(llm, report_content):
    """
    Send the report to the LLM for quick summarization.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_content: Content of the test report
        
    Returns:
        dict: Analysis results containing content, metadata, and usage info
    """
    messages = create_quick_summary_prompt(report_content)
    
    print("\n[Sending to Azure OpenAI for quick summary...]")
    response = llm.invoke(messages)
    
    return {
        'content': response.content,
        'metadata': response.response_metadata,
        'message_id': response.id,
        'usage': response.usage_metadata
    }


def create_comparison_prompt(report1_content, report2_content, build1_name, build2_name):
    """
    Create a specialized prompt for comparing two test reports.
    
    Args:
        report1_content: Content of the first test report
        report2_content: Content of the second test report
        build1_name: Name of the first build
        build2_name: Name of the second build
        
    Returns:
        list: List of messages for the LLM
    """
    system_message = SystemMessage(content="""You are an expert QA engineer specializing in 
comparative test analysis. Your role is to:
1. Compare two test runs and identify similarities and differences
2. Find common failure patterns across builds
3. Identify regressions (new failures) and fixes (resolved failures)
4. Detect flaky tests that fail intermittently
5. Provide insights on overall quality trends
6. Suggest root causes for common issues""")
    
    human_message = HumanMessage(content=f"""Please perform a detailed comparison of these two test runs.

BUILD 1: {build1_name}
{report1_content}

BUILD 2: {build2_name}
{report2_content}

Provide a comprehensive comparison analysis with:

1. OVERVIEW COMPARISON
   - Test counts and pass rates for each build
   - Overall quality trend (improving/declining/stable)

2. COMMON FAILURES
   - Tests that failed in BOTH builds
   - Likely indicating persistent issues
   - Potential root causes

3. REGRESSIONS (New Failures)
   - Tests that passed in Build 1 but failed in Build 2
   - Possible causes for these new failures

4. FIXES (Resolved Failures)
   - Tests that failed in Build 1 but passed in Build 2
   - What might have been fixed

5. FLAKY TESTS
   - Tests with inconsistent results
   - Tests that might need stability improvements

6. PATTERNS & INSIGHTS
   - Common failure patterns across both builds
   - Infrastructure or environment issues
   - Recommendations for improvement

Please provide a clear, well-structured analysis.""")
    
    return [system_message, human_message]


def compare_reports(llm, report1_content, report2_content, build1_name, build2_name):
    """
    Compare two test reports using AI analysis.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report1_content: Content of the first test report
        report2_content: Content of the second test report
        build1_name: Name of the first build
        build2_name: Name of the second build
        
    Returns:
        dict: Comparison results containing content, metadata, and usage info
    """
    messages = create_comparison_prompt(report1_content, report2_content, build1_name, build2_name)
    
    print(f"\n[Sending to Azure OpenAI for comparison analysis of {build1_name} vs {build2_name}...]")
    response = llm.invoke(messages)
    
    return {
        'content': response.content,
        'metadata': response.response_metadata,
        'message_id': response.id,
        'usage': response.usage_metadata
    }


def format_output(analysis_result, report_path, report_size):
    """
    Format the analysis results for display.
    
    Args:
        analysis_result: Dictionary containing analysis results
        report_path: Path to the report file
        report_size: Size of the report in characters
    """
    print("\n" + "=" * 100)
    print("TEST REPORT FAILURE ANALYSIS")
    print("=" * 100)
    print(f"\nReport File: {report_path}")
    print(f"Report Size: {report_size:,} characters")
    print(f"Model: {analysis_result['metadata'].get('model', 'N/A')}")
    print(f"Message ID: {analysis_result['message_id']}")
    
    if 'usage' in analysis_result and analysis_result['usage']:
        usage = analysis_result['usage']
        print(f"\nToken Usage:")
        print(f"  - Input Tokens: {usage.get('prompt_tokens', 'N/A')}")
        print(f"  - Output Tokens: {usage.get('completion_tokens', 'N/A')}")
        print(f"  - Total Tokens: {usage.get('total_tokens', 'N/A')}")
    
    print("\n" + "=" * 100)
    print("ANALYSIS RESULTS")
    print("=" * 100)
    print(f"\n{analysis_result['content']}\n")
    print("=" * 100)


def save_analysis_to_file(analysis_content, output_path):
    """
    Save the analysis to a file.
    
    Args:
        analysis_content: The analysis text to save
        output_path: Path where to save the analysis
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("TEST REPORT FAILURE ANALYSIS\n")
            f.write("=" * 100 + "\n\n")
            f.write(analysis_content)
            f.write("\n\n" + "=" * 100 + "\n")
        print(f"\n✅ Analysis saved to: {output_path}")
        return True
    except Exception as e:
        print(f"\n⚠️  Warning: Could not save analysis to file: {e}")
        return False


def main():
    """
    Main function to orchestrate the test report analysis.
    """
    print("=" * 100)
    print("TEST REPORT FAILURE ANALYZER")
    print("Using Cisco Azure OpenAI (chat-ai)")
    print("=" * 100)
    
    # Determine which report file to use
    if len(sys.argv) > 1:
        report_file = sys.argv[1]
    else:
        # Use default report file in the same directory as this script
        script_dir = Path(__file__).parent
        report_file = script_dir / DEFAULT_REPORT
        print(f"\nNo file specified. Using default: {report_file.name}")
    
    # Convert to Path object
    report_path = Path(report_file)
    
    # Step 1: Read the report file
    print(f"\n[1/4] Reading report file: {report_path}")
    try:
        report_content = read_report_file(report_path)
        print(f"✅ Successfully read {len(report_content):,} characters")
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nAvailable report files in current directory:")
        script_dir = Path(__file__).parent
        report_files = list(script_dir.glob("test_report_*.txt"))
        if report_files:
            for rf in report_files:
                print(f"  - {rf.name}")
        else:
            print("  (No test_report_*.txt files found)")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    # Step 2: Get OAuth token
    print("\n[2/4] Authenticating with Cisco identity service...")
    if CLIENT_ID and CLIENT_SECRET:
        access_token = get_oauth_token(CLIENT_ID, CLIENT_SECRET)
        print("✅ Authentication successful")
    else:
        print("❌ Error: CLIENT_ID and CLIENT_SECRET not configured")
        print("Please update the credentials in circuit_langchain_summarizer.py")
        return 1
    
    # Step 3: Initialize LLM
    print("\n[3/4] Initializing Azure OpenAI (GPT-4.1)...")
    try:
        llm = initialize_llm(access_token)
        print("✅ LLM initialized successfully")
    except Exception as e:
        print(f"\n❌ Error initializing LLM: {e}")
        return 1
    
    # Step 4: Analyze the report
    print("\n[4/4] Analyzing test report...")
    print("(This may take a moment for detailed analysis...)")
    try:
        analysis_result = analyze_report(llm, report_content)
        print("✅ Analysis complete")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Display results
    format_output(analysis_result, report_path, len(report_content))
    
    # Save to file
    output_file = report_path.parent / f"{report_path.stem}_failure_analysis.txt"
    save_analysis_to_file(analysis_result['content'], output_file)
    
    print("\n✅ Analysis complete!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


