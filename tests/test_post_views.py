"""Music search/Post-related views tests"""

import os, sys
from unittest import TestCase
from flask import g
from sqlalchemy import exc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, User, Post, Song

os.environ['DATABASE_URL'] = "postgresql:///melomap-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class PostViewsTestCase(TestCase):
    """Test views for posts."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Post.query.delete()
        Song.query.delete()
        
        self.client = app.test_client()

        self.user1 = User.signup(email = 'test@email.com',
                     username = 'testuser1',
                     password = 'testing')
        
        self.test_post = Post(description='Post test',
                              image = 'test-image.png')
        
        self.user1.posts.append(self.test_post)
        db.session.commit()

        self.test_song1 = Song(title='Test song',
                               artists='Test artists',
                               spotify_track_id = '12345',
                               spotify_url= "spotify.com/testsong1")
        
        self.test_song2 = Song(title='TEST song!',
                               artists='TEST artists!',
                               spotify_track_id = '98765',
                               spotify_url= "spotify.com/testsong2")
    
        self.test_song3 = Song(title='third TEST song!',
                          artists='third TEST artists!',
                          spotify_track_id = '33333',
                          spotify_url= "spotify.com/testsong3")
        self.test_song4 = Song(title='4th TEST song!',
                          artists='4th TEST artists!',
                          spotify_track_id = '40404',
                          spotify_url= "spotify.com/testsong4")
        self.test_song5 = Song(title='Fifth test',
                          artists='Fifth TEST artists',
                          spotify_track_id = '56789',
                          spotify_url= "spotify.com/testsong5")

        songs_arr = [self.test_song1, self.test_song2, self.test_song3, self.test_song4, self.test_song5]

        self.test_post.songs.extend(songs_arr)
        db.session.commit()

        self.id1 = self.user1.id
        self.postid = self.test_post.id

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response
    
    ############## Search Songs Test
    def test_search_songs(self):
        """Tests that search displays appropriate songs"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp=c.get('/search?q=song')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test song</a>', html)
            self.assertIn('TEST song!</a>', html)
            self.assertNotIn('Fake test', html)

    ############## Upload Image Form Tests
    def test_upload_search_music(self):
        """Tests that post upload route displays as expected"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/posts/upload')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('What songs will you get?', html)

    def test_invalid_upload_search_music(self):
        """Tests that post upload route handles invalid input"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # Post request with mock data
            image_path = 'test_file.pdf'
            # Open image file in binary code and add to mock form data
            with open(image_path, 'rb') as img:
                data={
                    'description': 'invalid test post',
                    'image': (img, image_path)
                }

                resp = c.post('/posts/upload', data = data,
                               content_type='multipart/form-data',
                               follow_redirects=True)
                
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Photo must be a png, jpg or jpeg file', html)
        
    ############## Post Tests
    def test_post_displays_songs(self):
        """Tests that songs in relationship with post are displayed"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            test_post = Post.query.get(self.postid)

            resp = c.get(f'/posts/{self.postid}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('results', html)
            # Checks that test songs show up in post display
            self.assertIn(test_post.songs[0].title, html)
            self.assertIn(test_post.songs[1].title, html)
            self.assertIn(test_post.songs[2].title, html)
            self.assertIn(test_post.songs[3].title, html)
            self.assertIn(test_post.songs[4].title, html)

    def test_post_deletion(self):
        """Tests that post deletion route works and Songs stay in db"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

        resp = c.delete(f'/posts/{self.postid}/delete')
        message = resp.json['message']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual('Deleted', message)

        # confirms that songs still exists as instances
        self.assertIsInstance(self.test_song1, Song)
        self.assertIsInstance(self.test_song2, Song)
        self.assertIsInstance(self.test_song3, Song)
        self.assertIsInstance(self.test_song4, Song)
        self.assertIsInstance(self.test_song5, Song)
