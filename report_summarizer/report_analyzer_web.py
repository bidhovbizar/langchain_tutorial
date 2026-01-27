"""
Test Report Analyzer Web Application

A Streamlit web interface for analyzing test reports from Supernova URLs.

Features:
- Convert Supernova URLs to local paths
- Extract errors from test results
- Quick and Full AI analysis modes
- History tracking (last 8 runs)
- Side-by-side comparison
- Download reports

Usage:
    streamlit run report_analyzer_web.py
"""

import streamlit as st
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import URLConverter, AnalyzerWrapper, SummarizerWrapper, SessionManager


# Page configuration
st.set_page_config(
    page_title="Test Report Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Apple-inspired white theme
st.markdown("""
<style>
    /* Import Inter font (Apple-style) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ============================================ */
    /* FORCE LIGHT MODE / WHITE THEME */
    /* ============================================ */
    
    /* Override color scheme to light */
    :root {
        color-scheme: light !important;
        --background-color: #ffffff !important;
        --text-color: #1d1d1f !important;
    }
    
    html, body {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
    }
    
    /* Force Streamlit theme to light */
    [data-theme="dark"] {
        color-scheme: light !important;
    }
    
    /* Force all major containers to white */
    section[tabindex="0"],
    .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    [data-testid="block-container"] {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
    }
    
    /* ============================================ */
    /* GLOBAL THEME - Apple-inspired Clean White */
    /* ============================================ */
    
    /* Main app background - subtle gradient */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%) !important;
        color: #1d1d1f !important;
    }
    
    /* Override Streamlit dark theme */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%) !important;
        color: #1d1d1f !important;
    }
    
    /* Force text elements to be dark (but not buttons) */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] div:not(.stButton):not(.stDownloadButton),
    [data-testid="stAppViewContainer"] label {
        color: #1d1d1f !important;
    }
    
    /* Main content area - COMPACT spacing */
    .main .block-container {
        background-color: #ffffff;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1400px;
        border-radius: 16px;
        box-shadow: 0 0 40px rgba(0,0,0,0.03);
    }
    
    /* Typography - Apple-style */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    /* FORCE ALL TEXT TO BE DARK/BLACK */
    body, p, span, div, label, li, a {
        color: #1d1d1f !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #1d1d1f !important;
    }
    
    .stText {
        color: #1d1d1f !important;
    }
    
    /* Force main container text to be dark */
    .main {
        color: #1d1d1f !important;
    }
    
    /* Force Streamlit-specific text elements to be dark */
    [data-testid="stText"],
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaption"],
    .stCaption {
        color: #1d1d1f !important;
    }
    
    /* Labels and help text */
    label {
        color: #1d1d1f !important;
    }
    
    /* Captions */
    .caption, small {
        color: #86868b !important;
    }
    
    /* ============================================ */
    /* HEADER STYLING - Minimal & Clean & COMPACT */
    /* ============================================ */
    
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1d1d1f !important;
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    h1, h2, h3, h4 {
        color: #1d1d1f !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px;
    }
    
    h1 {
        font-size: 1.8rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #1d1d1f !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        color: #1d1d1f !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.4rem !important;
        color: #1d1d1f !important;
    }
    
    h4 {
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
        color: #1d1d1f !important;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stTitle {
        color: #1d1d1f !important;
    }
    
    /* ============================================ */
    /* BUTTONS - Smaller, Prettier, Gradient Purple/Pink */
    /* ============================================ */
    
    /* Force ALL buttons to have base styling (catch-all) */
    button[data-testid="baseButton-primary"],
    button[kind="primary"],
    .stButton > button[data-testid*="primary"],
    button:has-text("Analyze"),
    button:has-text("Compare"),
    button:has-text("View") {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        height: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }
    
    /* Primary action buttons (Analyze, Compare, View) - Gradient */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        height: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Secondary buttons (Clear, Download, Back, etc.) - Sky Blue to Ocean Blue */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(47, 128, 237, 0.3) !important;
        height: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(47, 128, 237, 0.4) !important;
    }
    
    /* Download buttons - Sky Blue to Ocean Blue */
    .stDownloadButton > button,
    button[data-testid*="download"],
    button[data-testid="stDownloadButton"] {
        background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(47, 128, 237, 0.3) !important;
        height: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }
    
    .stDownloadButton > button:hover,
    button[data-testid*="download"]:hover,
    button[data-testid="stDownloadButton"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(47, 128, 237, 0.4) !important;
    }
    
    /* Fallback: Any remaining plain buttons get secondary gradient style */
    .stButton > button:not([kind]),
    button:not([kind]):not([data-testid*="download"]) {
        background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(47, 128, 237, 0.3) !important;
        height: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }
    
    /* ABSOLUTE CATCH-ALL: Force ALL button elements to have styling */
    /* EXCEPT Streamlit's header buttons (hamburger menu, etc.) */
    button:not([data-testid="stMainMenuButton"]):not([data-testid="stHeader"] button) {
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        height: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }
    
    /* If a button is still plain/default, force sky blue gradient */
    /* EXCEPT Streamlit's header buttons */
    button:not([style*="background"]):not(.stButton [kind="primary"]):not([data-testid="stMainMenuButton"]):not([data-testid="stHeader"] button) {
        background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(47, 128, 237, 0.3) !important;
    }
    
    /* Force Streamlit header buttons to stay black/dark */
    [data-testid="stHeader"] button,
    button[data-testid="stMainMenuButton"],
    [data-testid="stToolbar"] button,
    header button {
        background: transparent !important;
        color: #1d1d1f !important;
        border: none !important;
        box-shadow: none !important;
        height: auto !important;
        padding: 0.25rem !important;
    }
    
    [data-testid="stHeader"] button:hover,
    button[data-testid="stMainMenuButton"]:hover,
    [data-testid="stToolbar"] button:hover,
    header button:hover {
        background: rgba(0, 0, 0, 0.05) !important;
        color: #1d1d1f !important;
    }
    
    /* Hover effects for fallback buttons */
    .stButton > button:not([kind]):hover,
    button:not([kind]):not([data-testid*="download"]):hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(47, 128, 237, 0.4) !important;
    }
    
    /* Ensure button text/content is perfectly vertically centered */
    button p, button span, button div,
    .stButton p, .stButton span, .stButton div,
    .stDownloadButton p, .stDownloadButton span, .stDownloadButton div {
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        vertical-align: middle !important;
    }
    
    /* Ensure button containers are vertically centered in columns */
    .stButton, .stDownloadButton {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Ensure columns with buttons are vertically aligned */
    [data-testid="column"] > div {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* ============================================ */
    /* INPUT FIELDS - Clean & Light */
    /* ============================================ */
    
    .stTextInput > div > div > input {
        background-color: #f5f5f7 !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        color: #1d1d1f !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background-color: white !important;
    }
    
    /* Select boxes - WHITE THEME */
    .stSelectbox > div > div {
        background-color: #f5f5f7 !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Dropdown menu - Force white background */
    [data-baseweb="popover"] {
        background-color: white !important;
    }
    
    [data-baseweb="menu"] {
        background-color: white !important;
    }
    
    [role="option"] {
        background-color: white !important;
        color: #1d1d1f !important;
    }
    
    [role="option"]:hover {
        background-color: #f5f3ff !important;
    }
    
    /* ============================================ */
    /* METRICS CARDS - Elegant with gradient */
    /* ============================================ */
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #1d1d1f !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #86868b !important;
        font-weight: 500 !important;
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f7 100%) !important;
        padding: 1rem !important;
        border-radius: 12px !important;
        border: 1px solid #e5e5ea !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.08) !important;
    }
    
    /* ============================================ */
    /* EXPANDERS & CONTAINERS - Sleek cards */
    /* ============================================ */
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f7 100%) !important;
        border: 1px solid #e5e5ea !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        color: #1d1d1f !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #f5f5f7 0%, #e5e5ea 100%) !important;
        border-color: #667eea !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #e5e5ea !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
        background-color: white !important;
    }
    
    /* ============================================ */
    /* CHAT INTERFACE - Clean WHITE theme */
    /* ============================================ */
    
    /* Chat container - FORCE WHITE */
    .stChatFloatingInputContainer,
    [data-testid="stChatFloatingInputContainer"],
    [data-testid="stBottomBlockContainer"] {
        background-color: white !important;
        border-top: 1px solid #e5e5ea !important;
        padding: 1rem !important;
    }
    
    /* Chat input wrapper - FORCE WHITE */
    .stChatInput,
    [data-testid="stChatInput"],
    .stChatInput > div,
    .stChatInput > div > div {
        background-color: white !important;
    }
    
    /* Chat input field - FORCE WHITE background with DARK text */
    .stChatInput input,
    .stChatInput > div > div > input,
    [data-testid="stChatInput"] input,
    input[placeholder*="Ask"],
    textarea[placeholder*="Ask"] {
        background-color: #f5f5f7 !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 20px !important;
        padding: 0.5rem 1rem !important;
        color: #1d1d1f !important;
        caret-color: #1d1d1f !important;
        -webkit-text-fill-color: #1d1d1f !important;
    }
    
    .stChatInput input:focus,
    .stChatInput > div > div > input:focus,
    textarea[placeholder*="Ask"]:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background-color: white !important;
        color: #1d1d1f !important;
    }
    
    /* Placeholder text */
    .stChatInput input::placeholder,
    textarea[placeholder*="Ask"]::placeholder {
        color: #86868b !important;
        opacity: 1 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: transparent !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Force ALL chat message text to be DARK/BLACK */
    .stChatMessage,
    .stChatMessage *,
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] *,
    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessageContent"] *,
    .stMarkdown p,
    .stChatMessage p,
    .stChatMessage span,
    .stChatMessage div {
        color: #1d1d1f !important;
    }
    
    /* User messages - light gray background with dark text */
    [data-testid="stChatMessageContent"] {
        background-color: #f5f5f7 !important;
        color: #1d1d1f !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
    }
    
    /* Ensure all nested elements in chat have dark text */
    .stChatMessage * {
        color: #1d1d1f !important;
    }
    
    /* Chat message paragraphs specifically */
    .stChatMessage p,
    [data-testid="stChatMessage"] p {
        color: #1d1d1f !important;
    }
    
    /* ============================================ */
    /* TABLES - Sharp, clean design */
    /* ============================================ */
    
    .dataframe {
        border: 1px solid #e5e5ea !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    .dataframe thead tr {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .dataframe thead th {
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
        border: none !important;
    }
    
    .dataframe tbody tr {
        border-bottom: 1px solid #f5f5f7 !important;
        transition: background-color 0.2s ease !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f5f3ff !important;
    }
    
    .dataframe tbody td {
        padding: 0.75rem !important;
        color: #1d1d1f !important;
    }
    
    /* ============================================ */
    /* DIVIDERS - Elegant gradient lines */
    /* ============================================ */
    
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(to right, transparent, #d2d2d7, transparent) !important;
        margin: 1rem 0 !important;
    }
    
    /* ============================================ */
    /* SIDEBAR - Premium design */
    /* ============================================ */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%) !important;
        border-right: 1px solid #e5e5ea !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1d1d1f !important;
    }
    
    /* Sidebar buttons - compact */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 0.8rem !important;
        height: 36px !important;
    }
    
    /* ============================================ */
    /* CODE BLOCKS - Clean WHITE design */
    /* ============================================ */
    
    /* Force ALL code blocks to be light/white */
    .stCodeBlock,
    [data-testid="stCodeBlock"],
    pre,
    pre code,
    code {
        background-color: #f5f5f7 !important;
        color: #1d1d1f !important;
        border: 1px solid #e5e5ea !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    
    /* Inline code */
    code {
        background-color: #f5f5f7 !important;
        color: #667eea !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-size: 0.9rem !important;
        border: none !important;
    }
    
    /* Code block container */
    .stCodeBlock > div {
        background-color: #f5f5f7 !important;
    }
    
    /* Pre element (for st.code) */
    pre {
        background-color: #f5f5f7 !important;
        color: #1d1d1f !important;
        border: 1px solid #e5e5ea !important;
    }
    
    /* ============================================ */
    /* ALERTS - Refined styling */
    /* ============================================ */
    
    .stAlert {
        border-radius: 10px !important;
        border-left-width: 4px !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Success alerts */
    [data-baseweb="notification"][kind="success"] {
        background-color: #d4fc79 !important;
        border-left-color: #10b981 !important;
    }
    
    /* Error alerts */
    [data-baseweb="notification"][kind="error"] {
        background-color: #fee2e2 !important;
        border-left-color: #ef4444 !important;
    }
    
    /* Info alerts */
    [data-baseweb="notification"][kind="info"] {
        background-color: #dbeafe !important;
        border-left-color: #3b82f6 !important;
    }
    
    /* ============================================ */
    /* SCROLLBAR - Minimal design */
    /* ============================================ */
    
    ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: #f5f5f7 !important;
        border-radius: 10px !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d2d2d7 !important;
        border-radius: 10px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #86868b !important;
    }
    
    /* ============================================ */
    /* SPACING ADJUSTMENTS - COMPACT */
    /* ============================================ */
    
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact stMarkdown spacing */
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact expander spacing */
    details {
        margin-bottom: 0.75rem !important;
    }
    
    /* Tighter line height for paragraphs */
    p {
        line-height: 1.5 !important;
        margin-bottom: 0.5rem !important;
        color: #1d1d1f !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
    
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""
    
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False
    
    # Chat-related session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'chat_key_counter' not in st.session_state:
        st.session_state.chat_key_counter = 0


def display_header():
    """Display application header - Compact and professional"""
    st.markdown("""
    <div style="text-align: center; margin: 0.5rem 0 0.75rem 0;">
        <hr style="border: none; height: 2px; background: linear-gradient(to right, transparent, #d2d2d7, transparent); margin-bottom: 0.5rem;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #1d1d1f; margin: 0.5rem 0 0.3rem 0; letter-spacing: -1px;">
            🔍 Test Report Analyzer & Summarizer
        </h1>
        <p style="color: #86868b; font-size: 0.9rem; margin: 0.3rem 0 0.5rem 0; font-weight: 400;">
            AI-Powered Test Analysis with Cisco Azure OpenAI
        </p>
        <hr style="border: none; height: 2px; background: linear-gradient(to right, transparent, #d2d2d7, transparent); margin-top: 0.5rem;">
    </div>
    """, unsafe_allow_html=True)


def display_url_input():
    """Display URL input section"""
    st.markdown("#### 📝 Test Results URL")
    
    # Show examples
    with st.expander("📋 Click to see example URLs (Supernova & Reportio)"):
        examples = URLConverter.get_example_urls()
        st.markdown("**Supernova URLs:**")
        for url in examples[:3]:  # First 3 are Supernova
            st.code(url, language="text")
        st.markdown("**Reportio URLs:**")
        for url in examples[3:]:  # Remaining are Reportio
            st.code(url, language="text")
    
    # URL input
    url = st.text_input(
        "Test Results URL (Supernova or Reportio):",
        value=st.session_state.current_url,
        placeholder="https://supernova.cisco.com/... or http://reportio.cisco.com/...",
        help="Enter the URL to your test results (supports both Supernova and Reportio URLs)"
    )
    
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        analysis_mode = st.selectbox(
            "Analysis Mode:",
            ["Quick", "Full"],
            help="Quick: Fast text-based summary\nFull: Detailed AI analysis"
        )
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    with col3:
        clear_button = st.button("🗑️ Clear All", type="secondary", use_container_width=True)
    
    return url, analysis_mode, analyze_button, clear_button


def validate_and_convert_url(url: str):
    """Validate URL and convert to local path"""
    progress_container = st.empty()
    
    with progress_container.container():
        with st.expander("✅ URL Validation", expanded=True):
            # Step 1: Validate URL
            st.write("✓ Validating URL format...")
            url_type = URLConverter.get_url_type(url)
            if url_type == 'unknown':
                st.error("Invalid URL. Must be a Supernova or Reportio URL.")
                return None, None
            
            st.write(f"✓ Detected URL type: {url_type.upper()}")
            
            # Step 2: Extract build info
            st.write("✓ Extracting build information...")
            build_info = URLConverter.extract_build_info(url)
            
            # Step 3: Convert to path (get index.html for analyzer)
            st.write("✓ Converting URL to local path...")
            success, index_path, error = URLConverter.get_index_html_path(url)
            
            if not success:
                st.error(f"Error: {error}")
                return None, None
            
            st.write(f"✓ Located: `{index_path}`")
            st.success("✅ URL validated successfully!")
            
            return index_path, build_info


def run_analysis(index_path: Path, analysis_mode: str, build_info: dict, url: str):
    """Run the complete analysis pipeline"""
    results = {}
    
    with st.expander("📊 Running Analysis", expanded=True):
        # Step 1: Extract errors
        st.write("📊 Step 1/3: Extracting errors from test results...")
        
        analyzer = AnalyzerWrapper()
        # Always fetch logs for both Quick and Full modes
        # Only the AI prompt differs between modes, not the error report
        fetch_logs = True
        
        success, report_path, analyzer_results = analyzer.analyze(
            index_path,
            fetch_logs=fetch_logs,
            verbose=True  # Enable verbose to see what's happening
        )
        
        if not success:
            st.error(f"Error during analysis: {analyzer_results.get('error', 'Unknown error')}")
            return None
        
        st.write(f"✓ Errors extracted to: `{report_path}`")
        results['analyzer'] = analyzer_results
        results['report_path'] = report_path
        
        # Step 2: Generate summary (both modes now use AI)
        st.write("🤖 Step 2/3: Running AI analysis...")
        
        def progress_callback(message):
            st.write(f"   {message}")
        
        summarizer = SummarizerWrapper()
        
        if analysis_mode.lower() == "quick":
            st.write("⚡ Quick mode: Concise AI summary (10-20 seconds)...")
            success, summary_result, error = summarizer.analyze_quick(
                report_path,
                callback=progress_callback
            )
        else:  # Full analysis
            st.write("🔍 Full mode: Detailed AI analysis (30-60 seconds)...")
            success, summary_result, error = summarizer.analyze_full(
                report_path,
                callback=progress_callback
            )
        
        if not success:
            st.error(f"Error during AI analysis: {error}")
            return None
        
        results['summary'] = summary_result
        results['mode'] = analysis_mode.lower()
        
        # Step 3: Save to history
        st.write("💾 Step 3/3: Saving to history...")
        
        entry_id = st.session_state.session_manager.add_to_history(
            url=url,
            build_info=build_info,
            analyzer_results=analyzer_results,
            summary_results=results.get('summary') if analysis_mode.lower() == 'full' else None,
            analysis_mode=analysis_mode.lower()
        )
        
        results['entry_id'] = entry_id
        
        st.success("✅ Analysis complete!")
    
    return results


def display_results(results: dict):
    """Display analysis results"""
    st.markdown("---")
    st.markdown("### 📊 Analysis Results")
    
    # Summary statistics - showing FAILED and SKIPPED separately
    analyzer_results = results['analyzer']
    
    # Create 5 columns for Total, Passed, Failed, Skipped, Mode
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_tests = analyzer_results.get('total_tests', 0)
    
    # Parse failures array to separate FAILED from SKIPPED
    failures = analyzer_results.get('failures', [])
    actual_failed = 0
    actual_skipped = 0
    
    for failure in failures:
        status = failure.get('status', '').upper()
        if 'SKIP' in status:
            actual_skipped += 1
        else:
            actual_failed += 1
    
    # If failures array is empty or analyzer returns separate counts, use those
    if not failures:
        # Fallback to analyzer-provided counts (if available)
        actual_failed = analyzer_results.get('failed_tests', 0)
        actual_skipped = analyzer_results.get('skipped_tests', 0)
        # If skipped_tests is not provided, assume failed_tests might include both
        if actual_skipped == 0 and 'skipped_tests' not in analyzer_results:
            # Can't separate, show warning
            actual_failed = analyzer_results.get('failed_tests', 0)
    
    passed_tests = total_tests - actual_failed - actual_skipped
    
    # Calculate rates (excluding skipped from denominator)
    testable_count = total_tests - actual_skipped
    pass_rate = (passed_tests / testable_count * 100) if testable_count > 0 else 0
    fail_rate = (actual_failed / testable_count * 100) if testable_count > 0 else 0
    skip_rate = (actual_skipped / total_tests * 100) if total_tests > 0 else 0
    
    with col1:
        st.metric("Total", total_tests)
    
    with col2:
        st.metric("✅ Passed", passed_tests, delta=f"{pass_rate:.1f}%")
    
    with col3:
        st.metric("❌ Failed", actual_failed, delta=f"{fail_rate:.1f}%", delta_color="inverse")
    
    with col4:
        st.metric("⏭️ Skipped", actual_skipped, delta=f"{skip_rate:.1f}%", delta_color="off")
    
    with col5:
        mode_emoji = "⚡" if results['mode'] == 'quick' else "🤖"
        st.metric("Mode", f"{mode_emoji} {results['mode'].upper()}")
    
    # Display test configuration metadata
    summary = analyzer_results.get('summary', {})
    if summary:
        # Display metadata in a compact expander
        with st.expander("📋 Test Configuration Details", expanded=False):
            # Create columns for metadata
            meta_col1, meta_col2 = st.columns(2)
            
            with meta_col1:
                # Left column
                if 'Test_bed' in summary:
                    st.markdown(f"**🖥️ Test Bed:** `{summary['Test_bed']}`")
                if 'Start_time' in summary:
                    st.markdown(f"**⏰ Start Time:** `{summary['Start_time']}`")
                if 'Test_duration' in summary:
                    st.markdown(f"**⏱️ Duration:** `{summary['Test_duration']}`")
            
            with meta_col2:
                # Right column
                if 'Script_execution_server' in summary:
                    st.markdown(f"**🖧 Execution Server:** `{summary['Script_execution_server']}`")
                if 'Stop_time' in summary:
                    st.markdown(f"**🏁 Stop Time:** `{summary['Stop_time']}`")
                if 'Qali_id' in summary:
                    st.markdown(f"**🔖 Qali ID:** `{summary['Qali_id']}`")
                if 'Comment' in summary:
                    st.markdown(f"**💬 Comment:** `{summary['Comment']}`")
    
    # Display summary/analysis
    st.markdown("---")
    
    summary_result = results.get('summary')
    
    if results['mode'] == 'quick':
        st.markdown("#### ⚡ Quick AI Summary")
    else:
        st.markdown("#### 🔍 Detailed AI Analysis")
    
    # Display the AI-generated content
    if summary_result and isinstance(summary_result, dict) and 'content' in summary_result:
        st.markdown(summary_result['content'])
    elif summary_result and isinstance(summary_result, str):
        # Handle case where summary is stored as a string
        st.markdown(summary_result)
    else:
        st.warning("⚠️ AI analysis not available for this entry. This may be an older analysis from history.")
        st.info("💡 Tip: Re-run the analysis to generate a new AI summary with chat support.")
    
    # Show token usage in expander (for both modes)
    if summary_result and isinstance(summary_result, dict) and 'usage' in summary_result and summary_result['usage']:
        with st.expander("📈 Token Usage Statistics"):
            usage = summary_result['usage']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Input Tokens", usage.get('prompt_tokens', 'N/A'))
            with col2:
                st.metric("Output Tokens", usage.get('completion_tokens', 'N/A'))
            with col3:
                st.metric("Total Tokens", usage.get('total_tokens', 'N/A'))
    
    # Download buttons (compact)
    col1, col2 = st.columns(2)
    
    with col1:
        # Download error report
        try:
            with open(results['report_path'], 'r') as f:
                report_content = f.read()
            
            st.download_button(
                label="📥 Error Report",
                data=report_content,
                file_name=Path(results['report_path']).name,
                mime="text/plain",
                use_container_width=True,
                type="secondary"
            )
        except:
            st.error("Error reading report file")
    
    with col2:
        # Download analysis (both modes use same structure now)
        if summary_result and isinstance(summary_result, dict) and 'content' in summary_result:
            analysis_content = summary_result['content']
        elif summary_result and isinstance(summary_result, str):
            analysis_content = summary_result
        else:
            analysis_content = "AI analysis not available for this entry."
        
        mode_label = "quick_summary" if results['mode'] == 'quick' else "full_analysis"
        
        st.download_button(
            label="📥 Analysis",
            data=analysis_content,
            file_name=f"{mode_label}_{results['entry_id']}.txt",
            mime="text/plain",
            use_container_width=True,
            type="secondary"
        )
    
    # Interactive Chat Interface
    display_chat_interface(results, is_comparison=False)
    
    # Add "Back to Main Input" button
    st.markdown("---")
    if st.button("🏠 Back to Main Input", type="secondary", use_container_width=True):
        # Clear all state to return to input screen
        st.session_state.analysis_complete = False
        st.session_state.current_results = None
        st.session_state.current_url = ""
        st.rerun()


def display_history():
    """Display analysis history in sidebar"""
    history = st.session_state.session_manager.get_history()
    
    if not history:
        st.info("No analysis history yet. Run your first analysis to see it here!")
        return
    
    st.subheader(f"📚 History ({len(history)}/{SessionManager.MAX_HISTORY})")
    
    # Comparison controls
    selected_entries = st.session_state.session_manager.get_selected_entries()
    
    if len(selected_entries) >= 2:
        if st.button("🔄 Compare Selected", use_container_width=True, type="primary"):
            st.session_state.show_comparison = True
            st.rerun()
    
    if len(selected_entries) > 0:
        if st.button("❌ Clear Selection", type="secondary", use_container_width=True):
            st.session_state.session_manager.clear_comparison()
            st.rerun()
    
    st.markdown("---")
    
    # Display history entries
    for entry in history:
        with st.container():
            # Checkbox for comparison
            is_selected = entry.get('selected', False)
            
            col1, col2 = st.columns([1, 5])
            
            with col1:
                if st.checkbox("Select for comparison", value=is_selected, key=f"select_{entry['id']}", label_visibility="collapsed"):
                    if not is_selected:
                        st.session_state.session_manager.toggle_comparison(entry['id'])
                        st.rerun()
                else:
                    if is_selected:
                        st.session_state.session_manager.toggle_comparison(entry['id'])
                        st.rerun()
            
            with col2:
                summary = st.session_state.session_manager.format_history_summary(entry)
                st.markdown(summary)
                
                if st.button("👁️ View", key=f"view_{entry['id']}", type="primary", use_container_width=True):
                    st.session_state.current_results = {
                        'analyzer': entry['analyzer_results'],
                        'summary': entry.get('summary_results'),
                        'mode': entry['analysis_mode'],
                        'report_path': entry['analyzer_results'].get('report_path', ''),
                        'entry_id': entry['id']
                    }
                    st.session_state.analysis_complete = True
                    st.rerun()
            
            st.markdown("---")


def display_comparison():
    """Display AI-powered comparison view"""
    st.markdown("### 🔄 AI-Powered Build Comparison")
    
    selected = st.session_state.session_manager.get_selected_entries()
    
    if len(selected) < 2:
        st.warning("Please select at least 2 runs from history to compare")
        return
    
    # Get basic comparison data for stats
    entry_ids = [e['id'] for e in selected]
    comparison = st.session_state.session_manager.compare_entries(entry_ids)
    
    if 'error' in comparison:
        st.error(comparison['error'])
        return
    
    # Display quick stats comparison in compact table format
    st.markdown("#### 📊 Quick Statistics")
    
    # Build comparison table with FAILED and SKIPPED separate
    table_rows = []
    for entry_data in comparison['entries']:
        build_name = entry_data['build_name']
        total = entry_data['total_tests']
        failed = entry_data['failed_tests']
        skipped = entry_data.get('skipped_tests', 0)  # Get skipped count
        passed = total - failed - skipped
        
        # Calculate rates
        testable = total - skipped
        pass_rate = (passed / testable * 100) if testable > 0 else 0
        fail_rate = (failed / testable * 100) if testable > 0 else 0
        skip_rate = (skipped / total * 100) if total > 0 else 0
        
        # Add emoji indicator based on pass rate
        if pass_rate >= 95:
            status = "✅"
        elif pass_rate >= 85:
            status = "⚠️"
        else:
            status = "❌"
        
        table_rows.append(f"| {status} **{build_name}** | {total} | {passed} ({pass_rate:.1f}%) | {failed} ({fail_rate:.1f}%) | {skipped} ({skip_rate:.1f}%) |")
    
    # Display compact table with separate FAILED and SKIPPED columns
    st.markdown("| Build | Total | ✅ Passed | ❌ Failed | ⏭️ Skipped |")
    st.markdown("|-------|-------|-----------|-----------|------------|")
    for row in table_rows:
        st.markdown(row)
    
    st.markdown("---")
    
    # AI-Powered Comparison Analysis
    st.markdown("#### 🤖 AI Analysis")
    
    # Check if we already have a comparison result in session state
    comparison_key = f"comparison_{'_'.join(sorted(entry_ids))}"
    
    if comparison_key not in st.session_state:
        # Need to run AI comparison
        compare_button = st.button("🔍 Run AI Comparison Analysis", type="primary", use_container_width=True)
        
        if compare_button:
            with st.expander("🔍 Running AI Comparison", expanded=True):
                # Prepare report paths and build names
                report_paths = []
                for entry in selected[:2]:  # Compare first 2 for now
                    analyzer_results = entry.get('analyzer_results', {})
                    report_path = analyzer_results.get('report_path')
                    build_name = entry.get('build_info', {}).get('build_name', 'Unknown')
                    
                    if report_path:
                        report_paths.append((report_path, build_name))
                
                if len(report_paths) < 2:
                    st.error("Could not find report files for comparison")
                else:
                    def progress_callback(message):
                        st.write(f"   {message}")
                    
                    # Run AI comparison
                    summarizer = SummarizerWrapper()
                    success, result, error = summarizer.compare_multiple(
                        report_paths,
                        callback=progress_callback
                    )
                    
                    if success:
                        st.session_state[comparison_key] = result
                        st.success("✅ Comparison complete!")
                        st.rerun()
                    else:
                        st.error(f"Comparison failed: {error}")
    else:
        # Display cached comparison result
        result = st.session_state[comparison_key]
        
        # Display AI analysis
        st.markdown(result['content'])
        
        # Show token usage
        if 'usage' in result and result['usage']:
            with st.expander("📈 Token Usage Statistics"):
                usage = result['usage']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Input Tokens", usage.get('prompt_tokens', 'N/A'))
                with col2:
                    st.metric("Output Tokens", usage.get('completion_tokens', 'N/A'))
                with col3:
                    st.metric("Total Tokens", usage.get('total_tokens', 'N/A'))
        
        # Download and action buttons (side by side)
        builds = result.get('builds_compared', ['build1', 'build2'])
        comparison_filename = f"comparison_{builds[0]}_vs_{builds[1]}.txt"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download Comparison",
                data=result['content'],
                file_name=comparison_filename,
                mime="text/plain",
                use_container_width=True,
                type="secondary"
            )
        
        with col2:
            # Clear comparison button
            if st.button("🔄 Run New Comparison", type="secondary", use_container_width=True):
                del st.session_state[comparison_key]
                st.rerun()
        
        # Interactive Chat Interface for Comparison (only if comparison exists)
        st.markdown("---")
        comparison_results = {
            'comparison_result': result,
            'selected_entries': selected,
            'url': 'comparison'
        }
        display_chat_interface(comparison_results, is_comparison=True)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Back to Main Input", type="secondary", use_container_width=True):
            # Clear all state to return to input screen
            st.session_state.show_comparison = False
            st.session_state.analysis_complete = False
            st.session_state.current_results = None
            st.session_state.current_url = ""
            st.rerun()
    
    with col2:
        if st.button("← Back to Results", type="secondary", use_container_width=True):
            # Just go back to results view
            st.session_state.show_comparison = False
            st.rerun()


def display_chat_interface(results, is_comparison=False):
    """
    Display interactive chat interface for asking questions about the report.
    
    Args:
        results: Analysis results dictionary
        is_comparison: Whether this is a comparison view or single analysis
    """
    st.markdown("---")
    st.markdown("### 💬 Chat with AI About This Report")
    st.markdown("Ask questions to get deeper insights into the test results.")
    
    # Use entry_id to create a unique chat session per analysis
    # This ensures each analysis has its own isolated chat history
    if is_comparison:
        # For comparisons, create a unique key from both entry IDs
        selected_entries = results.get('selected_entries', [])
        if len(selected_entries) >= 2:
            id1 = selected_entries[0].get('id', 'a')
            id2 = selected_entries[1].get('id', 'b')
            chat_key = f"chat_comparison_{id1}_{id2}"
        else:
            chat_key = "chat_comparison_unknown"
    else:
        # For single analysis, use the unique entry_id
        entry_id = results.get('entry_id', results.get('url', 'unknown'))
        chat_key = f"chat_analysis_{entry_id}"
    
    # Initialize chat history for this specific analysis if not exists
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    chat_history = st.session_state[chat_key]
    
    # Show chat session info and clear button
    col1, col2 = st.columns([4, 1])
    with col1:
        if is_comparison:
            st.caption("💬 Chat session for this comparison")
        else:
            st.caption(f"💬 Chat session for this analysis (Session ID: {entry_id[:8]}...)")
    with col2:
        if st.button("🗑️ Clear Chat", key=f"clear_{chat_key}", type="secondary", use_container_width=True):
            st.session_state[chat_key] = []
            st.rerun()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        # Show welcome message if no chat history
        if len(chat_history) == 0:
            with st.chat_message("assistant"):
                st.markdown("👋 Hi! I'm here to help you understand this test report. You can ask me questions like:")
                st.markdown("- Why did test X fail?")
                st.markdown("- What should I fix first?")
                st.markdown("- Are these failures related?")
                st.markdown("- What's the root cause of these errors?")
        
        # Display chat history
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask a question about this report...")
    
    if user_input:
        # Add user message to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        # Get AI response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Initialize summarizer
                        summarizer = SummarizerWrapper()
                        
                        if is_comparison:
                            # Comparison chat
                            selected_entries = results.get('selected_entries', [])
                            comparison_result = results.get('comparison_result', {})
                            
                            if len(selected_entries) >= 2:
                                # Get report contents
                                report1_path = selected_entries[0].get('analyzer_results', {}).get('report_path')
                                report2_path = selected_entries[1].get('analyzer_results', {}).get('report_path')
                                build1_name = selected_entries[0].get('build_info', {}).get('build_name', 'Build 1')
                                build2_name = selected_entries[1].get('build_info', {}).get('build_name', 'Build 2')
                                
                                if report1_path and report2_path:
                                    # Read report files
                                    with open(report1_path, 'r') as f:
                                        report1_content = f.read()
                                    with open(report2_path, 'r') as f:
                                        report2_content = f.read()
                                    
                                    comparison_summary = comparison_result.get('content', '')
                                    
                                    success, ai_response, error = summarizer.chat_comparison(
                                        report1_content,
                                        report2_content,
                                        comparison_summary,
                                        build1_name,
                                        build2_name,
                                        chat_history[:-1],  # Exclude the just-added user message
                                        user_input
                                    )
                                else:
                                    success = False
                                    error = "Could not find report paths"
                            else:
                                success = False
                                error = "Not enough comparison data"
                        else:
                            # Single report chat
                            error_report_path = results.get('report_path')  # Fixed: was 'error_report_path', should be 'report_path'
                            ai_summary = results.get('summary', {}).get('content', '')  # Fixed: get content from summary dict
                            
                            if not error_report_path:
                                st.error("❌ Error: Report path not found. Please re-run the analysis.")
                                chat_history.append({"role": "assistant", "content": "❌ Error: Report path not found. Please re-run the analysis."})
                                st.session_state[chat_key] = chat_history
                                st.rerun()
                                return
                            
                            # Read report file
                            with open(error_report_path, 'r') as f:
                                report_content = f.read()
                            
                            success, ai_response, error = summarizer.chat(
                                report_content,
                                ai_summary,
                                chat_history[:-1],  # Exclude the just-added user message
                                user_input
                            )
                        
                        if success:
                            st.markdown(ai_response)
                            # Add AI response to chat history
                            chat_history.append({"role": "assistant", "content": ai_response})
                        else:
                            error_msg = f"❌ Error: {error}"
                            st.error(error_msg)
                            # Add error to chat history
                            chat_history.append({"role": "assistant", "content": error_msg})
                    
                    except Exception as e:
                        import traceback
                        error_msg = f"❌ Error getting AI response: {str(e)}"
                        st.error(error_msg)
                        traceback.print_exc()
                        # Add error to chat history
                        chat_history.append({"role": "assistant", "content": error_msg})
        
        # Update session state
        st.session_state[chat_key] = chat_history
        st.rerun()


def main():
    """Main application flow"""
    init_session_state()
    
    # Header
    display_header()
    
    # Sidebar for history
    with st.sidebar:
        st.title("History & Comparison")
        display_history()
        
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.session_manager.clear_history()
            st.session_state.analysis_complete = False
            st.session_state.current_results = None
            
            # Clean up all chat sessions associated with cleared history
            chat_keys_to_remove = [key for key in st.session_state.keys() if key.startswith('chat_')]
            for key in chat_keys_to_remove:
                del st.session_state[key]
            
            st.rerun()
    
    # Main content
    if st.session_state.show_comparison:
        display_comparison()
    else:
        # URL input and analysis
        url, analysis_mode, analyze_button, clear_button = display_url_input()
        
        # Clear button handler
        if clear_button:
            st.session_state.current_url = ""
            st.session_state.current_results = None
            st.session_state.analysis_complete = False
            st.rerun()
        
        # Analyze button handler
        if analyze_button and url:
            st.session_state.current_url = url
            
            # Validate and convert URL
            index_path, build_info = validate_and_convert_url(url)
            
            if index_path and build_info:
                # Run analysis
                results = run_analysis(index_path, analysis_mode, build_info, url)
                
                if results:
                    st.session_state.current_results = results
                    st.session_state.analysis_complete = True
                    st.rerun()
        
        # Display results if available
        if st.session_state.analysis_complete and st.session_state.current_results:
            display_results(st.session_state.current_results)


if __name__ == "__main__":
    main()

