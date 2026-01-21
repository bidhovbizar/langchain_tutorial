# Setup Notes

## Virtual Environment

All Python packages are installed in a virtual environment located at:
```
/ws/bbizar-bgl/Intersight/virtualenv/
```

## Quick Start

### Method 1: Using the start script (Recommended)
The start script automatically activates the virtual environment:
```bash
cd /ws/bbizar-bgl/Projects/langchain/report_summarizer
./start_web_app.sh
```

### Method 2: Manual activation
If you prefer to run manually:
```bash
# Activate virtual environment
source /ws/bbizar-bgl/Intersight/virtualenv/bin/activate

# Navigate to project directory
cd /ws/bbizar-bgl/Projects/langchain/report_summarizer

# Run the application
streamlit run report_analyzer_web.py
```

## Testing the Setup

To test if everything is configured correctly:
```bash
# Activate virtual environment
source /ws/bbizar-bgl/Intersight/virtualenv/bin/activate

# Run installation test
python test_installation.py
```

## Installing Additional Packages

If you need to install additional packages in the virtual environment:
```bash
# Activate virtual environment
source /ws/bbizar-bgl/Intersight/virtualenv/bin/activate

# Install packages
pip install <package-name>

# Or install from requirements
pip install -r requirements_web.txt
```

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Make sure you've activated the virtual environment:
```bash
source /ws/bbizar-bgl/Intersight/virtualenv/bin/activate
```

### Issue: Virtual environment not found
**Solution**: Verify the path exists:
```bash
ls -la /ws/bbizar-bgl/Intersight/virtualenv/bin/activate
```

If it doesn't exist, you may need to create it or use a different path.

## Environment Variables

The application uses these environment variables (optional):
- `LANGCHAIN_TRACING_V2=true` - Enable LangChain tracing
- `LANGSMITH_PROJECT=Tutorial3` - LangSmith project name

These are already configured in the code, so no additional setup is needed.

