from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from blogserver import db, s3
# from requests import request
from blogserver.posts.forms import (PostForm)
from blogserver.models import Document, Post
from flask_login import login_required, current_user, login_required
from botocore.exceptions import ClientError
import logging


posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods =['GET', 'POST'])
@login_required
def new_post():
    """Route to create a new post"""
    document_choices = []
    count = 0
    for document in current_user.documents:
        count+=1
        document_choices.append((count,document.name))

    form = PostForm()
    form.documents.choices = document_choices

    if form.validate_on_submit():

        document_name = dict(form.documents.choices).get(form.documents.data)
        document = Document.query.filter_by(name=document_name).first()
        post = Post(title= form.title.data, content = form.content.data, user_id = current_user.id, documents = [document])
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title = "New Post", 
                            form = form, legend = "New Post")


@posts.route('/post/<string:post_id>')
def post(post_id):
    """Route to view a post"""
    post = Post.query.get_or_404(post_id)    
    return render_template('post.html', title=post.title, post= post)


@posts.route('/post/<int:post_id>/update', methods =['GET', 'POST'])
@login_required
def update_post(post_id):
    """Route to update a post"""
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    document_choices = []
    count = 0
    for document in current_user.documents:
        count+=1
        document_choices.append((count,document.name))
    form = PostForm()
    form.documents.choices = document_choices

    if form.validate_on_submit():
        document_name = dict(form.documents.choices).get(form.documents.data)
        document = Document.query.filter_by(name=document_name).first()
        post.title = form.title.data
        post.content = form.content.data
        post.documents = [document]
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id = post.id))
    elif request.method =='GET':
        form.title.data = post.title
        form.content.data = post.content
        form.documents.choices = document_choices
    return render_template('create_post.html', title = "Update Post", 
                            form = form, legend = "Update Post")

@posts.route('/post/<int:post_id>/delete', methods =['POST'])
@login_required
def delete_post(post_id):
    """Route to delete a post"""
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

