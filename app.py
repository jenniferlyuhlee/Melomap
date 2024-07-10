"""Views for Melomap App"""

import os
from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import uuid as uuid

from views.forms import SignupForm, LoginForm, EditUserForm, EditPasswordForm, ImageUploadForm
from models.models import db, connect_db, User, Song, Post
from views.api_funcs import get_keywords, get_list_of_tracks
from functools import wraps

CURR_USER_KEY = 'curr_user'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get(
    'DATABASE_URL', 'postgresql:///melomap'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

# Photos upload directories - saving photo uploads to app folders for now
PROFILE_FOLDER  = 'static/profile-images'
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER

IMAGE_FOLDER = 'static/post-images'
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

connect_db(app)

###############################################################
# User auth decoraters/functions

@app.before_request
def add_user_to_g():
    """Before every request, checks if a user is logged in
    and adds current user to Flask global"""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def check_g_user(func):
    """Custom decorator function to check if g.user logged in 
    for routes requiring authorization"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            # return redirect(url_for('homepage'))
        return func(*args, **kwargs)
    return wrapper


def do_login(user):
    """Login user by adding id to session"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user by removing from session"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


###############################################################
# User signup/login/logout 

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Shows signup form and handles user signup"""

    form = SignupForm()

    # If form validated, create new user and add to DB
    if form.validate_on_submit():
        try:
            user = User.signup(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data  
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append('Username taken.')
            return render_template('form.html', form=form,
                                    title='Join melomap.',
                                    button='Sign up')
        
        # Login user to session and redirect to home page
        do_login(user)
        flash(f"Welcome to Melomap {user.username}!", "success")
        return redirect(url_for('homepage'))
    
    # Show signup form if not validating
    else:
        return render_template('form.html',
                               form=form, 
                               title='Join melomap.',
                               button='Sign up')
    

@app.route('/login', methods=["GET", "POST"])
def login():
    """Shows login form and handles user login"""

    form = LoginForm()

    # If form validated, authenticate user and login
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello {user.username}!", "success")
            return redirect(url_for('homepage'))

        form.username.errors.append('Invalid credentials.')
    
    # Show login form if not validating
    return render_template('form.html', 
                           form=form,
                           title="Welcome back.",
                           button="Login")


@app.route('/logout')
@check_g_user
def logout():
    """Handles logging out user"""

    name = g.user.username
    do_logout()

    flash(f'Logged out {name}.', 'success')
    return redirect (url_for('login'))


###############################################################
# Dynamic homepages 

@app.route('/')
def homepage():
    """Shows homepage:
    - anon users: signup page
    - logged in: 30 most recent posts
    """

    if g.user:
        posts = Post.query.order_by(Post.timestamp.desc()).limit(5).all()
        return render_template('homepages/home.html', posts=posts)

    else:
        return render_template('homepages/home-anon.html')

@app.route('/loadmore/posts')
@check_g_user
def loadmore_posts():
    """Shows more posts
    - sends response to axios request to be handled in JS"""

    offset = int(request.args.get('offset'))
    posts = Post.query.order_by(Post.timestamp.desc()).limit(5).offset(offset).all()
    return render_template('homepages/loadmore.html', posts=posts)


###############################################################
# User routes
    
@app.route('/users/<int:user_id>')
@check_g_user
def user_profile(user_id):
    """Show user profile - displays user's posts by default"""

    user = User.query.get_or_404(user_id)
    return render_template('user/profile.html', user=user)


@app.route('/users/<int:user_id>/posts')
@check_g_user
def show_user_posts(user_id):
    """Show all posts by user 
    - sends response to axios request to be handled in JS"""
   
    user = User.query.get_or_404(user_id)
    return render_template('user/posts.html', user=user)


@app.route('/users/<int:user_id>/bookmarked')
@check_g_user
def show_bookmarked_songs(user_id):
    """Show all bookmarked songs by user 
    - sends response to axios request to be handled in JS"""
   
    user = User.query.get_or_404(user_id)
    return render_template('user/saved.html', user=user)


@app.route('/bookmark/<int:song_id>', methods=['POST'])
@check_g_user
def bookmark(song_id):
    """ Add/remove bookmark for songs 
    - sends response to axios request to be handled in JS"""
   
    song = Song.query.get(song_id)
    if song in g.user.bookmarked_songs:
        g.user.bookmarked_songs.remove(song)
        message = 'removed'
    else:
        g.user.bookmarked_songs.append(song)
        message = 'added'

    db.session.commit()
    return jsonify(message=message)


@app.route('/user/edit', methods=['GET', 'POST'])
@check_g_user
def edit_user():
    """Shows edit user form and handles editing user info"""
    
    form = EditUserForm(obj=g.user)

    # If form validated, authenticate user to saved changes to db
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            try:
                g.user.name = form.name.data
                g.user.location = form.location.data
                g.user.bio = form.bio.data
                g.user.email = form.email.data
                g.user.username = form.username.data
                
                # If filefield filled, handles saving filename to db
                if ('profile_image' in request.files and request.files['profile_image']): 
                    # Grab file and filename
                    img_file = request.files['profile_image']
                    img_filename = secure_filename(img_file.filename)
                    # Set UUID to make unique filenames
                    img_name = f'{str(uuid.uuid1())}_{img_filename}'
                    # Save image to profile-images directory
                    img_file.save(os.path.join(app.config['PROFILE_FOLDER'], img_name))
                    # Save file's name to db
                    g.user.profile_image = img_name
                # Otherwise keep image file as is in db and commit
                db.session.commit()

            # Catches error if username already exists in db and refreshes form
            except IntegrityError:
                db.session.rollback()
                form.username.errors.append('Username taken.')
                return render_template('/user/edit.html', form=form,
                                       user=g.user,
                                       title = 'My Info',
                                       button='Save')
            
            # If no errors, then redirects to user profile
            flash("Saved profile edits.", "info")
            return redirect(url_for('user_profile', user_id=g.user.id))
        
        # If password authentification fails, display message
        form.password.errors.append('Invalid password.')

    # Displays edit user info form 
    return render_template('/user/edit.html', form=form, 
                           user=g.user,
                           title = 'My Info',
                           button='Save')

@app.route('/user/editpw', methods=['GET', 'POST'])
@check_g_user
def edit_password():
    """Shows edit password form and handles password changes"""

    form = EditPasswordForm()

    # If form validated, authenticates user's old credentials
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            new_pw = form.new_password1.data
            confirm_pw = form.new_password2.data
            
            # Checks if new password and confirm password fields are the same
            if new_pw == confirm_pw:
                # Hashes new password and saves to db
                g.user.password = User.hash_pw(new_pw)
                db.session.commit()
                flash("Changed password.", "info")
                return redirect(url_for('user_profile', user_id=g.user.id))
            # Let's user know if new password cannot be confirmed
            form.new_password2.errors.append('Passwords do not match.')
       
        else:
            form.password.errors.append('Invalid password.')

    # Displays edit password form
    return render_template('/user/edit-pw.html',form=form,
                           user=g.user,
                           title = 'Change Password',
                           button = 'Save')


@app.route('/user/delete', methods=['GET'])
@check_g_user
def delete_user():
    """Delete user"""

    do_logout()
    db.session.delete(g.user)
    db.session.commit()

    flash("Account deleted.", "success")
    return redirect(url_for('homepage'))


###############################################################
# Search music and posts routes

@app.route('/search')
@check_g_user
def search():
    """Search form filters and displays all songs and users in database"""
    
    # Grab search query 
    search = request.args.get('q')

    # Display all results if no search query entered
    if not search:
        songs = Song.query.limit(20).all()
        users = User.query.all()
    
    # Display filtered results based on search query 
    else:
        songs = Song.query.filter(
            (func.lower(Song.title).like(f"%{search}%")) | 
            (func.lower(Song.album).like(f"%{search}%")) | 
            (func.lower(Song.artists).like(f"%{search}%"))
            ).limit(20).all()
        users = User.query.filter(
            (func.lower(User.username).like(f"%{search}%")) | 
            (func.lower(User.name).like(f"%{search}%"))
            ).all()

    return render_template('search.html', 
                            songs=songs,
                            users=users,
                            search=search)

@app.route('/loadmore/songs')
@check_g_user
def loadmore_songs():
    """Shows more song results
    - sends response to axios request to be handled in JS"""

    search = request.args.get('q')
    offset = int(request.args.get('offset'))

    if not search:
        songs = Song.query.limit(20).offset(offset).all()

    else:
        songs = Song.query.filter(
            (func.lower(Song.title).like(f"%{search}%")) | 
            (func.lower(Song.album).like(f"%{search}%")) | 
            (func.lower(Song.artists).like(f"%{search}%"))
            ).limit(20).offset(offset).all()
    
    return render_template('homepages/loadmore.html', songs=songs)


@app.route('/posts/upload', methods=['GET', 'POST'])
@check_g_user
def search_music():
    """Shows image upload search form and handles 
    working with API requests responses and displaying results"""

    form = ImageUploadForm()

    if form.validate_on_submit():
        description = form.description.data

        # If filefield filled, grab file and make filename
        img_file = request.files['image'] 
        img_filename = secure_filename(img_file.filename)
        # Set UUID to make unique filenames
        img_name = f'{str(uuid.uuid1())}_{img_filename}'
        # Save image to profile-images directory to send to API
        img_file.save(os.path.join(app.config['IMAGE_FOLDER'], img_name))

        # send photo to AI-image API to get keywords
        keywords = get_keywords(f'static/post-images/{img_name}')
        
        # if API succeeds in sending keywords
        if (keywords):
            # send keywords to Spotify API to get song data as a list
            song_data_list = get_list_of_tracks(keywords)

            # Create Post instance
            new_post = Post(image=img_name, description=description)
            # Append post to user
            g.user.posts.append(new_post)

            # Create or find Song instances in db and append them to new_post
            for song_obj in song_data_list:
                # If not found in db, create new song instance
                found_song = Song.song_in_db(song_obj)
                if (found_song is None):
                    found_song = Song.create_song(song_obj)
                # Else append to post
                new_post.songs.append(found_song)
            
            try:
                db.session.commit()
                return redirect(url_for('music_results', post_id=new_post.id))

            except Exception as e:
                db.session.rollback()

        # API fails to send keywords show error 500 page
        else:
            abort(500)


    return render_template('form.html', 
                           title = 'What songs will you get?',
                           form=form,
                           button='Get Results')

@app.route('/posts/<int:post_id>')
@check_g_user
def music_results(post_id):
    """Displays post results of image-music search form"""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/results.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=['DELETE'])
@check_g_user
def delete_post(post_id):
    """Delete a post"""
    
    post = Post.query.get_or_404(post_id)
    if (g.user.id == post.user_id):
        db.session.delete(post)

        try:
            # if deletion goes through, sends "Deleted" message to handle in JS
            db.session.commit()
            return jsonify(message="Deleted")
        except:
            db.session.rollback()
            return jsonify(message="Failed")


###############################################################
# Error Pages
        
@app.errorhandler(404)
@check_g_user
def page_not_found(err):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
@check_g_user
def internal_error(err):
    return render_template('errors/500.html'), 500


@app.errorhandler(Exception)
@check_g_user
def handle_exception(err):
    if (isinstance(err, HTTPException)):
        return err
    return render_template('errors/500.html', err=err), 500