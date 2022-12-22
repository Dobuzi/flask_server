from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.utils import *

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
	db = get_db()
	posts = db.execute(
		'SELECT p.id, title, body, created, author_id, username, likes'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' ORDER BY created DESC'
	).fetchall()
	return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO post (title, body, author_id)'
				' VALUES (?, ?, ?)',
				(title, body, g.user['id'])
			)
			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
	post = get_post(id)

	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE post SET title = ?, body = ?'
				' WHERE id = ?',
				(title, body, id)
			)
			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	which_val = ('post', 'like', 'post_id') if request.args.get('is_post', 'False') == 'True' else ('comment', 'like_comment', 'comment_id')
	post_id = request.args.get('post_id', None)
	db = get_db()
	db.execute(f'DELETE FROM {which_val[0]} WHERE id = ?', (id,))
	db.execute(f'DELETE FROM {which_val[1]} WHERE {which_val[2]} = ?', (id,))
	db.commit()
	return redirect(url_for('blog.detail', id=post_id)) if post_id else redirect(url_for('blog.index'))

@bp.route('/<int:id>/like', methods=('GET', 'POST'))
@login_required
def like(id):
	if request.method == 'POST':
		db = get_db()
		click_dislike(db, id) if already_like(id) else click_like(db, id)
		update_likes(db, id)
	return redirect(url_for('blog.detail', id=id)) if request.args.get('is_detail', 'False') == 'True' else redirect(url_for('blog.index'))

@bp.route('/<int:id>/like_comment', methods=('GET', 'POST'))
@login_required
def like_comment(id):
	post_id = request.args.get('post_id', None)
	if request.method == 'POST':
		db = get_db()
		click_dislike(db, id, is_post=False) if already_like(id, is_post=False) else click_like(db, id, is_post=False)
		update_likes(db, id, is_post=False)
	return redirect(url_for('blog.detail', id=post_id))

@bp.route('/<int:id>/detail')
def detail(id):
	post = get_post(id, check_author=False)
	comments = get_comments(id)
	return render_template('blog/detail.html', post=post, comments=comments)

@bp.context_processor
def utility_processor():
	return dict(already_like=already_like)

@bp.route('/<int:id>/comment', methods=('GET', 'POST'))
@login_required
def comment(id):
	if request.method == 'POST':
		body = request.form['body']
		error = None
		
		if not body:
			error = 'Body is required.'
			
		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'INSERT INTO comment (post_id, author_id, body)'
				' VALUES (?, ?, ?)',
				(id, g.user['id'], body)
			)
			db.commit()
	return redirect(url_for('blog.detail', id=id))