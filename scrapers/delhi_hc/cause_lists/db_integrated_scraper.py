"""
Delhi High Court Cause List Scraper with Database Integration

This module provides a specialized scraper for Delhi High Court cause lists
that automatically processes and stores structured data in the database.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from ..delhi_hc_scraper import DelhiHCScraper
from utils.data_processor import CauseListProcessor
from db.connector import DBConnector


class DelhiHCCauseListDBScraper(DelhiHCScraper):
    """
    Specialized scraper for Delhi High Court cause lists with database integration.
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None,
        db_connector: Optional[DBConnector] = None
    ):
        """
        Initialize the Delhi High Court cause list scraper with database integration.
        
        Args:
            output_dir: Directory for downloaded files
            config_file: Path to configuration file
            db_connector: Database connector
        """
        super().__init__(output_dir=output_dir, config_file=config_file)
        
        # Override the output directory to include 'cause_lists'
        self.cause_lists_dir = os.path.join(self.court_dir, 'cause_lists')
        os.makedirs(self.cause_lists_dir, exist_ok=True)
        
        # Update the court_dir to point to the cause_lists directory
        self.court_dir = self.cause_lists_dir
        
        # Update today_dir to use the cause_lists directory instead of the original today_dir
        today = datetime.now().strftime("%Y-%m-%d")
        self.today_dir = os.path.join(self.court_dir, today)
        os.makedirs(self.today_dir, exist_ok=True)
        
        # Initialize database connector
        self.db = db_connector or DBConnector()
        
        # Initialize data processor
        try:
            self.data_processor = CauseListProcessor(self.db, "delhi_hc")
            self.db_enabled = True
        except Exception as e:
            self.logger.error(f"Failed to initialize data processor: {e}")
            self.db_enabled = False
        
        self.logger.info(f"Cause list output directory: {self.court_dir}")
        self.logger.info(f"Today's cause list directory: {self.today_dir}")
        self.logger.info(f"Database integration: {'Enabled' if self.db_enabled else 'Disabled'}")
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run the cause list scraper.
        
        Returns:
            List of metadata for downloaded cause lists
        """
        self.logger.info("Starting Delhi High Court cause list scraper with database integration")
        
        try:
            # Get cause list links
            cause_list_links = self.get_cause_list_links()
            
            # Filter links to only include cause lists with high confidence
            filtered_links = []
            for link_info in cause_list_links:
                pdf_url = link_info['url']
                
                # Skip if not a cause list with high confidence
                if not link_info.get('is_cause_list', False) or link_info.get('confidence', 0) < 0.7:
                    self.logger.debug(f"Skipping non-cause list or low confidence: {pdf_url}")
                    continue
                
                filtered_links.append(link_info)
            
            # Download PDFs in parallel
            pdf_files = self._download_pdfs_parallel(filtered_links)
            
            # Process PDFs with Gemini in parallel and store in database
            self._process_pdfs_with_db(pdf_files, filtered_links)
            
            # Save metadata
            metadata_path = self.save_metadata(format="json")
            self.logger.info(f"Saved metadata to: {metadata_path}")
            
            return self.metadata
        
        except Exception as e:
            self.logger.error(f"Error running cause list scraper: {e}", exc_info=True)
            return []
        
        finally:
            # Close the scraper
            self.close()
            
            # Disconnect from database
            if hasattr(self, 'db') and self.db:
                self.db.disconnect()
    
    def _process_pdfs_with_db(self, pdf_files: List[str], links: List[Dict[str, Any]]) -> None:
        """
        Process PDFs with Gemini API and store in database.
        
        Args:
            pdf_files: List of paths to PDF files
            links: List of link information dictionaries
        """
        # Check if database integration is enabled
        if not self.db_enabled:
            self.logger.warning("Database integration is disabled, falling back to standard processing")
            self._process_pdfs_parallel(pdf_files)
            return
        
        # Check if Gemini API is enabled
        if not self.config.get("use_gemini_api", True):
            self.logger.info("Gemini API processing is disabled")
            return
        
        # Get configuration for parallel processing
        parallel_processing = self.config.get("parallel_processing", True)
        max_workers = self.config.get("processing_workers", 3)
        
        # Create URL to path mapping for easier lookup
        url_to_path = {}
        for pdf_path in pdf_files:
            for link in links:
                if os.path.basename(pdf_path) == os.path.basename(link["url"]):
                    url_to_path[link["url"]] = pdf_path
                    break
        
        if not parallel_processing:
            # Fall back to sequential processing
            self.logger.info("Using sequential Gemini API processing with database integration")
            for pdf_path in pdf_files:
                # Find matching URL
                pdf_url = None
                for url, path in url_to_path.items():
                    if path == pdf_path:
                        pdf_url = url
                        break
                
                self._process_pdf_with_db(pdf_path, pdf_url)
            return
        
        # Use parallel processing
        self.logger.info(f"Using parallel Gemini API processing with database integration ({max_workers} workers)")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        # Thread-safe lock for updating shared resources
        metadata_lock = threading.Lock()
        
        def process_worker(pdf_path):
            try:
                # Find matching URL
                pdf_url = None
                for url, path in url_to_path.items():
                    if path == pdf_path:
                        pdf_url = url
                        break
                
                return self._process_pdf_with_db(pdf_path, pdf_url)
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
    
    def _process_pdf_with_db(self, pdf_path: str, pdf_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process a PDF file with Gemini API and store in database.
        
        Args:
            pdf_path: Path to the PDF file
            pdf_url: URL to the PDF file
            
        Returns:
            Structured data or None if processing failed
        """
        try:
            self.logger.info(f"Processing PDF with Gemini API and storing in database: {pdf_path}")
            
            # Extract date from PDF path
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', pdf_path)
            list_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
            
            # Process PDF with data processor
            structured_data = self.data_processor.process_pdf(pdf_path, pdf_url)
            
            if structured_data:
                self.logger.info(f"Successfully processed and stored data for: {pdf_path}")
                return structured_data
            else:
                self.logger.warning(f"Failed to process PDF with data processor: {pdf_path}")
                
                # Fall back to standard processing
                self.logger.info(f"Parsing PDF with Gemini API: {pdf_path}")
                markdown_path = self._process_pdf_with_gemini(pdf_path)
                
                if markdown_path:
                    self.logger.info(f"Successfully parsed PDF with Gemini API. Attempting to process structured data.")
                    
                    # Try to read the markdown file and process it
                    try:
                        with open(markdown_path, 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                        
                        # Extract structured data from markdown
                        structured_data = self.data_processor._extract_structured_data(markdown_content)
                        
                        if structured_data:
                            # Store data in database
                            success = self.data_processor._store_data_in_db(
                                structured_data, list_date, pdf_path, pdf_url
                            )
                            
                            if success:
                                self.logger.info(f"Successfully processed and stored data for: {pdf_path}")
                                return structured_data
                    except Exception as e:
                        self.logger.error(f"Error processing markdown file: {e}")
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing PDF with database integration: {e}")
            
            # Fall back to standard processing
            self.logger.info(f"Falling back to standard processing for: {pdf_path}")
            markdown_path = self._process_pdf_with_gemini(pdf_path)
            return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Delhi High Court Cause List Scraper with Database Integration")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--config", "-c", help="Configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    parser.add_argument("--db-host", help="Database host")
    parser.add_argument("--db-port", help="Database port")
    parser.add_argument("--db-name", help="Database name")
    parser.add_argument("--db-user", help="Database user")
    parser.add_argument("--db-password", help="Database password")
    args = parser.parse_args()
    
    # Create database connector if database parameters are provided
    db_connector = None
    if args.db_host or args.db_port or args.db_name or args.db_user or args.db_password:
        db_connector = DBConnector(
            host=args.db_host,
            port=args.db_port,
            dbname=args.db_name,
            user=args.db_user,
            password=args.db_password
        )
    
    scraper = DelhiHCCauseListDBScraper(
        output_dir=args.output,
        config_file=args.config,
        db_connector=db_connector
    )
    
    if args.debug:
        import logging
        scraper.logger.setLevel(logging.DEBUG)
    
    scraper.run()
