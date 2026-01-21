"""
Session Manager - Handles history and comparison of analysis results
"""

from datetime import datetime
from typing import List, Dict, Optional
from collections import deque


class SessionManager:
    """Manages session history and comparison features"""
    
    MAX_HISTORY = 8  # Keep last 8 analyses
    
    def __init__(self):
        """Initialize session manager"""
        self.history = deque(maxlen=self.MAX_HISTORY)
        self.selected_for_comparison = []
    
    def add_to_history(
        self,
        url: str,
        build_info: Dict,
        analyzer_results: Dict,
        summary_results: Optional[Dict] = None,
        analysis_mode: str = "quick"
    ) -> str:
        """
        Add an analysis to history.
        
        Args:
            url: Original URL
            build_info: Build information from URL
            analyzer_results: Results from analyzer
            summary_results: Results from AI summarizer (if full mode)
            analysis_mode: "quick" or "full"
            
        Returns:
            str: History entry ID
        """
        entry_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        entry = {
            'id': entry_id,
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'build_info': build_info,
            'analyzer_results': analyzer_results,
            'summary_results': summary_results,
            'analysis_mode': analysis_mode,
            'selected': False
        }
        
        self.history.append(entry)
        return entry_id
    
    def get_history(self) -> List[Dict]:
        """
        Get all history entries (most recent first).
        
        Returns:
            List of history entries
        """
        return list(reversed(self.history))
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """
        Get a specific history entry by ID.
        
        Args:
            entry_id: Entry ID to retrieve
            
        Returns:
            Dict: History entry or None if not found
        """
        for entry in self.history:
            if entry['id'] == entry_id:
                return entry
        return None
    
    def toggle_comparison(self, entry_id: str) -> bool:
        """
        Toggle an entry's selection for comparison.
        
        Args:
            entry_id: Entry ID to toggle
            
        Returns:
            bool: New selection state
        """
        for entry in self.history:
            if entry['id'] == entry_id:
                entry['selected'] = not entry['selected']
                
                if entry['selected']:
                    if entry_id not in self.selected_for_comparison:
                        self.selected_for_comparison.append(entry_id)
                else:
                    if entry_id in self.selected_for_comparison:
                        self.selected_for_comparison.remove(entry_id)
                
                return entry['selected']
        return False
    
    def get_selected_entries(self) -> List[Dict]:
        """
        Get entries selected for comparison.
        
        Returns:
            List of selected entries
        """
        selected = []
        for entry_id in self.selected_for_comparison:
            entry = self.get_entry(entry_id)
            if entry:
                selected.append(entry)
        return selected
    
    def clear_comparison(self):
        """Clear all comparison selections"""
        for entry in self.history:
            entry['selected'] = False
        self.selected_for_comparison = []
    
    def clear_history(self):
        """Clear all history"""
        self.history.clear()
        self.selected_for_comparison = []
    
    def format_history_summary(self, entry: Dict) -> str:
        """
        Format a history entry for display.
        
        Args:
            entry: History entry
            
        Returns:
            str: Formatted summary
        """
        build_name = entry['build_info'].get('build_name', 'Unknown')
        timestamp = entry.get('timestamp', '')
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        # Get test stats
        analyzer_results = entry.get('analyzer_results', {})
        total_tests = analyzer_results.get('total_tests', 0)
        failed_tests = analyzer_results.get('failed_tests', 0)
        
        if total_tests > 0:
            pass_rate = (1 - failed_tests / total_tests) * 100
        else:
            pass_rate = 0
        
        mode = entry.get('analysis_mode', 'quick').upper()
        
        summary = f"**{build_name}**\n"
        summary += f"📅 {time_str} | 🔍 {mode}\n"
        summary += f"✅ {total_tests - failed_tests}/{total_tests} passed ({pass_rate:.1f}%)"
        
        return summary
    
    def compare_entries(self, entry_ids: List[str]) -> Dict:
        """
        Compare multiple entries and generate comparison data.
        
        Args:
            entry_ids: List of entry IDs to compare
            
        Returns:
            Dict containing comparison data
        """
        entries = [self.get_entry(eid) for eid in entry_ids if self.get_entry(eid)]
        
        if len(entries) < 2:
            return {'error': 'Need at least 2 entries to compare'}
        
        comparison = {
            'entries': [],
            'common_failures': [],
            'unique_failures': {},
            'stats_comparison': []
        }
        
        # Collect all failure names
        all_failures = {}
        
        for entry in entries:
            build_name = entry['build_info'].get('build_name', 'Unknown')
            analyzer_results = entry.get('analyzer_results', {})
            
            entry_data = {
                'build_name': build_name,
                'total_tests': analyzer_results.get('total_tests', 0),
                'failed_tests': analyzer_results.get('failed_tests', 0),
                'failures': []
            }
            
            # Extract failure names
            failures = analyzer_results.get('failures', [])
            failure_names = set()
            
            for failure in failures:
                test_name = failure.get('test_name', 'Unknown')
                suite_name = failure.get('suite_name', 'Unknown')
                full_name = f"{suite_name}/{test_name}"
                failure_names.add(full_name)
                entry_data['failures'].append({
                    'name': full_name,
                    'status': failure.get('status', 'Unknown'),
                    'message': failure.get('error_message', '')[:100]
                })
            
            all_failures[build_name] = failure_names
            comparison['entries'].append(entry_data)
        
        # Find common failures (present in all builds)
        if len(all_failures) > 0:
            common = set.intersection(*all_failures.values())
            comparison['common_failures'] = list(common)
            
            # Find unique failures for each build
            for build_name, failures in all_failures.items():
                other_failures = set()
                for other_build, other_fail in all_failures.items():
                    if other_build != build_name:
                        other_failures.update(other_fail)
                
                unique = failures - other_failures
                if unique:
                    comparison['unique_failures'][build_name] = list(unique)
        
        return comparison

