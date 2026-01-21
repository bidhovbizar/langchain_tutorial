# Testbed Information in History Display

## 🎯 Goal

Add testbed information (region and environment) to the history sidebar so users can quickly:
- Identify which region tests ran in (eu_central_1, us_east_1, etc.)
- Identify which environment was used (staging, qatest, production)
- Compare results from same/different regions
- Filter by environment for targeted analysis

## ✅ Implementation

### Testbed Format

Testbeds follow this naming pattern:
```
{region}_{environment}_{service}_api_{timestamp}
```

**Examples:**
- `eu_central_1_staging_sars_api_20260120_104005`
- `us_east_1_qatest_sars_api_20260121_090045`
- `us_west_2_production_imm_api_20260119_153020`
- `ap_south_1_staging_imm_api_20260118_120030`

### Parsing Logic

**File**: `utils/session_manager.py`

```python
# Extract testbed information
testbed = summary_data.get('Test_bed', '')

# Parse to extract region and environment
# Format: eu_central_1_staging_sars_api_20260120_104005
region = ''
environment = ''

if testbed:
    parts = testbed.split('_')
    # First 3 parts are the region (e.g., eu_central_1)
    if len(parts) >= 3:
        region = '_'.join(parts[:3])
    # 4th part is the environment (staging, qatest, production)
    if len(parts) >= 4:
        environment = parts[3]
```

### Display Format

**Before (no testbed info):**
```
staging_sars_sanity_build_7500
📅 2026-01-21 22:30:00 | 🔍 FULL
✅ 151/155 passed (97.4%)
```

**After (with testbed info):**
```
staging_sars_sanity_build_7500
🌍 eu_central_1 | 🏷️ staging
📅 2026-01-21 22:30:00 | 🔍 FULL
✅ 151/155 passed (97.4%)
```

## 📊 Examples

### History Sidebar Display

```
┌─────────────────────────────────────────┐
│ History (3/8)                           │
├─────────────────────────────────────────┤
│ ☐ staging_sars_sanity_build_7500        │
│   🌍 eu_central_1 | 🏷️ staging          │
│   📅 2026-01-21 22:30:00 | 🔍 FULL      │
│   ✅ 151/155 passed (97.4%)             │
│   [👁️ View]                             │
├─────────────────────────────────────────┤
│ ☐ qatest_sars_sanity_build_7499         │
│   🌍 us_east_1 | 🏷️ qatest              │
│   📅 2026-01-21 21:45:00 | 🔍 QUICK     │
│   ✅ 161/171 passed (94.2%)             │
│   [👁️ View]                             │
├─────────────────────────────────────────┤
│ ☐ production_imm_sanity_build_8875      │
│   🌍 us_west_2 | 🏷️ production          │
│   📅 2026-01-21 20:15:00 | 🔍 FULL      │
│   ✅ 168/170 passed (98.8%)             │
│   [👁️ View]                             │
└─────────────────────────────────────────┘
```

## 🎯 Use Cases

### Use Case 1: Regional Comparison

**Scenario**: Compare test results across different regions

```
History shows:
  ☐ build_7500 | 🌍 eu_central_1 | 🏷️ staging | ✅ 97.4%
  ☐ build_7501 | 🌍 us_east_1    | 🏷️ staging | ✅ 95.2%
  ☐ build_7502 | 🌍 us_west_2    | 🏷️ staging | ✅ 98.1%

Observation:
  - EU Central: 97.4% pass rate
  - US East: 95.2% pass rate ⚠️ Lower!
  - US West: 98.1% pass rate

Action: Investigate US East region-specific issues
```

### Use Case 2: Environment Validation

**Scenario**: Verify staging matches production

```
History shows:
  ☐ build_7500 | 🌍 eu_central_1 | 🏷️ staging    | ✅ 97.4%
  ☐ build_7500 | 🌍 eu_central_1 | 🏷️ production | ✅ 97.8%

Observation:
  - Same region, same build
  - Similar pass rates (97.4% vs 97.8%)
  - Staging validated for production

Action: Safe to promote to production
```

### Use Case 3: QAtest vs. Staging

**Scenario**: Compare QAtest and staging environments

```
History shows:
  ☐ build_7499 | 🌍 us_east_1 | 🏷️ qatest  | ✅ 94.2%
  ☐ build_7499 | 🌍 us_east_1 | 🏷️ staging | ✅ 97.4%

Observation:
  - Same region, same build
  - QAtest has lower pass rate (94.2% vs 97.4%)
  - Environment parity issue

Action: Investigate QAtest environment configuration
```

### Use Case 4: Multi-Region Rollout

**Scenario**: Rolling out to multiple regions, track progress

```
History shows:
  ☐ build_8000 | 🌍 us_west_2    | 🏷️ production | ✅ 99.1% ✅
  ☐ build_8000 | 🌍 us_east_1    | 🏷️ production | ✅ 98.5% ✅
  ☐ build_8000 | 🌍 eu_central_1 | 🏷️ production | ✅ 98.9% ✅
  ☐ build_8000 | 🌍 ap_south_1   | 🏷️ production | ❌ 87.2% ⚠️

Observation:
  - US/EU regions: All >98% pass rate
  - AP South: Only 87.2% pass rate

Action: Hold AP South rollout, investigate regional issues
```

### Use Case 5: Flaky Region Detection

