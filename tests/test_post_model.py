"""Post model tests"""

import os, sys
from unittest import TestCase
from sqlalchemy import exc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, User, Post, Song
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///melomap-test"

from app import app

db.drop_all()
db.create_all()

class PostModelTestCase(TestCase):
    """Test Post Model."""

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
        db.session.commit()

        self.user1 = user1
        self.test_post = test_post

    def tearDown(self):
        """Deletes client data to cleanup tests."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_post_model(self):
        """Basic tests on post model."""

        # image names saved with random string in front
        self.assertTrue(self.test_post.image.endswith('test.jpg'))
        self.assertEqual(self.test_post.description, 'test test test')

    def test_invalid_post(self):
        """Tests invalid post creation."""

        with self.assertRaises(exc.IntegrityError) as context:
            # post with no image
            invalid_post = Post(image=None)
            # post with empty image string
            invalid_post2 = Post(image="")
            db.session.add_all([invalid_post, invalid_post2])
            db.session.commit()

    ############## Relationship Tests
    def test_post_user_relationship(self):
        """Tests post-user relationship."""

        self.assertIn(self.test_post, self.user1.posts)
        self.assertEqual(len(self.user1.posts), 1)
        self.assertEqual(self.test_post.user_id, self.user1.id)
        self.assertEqual(self.user1.posts[0].description, 'test test test')


        test_post2 = Post(image='test.png',
                          description='another test')
        self.user1.posts.append(test_post2)
        db.session.commit()
        
        self.assertIn(test_post2, self.user1.posts)
        self.assertEqual(len(self.user1.posts), 2)
        self.assertEqual(test_post2.user_id, self.user1.id)
        self.assertTrue(self.user1.posts[1].image.endswith('test.png'))

    def test_post_deletion(self):
        """Tests User-post relationship and detection of post deletion."""

        db.session.delete(self.test_post)
        db.session.commit()
        
        self.assertNotIn(self.test_post, self.user1.posts)
        self.assertEqual(len(self.user1.posts), 0)
    
    def test_post_songs_relationship(self):
        """Tests post-songs relationship."""

        post_song = Song(title='Test song',
                          artists='Test artists',
                          spotify_track_id = '12345',
                          spotify_url= "spotify.com/testsong")
        self.test_post.songs.append(post_song)
        db.session.commit()

        self.assertIn(post_song, self.test_post.songs)
        self.assertEqual(len(self.test_post.songs), 1)
        self.assertEqual(self.test_post.songs[0].title, 'Test song')
        self.assertEqual(self.test_post.songs[0].spotify_track_id, '12345')