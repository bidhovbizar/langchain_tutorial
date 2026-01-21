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

# OAuth2 credentials for Cisco identity service
# Please reach out for client_id and client_secret
CLIENT_ID = ''
CLIENT_SECRET = ''

# Cisco Brain configuration
CISCO_OPENAI_APP_KEY = 'egai-prd-networking-123120833-summarize-1768589443863'
CISCO_BRAIN_USER_ID = 'bbizar'

# Hardcoded token (for development - in production, get fresh token)
ACCESS_TOKEN = "eyJraWQiOiI5NGU4cmxzTzUyUmhoc1RfWDNVMkRvb1lFS2xRTzZlaFRaM3NVajBVUXpnIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmdaeThCLWY1bkJ5VEVXLV9LbXY1ajdYUmk0SUFMbXFzVWR4Z0ZvdnFKU1UiLCJpc3MiOiJodHRwczovL2lkLmNpc2NvLmNvbS9vYXV0aDIvZGVmYXVsdCIsImF1ZCI6ImFwaTovL2RlZmF1bHQiLCJpYXQiOjE3Njg5OTY1MDUsImV4cCI6MTc2OTAwMDEwNSwiY2lkIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJzY3AiOlsiY3VzdG9tc2NvcGUiXSwic3ViIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJhenAiOiIwb2FzaWp0aHQwS0p3OTlkVzVkNyJ9.JxUg1NmNpj6RbWuNSjbLciL2Wp_WiaGhxHk8D7cwiu73LrN7Qpjv2eMbxsegUK-0T-Fm_ON75bR8fSRzPMHuFvFw0APnyDo8uQCxzdcLQaFIZP7XQwY-J5AfXK1sJViV-NZRO_cMlwRje4YOsKUQXS6z-ww19hDuikgX4CdpKko4NG3ocmyB5xThmFxvJ99xTTbLm_O22h2E7Xe-n3-4lTlxDK6ZJlm7vT1CFGfdVmiZzN4YjW8n0XA2XhuPoOWPekZKhR94aKBG7-gWdOvjhNDRo2W9Vo6rYPNoWjAXRSJuDushGYB9wZRNwRzcPgcHgmzq8r-71G65q7MILaQGLA"


def get_oauth_token(client_id, client_secret):
    """
    Get OAuth2 access token from Cisco identity service.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        
    Returns:
        str: Access token
    """
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
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Warning: Could not get fresh token: {e}")
        print("Using hardcoded token instead...")
        return ACCESS_TOKEN


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


def analyze_report(llm, report_content):
    """
    Send the report to the LLM for analysis.
    
    Args:
        llm: Initialized AzureChatOpenAI instance
        report_content: Content of the test report
        
    Returns:
        dict: Analysis results containing content, metadata, and usage info
    """
    messages = create_analysis_prompt(report_content)
    
    print("\n[Sending to Azure OpenAI for analysis...]")
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
    
    # Step 2: Get OAuth token (or use hardcoded one)
    print("\n[2/4] Authenticating with Cisco identity service...")
    if CLIENT_ID and CLIENT_SECRET:
        access_token = get_oauth_token(CLIENT_ID, CLIENT_SECRET)
    else:
        print("⚠️  No client credentials provided, using hardcoded token")
        access_token = ACCESS_TOKEN
    print("✅ Authentication successful")
    
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

