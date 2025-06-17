#!/usr/bin/env python3
"""
Test both OMDB and TMDB APIs with real movie titles
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import OMDB_API_KEY, OMDB_BASE_URL, TMDB_API_KEY, TMDB_BASE_URL

def test_omdb_api():
    print("🎭 Testing OMDB API...")
    movie_title = "The Matrix"
    
    url = f"{OMDB_BASE_URL}?apikey={OMDB_API_KEY}&t={movie_title}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('Response') == 'True':
            print(f"✅ OMDB API Success: Found '{data.get('Title')}' ({data.get('Year')})")
            print(f"   Rating: {data.get('imdbRating')}, Director: {data.get('Director')}")
            return True
        else:
            print(f"❌ OMDB API Error: {data.get('Error')}")
    else:
        print(f"❌ OMDB API HTTP Error: {response.status_code}")
    return False

def test_tmdb_api():
    print("🎯 Testing TMDB API...")
    movie_title = "The Matrix"
    
    # Search for the movie
    search_url = f"{TMDB_BASE_URL}search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            movie = data['results'][0]
            print(f"✅ TMDB API Success: Found '{movie.get('title')}' ({movie.get('release_date')[:4] if movie.get('release_date') else 'N/A'})")
            print(f"   Popularity: {movie.get('popularity')}, Vote Average: {movie.get('vote_average')}")
            
            # Get detailed movie info
            movie_id = movie['id']
            details_url = f"{TMDB_BASE_URL}movie/{movie_id}?api_key={TMDB_API_KEY}"
            details_response = requests.get(details_url)
            
            if details_response.status_code == 200:
                details = details_response.json()
                print(f"   Budget: ${details.get('budget'):,}, Revenue: ${details.get('revenue'):,}")
                genres = [g['name'] for g in details.get('genres', [])]
                print(f"   Genres: {', '.join(genres)}")
            
            return True
        else:
            print(f"❌ TMDB API: No results found for '{movie_title}'")
    else:
        print(f"❌ TMDB API HTTP Error: {response.status_code}")
    return False

def main():
    print("🚀 Testing Both APIs with Real Movie Data")
    print("=" * 50)
    
    omdb_success = test_omdb_api()
    print()
    tmdb_success = test_tmdb_api()
    
    print("\n" + "=" * 50)
    if omdb_success and tmdb_success:
        print("🎉 Both APIs working perfectly! Your parallel pipeline is ready!")
        print("✅ OMDB API: Movie details, ratings, box office")
        print("✅ TMDB API: Popularity, budget, revenue, genres")
    else:
        if not omdb_success:
            print("❌ OMDB API issue - check your API key")
        if not tmdb_success:
            print("❌ TMDB API issue - check your API key")

if __name__ == "__main__":
    main() 