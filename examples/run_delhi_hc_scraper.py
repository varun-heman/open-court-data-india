"""
Example script to run the Delhi High Court scrapers.

This script demonstrates how to use the Delhi High Court scrapers.
"""
import os
import argparse
import logging
from datetime import datetime

from scrapers import DelhiHCScraper, DelhiHCCauseListScraper


def setup_logging(debug=False):
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"delhi_hc_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )


def main():
    """Run the Delhi High Court scrapers."""
    parser = argparse.ArgumentParser(description="Run Delhi High Court scrapers")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--config", "-c", help="Configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    parser.add_argument("--type", "-t", choices=["all", "base", "cause_list"], default="all",
                        help="Type of scraper to run")
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    
    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        # Use the project root's data directory by default
        project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        output_dir = os.path.join(project_root, "data")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Using output directory: {output_dir}")
    
    # Run the appropriate scraper(s)
    if args.type in ["all", "base"]:
        print("Running Delhi High Court base scraper...")
        base_scraper = DelhiHCScraper(
            output_dir=output_dir,
            config_file=args.config
        )
        base_scraper.run()
    
    if args.type in ["all", "cause_list"]:
        print("Running Delhi High Court cause list scraper...")
        cause_list_scraper = DelhiHCCauseListScraper(
            output_dir=output_dir,
            config_file=args.config
        )
        cause_list_scraper.run()
    
    print("Done!")


if __name__ == "__main__":
    main()
