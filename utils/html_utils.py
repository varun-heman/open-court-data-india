"""
HTML utilities for court scrapers.

This module provides utility functions for handling HTML content in court scrapers.
"""
import re
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .common import extract_date_from_text


logger = logging.getLogger(__name__)


def extract_text_from_html(html_content: Union[str, BeautifulSoup]) -> str:
    """
    Extract text from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
    
    Returns:
        Extracted text
    """
    if isinstance(html_content, str):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return ""
    else:
        soup = html_content
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_date_from_html(html_content: Union[str, BeautifulSoup]) -> Optional[str]:
    """
    Extract date from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
    
    Returns:
        Extracted date in YYYY-MM-DD format or None if no date found
    """
    text = extract_text_from_html(html_content)
    return extract_date_from_text(text)


def extract_links_from_html(html_content: Union[str, BeautifulSoup], base_url: str) -> List[Dict[str, str]]:
    """
    Extract links from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
        base_url: Base URL for resolving relative links
    
    Returns:
        List of dictionaries containing link information
    """
    if isinstance(html_content, str):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
    else:
        soup = html_content
    
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        text = a_tag.get_text(strip=True)
        title = a_tag.get('title', '')
        
        # Skip empty or javascript links
        if not href or href.startswith(('javascript:', '#')):
            continue
        
        # Resolve relative URLs
        full_url = urljoin(base_url, href)
        
        links.append({
            'url': full_url,
            'text': text,
            'title': title
        })
    
    return links


def is_navigation_page(html_content: Union[str, BeautifulSoup], min_links_threshold: int = 10) -> bool:
    """
    Determine if a page is a navigation page.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
        min_links_threshold: Minimum number of links to consider a page as navigation
    
    Returns:
        True if the page is a navigation page, False otherwise
    """
    if isinstance(html_content, str):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return False
    else:
        soup = html_content
    
    # Count links
    links = soup.find_all('a', href=True)
    
    # Filter out javascript and empty links
    valid_links = [link for link in links if link['href'] and not link['href'].startswith(('javascript:', '#'))]
    
    # Check if the page has many links
    if len(valid_links) >= min_links_threshold:
        return True
    
    # Check for pagination elements
    pagination_elements = soup.find_all(['div', 'ul', 'nav'], class_=lambda c: c and any(x in c.lower() for x in ['paging', 'pagination', 'pages', 'page-nav']))
    if pagination_elements:
        return True
    
    # Check for table of contents
    toc_elements = soup.find_all(['div', 'ul'], class_=lambda c: c and any(x in c.lower() for x in ['toc', 'contents', 'index', 'sitemap']))
    if toc_elements:
        return True
    
    return False


def extract_pdf_links_from_html(html_content: Union[str, BeautifulSoup], base_url: str) -> List[Dict[str, str]]:
    """
    Extract PDF links from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
        base_url: Base URL for resolving relative links
    
    Returns:
        List of dictionaries containing PDF link information
    """
    if isinstance(html_content, str):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
    else:
        soup = html_content
    
    pdf_links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        text = a_tag.get_text(strip=True)
        
        # Skip empty or javascript links
        if not href or href.startswith(('javascript:', '#')):
            continue
        
        # Check if it's a PDF link
        if href.lower().endswith('.pdf') or 'pdf' in href.lower():
            # Resolve relative URLs
            full_url = urljoin(base_url, href)
            
            pdf_links.append({
                'url': full_url,
                'text': text
            })
    
    return pdf_links


def extract_table_data_from_html(html_content: Union[str, BeautifulSoup]) -> List[List[str]]:
    """
    Extract table data from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
    
    Returns:
        List of lists containing table data
    """
    if isinstance(html_content, str):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
    else:
        soup = html_content
    
    tables_data = []
    
    for table in soup.find_all('table'):
        table_data = []
        
        # Extract headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
            table_data.append(headers)
        
        # Extract rows
        for tr in table.find_all('tr'):
            row_data = []
            for td in tr.find_all(['td', 'th']):
                row_data.append(td.get_text(strip=True))
            
            if row_data:  # Skip empty rows
                table_data.append(row_data)
        
        if table_data:  # Skip empty tables
            tables_data.append(table_data)
    
    return tables_data


def is_cause_list_page(html_content: Union[str, BeautifulSoup]) -> Tuple[bool, float]:
    """
    Determine if a page is a cause list page with a confidence score.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
    
    Returns:
        Tuple of (is_cause_list, confidence_score)
    """
    if isinstance(html_content, str):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return False, 0.0
    else:
        soup = html_content
    
    text = extract_text_from_html(soup)
    
    # Initialize confidence score
    confidence = 0.0
    
    # Check for cause list indicators in text
    cause_list_indicators = [
        (r"(?:DAILY|WEEKLY|MONTHLY)?\s*CAUSE\s*LIST", 0.4),
        (r"LIST\s*OF\s*CASES", 0.3),
        (r"(?:COURT|BOARD)\s*(?:NO\.?|NUMBER)\s*\d+", 0.2),
        (r"BEFORE\s+(?:HON'BLE|THE\s+HON'BLE)", 0.2),
        (r"(?:MATTERS|CASES)\s+(?:LISTED|FIXED)\s+FOR", 0.3),
        (r"(?:HEARING|ARGUMENTS|ORDERS|JUDGMENT)", 0.1),
        (r"DATED\s*:?\s*\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}", 0.2)
    ]
    
    # Check for non-cause list indicators
    non_cause_list_indicators = [
        (r"JUDGMENT", 0.3),  # Judgment is a strong indicator it's not a cause list
        (r"ORDER\s+SHEET", 0.3),
        (r"CERTIFIED\s+(?:TO\s+BE\s+)?TRUE\s+COPY", 0.4)
    ]
    
    # Calculate confidence based on indicators
    for pattern, weight in cause_list_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            confidence += weight
    
    for pattern, weight in non_cause_list_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            confidence -= weight
    
    # Check for tabular structure (common in cause lists)
    tables = soup.find_all('table')
    if tables:
        confidence += 0.2
    
    # Check for PDF links with "cause list" in text or href
    pdf_links = soup.find_all('a', href=lambda href: href and ('.pdf' in href.lower() or 'pdf' in href.lower()))
    for link in pdf_links:
        link_text = link.get_text(strip=True).lower()
        if 'cause' in link_text and 'list' in link_text:
            confidence += 0.3
            break
    
    # Normalize confidence to 0-1 range
    confidence = max(0.0, min(1.0, confidence))
    
    return confidence >= 0.6, confidence
