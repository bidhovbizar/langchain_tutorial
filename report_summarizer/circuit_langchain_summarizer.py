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
from langchain.schema import HumanMessage, SystemMessage, AIMessage
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
1. Identify and categorize test FAILURES and SKIPS separately
2. Extract root causes from error messages and stack traces
3. Provide concise, actionable summaries
4. Highlight patterns in failures and skips
5. Suggest potential fixes or areas for investigation

CRITICAL: Analyze FAILED tests and SKIPPED tests SEPARATELY:
- FAILED tests = actual test failures (code bugs, logic errors, assertion failures)
- SKIPPED tests = environment/infrastructure issues (device unavailable, cloud problems, prerequisites not met)""")
    
    human_message = HumanMessage(content=f"""Please analyze this test report with FAILED and SKIPPED tests analyzed SEPARATELY.

Test Report:
{report_content}

Provide analysis with these DISTINCT sections:

1. OVERALL TEST SUMMARY
   - Total tests, passed, failed, skipped counts
   - Pass rate (excluding skipped)

2. FAILED TESTS ANALYSIS (Code/Logic Issues)
   - List each FAILED test with its suite
   - Root cause for each (code bugs, assertion failures, logic errors)
   - Patterns or commonalities between failures
   - Recommendations for code/test fixes

3. SKIPPED TESTS ANALYSIS (Environment/Infrastructure Issues)  
   - List each SKIPPED test with its suite
   - Reason for skip (device state, cloud issues, missing prerequisites)
   - Patterns in skips (e.g., "all tests on device X", "all cloud-dependent tests")
   - Recommendations for environment/infrastructure fixes

4. KEY FINDINGS
   - Critical issues needing immediate attention
   - Environment vs. Code issue breakdown

5. ACTIONABLE RECOMMENDATIONS
   - For FAILED: Code fixes, test improvements, logic corrections
   - For SKIPPED: Device maintenance, infrastructure fixes, environment setup

