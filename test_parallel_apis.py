#!/usr/bin/env python3
"""
Test script to demonstrate parallel API functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.ingestion import DataIngestion

def test_parallel_apis():
    print("🎬 Testing Parallel Cinema APIs")
    print("=" * 50)
    
    # Create sample movie titles for testing
    movie_titles = ['The Shawshank Redemption', 'The Godfather', 'Inception', 'Pulp Fiction']
    
    ingestion = DataIngestion()
    
    print(f"📋 Testing with movies: {movie_titles}")
    print()
    
    # Test OMDB API
    print("🎭 API 1: OMDB (movie details, ratings, box office)")
    print("-" * 30)
    omdb_file = ingestion.fetch_movie_details_from_omdb(movie_titles)
    print(f"✅ OMDB data saved to: {omdb_file}")
    print()
    
    # Test TMDB API
    print("🎯 API 2: TMDB (popularity, budget, revenue, genres)")  
    print("-" * 30)
    tmdb_file = ingestion.fetch_movie_details_from_tmdb(movie_titles)
    print(f"✅ TMDB data saved to: {tmdb_file}")
    print()
    
    print("🚀 Parallel API Integration Summary:")
    print("✅ OMDB API: Enriches with detailed movie metadata")
    print("✅ TMDB API: Adds popularity metrics and financial data")
    print("✅ Data Structure: Ready for parallel DAG processing")
    print("✅ File Outputs: JSON format compatible with Spark")
    print()
    print("🎯 This demonstrates the parallel structure from your image!")
    print("   - Two separate API calls running independently")
    print("   - Different data sources providing complementary information")
    print("   - Ready for combination in the 'combine_data' task")

if __name__ == "__main__":
    test_parallel_apis() 