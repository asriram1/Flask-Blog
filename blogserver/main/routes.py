from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user
from blogserver import s3
from blogserver.models import Post
import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging
from botocore.exceptions import ClientError



main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    """Homepage route listing all posts on the application"""
    #default page is 1
    page = request.args.get('page',1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=5)
    return render_template('home.html', posts = posts)

@main.route('/about')
def about():
    """About page"""
    return render_template('about.html', title = 'About')