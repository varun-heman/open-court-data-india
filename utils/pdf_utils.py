"""
PDF utility functions for court scrapers
"""
import re
import os
import PyPDF2
from dateutil.parser import parse
from .common import extract_date_from_text
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str, max_pages: Optional[int] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract text from a PDF file
    
    Args:
        file_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (None for all)
        
    Returns:
        Tuple of (full_text, first_page_text)
    """
    try:
        # Check if file exists and is a PDF
        if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
            return None, None
                
        pdf = PyPDF2.PdfReader(file_path)
        
        if len(pdf.pages) == 0:
            return None, None
            
        # Extract text from first page
        first_page_text = pdf.pages[0].extract_text()
        
        # Extract text from all pages (or max_pages if specified)
        full_text = ""
        pages_to_extract = len(pdf.pages) if max_pages is None else min(max_pages, len(pdf.pages))
        
        for i in range(pages_to_extract):
            full_text += pdf.pages[i].extract_text() + "\n"
            
        return full_text, first_page_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None, None


def extract_date_from_pdf(file_path: str) -> Optional[str]:
    """Extract date from a PDF file"""
    try:
        full_text, first_page_text = extract_text_from_pdf(file_path, max_pages=1)
        if first_page_text:
            return extract_date_from_text(first_page_text)
        return None
    except Exception as e:
        logger.error(f"Error extracting date from PDF: {e}")
        return None


def extract_court_info_from_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extract court information from a PDF file
    
    Returns a dictionary with:
    - court_name
    - court_number
    - judge_name
    - date
    - list_type
    """
    try:
        full_text, first_page_text = extract_text_from_pdf(file_path, max_pages=1)
        if not first_page_text:
            return {"error": "Failed to extract text from PDF"}
            
        # Initialize data structure
        data = {
            'court_name': None,
            'court_number': None,
            'judge_name': None,
            'date': None,
            'list_type': None,  # e.g., "DAILY", "SUPPLEMENTARY"
        }
        
        # Extract court number
        court_no_match = re.search(r'COURT\s+NO\.?\s*(\d+)', first_page_text, re.IGNORECASE)
        if court_no_match:
            data['court_number'] = court_no_match.group(1)
        
        # Extract judge name
        judge_pattern = r"HON'BLE\s+(MR\.|MS\.|MRS\.|SHRI|SMT\.?|JUSTICE)\s+([A-Z\s\.]+)"
        judge_match = re.search(judge_pattern, first_page_text, re.IGNORECASE)
        if judge_match:
            data['judge_name'] = judge_match.group(0).strip()
        
        # Extract date
        data['date'] = extract_date_from_text(first_page_text)
        
        # Extract list type
        list_types = ["DAILY CAUSE LIST", "SUPPLEMENTARY CAUSE LIST", "ADVANCE CAUSE LIST"]
        for list_type in list_types:
            if list_type in first_page_text.upper():
                data['list_type'] = list_type
                break
        
        # Extract court name (Delhi High Court)
        if "DELHI HIGH COURT" in first_page_text.upper():
            data['court_name'] = "Delhi High Court"
        
        return data
    except Exception as e:
        logger.error(f"Error extracting court info from PDF: {e}")
        return {"error": "Failed to extract court info from PDF"}


def extract_cases_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract case information from a PDF file
    
    Returns a list of case dictionaries, each containing:
    - case_number
    - parties (if available)
    - raw_text
    """
    try:
        full_text, _ = extract_text_from_pdf(file_path)
        if not full_text:
            return [{"error": "Failed to extract text from PDF"}]
            
        cases = []
        
        # Common patterns for case numbers in Indian courts
        case_patterns = [
            r'([A-Z]+\s*\d+/\d+)',  # e.g., CRL A 123/2023
            r'(W\.?P\.?\s*\(C\)\s*\d+/\d+)',  # e.g., W.P.(C) 123/2023
            r'(C\.?M\.?\s*\d+/\d+)',  # e.g., C.M. 123/2023
            r'(CRL\.?M\.?C\.?\s*\d+/\d+)'  # e.g., CRL.M.C. 123/2023
        ]
        
        # Extract cases using patterns
        for pattern in case_patterns:
            case_matches = re.finditer(pattern, full_text)
            for match in case_matches:
                case_number = match.group(1)
                
                # Try to extract parties (usually follows the case number)
                # This is challenging due to varying formats
                start_pos = match.end()
                end_pos = full_text.find('\n', start_pos)
                if end_pos == -1:
                    end_pos = min(start_pos + 100, len(full_text))
                
                line = full_text[start_pos:end_pos].strip()
                
                # Look for "versus" or "vs" to separate parties
                parties = None
                if " VS " in line.upper():
                    parties = line.split(" VS ", 1)
                elif " V/S " in line.upper():
                    parties = line.split(" V/S ", 1)
                elif " VERSUS " in line.upper():
                    parties = line.split(" VERSUS ", 1)
                
                case_data = {
                    'case_number': case_number,
                    'parties': parties if parties else line,
                    'raw_text': line
                }
                
                # Add to cases if not already present
                if not any(c['case_number'] == case_number for c in cases):
                    cases.append(case_data)
        
        return cases
    except Exception as e:
        logger.error(f"Error extracting cases from PDF: {e}")
        return [{"error": "Failed to extract cases from PDF"}]


def parse_pdf_for_structured_data(file_path: str) -> Dict[str, Any]:
    """
    Parse a PDF file to extract structured data from cause lists
    Returns a dictionary with extracted data
    """
    try:
        # Get court info
        court_info = extract_court_info_from_pdf(file_path)
        if not court_info or "error" in court_info:
            return {"error": "Failed to extract court info from PDF"}
            
        # Get cases
        cases = extract_cases_from_pdf(file_path)
        
        # Combine data
        data = court_info.copy()
        data['cases'] = cases
        
        return data
    except Exception as e:
        logger.error(f"Error parsing PDF for structured data: {e}")
        return {"error": "Failed to parse PDF for structured data"}