Keep FAILED and SKIPPED completely separate to clearly identify whether issues are code-related or environment-related.""")
    
    return [system_message, human_message]


def condense_report_for_ai(report_content, max_logs_per_test=3):
    """
    Condense a large report by removing verbose logs while keeping essential failure info.
    
    Strategy:
    1. Keep summary section intact
    2. For each test failure:
       - Keep test name, status, failure message
       - Keep only first N error/log lines (not all 100+)
       - Skip repetitive JSON logs
    
    This reduces report size by 80-90% while preserving all essential information for AI analysis.
    
    Args:
        report_content: The full report content
        max_logs_per_test: Maximum log lines to keep per test failure
        
    Returns:
        str: Condensed report content
    """
    lines = report_content.split('\n')
    output_lines = []
    
    in_test_section = False
    current_test_logs = []
    logs_count = 0
    
    for line in lines:
        # Check if we're in the failures section
        if 'FAILURES & ERRORS:' in line or '=== FAILURES ===' in line:
            in_test_section = True
            output_lines.append(line)
            continue
        
        # Check if this is a new test
        if line.strip().startswith('Test:'):
            # Add previous test's condensed logs
            if current_test_logs:
                output_lines.extend(current_test_logs[:max_logs_per_test])
                if len(current_test_logs) > max_logs_per_test:
                    output_lines.append(f"    ... ({len(current_test_logs) - max_logs_per_test} more log lines omitted for brevity)")
                current_test_logs = []
                logs_count = 0
            
            # Start new test
            output_lines.append(line)
            continue
        
        # If we're in a test section and see log lines
        if in_test_section and ('"ts":' in line or '"level":' in line or 'ERROR' in line or 'FAILURE' in line):
            # This is a log line - only keep first few
            current_test_logs.append(line)
            logs_count += 1
        elif in_test_section and line.strip().startswith('Status:') or line.strip().startswith('Failure Message:') or line.strip().startswith('Error:'):
            # Keep status and error messages
            output_lines.append(line)
        elif not in_test_section or (in_test_section and line.strip() and not line.strip().startswith('{')):
            # Keep summary section and non-log lines
            output_lines.append(line)
    
    # Add last test's logs
    if current_test_logs:
        output_lines.extend(current_test_logs[:max_logs_per_test])
        if len(current_test_logs) > max_logs_per_test:
            output_lines.append(f"    ... ({len(current_test_logs) - max_logs_per_test} more log lines omitted for brevity)")
    
    condensed = '\n'.join(output_lines)
    
    # Log the condensing results
    original_size = len(report_content)
    condensed_size = len(condensed)
    reduction_pct = ((original_size - condensed_size) / original_size * 100) if original_size > 0 else 0
    
    if reduction_pct > 10:  # Only log if significant reduction
        print(f"[Report condensed: {original_size:,} → {condensed_size:,} chars ({reduction_pct:.1f}% reduction)]")
    
    return condensed


def split_report_into_chunks(report_content, max_chars_per_chunk=200000):
    """
    Split a large report into manageable chunks while preserving structure.
    
    NOTE: This is now a FALLBACK. We first try to condense the report.
    Chunking is only used if condensing still leaves the report too large.
    
    Strategy:
    1. Keep the summary section intact in all chunks
    2. Split the failures list into groups
    3. Each chunk gets: summary + subset of failures
    
    Args:
        report_content: The full report content
        max_chars_per_chunk: Maximum characters per chunk (~50K tokens)
        
    Returns:
        list: List of report chunks, or [report_content] if small enough
    """
    # If report is small enough, return as-is
    if len(report_content) <= max_chars_per_chunk:
        return [report_content]
    
    # Try to split intelligently by finding the failures section
    lines = report_content.split('\n')
    
    # Find where summary ends and failures begin
    summary_lines = []
    failure_lines = []
    in_failures = False
    
    for line in lines:
        if '=== FAILURES ===' in line or 'FAILED TESTS:' in line or 'Test Failures:' in line:
            in_failures = True
            failure_lines.append(line)
        elif in_failures:
            failure_lines.append(line)
        else:
            summary_lines.append(line)
    
    summary_text = '\n'.join(summary_lines)
    
    # If we couldn't find a clear split, do a simple character-based split
    if not failure_lines:
        chunks = []
        for i in range(0, len(report_content), max_chars_per_chunk):
            chunk = report_content[i:i + max_chars_per_chunk]
            if i > 0:
                chunk = "[...continued from previous chunk]\n\n" + chunk
            if i + max_chars_per_chunk < len(report_content):
                chunk = chunk + "\n\n[...continues in next chunk]"
            chunks.append(chunk)
        return chunks
    
    # Split failures into chunks, keeping summary with each
    chunks = []
    current_failure_lines = []
    current_size = len(summary_text)
    
    for line in failure_lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed the limit, create a chunk
        if current_size + line_size > max_chars_per_chunk and current_failure_lines:
            chunk = summary_text + '\n\n' + '\n'.join(current_failure_lines)
            chunks.append(chunk)
            current_failure_lines = [line]
            current_size = len(summary_text) + line_size
        else:
            current_failure_lines.append(line)
            current_size += line_size
    
    # Add the last chunk
    if current_failure_lines:
        chunk = summary_text + '\n\n' + '\n'.join(current_failure_lines)
        chunks.append(chunk)
    
    return chunks


def analyze_report_chunks(llm, report_chunks, callback=None):
    """
    Analyze a report that has been split into multiple chunks.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_chunks: List of report chunks
        callback: Optional callback function for progress updates
        
    Returns:
        dict: Combined analysis results
    """
    if len(report_chunks) == 1:
        # Single chunk, analyze normally
        return analyze_report(llm, report_chunks[0])
    
    msg = f"Large report detected: Analyzing in {len(report_chunks)} chunks..."
    print(f"\n[{msg}]")
    if callback:
        callback(msg)
    
    # Analyze each chunk
    chunk_analyses = []
    for i, chunk in enumerate(report_chunks, 1):
        msg = f"Analyzing chunk {i}/{len(report_chunks)} (this may take 15-30 seconds per chunk)..."
        print(f"[{msg}]")
        if callback:
            callback(msg)
        
        # Create a prompt that knows this is part of a larger report
        messages = create_chunked_analysis_prompt(chunk, i, len(report_chunks))
        response = llm.invoke(messages)
        chunk_analyses.append(response.content)
    
    # Combine the analyses
    msg = f"Combining {len(chunk_analyses)} chunk analyses into final report..."
    print(f"[{msg}]")
    if callback:
        callback(msg)
    
    combined_analysis = combine_chunk_analyses(llm, chunk_analyses)
    
    return combined_analysis


def create_chunked_analysis_prompt(chunk_content, chunk_num, total_chunks):
    """
    Create a prompt for analyzing a chunk of a larger report.
    
    Args:
        chunk_content: The chunk content
        chunk_num: Current chunk number (1-indexed)
        total_chunks: Total number of chunks
        
    Returns:
        list: List of messages for the LLM
    """
    system_message = SystemMessage(content="""You are an expert test automation engineer analyzing a portion of a large test report.
