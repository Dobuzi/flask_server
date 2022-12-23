from flask import g

from werkzeug.exceptions import abort
import uuid

from flaskr.db import get_db

def get_id():
	return str(uuid.uuid1())

def get_posts(db):
	return db.execute(
		'SELECT p.id, title, body, created, author_id, username, likes'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' ORDER BY created DESC'
	).fetchall()

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

def create_post(db, post_id, title, body):
	db.execute(
		'INSERT INTO post (id, title, body, author_id)'
		' VALUES (?, ?, ?, ?)',
		(post_id, title, body, g.user['id'])
	)
	return

def add_tag(db, post_id, tag_body):
	db.execute(
		'INSERT INTO tag (post_id, body)'
		' VALUES (?, ?)',
		(post_id, tag_body)
	)
	return

def delete_tag(db, post_id):
	db.execute(
		'DELETE FROM tag WHERE post_id = ?',
		(post_id, )
	)
	return

def update_post(db, title, body, id):
	db.execute(
		'UPDATE post SET title = ?, body = ?'
		' WHERE id = ?',
		(title, body, id)
	)
	return

def get_comments(id):
	return get_db().execute(
		'SELECT c.id, c.post_id, c.body, c.created, c.author_id, c.likes, u.username'
		' FROM comment c'
		' JOIN post p ON p.id = c.post_id'
		' LEFT JOIN user u'
		' WHERE p.id = ?'
		' ORDER BY c.likes DESC, c.created DESC',
		(id, )
	).fetchall()

def add_comment(db, comment_id, post_id, comment_body):
	db.execute(
		'INSERT INTO comment (id, post_id, author_id, body)'
		' VALUES (?, ?, ?, ?)',
		(comment_id, post_id, g.user['id'], comment_body)
	)
	return

def get_tags(id):
	return get_db().execute(
		'SELECT t.id, t.post_id, t.body, t.created'
		' FROM tag t'
		' JOIN post p ON p.id = t.post_id'
		' WHERE p.id = ?'
		' ORDER BY t.body ASC',
		(id, )
	).fetchall()

def parse_tags(body):
	return { tag.strip('#') for tag in body.split() if tag.startswith('#') and len(tag.strip('#')) > 0 }

def click_like(db, id, is_post=True):
	which_table, which_id = ('like', 'post_id') if is_post else ('like_comment', 'comment_id')
	db.execute(
		f'INSERT INTO {which_table} (user_id, {which_id})'
		' VALUES (?, ?)',
		(g.user['id'], id)
	)
	db.commit()
	return

def click_dislike(db, id, is_post=True):
	which_table, which_id = ('like', 'post_id') if is_post else ('like_comment', 'comment_id')
	db.execute(
		f'DELETE FROM {which_table}'
		f' WHERE user_id = ? AND {which_id} = ?',
		(g.user['id'], id)
	)
	db.commit()
	return

def count_likes(db, id, is_post=True):
	which_table, which_id = ('like', 'post_id') if is_post else ('like_comment', 'comment_id')
	c = db.execute(
		f'SELECT COUNT(*) as cnt FROM {which_table} WHERE {which_id} = ?',
		(id,)
	).fetchone()
	return c['cnt']

def already_like(id, is_post=True):
	which_table, which_id = ('like', 'post_id') if is_post else ('like_comment', 'comment_id')
	if g.user is None:
		return False
	db = get_db()
	c = db.execute(
		f'SELECT COUNT(*) as cnt FROM {which_table}'
		f' WHERE user_id = ? AND {which_id} = ?',
		(g.user['id'], id)
	).fetchone()
	return True if c['cnt'] > 0 else False

def update_likes(db, id, is_post=True):
	which_table = 'post' if is_post else 'comment'
	db.execute(
		f'UPDATE {which_table} SET likes = ? WHERE id = ?',
		(count_likes(db, id, is_post), id)
	)
	db.commit()
	return
