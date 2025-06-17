#!/usr/bin/env python3
"""
Quick Data Viewer - Direct Elasticsearch indexing with sample data
"""

import json
import requests
from datetime import datetime

# Sample movie data that will actually be indexed
sample_movies = [
    {
        "id": 1,
        "title": "The Shawshank Redemption",
        "year": 1994,
        "director": "Frank Darabont",
        "genre": ["Drama"],
        "imdb_rating": 9.3,
        "omdb_rating": 9.3,
        "tmdb_rating": 8.7,
        "plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "source": "Sample Data",
        "indexed_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "title": "The Godfather",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "genre": ["Crime", "Drama"],
        "imdb_rating": 9.2,
        "omdb_rating": 9.2,
        "tmdb_rating": 8.7,
        "plot": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "source": "Sample Data",
        "indexed_at": datetime.now().isoformat()
    },
    {
        "id": 3,
        "title": "The Dark Knight",
        "year": 2008,
        "director": "Christopher Nolan",
        "genre": ["Action", "Crime", "Drama"],
        "imdb_rating": 9.0,
        "omdb_rating": 9.0,
        "tmdb_rating": 8.5,
        "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.",
        "source": "Sample Data",
        "indexed_at": datetime.now().isoformat()
    }
]

def index_sample_data():
    """Index sample movie data directly to Elasticsearch."""
    print("🚀 Indexing sample movie data to Elasticsearch...")
    
    # Delete and recreate index
    try:
        requests.delete("http://localhost:9200/cinema_movies")
        print("✅ Deleted existing index")
    except:
        pass
    
    # Create index with mapping
    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "year": {"type": "integer"},
                "director": {"type": "text"},
                "genre": {"type": "keyword"},
                "imdb_rating": {"type": "float"},
                "omdb_rating": {"type": "float"},
                "tmdb_rating": {"type": "float"},
                "plot": {"type": "text"},
                "source": {"type": "keyword"},
                "indexed_at": {"type": "date"}
            }
        }
    }
    
    response = requests.put("http://localhost:9200/cinema_movies", json=mapping)
    if response.status_code == 200:
        print("✅ Created index with mapping")
    else:
        print(f"❌ Failed to create index: {response.text}")
        return False
    
    # Index sample movies
    for movie in sample_movies:
        response = requests.post(
            f"http://localhost:9200/cinema_movies/_doc/{movie['id']}", 
            json=movie
        )
        if response.status_code in [200, 201]:
            print(f"✅ Indexed: {movie['title']}")
        else:
            print(f"❌ Failed to index {movie['title']}: {response.text}")
    
    # Refresh index
    requests.post("http://localhost:9200/cinema_movies/_refresh")
    print("✅ Refreshed index")
    
    return True

def verify_data():
    """Verify the indexed data."""
    print("\n🔍 Verifying indexed data...")
    
    response = requests.get("http://localhost:9200/cinema_movies/_search?pretty")
    if response.status_code == 200:
        data = response.json()
        count = data['hits']['total']['value']
        print(f"✅ Found {count} movies in index")
        
        if count > 0:
            print("\n📊 Sample movie:")
            first_movie = data['hits']['hits'][0]['_source']
            print(f"   Title: {first_movie['title']}")
            print(f"   Year: {first_movie['year']}")
            print(f"   Director: {first_movie['director']}")
            print(f"   IMDB Rating: {first_movie['imdb_rating']}")
        
        return True
    else:
        print(f"❌ Failed to search: {response.text}")
        return False

def print_access_info():
    """Print access information."""
    print("\n" + "="*60)
    print("🎉 SUCCESS! Your movie data is now accessible:")
    print("="*60)
    print("\n🔍 Direct Elasticsearch Access:")
    print("   • All movies: http://localhost:9200/cinema_movies/_search?pretty")
    print("   • Movie count: http://localhost:9200/cinema_movies/_count")
    print("   • Index info: http://localhost:9200/cinema_movies")
    
    print("\n🎨 Kibana Dashboard (wait 30 seconds for startup):")
    print("   • Kibana UI: http://localhost:5601")
    print("   • Create index pattern: cinema_movies")
    print("   • Then go to Discover tab to explore data")
    
    print("\n📊 Quick Data Check:")
    print("   Copy this URL to your browser:")
    print("   http://localhost:9200/cinema_movies/_search?pretty&size=10")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🎬 QUICK CINEMA DATA INDEXER")
    print("="*40)
    
    success = index_sample_data()
    if success:
        success = verify_data()
        if success:
            print_access_info()
        else:
            print("❌ Data verification failed")
    else:
        print("❌ Indexing failed")
    
    print("\n✨ Done!") 