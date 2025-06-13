#!/usr/bin/env python3
"""
Script to regenerate formatted data from sample files.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from lib.formatting import DataFormatter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def regenerate_formatted_data():
    """Regenerate formatted data from sample files."""
    
    # Use the sample files we created
    raw_files = {
        'title_basics': 'data/raw/imdb/title_basics/20250612/title_basics_sample.tsv',
        'title_ratings': 'data/raw/imdb/title_ratings/20250612/title_ratings_sample.tsv'
    }
    
    # Check if files exist
    for key, path in raw_files.items():
        if not os.path.exists(path):
            logger.error(f"Sample file not found: {path}")
            return False
    
    logger.info("Regenerating formatted data from sample files...")
    
    formatter = DataFormatter()
    
    try:
        # Format the data
        formatted_files = formatter.format_all_datasets(raw_files)
        
        logger.info(f"Data formatting completed successfully!")
        logger.info(f"Formatted files: {list(formatted_files.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Data formatting failed: {e}")
        return False

if __name__ == "__main__":
    success = regenerate_formatted_data()
    sys.exit(0 if success else 1) 