# AI-Powered Build Comparison

## Overview

The system now includes intelligent AI-powered comparison of test runs. Instead of just showing statistics side-by-side, the AI analyzes both complete reports to find similarities, differences, patterns, and provides insights.

## What Changed

### ✅ New Functionality

1. **AI Comparison Analysis**
   - Sends both complete reports to GPT-4
   - Identifies common failures, regressions, and fixes
   - Detects flaky tests
   - Provides root cause insights
   - Suggests improvements

2. **Smart Caching**
   - Comparison results are cached in session
   - Avoid re-running expensive analysis
   - Clear and re-run if needed

3. **Comprehensive Output**
   - Overview comparison
   - Common failures analysis
   - Regression detection (new failures)
   - Fix detection (resolved failures)
   - Flaky test identification
   - Patterns and insights

## How It Works

### User Workflow

1. **Select Builds to Compare**
   - Check 2 or more builds from history
   - Click "Compare Selected"

2. **View Quick Stats**
   - See basic statistics side-by-side
   - Pass rates, test counts, etc.

3. **Run AI Comparison**
   - Click "Run AI Comparison Analysis"
   - Wait 30-60 seconds
   - View comprehensive AI analysis

4. **Download Results**
   - Download comparison report
   - Share with team

### Behind the Scenes

```
User selects 2 builds
      ↓
Load cached reports from /tmp/
      ↓
Read both complete reports
      ↓
Send to AI with comparison prompt
      ↓
AI analyzes:
  - Common failures
  - New failures (regressions)
  - Fixed failures
  - Flaky tests
  - Patterns
      ↓
Display comprehensive analysis
      ↓
Cache result for session
```

## AI Comparison Prompt

The AI receives both reports with this specialized prompt:

```
You are an expert QA engineer specializing in comparative test analysis.

Compare these two test runs and provide:

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
```

## Example Output

### Basic Stats (Shown First)

```
Build 1: staging_sars_sanity_build_7500
  Total Tests: 174
  Failed: 13
  Pass Rate: 92.5%

Build 2: qatest_sars_sanity_build_7499
  Total Tests: 174
  Failed: 13
  Pass Rate: 92.5%
```

### AI Analysis (After Clicking Button)

```
BUILD COMPARISON ANALYSIS
=========================

1. OVERVIEW COMPARISON
   
   Both builds show identical pass rates (92.5%), indicating
   stable test quality between staging and qatest environments.
   
   - Build 7500 (Staging): 174 tests, 13 failures
   - Build 7499 (QAtest): 174 tests, 13 failures
   
   Trend: STABLE ✓

2. COMMON FAILURES (Persistent Issues)
   
   The following 10 tests failed in BOTH builds:
   
   a) Config Drift Tests (3 failures)
      - c220m5_1_config_drift
      - c220m6_1_config_drift  
      - c225m8_1_config_drift
      
      Root Cause: All three timeout after 30 minutes waiting
      for config_context.config_state to transition from
      'Failed' to 'Associated'. This is a persistent backend
      issue affecting both environments.
      
      Impact: HIGH - Blocks config validation workflow
      Recommendation: Investigate backend config service
   
   b) Locator LED Tests (3 failures)
      - c220m5_1_locator_led
      - c220m6_1_locator_led
      - c225m8_1_locator_led
      
      Root Cause: LED state remains 'off' despite set command.
      Likely hardware interface issue.
      
      Impact: MEDIUM - Feature not critical
      Recommendation: Check CIMC communication layer

   [... continues ...]

3. REGRESSIONS (New in Build 7499)
   
   Build 7499 introduced 3 NEW failures not present in 7500:
   
   - test_new_feature_x
     Reason: Appears to be a new test that's failing
     
   - test_deployment_y
     Reason: Environment-specific configuration issue
     
   - test_api_z
     Reason: API version mismatch in qatest

   These regressions suggest environment differences between
   staging and qatest that need reconciliation.

4. FIXES (Resolved in Build 7499)
   
   Build 7499 FIXED 3 failures that were present in 7500:
   
   ✅ test_profile_creation - Now passes consistently
   ✅ test_policy_attachment - Backend fix applied
   ✅ test_server_inventory - Data sync issue resolved
   
   These fixes demonstrate good progress on previously
   known issues.

5. FLAKY TESTS
   
   No obvious flaky tests detected. The failures are
   consistent across both builds, suggesting deterministic
   issues rather than intermittent problems.

6. PATTERNS & INSIGHTS
   
   Key Observations:
   
   a) Environment Parity Issues
      - 3 tests behave differently between staging/qatest
      - Suggests configuration drift between environments
      - Recommendation: Audit environment configurations
   
   b) Timeout-Related Failures  
      - Multiple tests fail due to 30-minute timeouts
      - Pattern suggests backend performance issues
      - Recommendation: Profile backend service latency
   
   c) Hardware Communication Issues
      - LED and sensor tests failing consistently
      - May indicate CIMC communication problems
      - Recommendation: Check hardware interface layer
   
   d) Overall Quality Assessment
      - 92.5% pass rate is acceptable but not ideal
      - 10 persistent failures need attention
      - Focus on config drift and timeout issues first

RECOMMENDATIONS:

Priority 1 (High Impact):
- Fix config drift timeout issue (affects 3 tests)
- Investigate backend service performance
- Reconcile staging vs qatest environment differences

Priority 2 (Medium Impact):
- Fix CIMC LED communication issues
- Review timeout values for reasonableness  
- Add intermediate progress checking

Priority 3 (Low Impact):
- Document known hardware communication limitations
- Consider marking some hardware tests as non-blocking
```

