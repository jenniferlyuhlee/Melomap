"""User-related views tests"""

import os, sys
from unittest import TestCase
from flask import g
from sqlalchemy import exc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.models import db, User, Post, Song

os.environ['DATABASE_URL'] = "postgresql:///melomap-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Post.query.delete()
        Song.query.delete()
        
        self.client = app.test_client()

        self.user1 = User.signup(email = 'test@email.com',
                     username = 'testuser1',
                     password = 'testing')
        
        self.user2 = User.signup(email = 'test2@email.com',
                     username = 'testuser2',
                     password = 'testing2')

        self.test_song = Song(title='Test song',
                              artists='Test artists',
                              spotify_track_id = '12345',
                              spotify_url= "spotify.com/testsong")
        
        db.session.add(self.test_song)
        db.session.commit()

        self.songid = self.test_song.id

        self.id1 = self.user1.id
        self.id2 = self.user2.id

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response
    
    ############## Signup Tests
    def test_signup(self):
        """Tests that signup route works as expected. """

        # Get request
        get_resp = self.client.get('/signup')
        get_resp_html = get_resp.get_data(as_text=True)

        self.assertEqual(get_resp.status_code, 200)
        self.assertIn('Join melomap.', get_resp_html)

        # Post request
        data={
            'email': 'signup@test.com',
            'username': 'testsignup',
            'password': 'pwpwpwpwpw'
        }

        post_resp = self.client.post('/signup', data=data, follow_redirects=True)
        post_resp_html = post_resp.get_data(as_text=True)
        
        # checks if signup passes and redirects to homepage
        self.assertEqual(post_resp.status_code, 200)
        self.assertIn('Explore the latest searches', post_resp_html)

    def test_invalid_signup(self):
        """Tests that signup is invalid..."""

        # when username taken
        data = {
            'email': 'test@tester.com',
            'username': 'testuser1',
            'password': 'hashedpw'
        }
        resp = self.client.post('/signup', data=data)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Username taken.", html)
            
        # when password too short
        data2 = {
            'email': 'test2@tester.com',
            'username': 'testuser2',
            'password': 'hashed'
        }

        resp2 = self.client.post('/signup', data=data2)
        html2 = resp2.get_data(as_text=True)

        self.assertEqual(resp2.status_code, 200)
        self.assertIn("Password must be atleast 8 characters.", html2)

    ############## Login Tests
    def test_login(self):
        """Tests login route works as expecteds."""

        # Get request
        get_resp = self.client.get('/login')
        get_html = get_resp.get_data(as_text=True)

        self.assertEqual(get_resp.status_code, 200)
        self.assertIn('Welcome back', get_html)
        
        # Post request
        post_resp = self.client.post('/login', data={'username':'testuser1',
                                                'password':'testing',}, 
                                                follow_redirects=True)
        post_html = post_resp.get_data(as_text=True)
        
        self.assertEqual(post_resp.status_code, 200)
        self.assertIn('Hello testuser1', post_html)

    def test_invalid_login(self):
        """Tests login route responds to invalid credentials."""

        resp = self.client.post('/login', data={'username':'testuser1',
                                                'password':'testingwrongpw',}, 
                                                follow_redirects=True)
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Invalid credentials', html)


    ############## Logout Test
    def test_logout(self):
        """Tests logout route works as expected."""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Logged out", html)


    ############## Profile Tests
    def test_view_profiles(self):
        """Tests view profile route works as expected"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # Viewing own profile
            resp1 = c.get(f'/users/{self.id1}')
            html1 = resp1.get_data(as_text=True)

            self.assertEqual(resp1.status_code, 200)
            self.assertIn(f'@{self.user1.username}', html1)
            self.assertIn('bi-pencil-square', html1)

            # Viewing other user's profile
            resp2 = c.get(f'/users/{self.id2}')
            html2 = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn(f'@{self.user2.username}', html2)

    def test_user_not_found(self):
        """Tests that 404 page displays when user isn't found"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # user id that doesn't exist
            invalid_user_id = 5000
            resp1 = c.get(f'/users/{invalid_user_id}')
            html1 = resp1.get_data(as_text=True)

            self.assertEqual(resp1.status_code, 404)
            self.assertIn('404. Page not found', html1)
            
            # invalid user id param 
            resp2 = c.get('/users/invaliduser')
            html2 = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 404)
            self.assertIn('404. Page not found', html2)

    ############## Edit Profile Tests
    def test_edit_profile(self):
        """Tests edit profile route works as expected."""
 
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
        
            # Get request
            get_resp = c.get('/user/edit')
            get_html = get_resp.get_data(as_text=True)

            self.assertEqual(get_resp.status_code, 200)
            self.assertIn('My Info', get_html)

            # Post request with mock data
            data = {'name': 'Tester',
                    'location': 'LA',
                    'bio': 'I am just a test user!',
                    'email': 'test@email.com',
                    'username': self.user1.username,
                    'password': 'testing'
                    }

            post_resp = c.post('/user/edit', data = data,
                               content_type='multipart/form-data',
                               follow_redirects=True)
            post_html = post_resp.get_data(as_text=True)

            self.assertEqual(post_resp.status_code, 200)
            self.assertIn('<h4>Tester', post_html)
            self.assertIn('bi-geo-alt-fill', post_html)
            self.assertIn('LA', post_html)
            self.assertIn('I am just a test user!</p>', post_html)

    def test_invalid_edit_profile(self):
        """Tests edit profile route handles invalid inputs"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # Post request with TAKEN USERNAME
            data1 = {'name': 'Tester',
                    'location': 'LA',
                    'bio': 'I am just a test user!',
                    'email': 'test@email.com',
                    'username': self.user2.username,
                    'password': 'testing'
                    }

            post_resp1 = c.post('/user/edit', data = data1,
                               content_type='multipart/form-data',
                               follow_redirects=True)
            post_html1 = post_resp1.get_data(as_text=True)

            self.assertEqual(post_resp1.status_code, 200)
            self.assertIn('Username taken', post_html1)

            # Post request with WRONG PASSWORD
            data2 = {'name': 'Tester',
                    'location': 'LA',
                    'bio': 'I am just a test user!',
                    'email': 'test@email.com',
                    'username': self.user1.username,
                    'password': 'wrongpassword'
                    }

            post_resp2 = c.post('/user/edit', data = data2,
                               content_type='multipart/form-data',
                               follow_redirects=True)
            post_html2 = post_resp2.get_data(as_text=True)

            self.assertEqual(post_resp2.status_code, 200)
            self.assertIn('Invalid password', post_html2)

    ############## Edit Password Tests
    def test_edit_password(self):
        """Tests edit password route works as expected"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            data={
                'password': 'testing',
                'new_password1': 'testtest',
                'new_password2': 'testtest'
            }
            resp = c.post('/user/editpw', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Changed password', html)

    def test_invalid_edit_password(self):
        """Tests edit password route handles invalid inputs"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # Input wrong password
            data1={
                'password': 'wrongpassword',
                'new_password1': 'testtest',
                'new_password2': 'testtest'
            }
            
            resp1 = c.post('/user/editpw', data=data1, follow_redirects=True)
            html1 = resp1.get_data(as_text=True)
            
            self.assertEqual(resp1.status_code, 200)
            self.assertIn('Invalid password', html1)

            # New passwords don't match
            data2={
                'password': 'testing',
                'new_password1': 'testtest',
                'new_password2': 'testtesttest'
            }
            
            resp2 = c.post('/user/editpw', data=data2, follow_redirects=True)
            html2 = resp2.get_data(as_text=True)
            
            self.assertEqual(resp2.status_code, 200)
            self.assertIn('Passwords do not match', html2)
    
    ############## Bookmarking Songs Test
    def test_bookmark_song(self):
        """Test that bookmarking song route works as expected"""  

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id 

        # bookmarking song
            post_resp1 = c.post(f'/bookmark/{str(self.songid)}')
            message1 = post_resp1.json['message']

            self.assertEqual(post_resp1.status_code, 200)
            self.assertEqual('added', message1)
            
        # unbookmarking song
            post_resp2 = c.post(f'/bookmark/{str(self.songid)}')
            message2 = post_resp2.json['message']

            self.assertEqual(post_resp2.status_code, 200)
            self.assertEqual('removed', message2)

    def test_displays_bookmarking_songs(self):
        """Tests that (un)bookmarked songs are (un)displayed."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id    

        # bookmarking song
            post_resp1 = c.post(f'/bookmark/{str(self.songid)}')
        # getting profile bookmarked songs
            get_resp1 = c.get(f'/users/{self.id1}/bookmarked')
            html1 = get_resp1.get_data(as_text=True)

            self.assertIn('Test song</a>', html1)
            self.assertIn(f'href="{self.test_song.spotify_url}"', html1)
            self.assertIn('bi-bookmark-fill', html1)

        # unbookmarking song
            post_resp2 = c.post(f'/bookmark/{str(self.songid)}')
        # getting profile bookmarked songs
            get_resp2 = c.get(f'/users/{self.id1}/bookmarked')
            html2 = get_resp2.get_data(as_text=True)

            self.assertNotIn('Test song</a>', html2)
            self.assertNotIn(f'href="{self.test_song.spotify_url}"', html2)
            self.assertNotIn('bi-bookmark-fill', html2)

    ############## Search User Test
    def test_search_user(self):
        """Tests that search displays appropriate users"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp=self.client.get('/search?q=test')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{self.user1.username}', html)
            self.assertIn(f'@{self.user2.username}', html)
            self.assertNotIn('@fakeusername', html)

    ############## Delete Account
    def test_delete_user(self):
        """Tests that account deletion route works"""   

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = self.client.get('/user/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up now', html)