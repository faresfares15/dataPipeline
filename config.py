import os
from datetime import datetime

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Data Lake structure
DATA_LAYERS = {
    "RAW": "raw",
    "FORMATTED": "formatted", 
    "USAGE": "usage"
}

# Data sources
IMDB_DATASETS = {
    "title_basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title_ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "title_principals": "https://datasets.imdbws.com/title.principals.tsv.gz"
}

# OMDB API (free tier: 1000 requests/day)
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "ad2d0927")
OMDB_BASE_URL = "http://www.omdbapi.com/"

# Elasticsearch configuration
ELASTICSEARCH_CONFIG = {
    "host": os.getenv("ES_HOST", "localhost"),
    "port": int(os.getenv("ES_PORT", "9200")),
    "index_name": "cinema_analytics"
}

# Date format for folder structure
DATE_FORMAT = "%Y%m%d"
CURRENT_DATE = datetime.now().strftime(DATE_FORMAT)

def get_data_path(layer, group, entity, date=None):
    """Generate standardized data lake path."""
    if date is None:
        date = CURRENT_DATE
    return os.path.join(DATA_DIR, layer, group, entity, date) 