from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

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

def get_post(id, check_author=True):
	post = get_db().execute(
		'SELECT p.id, title, body, created, author_id, username, likes'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' WHERE p.id = ?',
		(id, )
	).fetchone()

	if post is None:
		abort(404, f'Post id {id} doesn\'t exist.')

	if check_author and post['author_id'] != g.user['id']:
		abort(403)
	
	return post

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
	get_post(id)
	db = get_db()
	db.execute('DELETE FROM post WHERE id = ?', (id,))
	db.commit()
	return redirect(url_for('blog.index'))

@bp.route('/<int:id>/like', methods=('GET', 'POST'))
@login_required
def like(id):
	if request.method == 'POST':
		db = get_db()
		click_dislike(db, id) if already_like(id) else click_like(db, id)
		update_likes(db, id)
	return redirect(url_for('blog.detail', id=id)) if request.args.get('is_detail', 'False') == 'True' else redirect(url_for('blog.index'))

def click_like(db, id):
	db.execute(
		'INSERT INTO like (user_id, post_id)'
		' VALUES (?, ?)',
		(g.user['id'], id)
	)
	db.commit()
	return

def click_dislike(db, id):
	db.execute(
		'DELETE FROM like'
		' WHERE user_id = ? AND post_id = ?',
		(g.user['id'], id)
	)
	db.commit()
	return

def count_likes(db, id):
	c = db.execute(
		'SELECT COUNT(*) as cnt FROM like WHERE post_id = ?',
		(id,)
	).fetchone()
	return c['cnt']

def already_like(id):
	if g.user is None:
		return False
	db = get_db()
	c = db.execute(
		'SELECT COUNT(*) as cnt FROM like'
		' WHERE user_id = ? AND post_id = ?',
		(g.user['id'], id)
	).fetchone()
	return True if c['cnt'] > 0 else False

@bp.context_processor
def utility_processor():
	return dict(already_like=already_like)

def update_likes(db, id):
	db.execute(
		'UPDATE post SET likes = ? WHERE id = ?',
		(count_likes(db, id), id)
	)
	db.commit()
	return

@bp.route('/<int:id>/detail')
def detail(id):
	post = get_post(id, check_author=False)
	return render_template('blog/detail.html', post=post)
