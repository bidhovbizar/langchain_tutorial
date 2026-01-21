# Test Report Analyzer Web Application

A comprehensive web-based tool for analyzing test reports from Supernova URLs with AI-powered insights.

## 🌟 Features

- **URL Conversion**: Automatically converts Supernova URLs to local filesystem paths
- **Error Extraction**: Extracts detailed error information from test results
- **Dual Analysis Modes**:
  - **Quick Mode**: AI-powered concise summary of all errors
  - **Full Mode**: Detailed AI-powered analysis with root cause investigation
- **History Tracking**: Keeps last 8 analysis runs
- **AI-Powered Comparison**: Intelligent comparison of test runs with:
  - Common failure detection
  - Regression identification (new failures)
  - Fix detection (resolved failures)
  - Flaky test identification
  - Root cause insights and recommendations
- **Download Reports**: Export error reports and analysis as text files
- **Multi-User Support**: Session-isolated for concurrent users
- **Smart Token Management**: Automatic OAuth token refresh (no manual intervention)

## 📋 Prerequisites

### Required Python Packages
```bash
pip install streamlit requests beautifulsoup4 langchain-openai python-dotenv
```

### Required Configuration
- Access to `/auto/intersight-sanity/sanity_logs/` directory
- Cisco Azure OpenAI credentials (for Full Analysis mode)
- Client ID and Secret (optional, can use hardcoded token)

## 🚀 Getting Started

### 1. Start the Web Application

```bash
cd /ws/bbizar-bgl/Projects/langchain/report_summarizer
streamlit run report_analyzer_web.py
```

The app will open in your default browser at `http://localhost:8501`

### 2. Enter a Supernova URL

Example URLs:
```
https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7449/test_results/sars/detail.html
https://supernova.cisco.com/logviewer/runtests/results/sanity/qatest_sars_sanity_build_7447/test_results/sars/detail.html
https://supernova.cisco.com/logviewer/runtests/results/sanity/production_sars_sanity_build_7448/test_results/sars/detail.html
```

### 3. Select Analysis Mode

- **Quick**: Fast text-based summary (no AI, instant results)
- **Full**: Comprehensive AI analysis (requires 30-60 seconds)

### 4. Click "Analyze"

The application will:
1. Validate and convert the URL
2. Extract errors from test results
3. Generate analysis based on selected mode
4. Save results to history

## 📖 Usage Guide

### Main Interface

The main page consists of:
- **URL Input**: Paste your Supernova URL here
- **Analysis Mode Selector**: Choose Quick or Full
- **Analyze Button**: Start the analysis
- **Clear All Button**: Reset the interface

### History Panel (Sidebar)

- View past 8 analysis runs
- Select multiple runs for comparison
- Click "View" to revisit any previous analysis
- Clear history when needed

### AI-Powered Comparison View

1. Select 2 or more runs from history (use checkboxes)
2. Click "Compare Selected"
3. View quick statistics comparison
4. Click "Run AI Comparison Analysis" for deep insights
5. AI analyzes both complete reports to provide:
   - **Overview**: Pass rates, test counts, quality trends
   - **Common Failures**: Issues present in both builds (persistent bugs)
   - **Regressions**: New failures in later build
   - **Fixes**: Resolved failures in later build
   - **Flaky Tests**: Tests with inconsistent results
   - **Patterns & Insights**: Root causes and recommendations
6. Download the comprehensive comparison report

**Note**: AI comparison takes 30-60 seconds but provides deep insights that save hours of manual analysis.

### Downloading Reports

After analysis completes, use the download buttons to:
- Download raw error report (`.txt`)
- Download AI analysis (`.txt`)

## 🏗️ Architecture

### File Structure

```
report_summarizer/
├── report_analyzer_web.py          # Main Streamlit application
├── utils/
│   ├── __init__.py                 # Package initialization
│   ├── url_converter.py            # URL to path conversion
│   ├── analyzer_wrapper.py         # Wraps test_results_analyzer
│   ├── summarizer_wrapper.py       # Wraps circuit_langchain_summarizer
│   └── session_manager.py          # History and comparison logic
├── test_results_analyzer_full_error.py  # Error extraction engine
├── circuit_langchain_summarizer.py      # AI analysis engine
└── client.py                            # Legacy simple client
```

### Data Flow

