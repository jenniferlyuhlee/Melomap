"""User model tests"""

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

class UserModelTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        """Create user with sample data."""

        User.query.delete()
        Post.query.delete()
        Song.query.delete()

 
        user1 = User.signup(email = 'test@email.com',
                     username = 'testuser1',
                     password = 'testing')

        db.session.add(user1)
        db.session.commit()

        self.user1 = user1
    
    def tearDown(self):
        """Deletes client data to cleanup tests."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_repr(self):
        """Tests if repr method works as expected"""
        
        self.assertEqual(self.user1.__repr__(), 
                         f"<User #{self.user1.id}: testuser1>")
        
    def test_user_model(self):
        """Basic tests on User model."""

        #User should have no posts, no bookmarked songs, default profile pic
        self.assertEqual(len(self.user1.posts), 0)
        self.assertEqual(len(self.user1.bookmarked_songs), 0)
        self.assertEqual(self.user1.profile_image, "default-profile.png")

    def test_add_user_info(self):
        """Tests if additional User data is saved to db."""

        self.user1.name = 'Test Name'
        self.user1.location = 'Test Location'
        self.user1.bio = 'Test Bio'
        db.session.commit()

        self.assertEqual(self.user1.name, 'Test Name')
        self.assertEqual(self.user1.location, 'Test Location')
        self.assertEqual(self.user1.bio, 'Test Bio')

    ############## Relationship Tests
    def test_user_posts(self):
        """Tests User-posts relationship"""

        new_post = Post(image='test.png',
                        description = 'Post test!')
        self.user1.posts.append(new_post)
        db.session.commit()

        self.assertIn(new_post, self.user1.posts)
        self.assertEqual(len(self.user1.posts), 1)
        self.assertEqual(self.user1.posts[0].description, 'Post test!')
        self.assertEqual(new_post.user, self.user1)

    def test_user_bookmarked_songs(self):
        """Tests User-bookmarked songs relationship"""

        saved_song = Song(title='Test song',
                          artists='Test artists',
                          spotify_track_id = '12345',
                          spotify_url= "spotify.com/testsong")
        self.user1.bookmarked_songs.append(saved_song)
        db.session.commit()

        self.assertIn(saved_song, self.user1.bookmarked_songs)
        self.assertEqual(len(self.user1.bookmarked_songs), 1)
        self.assertEqual(self.user1.bookmarked_songs[0].title, 'Test song')

    ############## Signup Tests
    def test_valid_signup(self):
        """Tests class method signup works as expected."""

        signup_user = User.signup('tester@test.com',
                                  'tester',
                                  'testpw')
        uid = 1000
        signup_user.id = uid
        db.session.commit()

        user2 = User.query.get(uid)
        self.assertIsNotNone(user2)
        self.assertEqual(user2.email, 'tester@test.com')
        self.assertEqual(user2.username, 'tester')
        # Checks that hashed password is saved to db
        self.assertNotEqual(user2.password, 'password')
        # Bcrypt password strings should start with $2b$
        self.assertTrue(user2.password.startswith('$2b$'))

    def test_invalid_username_signup(self):
        """Tests that signup fails with invalid usernames."""

        # No username
        invalid_user = User.signup('tester2@test.com', None, 'testpw')
        uid = 9998
        invalid_user.id = uid

        # Already taken username
        invalid_user2 = User.signup('tester3@test.com', 'testuser1', 'testpw' )
        uid = 9999
        invalid_user2.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """Tests that signup fails with invalid email."""

        # No email
        invalid_user = User.signup(None, 'tester', 'testpw')
        uid = 9998
        invalid_user.id = uid

        # Already taken email
        invalid_user2 = User.signup('test@email.com', 'invalidtester', 'testpw' )
        uid = 9999
        invalid_user2.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """Tests that signup fails with invalid password."""
        
        with self.assertRaises(ValueError) as context:
            # No password
            User.signup('tester2@test.com', 'tester', None)
            
            # Empty password
            User.signup('test@email.com', 'invalidtester', '' )
     
    ############## Authentification Tests 
    def test_valid_authentification(self):
        """Tests that class method authentification works as expected."""

        authUser = User.authenticate(self.user1.username, 'testing')
       
        self.assertIsNotNone(authUser)
        self.assertEqual(authUser.id, self.user1.id)
        self.assertIs(User.authenticate('testuser1', 'testing'), self.user1)

    def test_invalid_authentification(self):
        """Tests that authentification fails with invalid username/password"""

        # incorrect password
        invalidUser = User.authenticate(self.user1.username, 'wrongpassword')
        self.assertFalse(invalidUser)

        # wrong/invalid username
        invalidUser2 = User.authenticate('wrongusername', 'testing')
        self.assertFalse(invalidUser2)
