from decimal import Decimal
from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from blogserver import db, dynamo_db
import uuid
# from requests import request
from blogserver.posts.forms import (PostForm)
from blogserver.models import Post
from flask_login import login_required, current_user, login_required


posts = Blueprint('posts', __name__)
# post_table = dynamo_db.Table('Posts')

@posts.route('/post/new', methods =['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # post_id = uuid.uuid4().int
        # post_id = Decimal(str(post_id))
        # print(post_id)
        # post_table.put_item(Item={'post_id': post_id, 'title':form.title.data, 'content': form.content.data, 'author':current_user.username})
        post = Post(title= form.title.data, content = form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title = "New Post", 
                            form = form, legend = "Update Post")


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post= post)


@posts.route('/post/<int:post_id>/update', methods =['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id = post.id))
    elif request.method =='GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title = "Update Post", 
                            form = form, legend = "Update Post")

@posts.route('/post/<int:post_id>/delete', methods =['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

