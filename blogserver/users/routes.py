from flask import Blueprint

from flask import render_template, url_for, flash, redirect, request, abort
from blogserver import db, dynamo_db, bcrypt, s3
import boto3
from boto3.dynamodb.conditions import Key
import uuid
# from requests import request
from blogserver.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                            RequestResetForm, ResetPasswordForm, DocumentUploadForm)
from blogserver.models import Document, User, Post
from flask_login import login_required, login_user, current_user, logout_user, login_required
from blogserver.users.utils import save_picture, is_safe_url, send_reset_email, save_document, save_uploaded_docs
from botocore.exceptions import ClientError
import logging
from datetime import datetime


users = Blueprint('users', __name__)
doc_table = dynamo_db.Table('Documents')

@users.route('/register', methods = ['GET','POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title = "Register", form = form)

@users.route('/login', methods =['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not is_safe_url(next_page):
                return abort(400)
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title = "Login", form = form)

@users.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods =['GET', 'POST'])
@login_required
def account():
    """User's account route to update their profile picture, username or email"""
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data  
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title = "Account", 
                            image_file = image_file, form = form)



@users.route('/my_documents', methods =['GET', 'POST'])
@login_required
def documents():
    """User route to upload documents to their profile"""
    form = DocumentUploadForm()
    if form.validate_on_submit():
        try:
            username = current_user.username
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
            filename = username + "/" + dt_string+"_"+form.document.data.filename
            document_name = form.document_name.data
            description = form.document_description.data
            read_time = str(form.document_read_time.data)
            read_time_int = int(read_time)
            s3.upload_fileobj(form.document.data, "flaskportfoliodocuments", filename, ExtraArgs= { 'ContentType': 'application/pdf', 'ContentDisposition': 'inline', "Metadata":{"name": document_name,"description": description, "read_time": read_time }})
            document = Document(name=document_name, description=description, read_time=read_time_int, owner = current_user)
            db.session.add(document)
            db.session.commit()
            flash('Your document has been uploaded!', 'success')
            return redirect(url_for('users.documents'))
        except ClientError as e:
            logging.error(e)
            flash('Your document could not be uploaded. Please try again.', 'warning')
            return redirect(url_for('users.documents'))

    elif request.method =='GET':
        #Query db for all of the users documents
        #Print all document names & display documents
        username = current_user.username
        public_urls = []
        try:
            for item in s3.list_objects(Bucket="flaskportfoliodocuments")['Contents']:
                user = item['Key'].split('/')[0]
                if user == username:
                    presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket': "flaskportfoliodocuments", 'Key': item['Key']}, ExpiresIn = 600000)
                    metadata = s3.head_object(Bucket= "flaskportfoliodocuments", Key= item['Key'])
                    read_time = metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-read_time']
                    name =  metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-name']
                    document = Document.query.filter_by(name=name).first()
                    if document:
                        document.presigned_url = presigned_url
                        db.session.commit()
                    description =metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-description']
                    public_urls.append({'presigned_url': presigned_url, 'name': name, 'description': description, 'read_time': read_time})

            print(public_urls)
        except ClientError as e:
            logging.error(e)
            flash('Something went wrong', 'warning')
            return redirect(url_for('main.home'))
        
        copy_link = request.url_root + 'portfolio/' + username
        shareable_link =  '/portfolio/' + username
        return render_template("my_documents.html", title = "My Documents", documents = documents, form=form, public_urls = public_urls, shareable_link = shareable_link, copy_link = copy_link)



@users.route('/portfolio/<string:username>')
def user_portfolio(username):
    """Route to view the public portfolio of a user"""
    title = username.capitalize() +"'s Portfolio"
    user = User.query.filter_by(username=username).first()
    documents = user.documents
    return render_template('public_portfolio.html', title = title, documents = documents)

@users.route('/user/<string:username>')
def user_posts(username):
    """Route to view the post made by a user"""
    page = request.args.get('page',1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page = page, per_page=5)
    return render_template('user_posts.html', posts = posts, user=user)


@users.route('/reset_password', methods =['GET', 'POST'])
def reset_request():
    """Route to reset a user password"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)

@users.route('/reset_password/<token>', methods =['GET', 'POST'])
def reset_token(token):
    """Route to reset a user password"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)