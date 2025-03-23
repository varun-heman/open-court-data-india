"""
Data processor for structuring court data using Gemini API.

This module provides functions to process court data using the Gemini API
and store it in a structured format in the database.
"""

import os
import json
import uuid
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
from .gemini_utils import setup_gemini_api, parse_pdf_with_gemini
from db.connector import DBConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CauseListProcessor:
    """
    Process cause list data using Gemini API and store in database.
    """
    
    def __init__(
        self,
        db_connector: Optional[DBConnector] = None,
        court_code: str = "delhi_hc"
    ):
        """
        Initialize the cause list processor.
        
        Args:
            db_connector: Database connector
            court_code: Court code
        """
        # Initialize database connector
        self.db = db_connector or DBConnector()
        
        # Set court code
        self.court_code = court_code
        
        # Get court ID
        self.court_id = self.db.get_court_id(court_code)
        if not self.court_id:
            logger.error(f"Court not found: {court_code}")
            raise ValueError(f"Court not found: {court_code}")
        
        # Initialize Gemini API
        if not setup_gemini_api():
            logger.error("Failed to set up Gemini API")
            raise RuntimeError("Failed to set up Gemini API")
        
        logger.info(f"Initialized cause list processor for court: {court_code}")
    
    def process_pdf(self, pdf_path: str, pdf_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process a PDF file and store structured data in the database.
        
        Args:
            pdf_path: Path to PDF file
            pdf_url: URL to PDF file
            
        Returns:
            Structured data or None if processing failed
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Extract date from PDF path
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', pdf_path)
            list_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
            
            # Parse PDF with Gemini to get structured markdown
            markdown_content = parse_pdf_with_gemini(pdf_path)
            
            if not markdown_content:
                logger.warning(f"Failed to parse PDF with Gemini: {pdf_path}")
                return None
            
            # Extract structured data from markdown
            structured_data = self._extract_structured_data(markdown_content)
            
            if not structured_data:
                logger.warning(f"Failed to extract structured data: {pdf_path}")
                return None
            
            # Log structured data summary for debugging
            court_no = structured_data.get("courtNo", "UNKNOWN")
            bench = structured_data.get("bench", "UNKNOWN")
            cases_count = len(structured_data.get("cases", []))
            logger.info(f"Extracted data for {court_no}: {bench} with {cases_count} cases")
            
            if cases_count == 0:
                logger.warning(f"No cases found in structured data for {pdf_path}")
                # Log the first 500 characters of the markdown content for debugging
                logger.debug(f"Markdown content preview: {markdown_content[:500]}...")
            
            # Store data in database
            success = self._store_data_in_db(structured_data, list_date, pdf_path, pdf_url)
            
            if not success:
                logger.warning(f"Failed to store data in database: {pdf_path}")
                return structured_data
            
            logger.info(f"Successfully processed and stored data for: {pdf_path}")
            return structured_data
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _extract_structured_data(self, markdown_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from markdown using Gemini API.
        
        Args:
            markdown_content: Markdown content
            
        Returns:
            Structured data or None if extraction failed
        """
        try:
            # Use Gemini to extract structured data
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Analyze this court cause list markdown and extract structured data in JSON format.
            
            The JSON should have the following structure:
            {{
              "court": "DELHI HIGH COURT",
              "courtNo": "COURT NO. X",
              "bench": "BENCH - JUDGE NAMES",
              "cases": [
                {{
                  "caseNumber": "Case number exactly as formatted",
                  "title": "Case title with parties",
                  "tags": ["tag1", "tag2"],
                  "itemNumber": "Item number",
                  "fileNumber": "File number if available",
                  "causeList": "Type of cause list (e.g., Daily List)",
                  "petitionerAdv": "Petitioner advocate",
                  "respondentAdv": "Respondent advocate"
                }}
              ]
            }}
            
            IMPORTANT GUIDELINES:
            1. Extract ALL cases listed in the document, even if they're in different sections
            2. Look for patterns like "ITEM NO.", "CASE NO.", or numbered lists that indicate cases
            3. Look for case numbers which typically follow patterns like "W.P.(C)", "ITA", "FAO", "RFA", etc.
            4. Each numbered item in the markdown typically represents a case
            5. Preserve exact formatting of case numbers
            6. Include ALL parties in the title field (typically shown as "X Vs. Y")
            7. Extract tags from context (e.g., "Daily list", "Constitutional", "Tax matter")
            8. Include advocate names with their roles if available
            9. If any field is not available, use null or empty string
            10. Make sure the JSON is valid and properly formatted
            11. If no cases are found, return an empty array for "cases" but still include court information
            12. Pay special attention to sections that might contain case listings, even if they're not clearly formatted
            
            Return ONLY the JSON data without any explanations, markdown formatting, or code blocks.
            
            Here's the markdown content:
            {markdown_content}
            """
            
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            try:
                # Clean the response text to ensure it's valid JSON
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Log the first 500 characters of the response for debugging
                logger.debug(f"JSON response preview: {response_text[:500]}...")
                
                structured_data = json.loads(response_text)
                
                # Handle case where Gemini returns a list instead of a dictionary
                if isinstance(structured_data, list) and len(structured_data) > 0:
                    logger.warning(f"Gemini returned a list instead of a dictionary, using first item")
                    structured_data = structured_data[0]
                    
                    # If still not a dictionary, try to create a proper structure
                    if not isinstance(structured_data, dict):
                        logger.warning(f"Converting non-dictionary data to proper format")
                        structured_data = {
                            "court": "DELHI HIGH COURT",
                            "courtNo": "UNKNOWN",
                            "bench": "UNKNOWN",
                            "cases": []
                        }
                
                # Ensure the structured data has the required fields
                if "court" not in structured_data:
                    structured_data["court"] = "DELHI HIGH COURT"
                if "courtNo" not in structured_data:
                    # Try to extract court number from markdown
                    court_match = re.search(r'COURT NO\.\s*(\d+)', markdown_content, re.IGNORECASE)
                    structured_data["courtNo"] = f"COURT NO. {court_match.group(1)}" if court_match else "UNKNOWN"
                if "bench" not in structured_data:
                    # Try to extract bench information from markdown
                    bench_match = re.search(r'(HON\'BLE.*?)(?=\n\n|\Z)', markdown_content, re.DOTALL)
                    structured_data["bench"] = bench_match.group(1).strip() if bench_match else "UNKNOWN"
                if "cases" not in structured_data:
                    structured_data["cases"] = []
                
                # If no cases were extracted but we have numbered items in the markdown, try to extract them manually
                if len(structured_data["cases"]) == 0:
                    logger.warning("No cases found in structured data, attempting manual extraction")
                    # Look for numbered items that might be cases
                    case_matches = re.finditer(r'(\d+)\.\s+\*\*([^*]+)\*\*\s*\n\s*\*\s*([^\n]+)', markdown_content)
                    for match in case_matches:
                        item_number = match.group(1)
                        case_number = match.group(2).strip()
                        title_line = match.group(3).strip()
                        
                        # Extract parties if available (typically in the format "X Vs. Y")
                        parties = title_line.split("Vs.") if "Vs." in title_line else [title_line, ""]
                        petitioner = parties[0].strip() if len(parties) > 0 else ""
                        respondent = parties[1].strip() if len(parties) > 1 else ""
                        
                        # Create a case entry
                        case = {
                            "caseNumber": case_number,
                            "title": title_line,
                            "itemNumber": item_number,
                            "tags": [],
                            "causeList": "Daily List",
                            "petitionerAdv": "",
                            "respondentAdv": "",
                            "fileNumber": ""
                        }
                        structured_data["cases"].append(case)
                    
                    logger.info(f"Manually extracted {len(structured_data['cases'])} cases")
                
                return structured_data
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.debug(f"Response text: {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _store_data_in_db(
            self,
            data: Dict[str, Any],
            list_date: str,
            pdf_path: Optional[str] = None,
            pdf_url: Optional[str] = None
        ) -> bool:
        """
        Store structured data in the database.
        
        Args:
            data: Structured data
            list_date: List date
            pdf_path: Path to PDF file
            pdf_url: URL to PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Basic validation
            if not isinstance(data, dict):
                logger.error(f"Invalid data format: {type(data)}")
                return False
            
            if "courtNo" not in data or "bench" not in data:
                logger.error(f"Missing required fields in data: {data.keys()}")
                return False
            
            # Get bench information
            court_no = data.get("courtNo", "UNKNOWN")
            bench_name = data.get("bench", "UNKNOWN")
            
            logger.info(f"Processing data for bench: {court_no}, judges: {bench_name}")
            
            # Create bench if it doesn't exist
            bench_id = self.db.get_bench_id(self.court_id, court_no, bench_name)
            if not bench_id:
                bench_id = self.db.create_bench(self.court_id, court_no, bench_name)
                if not bench_id:
                    logger.error(f"Failed to create bench: {court_no}, {bench_name}")
                    return False
            
            # Create cause list
            cause_list_id = self.db.create_cause_list(
                self.court_id,
                bench_id,
                list_date,
                "Daily List",
                pdf_url,
                pdf_path
            )
            
            if not cause_list_id:
                logger.error(f"Failed to create cause list for bench: {court_no}")
                return False
            
            # Process cases
            cases = data.get("cases", [])
            logger.info(f"Found {len(cases)} cases for bench {court_no}")
            
            # Debug: Print a sample case if available
            if len(cases) > 0:
                logger.debug(f"Sample case data: {json.dumps(cases[0], indent=2)}")
            
            successful_cases = 0
            for case in cases:
                try:
                    # Extract case information
                    case_number = case.get("caseNumber")
                    if not case_number:
                        logger.warning(f"Missing case number in case data: {case}")
                        continue
                    
                    # Create case
                    case_id = self.db.create_case(
                        cause_list_id,
                        case_number,
                        case.get("title"),
                        case.get("itemNumber"),
                        case.get("fileNumber"),
                        case.get("petitionerAdv"),
                        case.get("respondentAdv"),
                        case.get("tags", [])
                    )
                    
                    if case_id:
                        successful_cases += 1
                    else:
                        logger.warning(f"Failed to create case: {case_number}")
                        
                except Exception as e:
                    logger.error(f"Error processing case: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            logger.info(f"Successfully stored {successful_cases} out of {len(cases)} cases for bench: {court_no}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing data in database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            List of structured data for successfully processed PDFs
        """
        try:
            logger.info(f"Processing directory: {directory_path}")
            
            # Get all PDF files in the directory
            pdf_files = []
            for file in os.listdir(directory_path):
                if file.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(directory_path, file))
            
            if not pdf_files:
                logger.warning(f"No PDF files found in {directory_path}")
                return []
            
            logger.info(f"Found {len(pdf_files)} PDF files")
            
            # Process each PDF file
            results = []
            for pdf_path in pdf_files:
                result = self.process_pdf(pdf_path)
                if result:
                    results.append(result)
            
            logger.info(f"Successfully processed {len(results)} out of {len(pdf_files)} PDF files")
            return results
            
        except Exception as e:
            logger.error(f"Error processing directory: {e}")
            return []

if __name__ == "__main__":
    import argparse
    import os
    from datetime import datetime
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Process court data using Gemini API')
    parser.add_argument('--court', type=str, default='delhi_hc', help='Court code')
    parser.add_argument('--date', type=str, help='Date to process (YYYY-MM-DD)')
    parser.add_argument('--directory', type=str, help='Directory to process')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    try:
        # Initialize processor
        processor = CauseListProcessor(court_code=args.court)
        
        # Determine directory to process
        if args.directory:
            directory_path = args.directory
        elif args.date:
            directory_path = os.path.join('data', args.court, 'cause_lists', args.date)
        else:
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            directory_path = os.path.join('data', args.court, 'cause_lists', today)
        
        # Check if directory exists
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            exit(1)
        
        logger.info(f"Processing directory: {directory_path}")
        
        # Process directory
        results = processor.process_directory(directory_path)
        
        # Print summary
        logger.info(f"Processed {len(results)} files successfully")
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        exit(1)
