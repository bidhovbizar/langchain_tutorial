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

# Custom CSS for compact, information-dense styling
st.markdown("""
<style>
    /* Reduce overall app padding but keep top padding for header visibility */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Compact headers - ensure main header is fully visible */
    .main-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 0.5rem 0;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    h1 {
        font-size: 1.6rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0.3rem !important;
    }
    
    h2 {
        font-size: 1.3rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    h3 {
        font-size: 1.1rem !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Compact metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.7rem !important;
    }
    
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.3rem !important;
    }
    
    /* Compact dividers */
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact message boxes */
    .success-box {
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: #d4edda;
        border-left: 3px solid #28a745;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    .error-box {
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: #f8d7da;
        border-left: 3px solid #dc3545;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    .info-box {
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: #d1ecf1;
        border-left: 3px solid #17a2b8;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    
    /* Compact history cards */
    .history-card {
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin: 0.3rem 0;
        font-size: 0.85rem;
    }
    
    /* Compact buttons */
    .stButton button {
        padding: 0.25rem 0.75rem !important;
        font-size: 0.9rem !important;
        height: 2rem !important;
    }
    
    /* Compact download buttons */
    .stDownloadButton button {
        padding: 0.25rem 0.75rem !important;
        font-size: 0.85rem !important;
    }
    
    /* Compact expanders */
    .streamlit-expanderHeader {
        font-size: 0.95rem !important;
        padding: 0.3rem !important;
    }
    
    /* Compact sidebar */
    section[data-testid="stSidebar"] {
        width: 280px !important;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding: 1rem 0.5rem !important;
    }
    
    /* Tighter line height for paragraphs */
    p {
        line-height: 1.4 !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Compact markdown */
    .stMarkdown {
        margin-bottom: 0.3rem !important;
    }
    
    /* Reduce spacing in columns */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    /* Compact status messages */
    .stAlert {
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    /* Compact tables */
    table {
        font-size: 0.85rem !important;
    }
    
    th {
        padding: 0.3rem 0.5rem !important;
    }
    
    td {
        padding: 0.3rem 0.5rem !important;
    }
    
    /* Reduce spacing in text areas */
    .stTextArea textarea {
        font-size: 0.85rem !important;
    }
    
    /* Compact code blocks */
    pre {
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
        font-size: 0.8rem !important;
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
    """Display application header"""
    st.markdown('<p class="main-header">🔍 Test Report Analyzer & Summarizer</p>', unsafe_allow_html=True)


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
        clear_button = st.button("🗑️ Clear All", use_container_width=True)
    
    return url, analysis_mode, analyze_button, clear_button


def validate_and_convert_url(url: str):
    """Validate URL and convert to local path"""
    progress_container = st.empty()
    
    with progress_container.container():
        with st.status("🔄 Processing URL...", expanded=True) as status:
            # Step 1: Validate URL
            st.write("✓ Validating URL format...")
            url_type = URLConverter.get_url_type(url)
            if url_type == 'unknown':
                st.error("Invalid URL. Must be a Supernova or Reportio URL.")
                status.update(label="❌ Invalid URL", state="error")
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
                status.update(label="❌ Path conversion failed", state="error")
                return None, None
            
            st.write(f"✓ Located: `{index_path}`")
            status.update(label="✅ URL validated successfully", state="complete")
            
            return index_path, build_info


def run_analysis(index_path: Path, analysis_mode: str, build_info: dict, url: str):
    """Run the complete analysis pipeline"""
    results = {}
    
    with st.status("🔄 Running Analysis...", expanded=True) as status:
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
            status.update(label="❌ Analysis failed", state="error")
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
            status.update(label="❌ AI analysis failed", state="error")
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
        
        status.update(label="✅ Analysis complete!", state="complete")
    
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
                use_container_width=True
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
            use_container_width=True
        )
    
    # Interactive Chat Interface
    display_chat_interface(results, is_comparison=False)
    
    # Add "Back to Main Input" button
    st.markdown("---")
    if st.button("🏠 Back to Main Input", use_container_width=True):
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
        if st.button("❌ Clear Selection", use_container_width=True):
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
                
                if st.button("👁️ View", key=f"view_{entry['id']}", use_container_width=True):
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
            with st.status("🔄 Running AI Comparison...", expanded=True) as status:
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
                    status.update(label="❌ Comparison failed", state="error")
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
                        status.update(label="✅ Comparison complete!", state="complete")
                        st.rerun()
                    else:
                        st.error(f"Comparison failed: {error}")
                        status.update(label="❌ Comparison failed", state="error")
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
                use_container_width=True
            )
        
        with col2:
            # Clear comparison button
            if st.button("🔄 Run New Comparison", use_container_width=True):
                del st.session_state[comparison_key]
                st.rerun()
    
    # Interactive Chat Interface for Comparison
    comparison_results = {
        'comparison_data': comparison_data,
        'ai_analysis': ai_comparison.get('content', ''),
        'url': 'comparison'
    }
    display_chat_interface(comparison_results, is_comparison=True)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Back to Main Input", use_container_width=True):
            # Clear all state to return to input screen
            st.session_state.show_comparison = False
            st.session_state.analysis_complete = False
            st.session_state.current_results = None
            st.session_state.current_url = ""
            st.rerun()
    
    with col2:
        if st.button("← Back to Results", use_container_width=True):
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
        comparison_data = results.get('comparison_data', {})
        entries = comparison_data.get('entries', [])
        if len(entries) >= 2:
            chat_key = f"chat_comparison_{entries[0].get('id', 'a')}_{entries[1].get('id', 'b')}"
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
        if st.button("🗑️ Clear Chat", key=f"clear_{chat_key}", use_container_width=True):
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
                            comparison_data = results.get('comparison_data', {})
                            entries = comparison_data.get('entries', [])
                            
                            if len(entries) >= 2:
                                # Get report contents
                                report1_path = entries[0].get('error_report_path')
                                report2_path = entries[1].get('error_report_path')
                                build1_name = entries[0].get('build_name', 'Build 1')
                                build2_name = entries[1].get('build_name', 'Build 2')
                                
                                # Read report files
                                with open(report1_path, 'r') as f:
                                    report1_content = f.read()
                                with open(report2_path, 'r') as f:
                                    report2_content = f.read()
                                
                                comparison_summary = results.get('ai_analysis', '')
                                
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
        
        if st.button("🗑️ Clear History", use_container_width=True):
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