```
Supernova URL
    ↓
URLConverter (validate & convert)
    ↓
Local Path (/auto/intersight-sanity/...)
    ↓
AnalyzerWrapper (extract errors)
    ↓
Error Report (/tmp/test_report_*.txt)
    ↓
SummarizerWrapper (AI analysis)
    ↓
Analysis Results
    ↓
SessionManager (history & comparison)
    ↓
Display & Download
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:
```bash
LANGCHAIN_TRACING_V2=true
LANGSMITH_PROJECT=Tutorial3
```

### Credentials

Edit `circuit_langchain_summarizer.py`:
```python
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
CISCO_OPENAI_APP_KEY = 'your-app-key'
CISCO_BRAIN_USER_ID = 'your-user-id'
```

## 🎯 Use Cases

### 1. Quick Triage
Use **Quick Mode** to rapidly assess test failures across multiple builds.

### 2. Deep Dive Investigation
Use **Full Mode** to get AI-powered root cause analysis with recommendations.

### 3. Regression Tracking
Compare multiple builds to identify new, fixed, or persistent failures.

### 4. Team Collaboration
Share download links to reports and analyses with team members.

## ⚠️ Troubleshooting

### Issue: "detail.html not found"
- **Cause**: Invalid URL or file not accessible
- **Solution**: Verify the URL and check filesystem permissions

### Issue: "AI analysis failed"
- **Cause**: OAuth token expired or network issues
- **Solution**: Update ACCESS_TOKEN or check CLIENT_ID/CLIENT_SECRET

### Issue: "Module not found"
- **Cause**: Missing dependencies
- **Solution**: Run `pip install -r requirements.txt`

### Issue: Multiple users conflict
- **Cause**: Session state issues
- **Solution**: Each user session is isolated; restart browser if issues persist

## 📊 Analysis Modes Comparison

| Feature | Quick Mode | Full Mode | AI Comparison |
|---------|-----------|-----------|---------------|
| Speed | 20-40 seconds | 30-60 seconds | 30-60 seconds |
| AI Analysis | Yes (GPT-4) | Yes (GPT-4) | Yes (GPT-4) |
| Scope | Single build summary | Single build deep dive | Multi-build analysis |
| Root Cause | Brief | Detailed | Pattern-based |
| Recommendations | No | Yes | Yes |
| Token Usage | ~2000-4000 | ~2000-5000 | ~5000-10000 |
| Best For | Quick overview | Deep investigation | Regression tracking |

### When to Use Each Mode

**Quick Mode**
- ✅ Need fast overview of failures
- ✅ Checking multiple builds rapidly
- ✅ Initial triage
- ✅ Daily sanity check

**Full Mode**
- ✅ Need detailed root cause analysis
- ✅ Investigating critical failures
- ✅ Planning fixes
- ✅ Technical deep dive

**AI Comparison**
- ✅ Comparing staging vs. production
- ✅ Tracking regressions between builds
- ✅ Finding common patterns
- ✅ Identifying flaky tests
- ✅ Quality trend analysis

## 🔐 Security Notes

- Application runs locally on your machine
- No authentication required (internal use)
- Session data stored in memory only
- Temp files stored in `/tmp/` (auto-cleaned by system)
- Multi-user sessions are isolated

## 🚦 Performance Tips

1. **Quick Mode First**: Start with Quick mode for initial assessment
2. **Selective Full Analysis**: Use Full mode only for critical failures
3. **Clear History**: Periodically clear history to free memory
4. **Comparison Limit**: Compare 2-4 builds max for best performance

## 📝 Limitations

- Maximum 8 entries in history
- Token limit for Full mode (~4000 tokens per request)
- Requires access to `/auto/intersight-sanity/` filesystem
- AI analysis requires valid Cisco Azure OpenAI credentials

## 🔄 Future Enhancements

Possible additions:
- [ ] Trend analysis across 3+ builds
- [ ] Email notifications for analysis completion
- [ ] Export to PDF/Excel formats
- [ ] Custom filtering and search
- [ ] Scheduled automated analysis
- [ ] Integration with JIRA for ticket creation
- [ ] Visual diff highlighting in comparisons
- [ ] Persistent comparison history across sessions

## 📞 Support

For issues or questions:
1. Check this README for troubleshooting
2. Verify all dependencies are installed
3. Ensure filesystem paths are accessible
4. Confirm OAuth credentials are valid

## 📄 License

Internal Cisco tool - For authorized use only

