"""
Delhi High Court Cause List Scraper

This module provides a specialized scraper for Delhi High Court cause lists.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..delhi_hc_scraper import DelhiHCScraper


class DelhiHCCauseListScraper(DelhiHCScraper):
    """
    Specialized scraper for Delhi High Court cause lists.
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize the Delhi High Court cause list scraper.
        
        Args:
            output_dir: Directory for downloaded files
            config_file: Path to configuration file
        """
        super().__init__(output_dir=output_dir, config_file=config_file)
        
        # Override the output directory to include 'cause_lists'
        self.cause_lists_dir = os.path.join(self.court_dir, 'cause_lists')
        os.makedirs(self.cause_lists_dir, exist_ok=True)
        
        # Update the court_dir to point to the cause_lists directory
        self.court_dir = self.cause_lists_dir
        
        self.logger.info(f"Cause list output directory: {self.court_dir}")
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run the cause list scraper.
        
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
                
                # Skip if not a cause list with high confidence
                if not link_info.get('is_cause_list', False) or link_info.get('confidence', 0) < 0.7:
                    self.logger.debug(f"Skipping non-cause list or low confidence: {pdf_url}")
                    continue
                
                self.processed_urls.add(pdf_url)
                self._process_pdf(pdf_url, link_info)
            
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


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Delhi High Court Cause List Scraper")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--config", "-c", help="Configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    scraper = DelhiHCCauseListScraper(
        output_dir=args.output,
        config_file=args.config
    )
    
    if args.debug:
        import logging
        scraper.logger.setLevel(logging.DEBUG)
    
    scraper.run()
