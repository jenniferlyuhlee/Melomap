"""SQLAlchemy models for Capstone Project 1"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect database to Flask app."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Model for user of the app"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                   primary_key=True,
                   autoincrement=True)
    
    email = db.Column(db.String, 
                      unique=True, 
                      nullable=False)
    
    username = db.Column(db.String(50), 
                         unique=True, 
                         nullable=False)
    
    password = db.Column(db.String, 
                         nullable=False)

    name = db.Column(db.String)
    
    location = db.Column(db.String)

    bio = db.Column(db.Text)

    profile_image = db.Column(db.Text, 
                              default = "default-profile.png")

    spotify_account_id = db.Column(db.String)

    # M:M relationship to map user bookmarks to songs
    bookmarked_songs = db.relationship('Song',
                                       secondary='bookmarked_songs')
    
    # bidirectional 1:M relationship between user <-> posts
    posts = db.relationship('Post',
                            back_populates='user')
    
    def __repr__(self):
        """Change representation of user object"""

        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, email, username, password):
        """Sign up user"""

        # Hashes password and adds user to system
        hashed_pwd = User.hash_pw(password)

        user = User(
            email=email,
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Login User"""

        user = cls.query.filter_by(username=username).first()

        if user:
            try:
                # Checks if password hash matches entered password and returns user
                is_auth = bcrypt.check_password_hash(user.password, password)
                if is_auth:
                    return user
            except ValueError:
                # Returns False if password doesn't match
                return False
        else:
            # Returns False if username not found
            return False

    @classmethod
    def hash_pw(cls, password):
        """Hashes password"""
        
        return bcrypt.generate_password_hash(password).decode('UTF-8')


class BookmarkedSongs(db.Model):
    """Mapping user to bookmarked songs"""

    __tablename__ = 'bookmarked_songs'

    id = db.Column(db.Integer, 
                   primary_key=True,
                   autoincrement=True)

    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id', ondelete='cascade'),
                        nullable=False)

    song_id = db.Column(db.Integer, 
                        db.ForeignKey('songs.id', ondelete='cascade'),
                        nullable=False)


class Song(db.Model):
    """Model for individual songs in database"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.String, 
                      nullable=False)

    artists = db.Column(db.String,
                       nullable=False)

    album = db.Column(db.String)

    album_year = db.Column(db.String)

    spotify_track_id = db.Column(db.String, 
                                 nullable=False)

    spotify_url = db.Column(db.Text,
                            nullable=False)

    audio_url = db.Column(db.Text)

    image_url = db.Column(db.Text)

    # bidirectional M:M relationship to associate song with posts
    posts = db.relationship('Post',
                            secondary='post_songs',
                            back_populates='songs')
    
    @classmethod
    def song_in_db(cls, song):
        """Checks if song instance already in db by passing in song object data, 
        returns song instance if true, else false"""
        
        spotify_track_id = song['spotify_track_id']
        found_song = Song.query.filter_by(spotify_track_id=spotify_track_id).first()
        if found_song:
            return found_song
        else:
            return None

    @classmethod
    def create_song(cls, song):
        """Creates a song instance from a song object"""

        song_to_add = Song(
                title= song['title'],
                album= song['album'], 
                album_year= song['album_year'],
                artists= song['artists'],
                spotify_track_id= song['spotify_track_id'],
                spotify_url= song['spotify_url'],
                image_url= song['image_url'],
                audio_url= song['audio_url']
            )
        db.session.add(song_to_add)
        db.session.commit()
        return song_to_add


class PostSongs(db.Model):
    """Model for connection between post and songs results"""

    __tablename__ = 'post_songs'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)  
      
    song_id = db.Column(db.Integer,
                        db.ForeignKey('songs.id', ondelete='cascade'),
                        nullable=False)
    
    post_id = db.Column(db.Integer, 
                        db.ForeignKey('posts.id', ondelete='cascade'),
                        nullable=False)


class Post(db.Model):
    """Model for individual post"""

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id', ondelete='cascade'),
                        nullable=False,)

    image = db.Column(db.Text,
                      nullable=False)
    
    description = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.now())
    
    # bidirectional 1:M relationship between post <-> user
    user = db.relationship('User',
                           back_populates='posts')
    
    # bidirectional M:M relationship to associate songs with a post
    songs = db.relationship('Song',
                            secondary='post_songs',
                            back_populates='posts')