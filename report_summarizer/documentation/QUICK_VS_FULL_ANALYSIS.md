# Quick vs Full Analysis Modes

## Overview

Both Quick and Full analysis modes now use AI and process the complete test report from `test_results_analyzer_full_error.py`. The only difference is the prompt used, which affects the depth and style of analysis.

## Key Changes

### ✅ What Changed
- **Quick Mode**: Now uses AI (previously was text-based parsing)
- **Both Modes**: Process the same complete report with all test details
- **Difference**: Only in the AI prompt - summary vs detailed analysis

### ❌ What Did NOT Change
- Report generation by `test_results_analyzer_full_error.py` (still the same)
- Error extraction and parsing (still comprehensive)
- Token management and authentication (still intelligent)

## Mode Comparison

### Quick Mode ⚡

**Purpose**: Fast, concise AI-powered summary of test results

**Prompt Focus**:
- Overall pass/fail statistics
- List of failed tests
- Brief description of failures
- Critical issues needing immediate attention

**Best For**:
- Quick triage of test results
- Getting overview of multiple builds
- Rapid assessment before deep dive
- Daily standup discussions

**Time**: ~10-20 seconds

**Output Example**:
```
Test Run Summary
================

Overall Statistics:
- Total Tests: 174
- Passed: 161
- Failed: 13
- Pass Rate: 92.5%

Failed Tests:
1. c220m5_1_config_drift - Config state failed after 30 minutes
2. c220m6_1_config_drift - Config state failed after 30 minutes
3. c225m8_1_config_drift - Attributes did not reach expected values

Critical Issues:
- Config drift tests consistently failing
- Timeout issues in profile association

Recommendation: Investigate config state validation timeouts
```

### Full Mode 🔍

**Purpose**: Deep, detailed AI-powered root cause analysis

**Prompt Focus**:
- Identify and categorize test failures
- Extract root causes from error messages and stack traces
- Provide concise, actionable summaries
- Highlight patterns in failures
- Suggest potential fixes or areas for investigation
- Group failures by root cause
- Provide detailed recommendations

**Best For**:
- Detailed investigation of failures
- Root cause analysis
- Creating bug reports
- Understanding complex failure patterns
- Planning fixes

**Time**: ~30-60 seconds

**Output Example**:
```
Detailed Failure Analysis
========================

Overall Test Summary:
- Total Tests: 174
- Failed: 13 (7.5%)
- Pass Rate: 92.5%

Failure Analysis (Grouped by Root Cause):

1. Configuration State Validation Failures (3 tests)
   Tests Affected:
   - c220m5_1_config_drift
   - c220m6_1_config_drift
   - c225m8_1_config_drift
   
   Root Cause:
   The config_context.config_state attribute remains in 'Failed' 
   state instead of transitioning to the expected state. This
   occurs after waiting 30 minutes for state transition.
   
   Stack Trace Analysis:
   - Exception originates in waitForAttributes() function
   - Timeout set to 1800 seconds (30 minutes)
   - Profile enters 'Failed' state instead of 'Associated'
   
   Recommendations:
   a) Investigate why profiles enter Failed state
   b) Check backend logs for profile deployment errors
   c) Verify network connectivity during profile association
   d) Review policy configurations attached to profiles

[... continues with other failure groups ...]

Key Findings:
- All config drift tests failing consistently
- Pattern suggests backend service issue
- Similar timeout behavior across different hardware

Recommendations:
1. Check backend service health
2. Review recent changes to config drift workflow
3. Investigate timeout configuration
4. Consider increasing timeout or adding intermediate checks
```

## Technical Implementation

### Quick Mode Implementation

```python
def create_quick_summary_prompt(report_content):
    system_message = "You are an expert QA engineer who provides concise test summaries..."
    
    human_message = f"""Please provide a concise summary of this test report.
Focus on:
- Overall test statistics
- List of failed tests
- Brief description of each failure
- Any patterns you notice

Keep the summary concise but informative.

Test Report:
{report_content}"""
```

### Full Mode Implementation