Your role is to:
1. Identify and categorize test FAILURES and SKIPS in this chunk
2. Extract root causes from error messages
3. Note patterns and commonalities
4. Provide focused analysis for this subset of tests

This is part of a larger report being analyzed in chunks.""")
    
    human_message = HumanMessage(content=f"""This is chunk {chunk_num} of {total_chunks} from a large test report.

Analyze the FAILED and SKIPPED tests in this chunk:

{chunk_content}

Provide:
1. Summary of tests in this chunk (counts)
2. FAILED tests analysis (list each with root cause)
3. SKIPPED tests analysis (list each with reason)
4. Patterns observed in this chunk

Be thorough but focused on this subset of tests.""")
    
    return [system_message, human_message]


def combine_chunk_analyses(llm, chunk_analyses):
    """
    Combine multiple chunk analyses into a coherent final analysis.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        chunk_analyses: List of analysis strings from each chunk
        
    Returns:
        dict: Combined analysis results
    """
    system_message = SystemMessage(content="""You are an expert test automation engineer.
You will receive multiple analyses from different parts of a large test report.
Your role is to:
1. Synthesize them into ONE coherent analysis
2. Combine counts and statistics
3. Identify overall patterns across all chunks
4. Provide unified recommendations
5. Keep FAILED and SKIPPED tests separate""")
    
    combined_content = "\n\n---CHUNK ANALYSIS SEPARATOR---\n\n".join(
        [f"CHUNK {i+1} ANALYSIS:\n{analysis}" for i, analysis in enumerate(chunk_analyses)]
    )
    
    human_message = HumanMessage(content=f"""Combine these chunk analyses into ONE comprehensive report:

{combined_content}

Provide a unified analysis with:
1. OVERALL TEST SUMMARY (combined counts from all chunks)
2. FAILED TESTS ANALYSIS (all failures with root causes, grouped by pattern)
3. SKIPPED TESTS ANALYSIS (all skips with reasons, grouped by pattern)
4. KEY FINDINGS (overall patterns across all tests)
5. RECOMMENDATIONS (prioritized based on all data)

Present as a single coherent analysis, not as separate chunks.""")
    
    print("[Sending combined analysis request to Azure OpenAI...]")
    response = llm.invoke([system_message, human_message])
    
    return {
        'content': response.content,
        'metadata': response.response_metadata,
        'message_id': response.id,
        'usage': response.usage_metadata
    }


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
1. Overall pass/fail/skip statistics
2. Which tests failed vs. which were skipped
3. Brief description of failures and skips
4. Any critical issues that need immediate attention

IMPORTANT: Distinguish between FAILED and SKIPPED tests:
- FAILED = code/logic issues
- SKIPPED = environment/infrastructure issues""")
    
    human_message = HumanMessage(content=f"""Please provide a concise summary of this test report with FAILED and SKIPPED tests listed separately.

Test Report:
{report_content}

Provide a brief summary with two sections:

1. FAILED TESTS (Code Issues)
   - Count and list of failed tests
   - Brief description of each failure
   - Any patterns

2. SKIPPED TESTS (Environment Issues)
   - Count and list of skipped tests  
   - Brief reason for each skip
   - Any patterns (e.g., all on same device/cloud)

Keep it concise but clearly separate FAILED from SKIPPED.""")
    
    return [system_message, human_message]


