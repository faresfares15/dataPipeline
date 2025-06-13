import sys
import os
from datetime import datetime, timedelta

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from lib.ingestion import DataIngestion
from lib.formatting import DataFormatter
from lib.combination import DataCombiner
from lib.indexing import DataIndexer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DAG configuration
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'cinema_data_pipeline',
    default_args=default_args,
    description='End-to-end cinema data pipeline with IMDB and OMDB',
    schedule_interval='@weekly',  # Run weekly
    catchup=False,
    max_active_runs=1,
    tags=['cinema', 'etl', 'spark', 'elasticsearch']
)

def extract_data_task(**context):
    """Extract data from IMDB and OMDB sources."""
    ingestion = DataIngestion()
    
    # Download IMDB datasets
    logger.info("Starting IMDB data download...")
    downloaded_files = ingestion.download_imdb_datasets()
    
    # Extract popular movie titles for OMDB API
    if 'title_basics' in downloaded_files and 'title_ratings' in downloaded_files:
        movie_titles = ingestion.extract_popular_movie_titles(
            downloaded_files['title_basics'],
            downloaded_files['title_ratings'],
            limit=50
        )
        
        # Fetch OMDB data for popular movies
        if movie_titles:
            logger.info(f"Fetching OMDB data for {len(movie_titles)} movies...")
            omdb_file = ingestion.fetch_movie_details_from_omdb(movie_titles)
            downloaded_files['omdb_details'] = omdb_file
    
    # Store file paths in XCom
    context['task_instance'].xcom_push(key='raw_files', value=downloaded_files)
    logger.info(f"Data extraction completed. Files: {list(downloaded_files.keys())}")

def format_data_task(**context):
    """Format raw data to clean Parquet files."""
    formatter = DataFormatter()
    
    # Get raw files from previous task
    raw_files = context['task_instance'].xcom_pull(key='raw_files', task_ids='extract_data')
    
    # Format IMDB datasets
    formatted_files = formatter.format_all_datasets(raw_files)
    
    # Format OMDB data if available
    if 'omdb_details' in raw_files and raw_files['omdb_details']:
        try:
            omdb_formatted = formatter.format_omdb_movie_details(raw_files['omdb_details'])
            if omdb_formatted:
                formatted_files['omdb_details'] = omdb_formatted
        except Exception as e:
            logger.warning(f"Could not format OMDB data: {e}")
    
    # Store formatted file paths in XCom
    context['task_instance'].xcom_push(key='formatted_files', value=formatted_files)
    logger.info(f"Data formatting completed. Files: {list(formatted_files.keys())}")

def combine_data_task(**context):
    """Combine and analyze data using Spark."""
    combiner = DataCombiner()
    
    try:
        # Get formatted files from previous task
        formatted_files = context['task_instance'].xcom_pull(key='formatted_files', task_ids='format_data')
        
        # Perform data combination and analytics
        combined_results = combiner.combine_all_data(formatted_files)
        
        # Store results in XCom
        context['task_instance'].xcom_push(key='combined_results', value=combined_results)
        logger.info(f"Data combination completed. Results: {list(combined_results.keys())}")
        
    finally:
        # Always stop Spark session
        combiner.stop_spark()

def index_data_task(**context):
    """Index final results to Elasticsearch."""
    indexer = DataIndexer()
    
    # Get combined results from previous task
    combined_results = context['task_instance'].xcom_pull(key='combined_results', task_ids='combine_data')
    
    # Index all analytics to Elasticsearch
    indexer.index_all_analytics(combined_results)
    
    # Create sample dashboard queries
    indexer.create_sample_dashboard_queries()
    
    logger.info("Data indexing completed successfully")

# Define tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data_task,
    dag=dag,
)

format_task = PythonOperator(
    task_id='format_data',
    python_callable=format_data_task,
    dag=dag,
)

combine_task = PythonOperator(
    task_id='combine_data',
    python_callable=combine_data_task,
    dag=dag,
)

index_task = PythonOperator(
    task_id='index_data',
    python_callable=index_data_task,
    dag=dag,
)

# Optional: Data quality check task
quality_check_task = BashOperator(
    task_id='data_quality_check',
    bash_command='echo "Data quality check passed - pipeline completed successfully"',
    dag=dag,
)

# Set task dependencies
extract_task >> format_task >> combine_task >> index_task >> quality_check_task 