```python
def create_analysis_prompt(report_content):
    system_message = """You are an expert test automation engineer specializing in 
analyzing test failure reports. Your role is to:
1. Identify and categorize test failures
2. Extract root causes from error messages and stack traces
3. Provide concise, actionable summaries
4. Highlight patterns in failures
5. Suggest potential fixes or areas for investigation"""
    
    human_message = f"""Please analyze this test report and provide a comprehensive summary 
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
- Recommendations"""
```

## Data Flow

Both modes follow the same workflow:

```
User provides URL
      ↓
URL converted to local path
      ↓
test_results_analyzer extracts errors
      ↓
Full report saved to /tmp/
      ↓
      ├─→ Quick Mode: Use quick_summary_prompt
      └─→ Full Mode: Use detailed_analysis_prompt
      ↓
Send to Azure OpenAI (GPT-4)
      ↓
Receive AI analysis
      ↓
Display to user
```

## Token Usage

### Quick Mode
- **Input Tokens**: ~2,000-4,000 (full report)
- **Output Tokens**: ~300-800 (concise summary)
- **Total**: ~2,500-5,000 tokens
- **Cost**: Lower due to shorter output

### Full Mode  
- **Input Tokens**: ~2,000-4,000 (full report)
- **Output Tokens**: ~800-2,000 (detailed analysis)
- **Total**: ~3,000-6,000 tokens
- **Cost**: Higher due to longer output

## When to Use Which Mode

### Use Quick Mode When:
- ✅ You need a fast overview
- ✅ Triaging multiple test runs
- ✅ Checking overall health
- ✅ Time is limited
- ✅ You know what to look for
- ✅ Daily status checks

### Use Full Mode When:
- ✅ Investigating specific failures
- ✅ Need root cause analysis
- ✅ Creating bug reports
- ✅ Complex failure patterns
- ✅ Need actionable recommendations
- ✅ Planning fixes

## User Experience

### In the Web UI

**Quick Mode**:
- Select "Quick" from dropdown
- Click "Analyze"
- Wait 10-20 seconds
- Get concise summary

**Full Mode**:
- Select "Full" from dropdown
- Click "Analyze"
- Wait 30-60 seconds
- Get detailed analysis

### Download Options

Both modes generate downloadable reports:
- `quick_summary_[timestamp].txt` - Quick mode
- `full_analysis_[timestamp].txt` - Full mode

## Benefits of New Quick Mode

### Before (Old Quick Mode)
- ❌ Simple text parsing
- ❌ No AI insights
- ❌ Limited to what's in report headers
- ❌ Missed subtle patterns
- ❌ No context understanding

### After (New Quick Mode)
- ✅ AI-powered analysis
- ✅ Full report coverage
- ✅ Identifies patterns
- ✅ Contextual understanding
- ✅ Professional summaries
- ✅ Faster than Full mode

## Example Workflow

### Scenario: Morning Triage

1. **Check overnight builds** (Quick Mode)
   - Build A: 98% pass → ✅ Looks good
   - Build B: 85% pass → ⚠️ Needs attention
   - Build C: 92% pass → ✅ Minor issues

2. **Investigate Build B** (Full Mode)
   - Deep dive into 15% failures
   - Get root cause analysis
   - Create action items

3. **Compare builds** (Quick Mode)
   - Use comparison feature
   - Identify regression patterns
   - Track failure trends

## Summary

| Aspect | Quick Mode | Full Mode |
|--------|-----------|-----------|
| **Uses AI** | ✅ Yes | ✅ Yes |
| **Full Report** | ✅ Yes | ✅ Yes |
| **Prompt Style** | Concise | Detailed |
| **Time** | 10-20 sec | 30-60 sec |
| **Output Length** | Short | Long |
| **Tokens Used** | 2.5-5K | 3-6K |
| **Best For** | Triage | Investigation |
| **Root Cause** | Brief | Deep |
| **Recommendations** | Basic | Detailed |

Both modes are powerful and use the complete test report - choose based on how much detail you need!