## Benefits

### Before (Old Comparison)
- ❌ Only showed basic statistics
- ❌ Manual analysis required
- ❌ Couldn't identify patterns
- ❌ No insights on root causes
- ❌ Limited actionability

### After (AI Comparison)
- ✅ Deep analysis of both reports
- ✅ Automated pattern detection
- ✅ Root cause insights
- ✅ Identifies regressions and fixes
- ✅ Detects flaky tests
- ✅ Actionable recommendations
- ✅ Priority-based guidance

## Use Cases

### 1. Regression Testing
**Scenario**: Compare production build with staging

```
Compare: production_7500 vs staging_7501
Result: AI identifies 5 new failures in staging
Action: Block staging promotion, investigate failures
```

### 2. Environment Validation
**Scenario**: Ensure qatest matches staging

```
Compare: staging_7500 vs qatest_7499  
Result: AI finds 3 environment-specific failures
Action: Fix environment parity issues
```

### 3. Trend Analysis
**Scenario**: Track improvements over time

```
Compare: build_7490 vs build_7500
Result: AI shows 10 fixes, 2 new failures
Action: Net positive trend, address new failures
```

### 4. Flaky Test Detection
**Scenario**: Find intermittent failures

```
Compare: Multiple runs of same build
Result: AI identifies tests with inconsistent results
Action: Stabilize flaky tests
```

## Token Usage

- **Input Tokens**: ~4,000-8,000 (both complete reports)
- **Output Tokens**: ~1,000-2,000 (comprehensive analysis)
- **Total**: ~5,000-10,000 tokens per comparison
- **Time**: ~30-60 seconds

## Caching Strategy

- Comparison results cached per session
- Key: `comparison_{id1}_{id2}`
- Persists until page refresh or manual clear
- Avoids expensive re-analysis

## Limitations

- Currently supports 2 builds at a time
- Requires both reports in /tmp/
- Token limit: ~4K tokens per report (very large reports may need truncation)
- Session-based caching (lost on refresh)

## Future Enhancements

Potential improvements:
- [ ] Compare 3+ builds simultaneously
- [ ] Persistent comparison history
- [ ] Visual diff highlighting
- [ ] Trend charts across multiple comparisons
- [ ] Email comparison reports
- [ ] Integration with JIRA for bug filing

## Technical Details

### Files Modified

1. **circuit_langchain_summarizer.py**
   - Added `create_comparison_prompt()`
   - Added `compare_reports()`

2. **utils/summarizer_wrapper.py**
   - Added `compare_multiple()` method
   - Token refresh and retry logic

3. **report_analyzer_web.py**
   - Enhanced `display_comparison()` with AI analysis
   - Added caching logic
   - Added download capability

### API Flow

```python
# User selects 2 builds
selected_entries = [entry1, entry2]

# Extract report paths
report_paths = [
    (entry1.report_path, entry1.build_name),
    (entry2.report_path, entry2.build_name)
]

# Run AI comparison
summarizer = SummarizerWrapper()
success, result, error = summarizer.compare_multiple(
    report_paths,
    callback=progress_callback
)

# Display result
if success:
    st.markdown(result['content'])
```

## Summary

🎉 **AI-Powered Comparison is Now Available!**

- ✅ Analyzes complete reports from both builds
- ✅ Identifies patterns and insights automatically
- ✅ Provides actionable recommendations
- ✅ Detects regressions, fixes, and flaky tests
- ✅ Saves time on manual comparison
- ✅ Download and share results

**The AI comparison transforms build comparison from a manual, tedious task into an automated, insightful analysis!**