def analyze_report(llm, report_content, callback=None):
    """
    Send the report to the LLM for detailed analysis.
    Automatically handles large reports by chunking them (no data loss).
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_content: Content of the test report
        callback: Optional callback function for progress updates
        
    Returns:
        dict: Analysis results containing content, metadata, and usage info
    """
    MAX_SAFE_CHARS = 200000  # ~50K tokens, leaves room for prompts + response
    
    # If report is large, chunk it (preserves all information)
    if len(report_content) > MAX_SAFE_CHARS:
        num_chunks = (len(report_content) + MAX_SAFE_CHARS - 1) // MAX_SAFE_CHARS
        msg = f"Report size: {len(report_content):,} characters - will analyze in {num_chunks} chunks"
        print(f"\n[{msg}]")
        if callback:
            callback(f"⚠️  Large report detected! {msg}")
            callback(f"⏱️  Estimated time: {num_chunks * 20}-{num_chunks * 30} seconds ({num_chunks * 20 // 60}-{num_chunks * 30 // 60} minutes)")
            callback("Please be patient, analyzing all data without loss...")
        
        chunks = split_report_into_chunks(report_content, max_chars_per_chunk=MAX_SAFE_CHARS)
        return analyze_report_chunks(llm, chunks, callback=callback)
    
    # Report is small enough, analyze normally
    messages = create_analysis_prompt(report_content)
    
    print("\n[Sending to Azure OpenAI for detailed analysis...]")
    if callback:
        callback("Sending to AI for analysis...")
    response = llm.invoke(messages)
    
    return {
        'content': response.content,
        'metadata': response.response_metadata,
        'message_id': response.id,
        'usage': response.usage_metadata
    }


def quick_summarize_report(llm, report_content, callback=None):
    """
    Send the report to the LLM for quick summarization.
    Automatically handles large reports by chunking them (no data loss).
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_content: Content of the test report
        callback: Optional callback function for progress updates
        
    Returns:
        dict: Analysis results containing content, metadata, and usage info
    """
    MAX_SAFE_CHARS = 200000
    
    # If report is large, chunk it (preserves all information)
    if len(report_content) > MAX_SAFE_CHARS:
        num_chunks = (len(report_content) + MAX_SAFE_CHARS - 1) // MAX_SAFE_CHARS
        msg = f"Report size: {len(report_content):,} characters - will analyze in {num_chunks} chunks"
        print(f"\n[{msg}]")
        if callback:
            callback(f"⚠️  Large report detected! {msg}")
            callback(f"⏱️  Estimated time: {num_chunks * 20}-{num_chunks * 30} seconds ({num_chunks * 20 // 60}-{num_chunks * 30 // 60} minutes)")
            callback("Please be patient, analyzing all data without loss...")
        
        chunks = split_report_into_chunks(report_content, max_chars_per_chunk=MAX_SAFE_CHARS)
        return analyze_report_chunks(llm, chunks, callback=callback)
    
    messages = create_quick_summary_prompt(report_content)
    
    print("\n[Sending to Azure OpenAI for quick summary...]")
    if callback:
        callback("Sending to AI for quick summary...")
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
2. Find common FAILURE patterns and SKIP patterns across builds
3. Identify regressions (new failures/skips) and fixes (resolved failures/skips)
4. Detect flaky tests that fail intermittently
5. Provide insights on overall quality trends
6. Suggest root causes for issues

CRITICAL: Analyze FAILED and SKIPPED tests separately:
- FAILED = code/logic issues
- SKIPPED = environment/infrastructure issues""")
    
    human_message = HumanMessage(content=f"""Please perform a detailed comparison of these two test runs, analyzing FAILED and SKIPPED separately.

BUILD 1: {build1_name}
{report1_content}

BUILD 2: {build2_name}
{report2_content}

Provide a comprehensive comparison analysis with:

1. OVERVIEW COMPARISON
   - Test counts (total, passed, failed, skipped) for each build
   - Pass rate and skip rate trends
   - Overall quality trend (improving/declining/stable)

2. FAILED TESTS COMPARISON (Code Issues)
   - Common failures in BOTH builds (persistent code issues)
   - New failures in Build 2 (code regressions)
   - Resolved failures in Build 2 (code fixes)
   - Patterns in failed tests

3. SKIPPED TESTS COMPARISON (Environment Issues)
   - Common skips in BOTH builds (persistent environment issues)
   - New skips in Build 2 (environment degradation)
   - Resolved skips in Build 2 (environment fixes)
   - Patterns in skips (e.g., specific devices, cloud dependencies)

