from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class SignupForm(FlaskForm):
    """Form for signing up new users"""

    email = StringField('E-mail', validators=
                        [InputRequired(message='E-mail required.'), 
                         Email(message='Please enter a valid e-mail.')])
    
    username = StringField('Username', validators=
                           [InputRequired(message='Username required.')])
    
    password = PasswordField('Password', validators=
                             [InputRequired(message='Password required.'), 
                              Length(min=8, message='Password must be atleast 8 characters.')])


class LoginForm(FlaskForm):
    """Form for logging in users"""

    username = StringField('Username', validators=
                           [InputRequired(message='Username required.')])

    password = PasswordField('Password', validators=
                             [InputRequired(message='Password required.')])


class EditUserForm(FlaskForm):
    """For for editing user profiles"""
    
    name = StringField('Name')

    location = StringField('Location')

    bio = TextAreaField('Bio')

    profile_image = FileField('Profile Pic', validators=
                              [FileAllowed(['png', 'jpg', 'jpeg'], message='Photo must be a png, jpg or jpeg file.')])

    spotify_account_id = StringField('Spotify username')

    email = StringField('E-mail', validators=
                        [InputRequired(),
                         Email()])
    
    username = StringField('Username', validators=[InputRequired()])

    password = PasswordField('Password', validators=[InputRequired()])


class EditPasswordForm(FlaskForm):   
    """Form for editing password"""

    password = PasswordField('Current Password', validators=[InputRequired()])

    new_password1 = PasswordField('New Password', validators=[InputRequired(),
                                                              Length(min=8, 
                                                                     message='Password must be atleast 8 characters.')])
    
    new_password2 = PasswordField('Confirm Password', validators=[InputRequired(),
                                                                  Length(min=8,
                                                                         message='Password must be atleast 8 characters.')])

class ImageUploadForm(FlaskForm):
    """Form for submitting image"""

    image = FileField('Upload a Photo', validators=
                      [FileAllowed(['png', 'jpg', 'jpeg'], message='Photo must be a png, jpg or jpeg file.'),
                       InputRequired(message='Please upload a photo to continue.')])

    description = TextAreaField('Add a photo description (optional)')

