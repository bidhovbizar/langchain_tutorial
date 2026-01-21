# AI Comparison - Quick Usage Guide

## 🎯 What Is AI Comparison?

AI Comparison uses GPT-4 to analyze **two complete test reports** and find:
- **Common Failures**: Issues present in BOTH builds (persistent bugs)
- **Regressions**: New failures that appeared in later build
- **Fixes**: Failures that got resolved in later build
- **Flaky Tests**: Tests with inconsistent results
- **Patterns**: Common root causes and recommendations

## 🚀 How to Use (3 Simple Steps)

### Step 1: Build Your History

Analyze multiple test runs to build your history:

```
1. Paste URL: https://supernova.cisco.com/.../staging_sars_sanity_build_7500/.../detail.html
2. Select "Quick" or "Full"
3. Click "Analyze"
4. Wait for results

Repeat for another build:

1. Paste URL: https://supernova.cisco.com/.../qatest_sars_sanity_build_7499/.../detail.html
2. Select "Quick" or "Full"
3. Click "Analyze"
4. Wait for results
```

Your history now has 2 entries!

### Step 2: Select Builds to Compare

In the sidebar history panel:

```
☐ staging_sars_sanity_build_7500 (2026-01-21 21:30)
☐ qatest_sars_sanity_build_7499 (2026-01-21 21:25)
```

Check the boxes:

```
☑ staging_sars_sanity_build_7500 (2026-01-21 21:30)
☑ qatest_sars_sanity_build_7499 (2026-01-21 21:25)
```

Click **"Compare Selected"**

### Step 3: Run AI Analysis

You'll see:

1. **Quick Stats** - Pass rates, test counts (instant)
2. **AI Analysis Button** - Click "Run AI Comparison Analysis"
3. **Progress Updates** - Watch as AI analyzes both reports (30-60 sec)
4. **Comprehensive Report** - View detailed comparison
5. **Download** - Save the comparison as `.txt` file

## 📊 What You'll See

### Before AI Comparison (Just Stats)

```
Build 1: staging_sars_sanity_build_7500
  Total: 174 tests
  Failed: 13
  Pass Rate: 92.5%

Build 2: qatest_sars_sanity_build_7499
  Total: 174 tests
  Failed: 13
  Pass Rate: 92.5%
```

*Okay, but what's actually different?*

### After AI Comparison (Deep Insights!)

```
BUILD COMPARISON ANALYSIS
=========================

1. OVERVIEW COMPARISON
   
   Both builds show identical 92.5% pass rate.
   Trend: STABLE ✓
   
2. COMMON FAILURES (10 tests)
   
   These PERSISTENT issues need attention:
   
   a) Config Drift Timeout (3 tests)
      - c220m5_1_config_drift
      - c220m6_1_config_drift
      - c225m8_1_config_drift
      
      Root Cause: Backend timeout after 30 minutes
      Impact: HIGH - blocks config workflow
      Fix: Investigate backend config service
   
   b) Locator LED Tests (3 tests)
      - c220m5_1_locator_led
      - c220m6_1_locator_led
      - c225m8_1_locator_led
      
      Root Cause: CIMC communication issue
      Impact: MEDIUM
      Fix: Check hardware interface layer
   
   c) FW Download Tests (2 tests)
      - test_fw_download_c220m5
      - test_fw_download_c220m6
      
      Root Cause: Download timeout
      Impact: MEDIUM
      Fix: Increase timeout or check network

3. REGRESSIONS (3 NEW failures in Build 7499)
   
   ⚠️ These tests PASSED in 7500 but FAILED in 7499:
   
   - test_profile_validation
     Reason: Schema validation changed
     Action: Review profile schema updates
   
   - test_server_discovery
     Reason: QAtest environment specific
     Action: Check environment parity
   
   - test_policy_binding
     Reason: API version mismatch
     Action: Align API versions

4. FIXES (2 resolved failures)
   
   ✅ These tests FAILED in 7500 but PASSED in 7499:
   
   - test_inventory_sync
     Fixed by: Backend sync improvement
   
   - test_alarm_notification
     Fixed by: Notification service update

5. FLAKY TESTS
   
   No obvious flaky tests detected.
   All failures are consistent across builds.

6. PATTERNS & INSIGHTS
   
   Key Findings:
   
   a) Environment Differences
      - 3 regressions are environment-specific
      - QAtest and Staging configurations differ
      - Action: Audit environment parity
   
   b) Timeout-Based Failures
      - Multiple 30-minute timeouts
      - Backend performance issue suspected
      - Action: Profile backend service
   
   c) Hardware Communication
      - LED/sensor tests consistently fail
      - CIMC interface problem
      - Action: Review CIMC communication
   
   d) Quality Trend
      - Overall: STABLE at 92.5%
      - Some fixes, some regressions (net zero)
      - Focus on persistent failures first

PRIORITY RECOMMENDATIONS:

Priority 1 (High Impact):
✓ Fix config drift timeout (affects 3 tests)
✓ Resolve environment differences
✓ Investigate backend performance

Priority 2 (Medium Impact):
✓ Fix CIMC LED communication
✓ Review timeout thresholds
✓ Validate profile schema changes

Priority 3 (Low Impact):
✓ Document hardware limitations
✓ Consider non-blocking LED tests
```

## 🎯 Real-World Use Cases

### Use Case 1: Pre-Production Validation

