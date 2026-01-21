#!/bin/bash
#
# Quick start script for Test Report Analyzer Web Application
#

echo "=========================================="
echo "Test Report Analyzer Web Application"
echo "=========================================="
echo ""

# Activate virtual environment
VENV_PATH="/ws/bbizar-bgl/Intersight/virtualenv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo "📦 Activating virtual environment..."
    source "$VENV_PATH"
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found at: $VENV_PATH"
    echo "Continuing without virtual environment..."
fi

echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed."
    echo ""
    echo "Would you like to install requirements now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Installing requirements..."
        pip install -r requirements_web.txt
        echo "✅ Installation complete!"
    else
        echo "Please install requirements manually:"
        echo "  source /ws/bbizar-bgl/Intersight/virtualenv/bin/activate"
        echo "  pip install -r requirements_web.txt"
        exit 1
    fi
fi

echo ""
echo "Starting Test Report Analyzer..."
echo ""
echo "📝 The application will open in your default browser"
echo "🌐 Default URL: http://localhost:8501"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""
echo "=========================================="
echo ""

# Start streamlit app
streamlit run report_analyzer_web.py
