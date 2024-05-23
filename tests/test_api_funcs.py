"""API Calls Function tests"""

import os, sys
from unittest import TestCase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_funcs import get_keywords, get_track_data, get_list_of_tracks

class ImageAPITestCase(TestCase):
    """Tests for AI Image API calls."""

    def test_get_keywords(self):
        """Tests that AI Image API call returns keywords as expected."""

        keywords = get_keywords('test_image.jpeg')
        
        self.assertIsNotNone(keywords)
        self.assertIsInstance(keywords, list)
        self.assertEqual(len(keywords), 5)

class SpotifyAPITestCase(TestCase):
    """Tests for Spotify API calls."""

    def test_getting_track_data(self):
        """Tests that Spotify API returns"""

        keyword = 'test'
        track_data = get_track_data(keyword)

        self.assertIsNotNone(track_data)
        self.assertIsInstance(track_data, dict)
        self.assertIsNotNone(track_data['title'])
        self.assertTrue(track_data['spotify_url'].startswith('http'))
        self.assertEqual(len(track_data['album_year']), 4)

    def test_get_list_of_tracks(self):
        """Tests that function returns list of song objects containing Spotify data"""

        keywords = ['test', 'my', 'app']
        track_data_list = get_list_of_tracks(keywords)
        
        self.assertIsNotNone(track_data_list)
        self.assertIsInstance(track_data_list, list)
        self.assertEqual(len(track_data_list), 3)
        self.assertIsInstance(track_data_list[0], dict)
        self.assertIsInstance(track_data_list[1], dict)
        self.assertIsInstance(track_data_list[2], dict)