"""
Delhi High Court Cause List Scraper

This module provides a scraper for Delhi High Court cause lists.
"""
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from utils import (
    BaseScraper,
    extract_links_from_html,
    extract_date_from_html,
    extract_pdf_links_from_html,
    is_cause_list_pdf,
    extract_structured_data_from_pdf,
    extract_date_from_pdf,
    clean_filename,
    build_full_url,
    get_content_type
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
            base_url="https://delhihighcourt.nic.in",
            output_dir=output_dir,
            config_file=config_file
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
        if ext.lower() not in self.DOCUMENT_EXTENSIONS:
            return False, 0.7, f"Not a document file type: {ext}"
        
        # If we know the content type, check it
        if content_type:
            if 'text/html' in content_type:
                return False, 0.8, "Content is HTML, not a document"
            if 'application/pdf' not in content_type and 'application/msword' not in content_type:
                return False, 0.6, f"Unexpected content type: {content_type}"
        
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
            full_url = build_full_url(self.base_url, href)
            title = a_tag.get_text(strip=True) or os.path.basename(href)
            
            # Skip if we've already processed this URL
            if full_url in self.processed_urls:
                self.logger.debug(f"Skipping already processed URL: {full_url}")
                continue
            
            # Check content type for better filtering
            content_type = get_content_type(full_url, self.session)
            
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
            # Get cause list links
            cause_list_links = self.get_cause_list_links()
            
            # Process each cause list link
            for link_info in cause_list_links:
                pdf_url = link_info['url']
                self.processed_urls.add(pdf_url)
                self._process_pdf(pdf_url, link_info)
            
            # Save metadata
            metadata_path = self.save_metadata(format="json")
            self.logger.info(f"Saved metadata to: {metadata_path}")
            
            return self.metadata
        
        except Exception as e:
            self.logger.error(f"Error running scraper: {e}", exc_info=True)
            return []
        
        finally:
            # Close the scraper
            self.close()
    
    def _process_pdf(self, pdf_url: str, link_info: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Process a PDF file from a URL.
        
        Args:
            pdf_url: URL of the PDF file
            link_info: Additional information about the link
        
        Returns:
            Path to the downloaded file or None if processing failed
        """
        self.logger.info(f"Processing PDF: {pdf_url}")
        
        try:
            # Download the PDF
            pdf_path = self.download_file(pdf_url)
            if not pdf_path:
                self.logger.warning(f"Failed to download PDF: {pdf_url}")
                return None
            
            # Check if it's a cause list PDF
            if not is_cause_list_pdf(pdf_path):
                self.logger.info(f"Not a cause list PDF: {pdf_path}")
                return pdf_path
            
            # Extract date from PDF
            pdf_date = extract_date_from_pdf(pdf_path)
            if pdf_date:
                self.logger.info(f"PDF date: {pdf_date}")
                
                # Create a directory for this date if it doesn't exist
                date_dir = os.path.join(
                    self.court_dir,
                    pdf_date.strftime("%Y-%m-%d")
                )
                os.makedirs(date_dir, exist_ok=True)
                
                # Move the file to the date directory
                filename = os.path.basename(pdf_path)
                new_path = os.path.join(date_dir, filename)
                
                if os.path.exists(new_path):
                    self.logger.debug(f"File already exists at destination: {new_path}")
                else:
                    os.rename(pdf_path, new_path)
                    self.logger.info(f"Moved file to: {new_path}")
                
                pdf_path = new_path
            
            # Add metadata
            metadata = {
                'url': pdf_url,
                'filename': os.path.basename(pdf_path),
                'path': pdf_path,
                'date': pdf_date.strftime("%Y-%m-%d") if pdf_date else None,
                'title': link_info.get('title') if link_info else os.path.basename(pdf_path),
                'content_type': link_info.get('content_type') if link_info else None,
                'is_cause_list': True,
                'confidence': link_info.get('confidence') if link_info else 1.0,
                'reason': link_info.get('reason') if link_info else "Direct download",
                'download_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.metadata.append(metadata)
            
            # Extract structured data if configured
            if self.config.get("extract_structured_data", True):
                try:
                    structured_data = extract_structured_data_from_pdf(pdf_path)
                    if structured_data:
                        # Save structured data
                        json_path = os.path.splitext(pdf_path)[0] + ".json"
                        with open(json_path, "w") as f:
                            import json
                            json.dump(structured_data, f, indent=2)
                        self.logger.info(f"Saved structured data to: {json_path}")
                        
                        # Add structured data to metadata
                        metadata['structured_data_path'] = json_path
                except Exception as e:
                    self.logger.error(f"Error extracting structured data: {e}")
            
            return pdf_path
        
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_url}: {e}")
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
