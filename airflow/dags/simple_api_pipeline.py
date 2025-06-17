#!/usr/bin/env python3
"""
Simple Cinema API Pipeline - Works perfectly in Airflow browser
Fetches real data from OMDB and TMDB APIs
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Import our libraries
from lib.ingestion import DataIngestion
from lib.formatting import DataFormatter
from lib.combination import DataCombiner
from lib.indexing import DataIndexer

import logging
logger = logging.getLogger(__name__)

# DAG configuration
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,  # No retries for demo
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'simple_api_pipeline',
    default_args=default_args,
    description='Simple Cinema API Pipeline - OMDB + TMDB',
    schedule=None,  # Manual trigger only
    catchup=False,
    max_active_runs=1,
    tags=['cinema', 'api', 'demo', 'simple']
)

def extract_api_data(**context):
    """Step 1: Extract data from both APIs"""
    logger.info("🚀 Starting API data extraction...")
    
    ingestion = DataIngestion()
    movies = ["The Shawshank Redemption", "The Godfather", "The Dark Knight"]
    
    # Get OMDB data
    logger.info("📡 Fetching OMDB data...")
    omdb_file = ingestion.fetch_movie_details_from_omdb_fast(movies)
    
    # Get TMDB data  
    logger.info("📡 Fetching TMDB data...")
    tmdb_file = ingestion.fetch_movie_details_from_tmdb_fast(movies)
    
    # Store in XCom
    context['task_instance'].xcom_push(key='omdb_file', value=omdb_file)
    context['task_instance'].xcom_push(key='tmdb_file', value=tmdb_file)
    
    logger.info(f"✅ API extraction completed!")
    logger.info(f"   OMDB: {omdb_file}")
    logger.info(f"   TMDB: {tmdb_file}")

def format_data(**context):
    """Step 2: Format the API data"""
    logger.info("🔧 Starting data formatting...")
    
    formatter = DataFormatter()
    
    # Get files from previous task
    omdb_file = context['task_instance'].xcom_pull(key='omdb_file', task_ids='extract_api_data')
    tmdb_file = context['task_instance'].xcom_pull(key='tmdb_file', task_ids='extract_api_data')
    
    formatted_files = {}
    
    # Format OMDB data
    if omdb_file:
        logger.info("📝 Formatting OMDB data...")
        formatted_omdb = formatter.format_omdb_movie_details(omdb_file)
        formatted_files['omdb_details'] = formatted_omdb
        logger.info(f"✅ OMDB formatted: {formatted_omdb}")
    
    # Format TMDB data
    if tmdb_file:
        logger.info("📝 Formatting TMDB data...")
        formatted_tmdb = formatter.format_tmdb_movie_details(tmdb_file)
        formatted_files['tmdb_details'] = formatted_tmdb
        logger.info(f"✅ TMDB formatted: {formatted_tmdb}")
    
    # Store in XCom
    context['task_instance'].xcom_push(key='formatted_files', value=formatted_files)
    logger.info(f"✅ Formatting completed for {len(formatted_files)} sources!")

def combine_and_analyze(**context):
    """Step 3: Combine data and create analytics"""
    logger.info("🔄 Starting data combination and analytics...")
    
    combiner = DataCombiner()
    
    try:
        # Get formatted files
        formatted_files = context['task_instance'].xcom_pull(key='formatted_files', task_ids='format_data')
        
        logger.info(f"📊 Combining data from: {list(formatted_files.keys())}")
        
        # Perform analytics
        results = combiner.combine_all_data(formatted_files)
        
        # Store results
        context['task_instance'].xcom_push(key='analytics_results', value=results)
        
        logger.info(f"✅ Analytics completed!")
        logger.info(f"   Results: {list(results.keys())}")
        
    finally:
        combiner.stop_spark()

def index_to_elasticsearch(**context):
    """Step 4: Index results to Elasticsearch"""
    logger.info("📊 Starting Elasticsearch indexing...")
    
    indexer = DataIndexer()
    
    # Get analytics results
    results = context['task_instance'].xcom_pull(key='analytics_results', task_ids='combine_and_analyze')
    
    if results:
        # Index to Elasticsearch
        indexer.index_all_analytics(results)
        indexer.create_sample_dashboard_queries()
        
        logger.info("✅ Elasticsearch indexing completed!")
        logger.info("🎯 Data is now available in Kibana at http://localhost:5601")
    else:
        logger.warning("⚠️ No results to index")

# Define the tasks
extract_task = PythonOperator(
    task_id='extract_api_data',
    python_callable=extract_api_data,
    dag=dag,
)

format_task = PythonOperator(
    task_id='format_data',
    python_callable=format_data,
    dag=dag,
)

analyze_task = PythonOperator(
    task_id='combine_and_analyze',
    python_callable=combine_and_analyze,
    dag=dag,
)

index_task = PythonOperator(
    task_id='index_to_elasticsearch',
    python_callable=index_to_elasticsearch,
    dag=dag,
)

success_task = BashOperator(
    task_id='pipeline_success',
    bash_command='echo "🎉 Simple API Pipeline completed successfully! Check Kibana at http://localhost:5601"',
    dag=dag,
)

# Set up the dependencies - simple linear flow
extract_task >> format_task >> analyze_task >> index_task >> success_task 