**Scenario**: Identify if a region has infrastructure problems

```
History over time:
  build_7495 | 🌍 eu_central_1 | 🏷️ staging | ✅ 95.2%
  build_7496 | 🌍 eu_central_1 | 🏷️ staging | ✅ 96.1%
  build_7497 | 🌍 eu_central_1 | 🏷️ staging | ✅ 89.5% ⚠️
  build_7498 | 🌍 eu_central_1 | 🏷️ staging | ✅ 90.2% ⚠️
  build_7499 | 🌍 eu_central_1 | 🏷️ staging | ✅ 94.8%

Observation:
  - EU Central staging had dip in builds 7497-7498
  - Recovered in 7499
  - Possible infrastructure hiccup

Action: Review EU Central infrastructure logs for that time period
```

## 🔍 Parsing Details

### Region Extraction

Regions are the first 3 underscore-separated parts:

| Testbed | Region |
|---------|--------|
| `eu_central_1_staging_sars_api_...` | `eu_central_1` |
| `us_east_1_qatest_sars_api_...` | `us_east_1` |
| `us_west_2_production_imm_api_...` | `us_west_2` |
| `ap_south_1_staging_imm_api_...` | `ap_south_1` |
| `ap_southeast_1_qatest_sars_api_...` | `ap_southeast_1` |

### Environment Extraction

Environment is the 4th underscore-separated part:

| Testbed | Environment |
|---------|-------------|
| `eu_central_1_staging_sars_api_...` | `staging` |
| `us_east_1_qatest_sars_api_...` | `qatest` |
| `us_west_2_production_imm_api_...` | `production` |

### Fallback Handling

```python
# If testbed doesn't follow expected format
if not testbed:
    # Don't show region/environment line
    pass

# If parsing fails
if not region and not environment:
    # Don't show region/environment line
    pass
```

## 📋 Benefits

### Quick Identification
- ✅ Instantly see which region test ran in
- ✅ Instantly see which environment
- ✅ No need to expand details or check metadata

### Easy Comparison
- ✅ Compare same region across builds
- ✅ Compare different regions for same build
- ✅ Compare environments (staging vs production)

### Better Decision Making
- ✅ Regional rollout decisions
- ✅ Environment parity validation
- ✅ Infrastructure issue detection
- ✅ Targeted debugging

### Improved Workflow
- ✅ Filter mentally by region/environment
- ✅ Quickly find relevant comparisons
- ✅ Spot patterns in failures
- ✅ Track regional health over time

## 🎨 Design Choices

### 1. **Separate Line for Testbed Info**
```
staging_sars_sanity_build_7500
🌍 eu_central_1 | 🏷️ staging      ← Separate line
📅 2026-01-21 22:30:00 | 🔍 FULL
```
**Why**: Keeps build name clean, groups related info (region/env)

### 2. **Emoji Icons**
- 🌍 for Region - Universal globe symbol
- 🏷️ for Environment - Tag/label symbol
**Why**: Quick visual identification, consistent with rest of UI

### 3. **Pipe Separator**
```
🌍 eu_central_1 | 🏷️ staging
```
**Why**: Clear separation, easy to scan

### 4. **Abbreviated Display**
- Region: `eu_central_1` (not full testbed)
- Environment: `staging` (not full testbed)
**Why**: Compact, shows only relevant info

### 5. **Conditional Display**
- Only show line if testbed data exists
**Why**: Graceful degradation for old data or missing testbed

## 📊 Visual Impact

### Sidebar Space Usage

**Before**: 3 lines per entry
```
staging_sars_sanity_build_7500
📅 2026-01-21 22:30:00 | 🔍 FULL
✅ 151/155 passed (97.4%)
```

**After**: 4 lines per entry
```
staging_sars_sanity_build_7500
🌍 eu_central_1 | 🏷️ staging
📅 2026-01-21 22:30:00 | 🔍 FULL
✅ 151/155 passed (97.4%)
```

**Trade-off**: +1 line per entry, but provides critical context

**With 8 entries**: +8 lines total (acceptable with compact UI)

## 🔧 Technical Details

### Data Flow

```
1. User analyzes report
   ↓
2. Analyzer extracts testbed from index.html
   ↓
3. Stored in analyzer_results['summary']['Test_bed']
   ↓
4. SessionManager.add_to_history() saves entry
   ↓
5. SessionManager.format_history_summary() parses testbed
   ↓
6. Displays region and environment in sidebar
```

### Code Location

**File**: `utils/session_manager.py`
**Function**: `format_history_summary()`
**Lines**: ~165-175 (testbed parsing and display)

### Compatibility

- ✅ Works with existing history entries (gracefully handles missing testbed)
- ✅ Works with all testbed formats (flexible parsing)
- ✅ No changes needed to other components
- ✅ Backward compatible

## 🎉 Summary

**Added**: Region and environment display in history sidebar

**Format**:
```
🌍 {region} | 🏷️ {environment}
```

**Benefits**:
- ✅ Quick identification of test environment
- ✅ Easy regional comparison
- ✅ Better decision making
- ✅ Improved debugging workflow

**Impact**: Makes it immediately clear where tests ran, enabling better comparisons and faster triage!

---

**Now you can instantly see if tests ran in EU vs US, staging vs production - critical for regional rollouts and environment validation!** 🚀

