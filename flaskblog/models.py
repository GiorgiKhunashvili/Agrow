from datetime import datetime
from flaskblog import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
import random
import time

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='5.jpg' )
	password = db.Column(db.String(60), nullable=False)
	admin = db.Column(db.Boolean, nullable=False, default=False)
	posts = db.relationship('Post', backref='author', lazy=True)
	user_comment = db.relationship('Comment', backref='author_comm', lazy=True)
	followers = db.relationship('Followers', backref='user_followers', lazy=True)
	following = db.relationship('Following', backref='user_following', lazy=True)
	likes = db.relationship('Like', backref='user_like', lazy=True)

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id':self.id}).decode('utf-8')
	def __repr__(self):
		return 'User {}, {}, {}'.format(self.username, self.email, self.image_file)



class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
	content = db.Column(db.Text, nullable=False)
	image = db.Column(db.String, nullable=True)
	view = db.Column(db.Integer, nullable=False, default=0)
	photo = db.Column(db.String, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	comment = db.Column(db.Text, nullable=True)
	post_comment = db.relationship('Comment', backref='post_comm', lazy=True)
	likes = db.relationship('Like', backref='post_like', lazy=True)

	def __repr__(self):
		return 'Post {}, {}, {}'.format(self.title, self.date_posted, self.view, self.comment)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text_comment = db.Column(db.Text, nullable=False)
	post_id_comm = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	user_id_comm = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


	def __repr__(self):
		return "Comment {}".format(self.text_comment)


class Followers(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username_for_filter_foll = db.Column(db.String, nullable=False)
	user_username =db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
	followers_num = db.Column(db.Integer, nullable=True, default=0)


class Following(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username_for_filter_folling = db.Column(db.String, nullable=False)
	user_username_foll = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
	following_num = db.Column(db.Integer, nullable=True, default=0)

class Like(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, db.ForeignKey('user.username'), nullable=True)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	likes = db.Column(db.Integer, default=0, nullable=True)

	def __repr__(self):
		return '{} {}'.format(self.post_id, self.username)


class DataApi(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	image_link = db.Column(db.String, nullable=True)
	image_file = db.Column(db.String, nullable=True)
	title = db.Column(db.String, nullable=False)
	place = db.Column(db.String, nullable=False)
	category = db.Column(db.String, nullable=False)
	land = db.Column(db.String, nullable=False)
	depth = db.Column(db.Integer, nullable=False)
	distance_from = db.Column(db.Integer, nullable=False)
	width = db.Column(db.Integer, nullable=False)
	watering = db.Column(db.String, nullable=False)
	time = db.Column(db.String, nullable=False)
	fertiizer = db.Column(db.String, nullable=False)
	to_admin = db.Column(db.Boolean, nullable=False, default=True)

	def __repr__(self):
		return '{}'.format(self.title)
