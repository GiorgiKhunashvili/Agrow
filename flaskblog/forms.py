from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username',
							validators=[DataRequired(),Length(min=2, max=20)])
	email = StringField('Email',
							validators=[DataRequired(),Email()])
	password = PasswordField('Password',
							validators=[DataRequired(),Length(min=6, max=16)])
	confrim_password = PasswordField('Confrim Password',
							validators=[DataRequired(),EqualTo('password')])
	admin = BooleanField('Admin')
	submit = SubmitField('Sign up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is already take. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is already take. Please choose a different one.')


class LoginForm(FlaskForm):
	email = StringField('Email',
						validators=[DataRequired(),Email()])
	password = PasswordField('Password',
						validators=[DataRequired()])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	username = StringField('Username',
							validators=[DataRequired(),Length(min=2, max=20)])
	email = StringField('Email',
							validators=[DataRequired(),Email()])
	picture = FileField('Update profile picture',
						validators=[FileAllowed(['jpg', 'png'])])

	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is already take. Please choose a different one.')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is already take. Please choose a different one.')


class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	image = FileField('Upload image', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Post')


class CommentForm(FlaskForm):
	comment_text = TextAreaField('Write Comment', validators=[DataRequired()])
	submit = SubmitField('Write Comment')


class FollowersForm(FlaskForm):
	unfollow = SubmitField('Unfollow')
	submit = SubmitField('Follow')


class PostFormAdmin(FlaskForm):
	title = StringField('title',validators=[DataRequired()])
	place = StringField('place', validators=[DataRequired()])
	image_link = StringField('image link', validators=[DataRequired()])
	category = StringField('category', validators=[DataRequired()])
	land = StringField('land', validators=[DataRequired()])
	depth = IntegerField('depth', validators=[DataRequired()])
	width = IntegerField('width', validators=[DataRequired()])
	distance_form = IntegerField('distance_form', validators=[DataRequired()])
	watering = StringField('watering', validators=[DataRequired()])
	time = StringField('time', validators=[DataRequired()])
	fertiizer = StringField('fertiizer', validators=[DataRequired()])
	submit = SubmitField('Post')

class AdminForm(FlaskForm):
	Success = SubmitField('Success')
	Delete = SubmitField('Delete')

class MapForm(FlaskForm):
	Number = IntegerField('number', validators=[DataRequired()])
	submit = SubmitField('Submit')