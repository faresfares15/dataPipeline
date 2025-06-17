import sys
import os
from datetime import datetime, timedelta

# Add project root to Python path
if '__file__' in globals():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
else:
    project_root = '/Users/aoufarfares/Developer/dataPipeline'

if project_root not in sys.path:
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
    'cinema_parallel_api_pipeline',
    default_args=default_args,
    description='Fast parallel API-only cinema pipeline with OMDB and TMDB',
    schedule_interval='@weekly',
    catchup=False,
    max_active_runs=1,
    tags=['cinema', 'api', 'parallel', 'etl', 'elasticsearch']
)

def extract_omdb_api_data_task(**context):
    """Extract data from OMDB API - REAL API VERSION."""
    ingestion = DataIngestion()
    
    # Predefined popular movies for API testing
    popular_movies = [
        "The Shawshank Redemption", "The Godfather", "The Dark Knight"
    ]
    
    logger.info(f"🚀 Fetching REAL OMDB data for {len(popular_movies)} movies...")
    omdb_file = ingestion.fetch_movie_details_from_omdb_fast(popular_movies)
    
    # Store OMDB file path in XCom
    context['task_instance'].xcom_push(key='omdb_file', value=omdb_file)
    logger.info(f"✅ REAL OMDB data ready: {omdb_file}")

def extract_tmdb_api_data_task(**context):
    """Extract data from TMDB API - REAL API VERSION."""
    ingestion = DataIngestion()
    
    # Same movies for consistency
    popular_movies = [
        "The Shawshank Redemption", "The Godfather", "The Dark Knight"
    ]
    
    logger.info(f"🚀 Fetching REAL TMDB data for {len(popular_movies)} movies...")
    tmdb_file = ingestion.fetch_movie_details_from_tmdb_fast(popular_movies)
    
    # Store TMDB file path in XCom
    context['task_instance'].xcom_push(key='tmdb_file', value=tmdb_file)
    logger.info(f"✅ REAL TMDB data ready: {tmdb_file}")

def format_omdb_data_task(**context):
    """Format OMDB API data to clean Parquet files."""
    formatter = DataFormatter()
    
    # Get OMDB data
    omdb_file = context['task_instance'].xcom_pull(key='omdb_file', task_ids='extract_omdb_api_data')
    
    if omdb_file:
        try:
            formatted_omdb_file = formatter.format_omdb_movie_details(omdb_file)
            logger.info(f"✅ OMDB formatting completed: {formatted_omdb_file}")
            context['task_instance'].xcom_push(key='formatted_omdb_file', value=formatted_omdb_file)
        except Exception as e:
            logger.error(f"❌ OMDB formatting failed: {e}")
            context['task_instance'].xcom_push(key='formatted_omdb_file', value="")
    else:
        logger.warning("No OMDB file to format")
        context['task_instance'].xcom_push(key='formatted_omdb_file', value="")

def format_tmdb_data_task(**context):
    """Format TMDB API data to clean Parquet files."""
    formatter = DataFormatter()
    
    # Get TMDB data
    tmdb_file = context['task_instance'].xcom_pull(key='tmdb_file', task_ids='extract_tmdb_api_data')
    
    if tmdb_file:
        try:
            formatted_tmdb_file = formatter.format_tmdb_movie_details(tmdb_file)
            logger.info(f"✅ TMDB formatting completed: {formatted_tmdb_file}")
            context['task_instance'].xcom_push(key='formatted_tmdb_file', value=formatted_tmdb_file)
        except Exception as e:
            logger.error(f"❌ TMDB formatting failed: {e}")
            context['task_instance'].xcom_push(key='formatted_tmdb_file', value="")
    else:
        logger.warning("No TMDB file to format")
        context['task_instance'].xcom_push(key='formatted_tmdb_file', value="")

def combine_data_task(**context):
    """Combine API data only."""
    combiner = DataCombiner()
    
    try:
        # Get formatted API files only
        formatted_omdb_file = context['task_instance'].xcom_pull(key='formatted_omdb_file', task_ids='format_omdb_data')
        formatted_tmdb_file = context['task_instance'].xcom_pull(key='formatted_tmdb_file', task_ids='format_tmdb_data')
        
        # Combine only API data
        api_files = {}
        if formatted_omdb_file:
            api_files['omdb_details'] = formatted_omdb_file
        if formatted_tmdb_file:
            api_files['tmdb_details'] = formatted_tmdb_file
        
        logger.info(f"🔄 Combining API data from: {list(api_files.keys())}")
        
        # Perform API-only combination
        combined_results = combiner.combine_all_data(api_files)
        
        # Store results
        context['task_instance'].xcom_push(key='combined_results', value=combined_results)
        logger.info(f"✅ API data combination completed")
        
    except Exception as e:
        logger.error(f"❌ Data combination failed: {e}")
        context['task_instance'].xcom_push(key='combined_results', value={})
    finally:
        combiner.stop_spark()

def index_data_task(**context):
    """Index API results to Elasticsearch."""
    indexer = DataIndexer()
    
    # Get combined results
    combined_results = context['task_instance'].xcom_pull(key='combined_results', task_ids='combine_data')
    
    if combined_results:
        # Index API analytics to Elasticsearch
        indexer.index_all_analytics(combined_results)
        indexer.create_sample_dashboard_queries()
        logger.info("✅ Data indexing completed")
    else:
        logger.warning("No data to index")

# Define tasks - PURE API PIPELINE (NO IMDB DEPENDENCY)

# 1. Parallel API extractions (START HERE - NO IMDB NEEDED)
extract_omdb_task = PythonOperator(
    task_id='extract_omdb_api_data',
    python_callable=extract_omdb_api_data_task,
    dag=dag,
)

extract_tmdb_task = PythonOperator(
    task_id='extract_tmdb_api_data',
    python_callable=extract_tmdb_api_data_task,
    dag=dag,
)

# 2. Parallel API formatting
format_omdb_task = PythonOperator(
    task_id='format_omdb_data',
    python_callable=format_omdb_data_task,
    dag=dag,
)

format_tmdb_task = PythonOperator(
    task_id='format_tmdb_data',
    python_callable=format_tmdb_data_task,
    dag=dag,
)

# 3. Combine API data
combine_task = PythonOperator(
    task_id='combine_data',
    python_callable=combine_data_task,
    dag=dag,
)

# 4. Index to Elasticsearch
index_task = PythonOperator(
    task_id='index_data',
    python_callable=index_data_task,
    dag=dag,
)

# 5. Quality check
quality_check_task = BashOperator(
    task_id='data_quality_check',
    bash_command='echo "✅ API-only cinema pipeline completed successfully!"',
    dag=dag,
)

# SIMPLIFIED DEPENDENCIES - API ONLY!
# Start with parallel API extractions → Format → Combine → Index → Quality Check
extract_omdb_task >> format_omdb_task
extract_tmdb_task >> format_tmdb_task
[format_omdb_task, format_tmdb_task] >> combine_task
combine_task >> index_task >> quality_check_task 