"""Song model tests"""

import os, sys
from unittest import TestCase
from sqlalchemy import exc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.models import db, User, Post, Song
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///melomap-test"

from app import app

db.drop_all()
db.create_all()

class SongModelTestCase(TestCase):
    """Test Song Model."""

    def setUp(self):
        """Create test data."""

        User.query.delete()
        Post.query.delete()
        Song.query.delete()

 
        user1 = User.signup(email = 'test@email.com',
                     username = 'testuser1',
                     password = 'testing')
        db.session.add(user1)

        test_post = Post(image='test.jpg',
                         description = 'test test test')
        user1.posts.append(test_post)

        test_song = Song(title='Test song',
                         artists='Test artists',
                         spotify_track_id = '12345',
                         spotify_url= "spotify.com/testsong")
        test_post.songs.append(test_song)
        db.session.commit()
        
        self.user1 = user1
        self.test_post = test_post
        self.test_song = test_song
    
    def tearDown(self):
        """Deletes client data to cleanup tests."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_song_model(self):
        """Basic tests on song model."""

        self.assertEqual(self.test_song.title, 'Test song')
        self.assertEqual(self.test_song.artists, 'Test artists')
        self.assertEqual(self.test_song.spotify_track_id, '12345')
        self.assertEqual(self.test_song.spotify_url, 'spotify.com/testsong')

    def test_add_song_info(self):
        """Tests if additional song info is saved to db."""

        self.test_song.album = 'Test album'
        self.test_song.album_year = '2024'
        self.test_song.audio_url = 'testaudio.com'
        self.test_song.image_url = 'testimage.com'

        self.assertEqual(self.test_song.album, 'Test album')
        self.assertEqual(self.test_song.album_year, '2024')
        self.assertEqual(self.test_song.audio_url, 'testaudio.com')
        self.assertEqual(self.test_song.image_url, 'testimage.com')

    ############## Class Methods Tests
    def test_song_in_db_method(self):
        """Tests if class method song_in_db works as expected."""

        test_song_obj={
            'title': 'Test song',
            'artists' :'Test artists',
            'spotify_track_id' : '12345',
            'spotify_url' :'spotify.com/testsong'
        }

        self.assertIsNotNone(Song.song_in_db(test_song_obj))
        self.assertIsInstance(Song.song_in_db(test_song_obj), Song)
        self.assertIn(Song.song_in_db(test_song_obj), Song.query.all())

        test2_song_obj = {
            'title': 'Not in db',
            'artists' :'Not in db',
            'spotify_track_id' : '404',
            'spotify_url' :'spotify.com/notindbsong'
        }

        self.assertFalse(Song.song_in_db(test2_song_obj))
        self.assertNotIsInstance(Song.song_in_db(test2_song_obj), Song)
        self.assertNotIn(Song.song_in_db(test2_song_obj), Song.query.all())

    def test_create_song_method(self):
        """Tests if class method create_song works as expected"""

        testing_song_obj={
            'title': 'Testing another song',
            'artists' :'Testing artists',
            'album': 'Testing album',
            'album_year': '2024',
            'spotify_track_id' : '1000',
            'spotify_url' :'spotify.com/testing',
            'image_url': 'testingimage.com',
            'audio_url': 'testingurl.com'
        }

        testing_song = Song.create_song(testing_song_obj)
        self.assertIsInstance(testing_song, Song)
        self.assertEqual(testing_song.title, 'Testing another song')
        self.assertEqual(testing_song.album, 'Testing album')
        self.assertEqual(testing_song.image_url, 'testingimage.com')

    def test_invalid_create_song(self):
        """Tests that error is thrown when invalid song is created."""
        
        # Song with no title
        invalid_song_obj1 = {
            'title': None,
            'artists': 'Artists',
            'spotify_track_id' : '2000',
            'spotify_url' :'spotify.com/testing',
        }
        
        with self.assertRaises(KeyError) as context:
            db.session.add(Song.create_song(invalid_song_obj1))
            db.session.commit()

        # Song with no spotify track id
        invalid_song_obj2 = {
            'title': 'Test title',
            'artists': 'Artists',
            'spotify_track_id' : '',
            'spotify_url' :'spotify.com/testing',
        }

        with self.assertRaises(KeyError) as context:
            db.session.add_all(Song.create_song(invalid_song_obj2))
            db.session.commit()

    ############## Relationship Tests
    def test_user_bookmarked_songs(self):

        self.user1.bookmarked_songs.append(self.test_song)

        self.assertIn(self.test_song, self.user1.bookmarked_songs)
        self.assertEqual(len(self.user1.bookmarked_songs), 1)
  