4. FLAKY TESTS
   - Tests with inconsistent results (pass/fail/skip varies)
   - Tests that might need stability improvements

5. ENVIRONMENT vs. CODE HEALTH
   - Is quality declining due to code issues or environment issues?
   - Which is more critical to address?

6. ACTIONABLE RECOMMENDATIONS
   - For FAILED tests: Code fixes needed
   - For SKIPPED tests: Infrastructure/device fixes needed
   - Priority order

Keep FAILED and SKIPPED analysis completely separate to identify whether problems are code-related or environment-related.""")
    
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


def chat_with_report(llm, report_content, ai_summary, chat_history, user_question):
    """
    Interactive chat with AI about the test report.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_content: The full test report content
        ai_summary: The AI-generated summary (from quick or full analysis)
        chat_history: List of previous chat messages [{"role": "user/assistant", "content": "..."}]
        user_question: The user's current question
        
    Returns:
        dict: Chat response containing content, metadata, and usage info
    """
    # Build the system message with report context
    system_message = SystemMessage(content=f"""You are an expert test automation engineer assistant. 
You have access to a test report and its analysis. Your role is to:
1. Answer questions about the test report accurately
2. Provide insights about test failures and their causes
3. Help users understand error messages and patterns
4. Suggest actionable next steps
5. Be concise but thorough in your explanations

Here is the test report you're analyzing:

--- TEST REPORT ---
{report_content[:8000]}  # Limit to first 8000 chars to manage tokens
--- END TEST REPORT ---

Here is the AI analysis summary:
--- AI ANALYSIS ---
{ai_summary}
--- END AI ANALYSIS ---

Answer the user's questions based on this context. If the information isn't in the report, 
say so clearly. Always ground your answers in the actual report data.""")
    
    # Build messages list with chat history
    messages = [system_message]
    
    # Add chat history (last 5 exchanges to manage token usage)
    for msg in chat_history[-10:]:  # Last 10 messages (5 exchanges)
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(AIMessage(content=msg['content']))
    
    # Add current question
    messages.append(HumanMessage(content=user_question))
    
    # Get response from LLM
    response = llm.invoke(messages)
    
    return {
        'content': response.content,
        'metadata': response.response_metadata,
        'message_id': response.id,
        'usage': response.usage_metadata
    }


def chat_with_comparison(llm, report1_content, report2_content, comparison_summary, 
                         build1_name, build2_name, chat_history, user_question):
    """
    Interactive chat with AI about the comparison of two test reports.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report1_content: Content of the first test report
        report2_content: Content of the second test report
        comparison_summary: The AI-generated comparison summary
        build1_name: Name of the first build
        build2_name: Name of the second build
        chat_history: List of previous chat messages
        user_question: The user's current question
        
    Returns:
        dict: Chat response containing content, metadata, and usage info
    """
    # Build the system message with comparison context
    system_message = SystemMessage(content=f"""You are an expert test automation engineer assistant. 
You have access to two test reports and their comparison analysis. Your role is to:
1. Answer questions about the comparison accurately
2. Explain differences, regressions, and fixes
3. Identify patterns across both runs
4. Help users understand what changed between builds
5. Suggest actionable next steps

Here are the two builds being compared:
- Build 1: {build1_name}
- Build 2: {build2_name}

--- REPORT 1 ({build1_name}) ---
{report1_content[:4000]}  # Limit to manage tokens
--- END REPORT 1 ---

--- REPORT 2 ({build2_name}) ---
{report2_content[:4000]}  # Limit to manage tokens
--- END REPORT 2 ---

Here is the comparison analysis:
--- COMPARISON ANALYSIS ---
{comparison_summary}
--- END COMPARISON ANALYSIS ---

Answer the user's questions based on this comparison context. If the information isn't in the 
reports, say so clearly. Always ground your answers in the actual report data.""")
    
    # Build messages list with chat history
    messages = [system_message]
    
    # Add chat history (last 10 messages to manage token usage)
    for msg in chat_history[-10:]:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(AIMessage(content=msg['content']))
    
    # Add current question
    messages.append(HumanMessage(content=user_question))
    
    # Get response from LLM
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


