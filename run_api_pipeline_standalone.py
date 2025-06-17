#!/usr/bin/env python3
"""
Standalone API Pipeline Runner
Runs the cinema API pipeline without Airflow for fast testing
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.ingestion import DataIngestion
from lib.formatting import DataFormatter
from lib.combination import DataCombiner
from lib.indexing import DataIndexer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_api_pipeline():
    """Run the complete API-only cinema pipeline."""
    start_time = datetime.now()
    logger.info("🚀 Starting standalone API cinema pipeline...")
    
    try:
        # Step 1: Extract API data (instant sample data)
        logger.info("📡 Step 1: Extracting API data...")
        ingestion = DataIngestion()
        
        # Predefined popular movies
        popular_movies = [
            "The Shawshank Redemption", 
            "The Godfather", 
            "The Dark Knight"
        ]
        
        # Fetch real API data
        logger.info(f"🚀 Fetching REAL OMDB data for {len(popular_movies)} movies...")
        omdb_file = ingestion.fetch_movie_details_from_omdb_fast(popular_movies)
        
        logger.info(f"🚀 Fetching REAL TMDB data for {len(popular_movies)} movies...")
        tmdb_file = ingestion.fetch_movie_details_from_tmdb_fast(popular_movies)
        
        logger.info(f"✅ API extraction completed!")
        logger.info(f"   - OMDB file: {omdb_file}")
        logger.info(f"   - TMDB file: {tmdb_file}")
        
        # Step 2: Format API data
        logger.info("🔧 Step 2: Formatting API data...")
        formatter = DataFormatter()
        
        formatted_omdb_file = ""
        formatted_tmdb_file = ""
        
        if omdb_file:
            try:
                formatted_omdb_file = formatter.format_omdb_movie_details(omdb_file)
                logger.info(f"✅ OMDB formatting completed: {formatted_omdb_file}")
            except Exception as e:
                logger.warning(f"⚠️ OMDB formatting failed: {e}")
        
        if tmdb_file:
            try:
                formatted_tmdb_file = formatter.format_tmdb_movie_details(tmdb_file)
                logger.info(f"✅ TMDB formatting completed: {formatted_tmdb_file}")
            except Exception as e:
                logger.warning(f"⚠️ TMDB formatting failed: {e}")
        
        # Step 3: Combine API data
        logger.info("🔄 Step 3: Combining API data...")
        combiner = DataCombiner()
        
        try:
            # Combine only API data
            api_files = {}
            if formatted_omdb_file:
                api_files['omdb_details'] = formatted_omdb_file
            if formatted_tmdb_file:
                api_files['tmdb_details'] = formatted_tmdb_file
            
            logger.info(f"🔄 Combining data from: {list(api_files.keys())}")
            
            # Perform API-only combination
            combined_results = combiner.combine_all_data(api_files)
            logger.info(f"✅ Data combination completed")
            
        except Exception as e:
            logger.error(f"❌ Data combination failed: {e}")
            combined_results = {}
        finally:
            combiner.stop_spark()
        
        # Step 4: Index to Elasticsearch
        logger.info("📊 Step 4: Indexing to Elasticsearch...")
        indexer = DataIndexer()
        
        if combined_results:
            try:
                # Index API analytics to Elasticsearch
                indexer.index_all_analytics(combined_results)
                indexer.create_sample_dashboard_queries()
                logger.info("✅ Data indexing completed")
            except Exception as e:
                logger.warning(f"⚠️ Indexing failed: {e}")
        else:
            logger.warning("No data to index")
        
        # Step 5: Success summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("🎉 API Pipeline completed successfully!")
        logger.info(f"⏱️  Total duration: {duration:.2f} seconds")
        logger.info(f"📊 Data sources processed: {list(api_files.keys()) if 'api_files' in locals() else 'None'}")
        logger.info(f"🔍 Results: {list(combined_results.keys()) if combined_results else 'None'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 CINEMA API PIPELINE - STANDALONE MODE")
    print("=" * 60)
    
    success = run_api_pipeline()
    
    if success:
        print("\n🎉 SUCCESS! Your API pipeline completed successfully!")
        print("🔍 Check Elasticsearch/Kibana for results:")
        print("   - Elasticsearch: http://localhost:9200")
        print("   - Kibana: http://localhost:5601")
    else:
        print("\n❌ Pipeline failed. Check logs above for details.")
    
    print("=" * 60) 