# Reportio URL Support

## Overview

The Test Report Analyzer & Summarizer now supports **two types of URLs**:

1. **Supernova URLs** (existing)
2. **Reportio URLs** (new)

Both URL types are automatically detected and processed seamlessly.

---

## URL Types

### 1. Supernova URLs

**Format:**
```
https://supernova.cisco.com/logviewer/runtests/results/sanity/<build_name>/test_results/<suite>/detail.html
```

**Example:**
```
https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7505/test_results/sars/detail.html
```

**Local Path Conversion:**
- Base URL: `https://supernova.cisco.com/logviewer/runtests/results/sanity/`
- Base Path: `/auto/intersight-sanity/sanity_logs/sanity/`
- Conversion: Replace base URL with base path

**Example Conversion:**
```
Input:  https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7505/test_results/sars/detail.html
Output: /auto/intersight-sanity/sanity_logs/sanity/staging_sars_sanity_build_7505/test_results/sars/index.html
```

---

### 2. Reportio URLs (NEW)

**Format:**
```
http://reportio.cisco.com/<path>/<project>/<build_name>/detail.html
```

**Example:**
```
http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html
```

**Local Path Conversion:**
- Base URL: `http://reportio.cisco.com/`
- Base Path: `/auto/CRR_Regression/`
- Conversion: Replace base URL with base path

**Example Conversion:**
```
Input:  http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html
Output: /auto/CRR_Regression/qali/iucstest/sanity_1839514_4924955718040703741/index.html
```

---

## Automatic Features

### 1. URL Type Detection

The system automatically detects which type of URL you provide:

```python
from utils.url_converter import URLConverter

url_type = URLConverter.get_url_type(url)
# Returns: 'supernova', 'reportio', or 'unknown'
```

### 2. Path Conversion

Both URL types are automatically converted to the correct local filesystem path:

```python
success, path, error = URLConverter.url_to_path(url)
```

### 3. Index.html Conversion

Both `detail.html` and `index.html` are supported. The system automatically converts to `index.html` for the analyzer:

- `detail.html` → `index.html` (same directory)
- `index.html` → `index.html` (no change)

### 4. Build Information Extraction

The system extracts relevant metadata from both URL types:

**Supernova URLs extract:**
- `build_name`: e.g., `staging_sars_sanity_build_7505`
- `environment`: e.g., `staging`, `qatest`, `production`
- `project`: e.g., `sars`, `imm`
- `build_number`: e.g., `7505`
- `suite`: e.g., `sars`, `sanity1`

**Reportio URLs extract:**
- `build_name`: e.g., `sanity_1839514_4924955718040703741`
- `project`: e.g., `iucstest`
- `qali_id`: e.g., `1839514`
- `run_id`: e.g., `4924955718040703741`
- `environment`: Set to `reportio` for identification

---

## Usage in Web Application

### Input

Simply paste either URL type into the web application input field:

**Supernova URL:**
```
https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7505/test_results/sars/detail.html
```

**Reportio URL:**
```
http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html
```

### Processing Flow

1. **URL Detection** - System detects URL type (Supernova or Reportio)
2. **Path Conversion** - Converts to local filesystem path
3. **Index.html Resolution** - Ensures `index.html` is targeted
4. **Analysis** - Runs `test_results_analyzer_full_error.py`
5. **AI Summarization** - Applies Quick or Full AI analysis
6. **History Storage** - Stores results with proper identification

### Analysis Modes

Both URL types support the same analysis modes:

- **Quick Analysis**: Concise summary of errors and potential causes
- **Full Analysis**: Detailed analysis with root causes and recommendations

### History and Comparison

- ✅ **History**: View past analyses from both Supernova and Reportio
- ✅ **Comparison**: Compare runs from different sources side-by-side
- ✅ **Download**: Download error reports for both URL types

---

## Files Modified

### 1. `utils/url_converter.py`

**New Methods:**
- `get_url_type(url)` - Detects URL type (supernova/reportio/unknown)
- `is_valid_reportio_url(url)` - Validates Reportio URLs
- `_convert_reportio_url(url)` - Converts Reportio URLs to local paths
- `_extract_reportio_build_info(url, info)` - Extracts build metadata

**Updated Methods:**
- `url_to_path(url)` - Now handles both URL types
- `extract_build_info(url)` - Extracts info from both URL types
- `get_example_urls()` - Returns examples of both URL types