**Scenario**: Check if staging is ready for production

```bash
Step 1: Analyze staging build
Step 2: Analyze production build
Step 3: Compare both
Step 4: Review regressions section
Decision: If no regressions → Deploy
         If regressions found → Investigate before deploy
```

**Example**:
```
Comparison Result:
- 0 regressions ✓
- 5 fixes ✓
- 3 common failures (known issues) ⚠️

Decision: SAFE TO DEPLOY
```

### Use Case 2: Environment Parity Check

**Scenario**: Ensure QAtest matches staging

```bash
Step 1: Analyze staging_build_7500
Step 2: Analyze qatest_build_7500 (same build, different env)
Step 3: Compare
Step 4: Look for environment-specific failures
```

**Example**:
```
Comparison Result:
- 8 environment-specific failures ❌
- Different API versions
- Configuration mismatches

Decision: ENVIRONMENTS OUT OF SYNC
Action: Fix environment parity issues
```

### Use Case 3: Regression Tracking

**Scenario**: Did the new code break anything?

```bash
Step 1: Analyze build_7490 (before changes)
Step 2: Analyze build_7500 (after changes)
Step 3: Compare
Step 4: Check regressions section
```

**Example**:
```
Comparison Result:
- 0 regressions ✓
- 10 new fixes ✓
- Code changes improved quality!

Decision: CHANGES ARE GOOD
```

### Use Case 4: Flaky Test Detection

**Scenario**: Find unreliable tests

```bash
Step 1: Analyze same build (run 1)
Step 2: Re-analyze same build (run 2)
Step 3: Compare
Step 4: Look for flaky tests section
```

**Example**:
```
Comparison Result:
- 5 tests failed in run 1, passed in run 2
- Flaky tests identified:
  * test_connection_pool
  * test_async_callback
  * test_race_condition

Decision: STABILIZE THESE TESTS
```

## ⏱️ Timing

- **Quick Stats**: Instant (< 1 second)
- **AI Analysis**: 30-60 seconds
- **Total Time**: ~1 minute

**Manual Analysis Alternative**: 30-60 minutes per comparison

**Time Saved**: ~30-59 minutes!

## 💡 Tips & Tricks

### Tip 1: Build History Strategically

Analyze builds in a logical order:
```
1. Production baseline
2. Staging candidate
3. QAtest validation
4. Development latest
```

This gives you meaningful comparisons!

### Tip 2: Compare Related Builds

**Good Comparisons**:
- ✅ Staging vs Production (same version, different env)
- ✅ Build N vs Build N+1 (consecutive builds)
- ✅ Before fix vs After fix

**Less Useful Comparisons**:
- ❌ Staging vs QAtest (different builds AND environments)
- ❌ Build 7000 vs Build 7500 (too far apart)

### Tip 3: Use Cached Results

Once you run a comparison, it's cached for your session!

You can:
- Go back to main analysis
- Return to comparison
- See same results instantly (no re-analysis)

To force fresh analysis:
- Click "Run New Comparison"

### Tip 4: Download Everything

Always download comparison reports:
- Share with team
- Track over time
- Include in release notes
- Attach to bug reports

### Tip 5: Focus on Actionable Items

The AI provides priorities:
```
Priority 1 (High Impact): FIX THESE FIRST
Priority 2 (Medium Impact): FIX NEXT
Priority 3 (Low Impact): FIX IF TIME PERMITS
```

Follow this guidance for maximum impact!

## 🔄 Complete Example Workflow

```
=== Morning Sanity Check ===

1. Paste URL: https://supernova.cisco.com/.../staging_sars_sanity_build_7501/.../detail.html
2. Select "Quick"
3. Click "Analyze"
   Result: 174 tests, 15 failures, 91.4% pass rate

4. Check history - compare with yesterday's 7500
5. Select both in history
6. Click "Compare Selected"
7. Click "Run AI Comparison Analysis"
8. Wait 45 seconds...

=== AI Report ===

REGRESSIONS: 2 new failures
- test_config_validation (timeout)
- test_profile_update (API error)

FIXES: 0

COMMON: 13 persistent failures

RECOMMENDATION: Investigate 2 new failures before promoting

=== Action ===

9. Download comparison report
10. File bugs for 2 new failures
11. Share report with dev team
12. Don't promote until fixed

Total Time: 3 minutes
Manual Alternative: 45+ minutes
```

## 📈 What Makes This Valuable?

### Without AI Comparison:
1. Open build 1 detail.html in browser
2. Manually list all failures
3. Open build 2 detail.html in browser
4. Manually list all failures
5. Compare lists by hand
6. Try to find patterns
7. Miss subtle differences
8. No root cause insights
9. No prioritization
10. Takes 30-60 minutes

### With AI Comparison:
1. Select 2 builds
2. Click button
3. Wait 1 minute
4. Get comprehensive analysis
5. See patterns, root causes, priorities
6. Download report
7. Share with team
8. Done!

## 🎊 Summary

**AI Comparison = Intelligence + Speed**

- 🧠 **Intelligent**: Finds patterns humans miss
- ⚡ **Fast**: 1 minute vs 30+ minutes
- 🎯 **Actionable**: Prioritized recommendations
- 📊 **Comprehensive**: All aspects covered
- 💾 **Shareable**: Download and distribute

**Use it every time you need to compare builds!**

---

*Questions? See `AI_COMPARISON_FEATURE.md` for technical details.*

