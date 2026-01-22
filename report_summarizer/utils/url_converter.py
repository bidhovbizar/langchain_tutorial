"""
URL Converter - Converts Supernova and Reportio URLs to local file paths
"""

import re
from pathlib import Path
from typing import Optional, Tuple


class URLConverter:
    """Converts supernova.cisco.com and reportio.cisco.com URLs to local file system paths"""
    
    # Base mapping from URL to filesystem for Supernova
    SUPERNOVA_BASE_URL = "https://supernova.cisco.com/logviewer/runtests/results/sanity/"
    SUPERNOVA_BASE_PATH = "/auto/intersight-sanity/sanity_logs/sanity/"
    
    # Base mapping from URL to filesystem for Reportio
    REPORTIO_BASE_URL = "http://reportio.cisco.com/"
    REPORTIO_BASE_PATH = "/auto/CRR_Regression/"
    
    @classmethod
    def get_url_type(cls, url: str) -> str:
        """
        Determine the type of URL (supernova or reportio).
        
        Args:
            url: URL string to check
            
        Returns:
            str: 'supernova', 'reportio', or 'unknown'
        """
        if not url or not isinstance(url, str):
            return 'unknown'
        
        url = url.strip()
        
        if url.startswith(cls.SUPERNOVA_BASE_URL):
            return 'supernova'
        elif url.startswith(cls.REPORTIO_BASE_URL):
            return 'reportio'
        else:
            return 'unknown'
    
    @classmethod
    def is_valid_supernova_url(cls, url: str) -> bool:
        """
        Check if the URL is a valid supernova URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return cls.get_url_type(url) == 'supernova'
    
    @classmethod
    def is_valid_reportio_url(cls, url: str) -> bool:
        """
        Check if the URL is a valid reportio URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return cls.get_url_type(url) == 'reportio'
    
    @classmethod
    def url_to_path(cls, url: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Convert Supernova or Reportio URL to local filesystem path.
        
        Args:
            url: Supernova or Reportio URL
                - Supernova: https://supernova.cisco.com/logviewer/runtests/results/sanity/...
                - Reportio: http://reportio.cisco.com/qali/iucstest/...
            
        Returns:
            Tuple of (success, path, error_message)
            - success: bool indicating if conversion was successful
            - path: Path object if successful, None otherwise
            - error_message: Error message if unsuccessful, None otherwise
        """
        url_type = cls.get_url_type(url)
        
        if url_type == 'unknown':
            return False, None, "Invalid URL. Must be a Supernova or Reportio URL."
        
        try:
            if url_type == 'supernova':
                return cls._convert_supernova_url(url)
            elif url_type == 'reportio':
                return cls._convert_reportio_url(url)
            else:
                return False, None, "Unsupported URL type"
                
        except Exception as e:
            return False, None, f"Error converting URL: {str(e)}"
    
    @classmethod
    def _convert_supernova_url(cls, url: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Convert Supernova URL to local filesystem path.
        
        Args:
            url: Supernova URL
            
        Returns:
            Tuple of (success, path, error_message)
        """
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
        local_path = Path(cls.SUPERNOVA_BASE_PATH) / relative_path
        
        return True, local_path, None
    
    @classmethod
    def _convert_reportio_url(cls, url: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Convert Reportio URL to local filesystem path.
        
        Args:
            url: Reportio URL (e.g., http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html)
            
        Returns:
            Tuple of (success, path, error_message)
        """
        # Remove the base URL to get the relative path
        # From: http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html
        # To: qali/iucstest/sanity_1839514_4924955718040703741/detail.html
        relative_path = url.replace(cls.REPORTIO_BASE_URL, '')
        
        if not relative_path:
            return False, None, "URL path is empty after removing base URL"
        
        # Build the local path: /auto/CRR_Regression/ + relative_path
        local_path = Path(cls.REPORTIO_BASE_PATH) / relative_path
        
        return True, local_path, None
    
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
        Extract build information from the URL (Supernova or Reportio).
        
        Args:
            url: Supernova or Reportio URL
            
        Returns:
            dict: Dictionary containing build information
        """
        info = {
            'build_name': None,
            'suite': None,
            'environment': None,  # staging, qatest, production
            'project': None,  # sars, imm, iucstest, etc.
            'url_type': None  # supernova or reportio
        }
        
        url_type = cls.get_url_type(url)
        info['url_type'] = url_type
        
        if url_type == 'unknown':
            return info
        
        try:
            if url_type == 'supernova':
                return cls._extract_supernova_build_info(url, info)
            elif url_type == 'reportio':
                return cls._extract_reportio_build_info(url, info)
        except Exception:
            pass
        
        return info
    
    @classmethod
    def _extract_supernova_build_info(cls, url: str, info: dict) -> dict:
        """
        Extract build information from a Supernova URL.
        
        Args:
            url: Supernova URL
            info: Dictionary to populate with build information
            
        Returns:
            dict: Updated info dictionary
        """
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
        
        return info
    
    @classmethod
    def _extract_reportio_build_info(cls, url: str, info: dict) -> dict:
        """
        Extract build information from a Reportio URL.
        
        Args:
            url: Reportio URL (e.g., http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html)
            info: Dictionary to populate with build information
            
        Returns:
            dict: Updated info dictionary
        """
        # Get the relative path after reportio.cisco.com
        relative_path = url.replace(cls.REPORTIO_BASE_URL, '')
        url_parts = relative_path.split('/')
        
        # Format: qali/iucstest/sanity_1839514_4924955718040703741/detail.html
        # Parts: [qali, iucstest, sanity_1839514_4924955718040703741, detail.html]
        
        if len(url_parts) >= 2:
            # Project is typically the second part (e.g., iucstest)
            info['project'] = url_parts[1]
        
        if len(url_parts) >= 3:
            # Build name is typically the third part (e.g., sanity_1839514_4924955718040703741)
            build_name = url_parts[2]
            info['build_name'] = build_name
            
            # Try to extract additional info from build name
            # Format might be: sanity_<qali_id>_<run_id>
            match = re.match(r'sanity_(\d+)_(\d+)', build_name)
            if match:
                info['qali_id'] = match.group(1)
                info['run_id'] = match.group(2)
        
        # Note: Reportio URLs don't typically have environment in the path
        # We might need to extract it from other sources or mark as 'unknown'
        info['environment'] = 'reportio'  # Mark as reportio-based
        
        return info
    
    @classmethod
    def get_example_urls(cls) -> list:
        """
        Get example URLs for display purposes.
        
        Returns:
            list: List of example URL strings (both Supernova and Reportio)
        """
        return [
            # Supernova URLs
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_sars_sanity_build_7449/test_results/sars/detail.html",
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/qatest_sars_sanity_build_7447/test_results/sars/detail.html",
            "https://supernova.cisco.com/logviewer/runtests/results/sanity/staging_imm_sanity_build_8875/test_results/sanity1/detail.html",
            # Reportio URLs
            "http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/detail.html",
            "http://reportio.cisco.com/qali/iucstest/sanity_1839514_4924955718040703741/index.html"
        ]

