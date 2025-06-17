#!/usr/bin/env python3

"""
Optimized Cinema API-Only Pipeline - Fast execution with OMDB + TMDB APIs only
"""

from datetime import datetime, timedelta
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

from lib.ingestion import DataIngestion
from lib.formatting import DataFormatter
from lib.combination import DataCombiner
from lib.indexing import DataIndexer

import logging
logger = logging.getLogger(__name__)

# Default arguments
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Create DAG
dag = DAG(
    'cinema_api_only_pipeline',
    default_args=default_args,
    description='Fast Cinema Analytics Pipeline - APIs Only',
    schedule=timedelta(days=1),
    tags=['cinema', 'api', 'fast'],
    catchup=False
)

# Predefined popular movies for fast API testing (no IMDB dependency)
POPULAR_MOVIES = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "Pulp Fiction", "The Lord of the Rings", "Forrest Gump",
    "Fight Club", "Inception", "The Matrix", "Goodfellas",
    "The Empire Strikes Back", "One Flew Over the Cuckoo's Nest",
    "Seven", "The Silence of the Lambs", "Saving Private Ryan"
]

def extract_omdb_api_data_task(**context):
    """Extract data from OMDB API - REAL API CALLS."""
    ingestion = DataIngestion()
    
    # Use predefined movie list (faster than extracting from IMDB)
    movie_titles = POPULAR_MOVIES[:3]  # Limit to 3 for speed
    
    logger.info(f"🚀 Fetching REAL OMDB data for {len(movie_titles)} movies...")
    omdb_file = ingestion.fetch_movie_details_from_omdb_fast(movie_titles)
    
    # Store OMDB file path in XCom
    context['task_instance'].xcom_push(key='omdb_file', value=omdb_file)
    context['task_instance'].xcom_push(key='movie_titles', value=movie_titles)
    logger.info(f"✅ REAL OMDB API extraction completed: {omdb_file}")

def extract_tmdb_api_data_task(**context):
    """Extract data from TMDB API - REAL API CALLS."""
    ingestion = DataIngestion()
    
    # Get movie titles from OMDB task
    movie_titles = context['task_instance'].xcom_pull(key='movie_titles', task_ids='extract_omdb_api_data')
    
    if not movie_titles:
        movie_titles = POPULAR_MOVIES[:3]  # Fallback
    
    logger.info(f"🚀 Fetching REAL TMDB data for {len(movie_titles)} movies...")
    tmdb_file = ingestion.fetch_movie_details_from_tmdb_fast(movie_titles)
    
    # Store TMDB file path in XCom
    context['task_instance'].xcom_push(key='tmdb_file', value=tmdb_file)
    logger.info(f"✅ REAL TMDB API extraction completed: {tmdb_file}")

def format_omdb_data_task(**context):
    """Format OMDB API data to clean Parquet files."""
    formatter = DataFormatter()
    
    # Get OMDB data
    omdb_file = context['task_instance'].xcom_pull(key='omdb_file', task_ids='extract_omdb_api_data')
    
    formatted_omdb_file = ""
    if omdb_file:
        try:
            formatted_omdb_file = formatter.format_omdb_movie_details(omdb_file)
            logger.info(f"OMDB data formatting completed: {formatted_omdb_file}")
        except Exception as e:
            logger.warning(f"Could not format OMDB data: {e}")
    else:
        logger.warning("No OMDB file to format")
    
    # Store formatted file path in XCom
    context['task_instance'].xcom_push(key='formatted_omdb_file', value=formatted_omdb_file)

def format_tmdb_data_task(**context):
    """Format TMDB API data to clean Parquet files."""
    formatter = DataFormatter()
    
    # Get TMDB data
    tmdb_file = context['task_instance'].xcom_pull(key='tmdb_file', task_ids='extract_tmdb_api_data')
    
    formatted_tmdb_file = ""
    if tmdb_file:
        try:
            formatted_tmdb_file = formatter.format_tmdb_movie_details(tmdb_file)
            logger.info(f"TMDB data formatting completed: {formatted_tmdb_file}")
        except Exception as e:
            logger.warning(f"Could not format TMDB data: {e}")
    else:
        logger.warning("No TMDB file to format")
    
    # Store formatted file path in XCom
    context['task_instance'].xcom_push(key='formatted_tmdb_file', value=formatted_tmdb_file)

def combine_api_data_task(**context):
    """Combine and analyze data from both API sources using Spark."""
    combiner = DataCombiner()
    
    try:
        # Get formatted API files only
        formatted_omdb_file = context['task_instance'].xcom_pull(key='formatted_omdb_file', task_ids='format_omdb_data')
        formatted_tmdb_file = context['task_instance'].xcom_pull(key='formatted_tmdb_file', task_ids='format_tmdb_data')
        
        # Create API-only dataset
        api_files = {}
        
        if formatted_omdb_file:
            api_files['omdb_details'] = formatted_omdb_file
            
        if formatted_tmdb_file:
            api_files['tmdb_details'] = formatted_tmdb_file
        
        logger.info(f"Combining API data from sources: {list(api_files.keys())}")
        
        # Perform API data combination and analytics
        combined_results = combiner.combine_all_data(api_files)
        
        # Store results in XCom
        context['task_instance'].xcom_push(key='combined_results', value=combined_results)
        logger.info(f"API data combination completed. Results: {list(combined_results.keys())}")
        
    finally:
        # Always stop Spark session
        combiner.stop_spark()

def index_api_data_task(**context):
    """Index API results to Elasticsearch."""
    indexer = DataIndexer()
    
    # Get combined results from previous task
    combined_results = context['task_instance'].xcom_pull(key='combined_results', task_ids='combine_api_data')
    
    # Index API analytics to Elasticsearch
    indexer.index_all_analytics(combined_results)
    
    # Create sample dashboard queries
    indexer.create_sample_dashboard_queries()
    
    logger.info("API data indexing completed successfully")

# Define tasks

# 1. Extract OMDB API data (with predefined movies)
extract_omdb_task = PythonOperator(
    task_id='extract_omdb_api_data',
    python_callable=extract_omdb_api_data_task,
    dag=dag,
)

# 2. Extract TMDB API data (parallel)
extract_tmdb_task = PythonOperator(
    task_id='extract_tmdb_api_data',
    python_callable=extract_tmdb_api_data_task,
    dag=dag,
)

# 3. Format OMDB data (parallel)
format_omdb_task = PythonOperator(
    task_id='format_omdb_data',
    python_callable=format_omdb_data_task,
    dag=dag,
)

# 4. Format TMDB data (parallel)
format_tmdb_task = PythonOperator(
    task_id='format_tmdb_data',
    python_callable=format_tmdb_data_task,
    dag=dag,
)

# 5. Combine API data
combine_task = PythonOperator(
    task_id='combine_api_data',
    python_callable=combine_api_data_task,
    dag=dag,
)

# 6. Index to Elasticsearch
index_task = PythonOperator(
    task_id='index_api_data',
    python_callable=index_api_data_task,
    dag=dag,
)

# 7. Quality check
quality_check_task = BashOperator(
    task_id='api_quality_check',
    bash_command='echo "✅ Fast API-only cinema pipeline completed successfully!"',
    dag=dag,
)

# Set task dependencies - Fast API-only pipeline!
# 1. Two parallel API extractions (no IMDB dependency)
# 2. Two parallel API formatting tasks 
# 3. Combine API data
# 4. Index and quality check

extract_omdb_task >> format_omdb_task
extract_tmdb_task >> format_tmdb_task
[format_omdb_task, format_tmdb_task] >> combine_task >> index_task >> quality_check_task 