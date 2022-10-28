import secrets
import os
from PIL import Image
from flask import url_for, request, current_app
from blogserver import mail
from urllib.parse import urlparse, urljoin
from flask_mail import Message

def save_picture(form_picture):
    """function to save user profile picture"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics',picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

def save_document(form_document):
    """function to save a user document to db"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_document.filename)
    document_fn = random_hex+f_ext
    document_path = os.path.join(current_app.root_path, 'static/documents',document_fn)

    form_document.save(document_path)

    # output_size = (125,125)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(picture_path)
    
    return document_fn

def save_uploaded_docs(form_document):
    """function to save a save all user documents"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_document.filename)
    document_fn = form_document.filename
    document_path = os.path.join(current_app.root_path, 'static/uploaded_docs',document_fn)

    form_document.save(document_path)

    # output_size = (125,125)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(picture_path)
    
    return {'document_fn': document_fn, 'document_path': document_path}


def send_reset_email(user):
    """function to reset email"""
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                sender='noreply@demo.com', 
                recipients =[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token = token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc
