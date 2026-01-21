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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
    .history-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
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


def display_header():
    """Display application header"""
    st.markdown('<p class="main-header">🔍 Test Report Analyzer & Summarizer</p>', unsafe_allow_html=True)
    st.markdown("---")


def display_url_input():
    """Display URL input section"""
    st.subheader("📝 Enter Supernova URL")
    
    # Show examples
    with st.expander("📋 Click to see example URLs"):
        examples = URLConverter.get_example_urls()
        for i, url in enumerate(examples, 1):
            st.code(url, language="text")
    
    # URL input
    url = st.text_input(
        "Supernova Test Results URL:",
        value=st.session_state.current_url,
        placeholder="https://supernova.cisco.com/logviewer/runtests/results/sanity/...",
        help="Enter the URL to your test results detail.html page"
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
            if not URLConverter.is_valid_supernova_url(url):
                status.update(label="❌ Invalid URL", state="error")
                return None, None
            
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
        fetch_logs = (analysis_mode.lower() == "full")
        
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
    st.subheader("📊 Analysis Results")
    
    # Summary statistics
    analyzer_results = results['analyzer']
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_tests = analyzer_results.get('total_tests', 0)
    failed_tests = analyzer_results.get('failed_tests', 0)
    passed_tests = total_tests - failed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    with col1:
        st.metric("Total Tests", total_tests)
    
    with col2:
        st.metric("Passed", passed_tests, delta=f"{pass_rate:.1f}%")
    
    with col3:
        st.metric("Failed", failed_tests, delta=f"-{100-pass_rate:.1f}%", delta_color="inverse")
    
    with col4:
        mode_emoji = "⚡" if results['mode'] == 'quick' else "🤖"
        st.metric("Analysis Mode", f"{mode_emoji} {results['mode'].upper()}")
    
    # Display summary/analysis
    st.markdown("---")
    
    summary_result = results['summary']
    
    if results['mode'] == 'quick':
        st.subheader("⚡ Quick AI Summary")
    else:
        st.subheader("🔍 Detailed AI Analysis")
    
    # Display the AI-generated content
    st.markdown(summary_result['content'])
    
    # Show token usage in expander (for both modes)
    if 'usage' in summary_result and summary_result['usage']:
        with st.expander("📈 Token Usage Statistics"):
            usage = summary_result['usage']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Input Tokens", usage.get('prompt_tokens', 'N/A'))
            with col2:
                st.metric("Output Tokens", usage.get('completion_tokens', 'N/A'))
            with col3:
                st.metric("Total Tokens", usage.get('total_tokens', 'N/A'))
    
    # Download buttons
    st.markdown("---")
    st.subheader("💾 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download error report
        try:
            with open(results['report_path'], 'r') as f:
                report_content = f.read()
            
            st.download_button(
                label="📄 Download Error Report",
                data=report_content,
                file_name=Path(results['report_path']).name,
                mime="text/plain"
            )
        except:
            st.error("Error reading report file")
    
    with col2:
        # Download analysis (both modes use same structure now)
        analysis_content = results['summary']['content']
        
        mode_label = "quick_summary" if results['mode'] == 'quick' else "full_analysis"
        
        st.download_button(
            label="📄 Download Analysis",
            data=analysis_content,
            file_name=f"{mode_label}_{results['entry_id']}.txt",
            mime="text/plain"
        )


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
    st.subheader("🔄 AI-Powered Build Comparison")
    
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
    
    # Display quick stats comparison
    st.markdown("### 📊 Quick Statistics")
    
    cols = st.columns(len(comparison['entries']))
    
    for idx, entry_data in enumerate(comparison['entries']):
        with cols[idx]:
            st.markdown(f"**{entry_data['build_name']}**")
            st.metric("Total Tests", entry_data['total_tests'])
            st.metric("Failed", entry_data['failed_tests'])
            
            pass_rate = ((entry_data['total_tests'] - entry_data['failed_tests']) / entry_data['total_tests'] * 100) if entry_data['total_tests'] > 0 else 0
            st.metric("Pass Rate", f"{pass_rate:.1f}%")
    
    st.markdown("---")
    
    # AI-Powered Comparison Analysis
    st.markdown("### 🤖 AI Analysis")
    
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
        
        # Download button
        st.markdown("---")
        builds = result.get('builds_compared', ['build1', 'build2'])
        comparison_filename = f"comparison_{builds[0]}_vs_{builds[1]}.txt"
        
        st.download_button(
            label="📄 Download Comparison Analysis",
            data=result['content'],
            file_name=comparison_filename,
            mime="text/plain"
        )
        
        # Clear comparison button
        if st.button("🔄 Run New Comparison", use_container_width=True):
            del st.session_state[comparison_key]
            st.rerun()
    
    st.markdown("---")
    
    # Back button
    if st.button("← Back to Results", use_container_width=True):
        st.session_state.show_comparison = False
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

