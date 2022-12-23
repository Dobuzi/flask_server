from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.utils import *

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
	db = get_db()
	posts = get_posts(db)
	return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		post_id = get_id()
		title = request.form['title']
		body = request.form['body']
		tags = parse_tags(body)
		error = None

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			create_post(db, post_id, title, body)

			for tag_body in tags:
				add_tag(db, post_id, tag_body)

			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/create.html')

@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		tags = parse_tags(body)
		error = None

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			update_post(db, title, body, id)

			delete_tag(db, id)

			for tag_body in tags:
				add_tag(db, id, tag_body)
				
			db.commit()
			return redirect(url_for('blog.index'))

	post = get_post(id)
	return render_template('blog/update.html', post=post)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
	which_val = ('post', 'like', 'post_id') if request.args.get('is_post', 'False') == 'True' else ('comment', 'like_comment', 'comment_id')
	post_id = request.args.get('post_id', None)
	db = get_db()
	db.execute(f'DELETE FROM {which_val[0]} WHERE id = ?', (id,))
	db.execute(f'DELETE FROM {which_val[1]} WHERE {which_val[2]} = ?', (id,))
	db.commit()
	return redirect(url_for('blog.detail', id=post_id)) if post_id else redirect(url_for('blog.index'))

@bp.route('/<string:id>/like', methods=('GET', 'POST'))
@login_required
def like(id):
	if request.method == 'POST':
		db = get_db()
		click_dislike(db, id) if already_like(id) else click_like(db, id)
		update_likes(db, id)
	return redirect(url_for('blog.detail', id=id)) if request.args.get('is_detail', 'False') == 'True' else redirect(url_for('blog.index'))

@bp.route('/<string:id>/like_comment', methods=('GET', 'POST'))
@login_required
def like_comment(id):
	post_id = request.args.get('post_id', None)
	if request.method == 'POST':
		db = get_db()
		click_dislike(db, id, is_post=False) if already_like(id, is_post=False) else click_like(db, id, is_post=False)
		update_likes(db, id, is_post=False)
	return redirect(url_for('blog.detail', id=post_id))

@bp.route('/<string:id>/detail')
def detail(id):
	post = get_post(id, check_author=False)
	comments = get_comments(id)
	tags = get_tags(id)
	return render_template('blog/detail.html', post=post, comments=comments, tags=tags)

@bp.context_processor
def utility_processor():
	return dict(already_like=already_like)

@bp.route('/<string:id>/comment', methods=('GET', 'POST'))
@login_required
def comment(id):
	if request.method == 'POST':
		comment_id = get_id()
		body = request.form['body']
		error = None
		
		if not body:
			error = 'Body is required.'
			
		if error is not None:
			flash(error)
		else:
			db = get_db()
			add_comment(db, comment_id, id, body)
			db.commit()
	return redirect(url_for('blog.detail', id=id))