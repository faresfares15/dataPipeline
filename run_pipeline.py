#!/usr/bin/env python3
"""
Cinema Data Pipeline Runner
A simple script to run the complete data pipeline without Airflow.
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def run_complete_pipeline():
    """Run the complete cinema data pipeline."""
    
    start_time = datetime.now()
    logger.info("🎬 Starting Cinema Data Pipeline...")
    
    try:
        # Step 1: Data Extraction
        logger.info("📥 Step 1: Extracting data from IMDB and OMDB...")
        ingestion = DataIngestion()
        
        # Download IMDB datasets (using sample data for performance)
        downloaded_files = ingestion.download_imdb_datasets()
        logger.info(f"Downloaded IMDB files: {list(downloaded_files.keys())}")
        
        # Extract popular movie titles and fetch OMDB data
        if 'title_basics' in downloaded_files and 'title_ratings' in downloaded_files:
            movie_titles = ingestion.extract_popular_movie_titles(
                downloaded_files['title_basics'],
                downloaded_files['title_ratings'],
                limit=50
            )
            
            if movie_titles:
                logger.info(f"Fetching OMDB data for {len(movie_titles)} movies...")
                omdb_file = ingestion.fetch_movie_details_from_omdb(movie_titles)
                if omdb_file:
                    downloaded_files['omdb_details'] = omdb_file
        
        # Step 2: Data Formatting
        logger.info("🔧 Step 2: Formatting raw data to clean Parquet files...")
        formatter = DataFormatter()
        formatted_files = formatter.format_all_datasets(downloaded_files)
        
        # Format OMDB data if available
        if 'omdb_details' in downloaded_files and downloaded_files['omdb_details']:
            try:
                omdb_formatted = formatter.format_omdb_movie_details(downloaded_files['omdb_details'])
                if omdb_formatted:
                    formatted_files['omdb_details'] = omdb_formatted
            except Exception as e:
                logger.warning(f"Could not format OMDB data: {e}")
        
        logger.info(f"Formatted files: {list(formatted_files.keys())}")
        
        # Step 3: Data Combination and Analytics
        logger.info("⚡ Step 3: Combining data and performing analytics with Spark...")
        combiner = DataCombiner()
        
        try:
            combined_results = combiner.combine_all_data(formatted_files)
            logger.info(f"Analytics completed: {list(combined_results.keys())}")
        finally:
            combiner.stop_spark()
        
        # Step 4: Data Indexing
        logger.info("🔍 Step 4: Indexing data to Elasticsearch...")
        indexer = DataIndexer()
        indexer.index_all_analytics(combined_results)
        
        # Create sample dashboard queries
        indexer.create_sample_dashboard_queries()
        
        # Step 5: Success Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("✅ Cinema Data Pipeline completed successfully!")
        logger.info(f"⏱️  Total execution time: {duration:.2f} seconds")
        logger.info(f"📊 Results created: {list(combined_results.keys())}")
        logger.info("🎯 Data is now available in Elasticsearch for visualization in Kibana")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        return False

def main():
    """Main function to run the pipeline."""
    print("=" * 60)
    print("🎬 CINEMA DATA PIPELINE")
    print("=" * 60)
    print("This pipeline will:")
    print("1. 📥 Extract data from IMDB & OMDB APIs")
    print("2. 🔧 Format and clean the data")
    print("3. ⚡ Perform analytics with Apache Spark")
    print("4. 🔍 Index results to Elasticsearch")
    print("5. 📊 Create sample Kibana dashboard queries")
    print("=" * 60)
    
    success = run_complete_pipeline()
    
    if success:
        print("\n🎉 Pipeline completed successfully!")
        print("🚀 Your cinema analytics are ready!")
        print("💡 Access Kibana at: http://localhost:5601")
        print("📋 Check the sample queries in: data/usage/elasticsearch/sample_queries/")
    else:
        print("\n❌ Pipeline failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 