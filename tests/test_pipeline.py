import unittest
import os
import sys
import pandas as pd
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.ingestion import DataIngestion
from lib.formatting import DataFormatter
from config import get_data_path

class TestDataPipeline(unittest.TestCase):
    """Test cases for the cinema data pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ingestion = DataIngestion()
        self.formatter = DataFormatter()
        
    def test_get_data_path(self):
        """Test data path generation."""
        path = get_data_path("raw", "imdb", "title_basics", "20240101")
        expected = os.path.join("data", "raw", "imdb", "title_basics", "20240101")
        self.assertTrue(path.endswith(expected.replace("/", os.sep)))
    
    def test_data_ingestion_init(self):
        """Test DataIngestion initialization."""
        self.assertIsNotNone(self.ingestion.session)
    
    @patch('requests.Session.get')
    def test_omdb_api_call(self, mock_get):
        """Test OMDB API call functionality."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'Response': 'True',
            'Title': 'Test Movie',
            'imdbRating': '8.5'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test with minimal movie list
        movie_titles = ['Test Movie']
        result = self.ingestion.fetch_movie_details_from_omdb(movie_titles)
        
        # Verify the call was made
        mock_get.assert_called()
        self.assertTrue(result.endswith('.json'))
    
    def test_data_formatter_init(self):
        """Test DataFormatter initialization."""
        self.assertIsNotNone(self.formatter)
    
    def test_extract_popular_movie_titles(self):
        """Test extraction of popular movie titles."""
        # Create sample test data
        basics_data = {
            'tconst': ['tt0000001', 'tt0000002'],
            'titleType': ['movie', 'movie'],
            'primaryTitle': ['Test Movie 1', 'Test Movie 2']
        }
        
        ratings_data = {
            'tconst': ['tt0000001', 'tt0000002'],
            'averageRating': [8.5, 7.2],
            'numVotes': [15000, 20000]
        }
        
        # Create temporary CSV files
        basics_df = pd.DataFrame(basics_data)
        ratings_df = pd.DataFrame(ratings_data)
        
        basics_path = '/tmp/test_basics.tsv'
        ratings_path = '/tmp/test_ratings.tsv'
        
        basics_df.to_csv(basics_path, sep='\t', index=False)
        ratings_df.to_csv(ratings_path, sep='\t', index=False)
        
        try:
            titles = self.ingestion.extract_popular_movie_titles(
                basics_path, ratings_path, limit=10
            )
            self.assertIsInstance(titles, list)
        finally:
            # Clean up
            if os.path.exists(basics_path):
                os.remove(basics_path)
            if os.path.exists(ratings_path):
                os.remove(ratings_path)

if __name__ == '__main__':
    unittest.main() 