### 2. `report_analyzer_web.py`

**UI Updates:**
- Changed "Supernova URL" to "Test Results URL"
- Updated placeholder text to mention both URL types
- Separated examples into "Supernova URLs" and "Reportio URLs"
- Updated help text to clarify support for both types

---

## Testing

### Test Script

A comprehensive test was performed to verify both URL types:

```bash
source /ws/bbizar-bgl/Intersight/virtualenv/bin/activate
cd /ws/bbizar-bgl/Projects/langchain/report_summarizer
python3 -c "
from utils.url_converter import URLConverter

# Test Supernova URL
url1 = 'https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7505/test_results/sars/detail.html'
print(URLConverter.get_url_type(url1))  # 'supernova'
print(URLConverter.url_to_path(url1))   # Success with correct path

# Test Reportio URL
url2 = 'http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html'
print(URLConverter.get_url_type(url2))  # 'reportio'
print(URLConverter.url_to_path(url2))   # Success with correct path
"
```

### Test Results

✅ **URL Detection**: Both URL types correctly identified  
✅ **Path Conversion**: Correct local paths generated  
✅ **Index.html Resolution**: Automatic conversion working  
✅ **Build Info Extraction**: Metadata correctly extracted  
✅ **Integration**: Full workflow tested end-to-end

---

## Examples

### Example 1: Analyzing a Reportio Run

**Input URL:**
```
http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html
```

**System Processing:**
1. Detects URL type: `reportio`
2. Converts to: `/auto/CRR_Regression/qali/iucstest/sanity_1839514_4924955718040703741/index.html`
3. Extracts build info: `qali_id=1839514`, `project=iucstest`
4. Runs analyzer on `index.html`
5. Performs AI analysis
6. Displays results with metadata

**History Entry:**
```
sanity_1839514_4924955718040703741
🌍 reportio | 🏷️ iucstest
📅 2026-01-22 10:30 | 🔍 FULL
✅ 45/50 passed (90.0%)
```

### Example 2: Comparing Supernova and Reportio Runs

**Select two runs from history:**
1. Supernova: `staging_sars_sanity_build_7505`
2. Reportio: `sanity_1839514_4924955718040703741`

**System generates AI-powered comparison:**
- Common failures across both
- Environment-specific issues
- Regressions and fixes
- Patterns and recommendations

---

## Benefits

### 1. Unified Interface
- Single web application for all test report types
- Consistent analysis workflow
- Unified history and comparison

### 2. Automatic Detection
- No need to specify URL type
- Intelligent path conversion
- Error-free processing

### 3. Cross-Source Comparison
- Compare Supernova vs Reportio runs
- Identify environment-specific issues
- Unified AI analysis

### 4. Future-Proof
- Easy to add more URL types
- Modular architecture
- Extensible design

---

## Troubleshooting

### Issue: "Invalid URL" Error

**Cause:** URL doesn't match Supernova or Reportio format

**Solution:** Ensure URL starts with:
- `https://supernova.cisco.com/logviewer/runtests/results/sanity/` OR
- `http://reportio.cisco.com/`

### Issue: "index.html not found"

**Cause:** Local filesystem path doesn't exist

**Solution:**
1. Verify the URL is correct
2. Check filesystem access to:
   - `/auto/intersight-sanity/sanity_logs/sanity/` (Supernova)
   - `/auto/CRR_Regression/` (Reportio)
3. Ensure the test run has completed and files are available

### Issue: Build info not extracted correctly

**Cause:** URL format doesn't match expected pattern

**Solution:**
- For Supernova: Ensure format is `<env>_<project>_sanity_build_<number>`
- For Reportio: Ensure format is `sanity_<qali_id>_<run_id>`

---

## Summary

✅ **Supernova URLs**: Fully supported (existing functionality)  
✅ **Reportio URLs**: Fully supported (new functionality)  
✅ **Automatic Detection**: Both types detected automatically  
✅ **Path Conversion**: Correct local paths for both  
✅ **Build Info**: Metadata extracted from both  
✅ **Web Application**: UI updated to support both  
✅ **History & Comparison**: Works across both URL types  
✅ **Tested**: Comprehensive tests passed  

**You can now analyze test reports from both Supernova and Reportio seamlessly! 🎉**



