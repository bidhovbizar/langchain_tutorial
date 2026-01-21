"""
URL Converter - Converts Supernova URLs to local file paths
"""

import re
from pathlib import Path
from typing import Optional, Tuple


class URLConverter:
    """Converts supernova.cisco.com URLs to local file system paths"""
    
    # Base mapping from URL to filesystem
    BASE_URL = "https://supernova.cisco.com/logviewer/runtests/results/sanity/"
    BASE_PATH = "/auto/intersight-sanity/sanity_logs/sanity/"
    
    @classmethod
    def is_valid_supernova_url(cls, url: str) -> bool:
        """
        Check if the URL is a valid supernova URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        return url.startswith(cls.BASE_URL)
    
    @classmethod
    def url_to_path(cls, url: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Convert supernova URL to local filesystem path.
        
        Args:
            url: Supernova URL (e.g., https://supernova.cisco.com/logviewer/runtests/results/sanity/...)
            
        Returns:
            Tuple of (success, path, error_message)
            - success: bool indicating if conversion was successful
            - path: Path object if successful, None otherwise
            - error_message: Error message if unsuccessful, None otherwise
        """
        # Validate URL
        if not cls.is_valid_supernova_url(url):
            return False, None, "Invalid URL. Must start with https://supernova.cisco.com/logviewer/runtests/results/sanity/"
        
        try:
            # Split URL by '/' and find the parts after 'sanity'
            url_parts = url.split('/')
            
            # Find the index of 'sanity' in the URL parts
            try:
                sanity_index = url_parts.index('sanity')
            except ValueError:
                return False, None, "Could not find 'sanity' in URL path"
            
            # Get all parts after 'sanity' (the build name and remaining path)
            # Format: staging_sars_sanity_build_7449/test_results/sars/detail.html
            remaining_parts = url_parts[sanity_index + 1:]
            
            if len(remaining_parts) < 1:
                return False, None, "URL path is too short. Expected format: .../sanity/<build_name>/test_results/..."
            
            # Join the remaining parts to create relative path
            relative_path = '/'.join(remaining_parts)
            
            # Build the local path: /auto/intersight-sanity/sanity_logs/sanity/ + relative_path
            local_path = Path(cls.BASE_PATH) / relative_path
            
            return True, local_path, None
            
        except Exception as e:
            return False, None, f"Error converting URL: {str(e)}"
    
    @classmethod
    def get_detail_html_path(cls, url: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Get the path to detail.html from any URL in the test results.
        
        Args:
            url: Supernova URL
            
        Returns:
            Tuple of (success, path_to_detail_html, error_message)
        """
        success, path, error = cls.url_to_path(url)
        
        if not success:
            return False, None, error
        
        # If the URL already points to detail.html, use it directly
        if path.name == 'detail.html':
            detail_path = path
        else:
            # Otherwise, assume we need to find detail.html in the same directory
            # or go up to test_results/<suite>/detail.html
            if 'test_results' in path.parts:
                # Find the test_results directory and suite name
                parts = list(path.parts)
                try:
                    test_results_idx = parts.index('test_results')
                    if test_results_idx + 1 < len(parts):
                        # Reconstruct path to detail.html
                        suite_path = Path(*parts[:test_results_idx + 2])
                        detail_path = suite_path / 'detail.html'
                    else:
                        detail_path = path.parent / 'detail.html'
                except ValueError:
                    detail_path = path.parent / 'detail.html'
            else:
                detail_path = path.parent / 'detail.html'
        
        # Check if detail.html exists
        if not detail_path.exists():
            return False, None, f"detail.html not found at: {detail_path}"
        
        return True, detail_path, None
    
    @classmethod
    def get_index_html_path(cls, url: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Get the path to index.html from any URL in the test results.
        This is what test_results_analyzer expects.
        
        Args:
            url: Supernova URL
            
        Returns:
            Tuple of (success, path_to_index_html, error_message)
        """
        success, path, error = cls.url_to_path(url)
        
        if not success:
            return False, None, error
        
        # If the URL points to index.html, use it directly
        if path.name == 'index.html':
            index_path = path
        # If it points to detail.html, replace with index.html
        elif path.name == 'detail.html':
            index_path = path.parent / 'index.html'
        else:
            # Otherwise, look for index.html in the test_results/<suite>/ directory
            if 'test_results' in path.parts:
                # Find the test_results directory and suite name
                parts = list(path.parts)
                try:
                    test_results_idx = parts.index('test_results')
                    if test_results_idx + 1 < len(parts):
                        # Reconstruct path to index.html
                        suite_path = Path(*parts[:test_results_idx + 2])
                        index_path = suite_path / 'index.html'
                    else:
                        index_path = path.parent / 'index.html'
                except ValueError:
                    index_path = path.parent / 'index.html'
            else:
                index_path = path.parent / 'index.html'
        
        # Check if index.html exists
        if not index_path.exists():
            return False, None, f"index.html not found at: {index_path}"
        
        return True, index_path, None
    
    @classmethod
    def extract_build_info(cls, url: str) -> dict:
        """
        Extract build information from the URL.
        
        Args:
            url: Supernova URL
            
        Returns:
            dict: Dictionary containing build information
        """
        info = {
            'build_name': None,
            'suite': None,
            'environment': None,  # staging, qatest, production
            'project': None  # sars, imm, etc.
        }
        
        if not cls.is_valid_supernova_url(url):
            return info
        
        try:
            # Split URL by '/' and find parts after 'sanity'
            url_parts = url.split('/')
            
            try:
                sanity_index = url_parts.index('sanity')
            except ValueError:
                return info
            
            # Get parts after 'sanity'
            remaining_parts = url_parts[sanity_index + 1:]
            
            if len(remaining_parts) >= 1:
                # Build name is the first part after 'sanity'
                build_name = remaining_parts[0]
                info['build_name'] = build_name
                
                # Extract environment and project from build name
                # Format: <environment>_<project>_sanity_build_<number>
                match = re.match(r'(\w+)_(\w+)_sanity_build_(\d+)', build_name)
                if match:
                    info['environment'] = match.group(1)
                    info['project'] = match.group(2)
                    info['build_number'] = match.group(3)
            
            # Suite name is typically after test_results/
            if 'test_results' in remaining_parts:
                idx = remaining_parts.index('test_results')
                if idx + 1 < len(remaining_parts):
                    info['suite'] = remaining_parts[idx + 1]
        
        except Exception:
            pass
        
        return info
    
    @classmethod
    def get_example_urls(cls) -> list:
        """
        Get example URLs for display purposes.
        
        Returns:
            list: List of example URL strings
        """
        return [
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7449/test_results/sars/detail.html",
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/qatest_sars_sanity_build_7447/test_results/sars/detail.html",
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/production_sars_sanity_build_7448/test_results/sars/detail.html",
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_imm_sanity_build_8875/test_results/sanity1/detail.html"
        ]

