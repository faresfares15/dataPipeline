#!/usr/bin/env python3
"""
Test script to verify the pipeline works with existing formatted data.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from lib.combination import DataCombiner
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Test the pipeline with existing formatted data."""
    
    # Simulate formatted files that exist
    formatted_files = {
        'title_basics': 'data/formatted/imdb/title_basics/20250613/title_basics.parquet',
        'title_ratings': 'data/formatted/imdb/title_ratings/20250613/title_ratings.parquet'
    }
    
    # Check if files exist
    for key, path in formatted_files.items():
        if not os.path.exists(path):
            logger.error(f"File not found: {path}")
            return False
    
    logger.info("Testing data combination with existing formatted files...")
    
    combiner = DataCombiner()
    
    try:
        # Test data combination
        combined_results = combiner.combine_all_data(formatted_files)
        
        logger.info(f"Pipeline test completed successfully!")
        logger.info(f"Results: {list(combined_results.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        return False
        
    finally:
        # Always stop Spark session
        combiner.stop_spark()

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1) 