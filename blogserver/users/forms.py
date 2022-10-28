from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from blogserver.models import User
from wtforms.widgets import TextArea

class RegistrationForm(FlaskForm):
    """Form for users to register"""
    username = StringField('Username', 
                            validators = [DataRequired(), Length(min=2,max=20)])

    email = StringField('Email', 
                        validators = [DataRequired(), Email()])
    password = PasswordField('Password', 
                              validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                        validators = [DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



class LoginForm(FlaskForm):
    """Form for users to login"""
    email = StringField('Email', 
                        validators = [DataRequired(), Email()])
    password = PasswordField('Password', 
                              validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class DocumentUploadForm(FlaskForm):
    """Form for users to upload any documents to their portfolio"""
    document_name = StringField('Document Name', 
                            validators = [DataRequired(), Length(min=2,max=20)])

    document_description = StringField('Document Description (Max Length: 300 char)', widget=TextArea(),
                                    validators = [Length(max=300)])
    
    document_read_time = IntegerField('Read Time (in minutes)',
                                    validators = [DataRequired(), NumberRange(min=1, max = 500)])

    document = FileField('Add your document', validators =[DataRequired(), FileAllowed(['pdf'])])

    submit = SubmitField('Upload')


class UpdateAccountForm(FlaskForm):
    """Form for users to update their account"""
    username = StringField('Username', 
                            validators = [DataRequired(), Length(min=2,max=20)])

    email = StringField('Email', 
                        validators = [DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators =[FileAllowed(['jpg','png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    """Form for users to request a password reset"""
    email = StringField('Email', 
                        validators = [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    """Form for users to reset their password"""
    password = PasswordField('Password', 
                              validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                        validators = [DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset Password')