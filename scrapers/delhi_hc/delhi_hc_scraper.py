"""
Delhi High Court Cause List Scraper

This module provides a scraper for Delhi High Court cause lists.
"""
import os
import re
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Set, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime

from utils import (
    BaseScraper,
    extract_text_from_pdf,
    clean_filename,
    build_full_url,
    get_content_type,
    ensure_directory,
    parse_pdf_with_gemini,
    save_markdown_output
)


class DelhiHCScraper(BaseScraper):
    """
    Scraper for Delhi High Court cause lists.
    """
    
    # Keywords and patterns that indicate a document is a cause list
    CAUSE_LIST_KEYWORDS = [
        'cause list', 'causelist', 'cause-list', 
        'daily list', 'daily-list', 'dailylist',
        'court no', 'court-no', 'courtno',
        'court-wise', 'courtwise',
        'daily cause list', 'advance cause list',
        'supplementary cause list', 'supplementary list',
        'case wise', 'case-wise', 'fir no wise', 'fir-no-wise',
        'impugned order wise'
    ]
    
    # Keywords and patterns that indicate a document is NOT a cause list
    NON_CAUSE_LIST_KEYWORDS = [
        'help', 'manual', 'guide', 'instruction', 'rule', 
        'notification', 'circular', 'notice', 'vc rule', 
        'video conferencing', 'sop', 'procedure', 'portal',
        'login', 'register', 'sign in', 'sign up', 'feedback',
        'contact', 'about', 'faq', 'disclaimer', 'privacy',
        'terms', 'conditions', 'copyright'
    ]
    
    # File extensions that are likely to be documents
    DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize the Delhi High Court scraper.
        
        Args:
            output_dir: Directory for downloaded files
            config_file: Path to configuration file
        """
        # If no output directory is specified, use the project root's data directory
        if output_dir is None:
            # Get the project root directory (assuming this file is in scrapers/delhi_hc/)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            output_dir = os.path.join(project_root, "data")
        
        # Get base URL from config or use default
        super().__init__(
            court_name="Delhi High Court",
            court_dir_name="delhi_hc",  # Override the default snake_case conversion
            base_url="https://delhihighcourt.nic.in",
            output_dir=output_dir,
            config_file=config_file,
            create_date_dir=False  # Don't create date directory by default
        )
        
        # Set the court directory to match the scraper folder structure
        self.court_dir = os.path.join(self.output_dir, "delhi_hc")
        os.makedirs(self.court_dir, exist_ok=True)
        
        # Set cause list URL from config or use default
        self.cause_list_url = self.config.get(
            "cause_list_url",
            "https://delhihighcourt.nic.in/reports/cause_list/current"
        )
        
        # For tracking processed URLs
        self.processed_urls: Set[str] = set()
        
        self.logger.info(f"Initialized Delhi High Court scraper")
        self.logger.info(f"Output directory: {self.court_dir}")
        self.logger.info(f"Cause list URL: {self.cause_list_url}")
    
    def is_likely_cause_list(self, url: str, title: str, content_type: Optional[str] = None) -> Tuple[bool, float, str]:
        """
        Determine if a link is likely to be a cause list based on URL, title, and content type.
        
        Args:
            url: The URL to check
            title: The title or text of the link
            content_type: The content type of the URL, if known
            
        Returns:
            Tuple of (is_cause_list, confidence, reason)
        """
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Parse URL to get path components
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Check for explicit non-cause list indicators
        for keyword in self.NON_CAUSE_LIST_KEYWORDS:
            if keyword in title_lower:
                return False, 0.9, f"Title contains non-cause list keyword: {keyword}"
            if keyword in path:
                return False, 0.8, f"URL path contains non-cause list keyword: {keyword}"
        
        # Check for explicit cause list indicators in title
        for keyword in self.CAUSE_LIST_KEYWORDS:
            if keyword in title_lower:
                return True, 0.9, f"Title contains cause list keyword: {keyword}"
        
        # Check for explicit cause list indicators in URL path
        for keyword in self.CAUSE_LIST_KEYWORDS:
            if keyword in path:
                return True, 0.8, f"URL path contains cause list keyword: {keyword}"
        
        # Check file extension - only PDFs are likely to be cause lists
        _, ext = os.path.splitext(parsed_url.path)
        if ext.lower() not in ['.pdf']:  # Restrict to only PDF files
            return False, 0.7, f"Not a PDF file: {ext}"
        
        # If we know the content type, check it
        if content_type:
            if 'application/pdf' not in content_type:
                return False, 0.8, f"Not a PDF content type: {content_type}"
        
        # Check for date patterns in URL or title which often indicate cause lists
        date_pattern = r'\d{1,2}[-_.]\d{1,2}[-_.]\d{2,4}|\d{2,4}[-_.]\d{1,2}[-_.]\d{1,2}'
        if re.search(date_pattern, url) or re.search(date_pattern, title):
            return True, 0.7, "Contains date pattern"
        
        # Check if it's a PDF with a random-looking filename (common for court documents)
        if ext.lower() == '.pdf' and re.search(r'\d{8,}', os.path.basename(url)):
            # Additional check for numeric-only filenames which are often system-generated
            if re.match(r'^[0-9]+$', os.path.splitext(os.path.basename(url))[0]):
                return True, 0.6, "PDF with numeric-only filename"
            return True, 0.5, "PDF with numeric ID in filename"
        
        # Default: not confident enough to say it's a cause list
        return False, 0.3, "No clear indicators"
    
    def get_cause_list_links(self) -> List[Dict[str, Any]]:
        """
        Get all cause list links from the main page.
        
        Returns:
            List of dictionaries containing link information
        """
        self.logger.info(f"Fetching cause list links from {self.cause_list_url}")
        
        soup = self.fetch_page(self.cause_list_url)
        if not soup:
            self.logger.error(f"Failed to fetch cause list page: {self.cause_list_url}")
            return []
        
        all_links = []
        cause_list_links = []
        skipped_links = []
        
        # Look for links in the page
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            title = a_tag.get_text(strip=True) or os.path.basename(href)
            
            # Skip JavaScript links
            if href.startswith('javascript:') or href.startswith('javaScript:'):
                self.logger.debug(f"Skipping JavaScript link: {href}")
                continue
            
            # Skip non-PDF links
            _, ext = os.path.splitext(href)
            if ext.lower() != '.pdf':
                self.logger.debug(f"Skipping non-PDF link: {href}")
                continue
                
            full_url = build_full_url(self.base_url, href)
            
            # Skip if we've already processed this URL
            if full_url in self.processed_urls:
                self.logger.debug(f"Skipping already processed URL: {full_url}")
                continue
            
            # Check content type for better filtering
            try:
                content_type = get_content_type(full_url, self.session)
            except Exception as e:
                self.logger.debug(f"Error checking content type for {full_url}: {e}")
                content_type = None
            
            is_cause_list, confidence, reason = self.is_likely_cause_list(full_url, title, content_type)
            
            link_info = {
                'url': full_url,
                'title': title,
                'content_type': content_type,
                'is_cause_list': is_cause_list,
                'confidence': confidence,
                'reason': reason
            }
            all_links.append(link_info)
            
            if is_cause_list and confidence >= 0.5:  # Only include if confidence is at least 0.5
                cause_list_links.append(link_info)
                self.logger.debug(f"Found cause list link: {full_url} ({reason})")
            else:
                skipped_links.append(link_info)
                self.logger.debug(f"Skipped link: {full_url} ({reason})")
        
        # Print summary of filtering
        self.logger.info(f"Found {len(all_links)} total links")
        self.logger.info(f"Identified {len(cause_list_links)} cause list links")
        self.logger.info(f"Skipped {len(skipped_links)} non-cause list links")
        
        return cause_list_links
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run the scraper to fetch and process cause lists.
        
        Returns:
            List of metadata for downloaded cause lists
        """
        self.logger.info("Starting Delhi High Court cause list scraper")
        
        try:
            # Get all cause list links
            self.logger.info(f"Fetching cause list links from {self.cause_list_url}")
            cause_list_links = self.get_cause_list_links()
            
            if not cause_list_links:
                self.logger.warning(f"No cause list links found at {self.cause_list_url}")
                return []
            
            self.logger.info(f"Found {len(cause_list_links)} cause list links")
            
            # Download PDFs in parallel
            pdf_files = self._download_pdfs_parallel(cause_list_links)
            
            # Process PDFs with Gemini in parallel
            self._process_pdfs_parallel(pdf_files)
            
            # Save metadata
            if self.metadata:
                metadata_path = self.save_metadata()
                self.logger.info(f"Saved metadata to: {metadata_path}")
            
            return self.metadata
        
        except Exception as e:
            self.logger.error(f"Error running scraper: {e}", exc_info=True)
            return []
        
        finally:
            # Close the scraper
            self.close()
    
    def _download_pdfs_parallel(self, links: List[Dict[str, Any]]) -> List[str]:
        """
        Download PDFs in parallel.
        
        Args:
            links: List of link information dictionaries
            
        Returns:
            List of paths to downloaded PDF files
        """
        # Get configuration for parallel downloads
        parallel_downloads = self.config.get("parallel_downloads", True)
        max_workers = self.config.get("download_workers", 5)
        
        if not parallel_downloads:
            # Fall back to sequential downloads
            self.logger.info("Using sequential PDF downloads")
            pdf_files = []
            for link in links:
                pdf_path = self._download_pdf(link["url"], link)
                if pdf_path:
                    pdf_files.append(pdf_path)
            return pdf_files
        
        # Use parallel downloads
        self.logger.info(f"Using parallel PDF downloads with {max_workers} workers")
        pdf_files = []
        
        # Thread-safe lock for updating shared resources
        metadata_lock = threading.Lock()
        
        def download_worker(link):
            try:
                url = link["url"]
                # Skip if not a PDF
                if not url.lower().endswith('.pdf'):
                    self.logger.debug(f"Skipping non-PDF file: {url}")
                    return None
                
                # Mark URL as processed
                with metadata_lock:
                    self.processed_urls.add(url)
                
                # Download the PDF
                self.logger.info(f"Downloading file: {url}")
                pdf_path = self.download_file(url)
                
                if not pdf_path:
                    self.logger.warning(f"Failed to download file: {url}")
                    return None
                
                # Add metadata
                metadata = {
                    "url": url,
                    "file_path": pdf_path,
                    "court": "Delhi High Court",
                    "date": None,
                    "title": link.get("title") if link else os.path.basename(pdf_path),
                    "content_type": link.get("content_type") if link else "application/pdf",
                    "download_time": datetime.now().isoformat()
                }
                
                with metadata_lock:
                    self.metadata.append(metadata)
                
                return pdf_path
            except Exception as e:
                self.logger.error(f"Error downloading PDF {link.get('url')}: {e}")
                return None
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {executor.submit(download_worker, link): link for link in links}
            
            for future in as_completed(future_to_link):
                pdf_path = future.result()
                if pdf_path:
                    pdf_files.append(pdf_path)
        
        self.logger.info(f"Downloaded {len(pdf_files)} PDF files")
        return pdf_files
    
    def _process_pdfs_parallel(self, pdf_files: List[str]) -> None:
        """
        Process PDFs with Gemini API in parallel.
        
        Args:
            pdf_files: List of paths to PDF files
        """
        # Check if Gemini API is enabled
        if not self.config.get("use_gemini_api", True):
            self.logger.info("Gemini API processing is disabled")
            return
        
        # Get configuration for parallel processing
        parallel_processing = self.config.get("parallel_processing", True)
        max_workers = self.config.get("processing_workers", 3)
        
        if not parallel_processing:
            # Fall back to sequential processing
            self.logger.info("Using sequential Gemini API processing")
            for pdf_path in pdf_files:
                self._process_pdf_with_gemini(pdf_path)
            return
        
        # Use parallel processing
        self.logger.info(f"Using parallel Gemini API processing with {max_workers} workers")
        
        def process_worker(pdf_path):
            try:
                return self._process_pdf_with_gemini(pdf_path)
            except Exception as e:
                self.logger.error(f"Error processing PDF {pdf_path} with Gemini: {e}")
                return None
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_pdf = {executor.submit(process_worker, pdf_path): pdf_path for pdf_path in pdf_files}
            
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    result = future.result()
                    if result:
                        self.logger.info(f"Successfully processed PDF: {pdf_path}")
                except Exception as e:
                    self.logger.error(f"Error processing PDF {pdf_path}: {e}")
    
    def _process_pdf_with_gemini(self, pdf_path: str) -> Optional[str]:
        """
        Process a PDF file with Gemini API.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Path to the markdown file or None if processing failed
        """
        try:
            self.logger.info(f"Parsing PDF with Gemini API: {pdf_path}")
            markdown_content = parse_pdf_with_gemini(pdf_path)
            
            if markdown_content:
                markdown_path = save_markdown_output(pdf_path, markdown_content)
                self.logger.info(f"Saved structured markdown to: {markdown_path}")
                return markdown_path
            else:
                self.logger.warning(f"Failed to parse PDF with Gemini: {pdf_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing PDF with Gemini: {e}")
            return None
    
    def _download_pdf(self, pdf_url: str, link_info: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Download a PDF file from a URL.
        
        Args:
            pdf_url: URL of the PDF file
            link_info: Additional information about the link
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        # Mark URL as processed
        self.processed_urls.add(pdf_url)
        
        # Skip if not a PDF
        if not pdf_url.lower().endswith('.pdf'):
            self.logger.debug(f"Skipping non-PDF file: {pdf_url}")
            return None
            
        try:
            # Download the PDF
            self.logger.info(f"Downloading file: {pdf_url}")
            pdf_path = self.download_file(pdf_url)
            
            if not pdf_path:
                self.logger.warning(f"Failed to download file: {pdf_url}")
                return None
            
            # Add metadata
            metadata = {
                "url": pdf_url,
                "file_path": pdf_path,
                "court": "Delhi High Court",
                "date": None,
                "title": link_info.get("title") if link_info else os.path.basename(pdf_path),
                "content_type": link_info.get("content_type") if link_info else "application/pdf",
                "download_time": datetime.now().isoformat()
            }
            self.metadata.append(metadata)
            
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"Error downloading PDF: {e}")
            return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Delhi High Court Cause List Scraper")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--config", "-c", help="Configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    scraper = DelhiHCScraper(
        output_dir=args.output,
        config_file=args.config
    )
    
    if args.debug:
        import logging
        scraper.logger.setLevel(logging.DEBUG)
    
    scraper.run()
