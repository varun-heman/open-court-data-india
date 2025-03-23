"""
Court scrapers package.

This package contains scrapers for various Indian courts.
"""

# Import court-specific scrapers
from .delhi_hc import DelhiHCScraper, DelhiHCCauseListScraper

__all__ = [
    'DelhiHCScraper',
    'DelhiHCCauseListScraper'
]
