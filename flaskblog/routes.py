import os
import secrets
from PIL import Image
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post, Comment, Followers, Following, DataApi, Like
from flaskblog.forms import(RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm, FollowersForm, PostFormAdmin, 
							AdminForm, MapForm)
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts)

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data,
					 email=form.email.data, password=hashed_password, admin=form.admin.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			flash('You have been logged in!', 'success')
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful Please check username and password', 'danger')
	return render_template('login.html', title="Login", form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture,current_picture, path):
	random_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn =random_hex + f_ext
	picture_path = os.path.join(app.root_path, path, picture_fn)
	del_picture_path = os.path.join(app.root_path, path, current_picture)
	output_size = (125, 125)
	resized_image = Image.open(form_picture)
	resized_image.thumbnail(output_size)
	if current_picture != '5.jpg':
		os.remove(del_picture_path)
	resized_image.save(picture_path)
	return picture_fn

def save_post_picture(form_picture):
	random_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)
	output_size = (835, 350)
	resized_image = Image.open(form_picture)
	resized_image.thumbnail(output_size)
	resized_image.save(picture_path)
	return picture_fn

@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data, current_user.image_file, 'static/profile_pics')
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email


	image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account',
							 image_file=image_file, form=form)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		if form.image.data:
			post_photo = save_post_picture(form.image.data)
		post = Post(title=form.title.data, content=form.content.data, author=current_user,
		 			date_posted=datetime.now(), photo = post_photo)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post',
	 						form=form, legend='New Post')


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
	post = Post.query.get_or_404(post_id)
	comments = Comment.query.filter_by(post_id_comm=post_id).all()
	likes = Like.query.filter_by(post_id=post_id, username=current_user.username)
	# likes_2 = Like.query.filter_by(post_id=post_id, username=current_user.username)
	number_of_likes = Like.query.filter_by(post_id=post_id).count()

	form = CommentForm()
	if request.method == 'GET':
		post.view +=1
		db.session.commit()

	if request.method == 'POST':
		if form.validate_on_submit():
			new_comment = Comment(text_comment=form.comment_text.data, post_id_comm=post_id,
								 user_id_comm=current_user.id)
			db.session.add(new_comment)
			db.session.commit()
			return redirect(url_for('home'))

	return render_template('post.html', title=post.title, post=post, form=form, comments=comments,
										 likes=likes, number_of_likes=number_of_likes)



@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Update Post', post=post,
	 						form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	comments = Comment.query.filter_by(post_id_comm=post_id).all()
	if post.author != current_user:
		abort(403)
	for i in comments:
		db.session.delete(i)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))

@app.route('/user/<string:username>', methods=['GET'])
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())\
								.paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)


@app.route('/userinfo/<string:username>', methods=['GET', 'POST'])
def user_info(username):
	user = User.query.filter_by(username=username).first_or_404()
	image_file = url_for('static',filename='profile_pics/' + user.image_file)
	form = FollowersForm()
	user_followers = Followers.query.filter_by(username_for_filter_foll=username)
	user_followings = Following.query.filter_by(username_for_filter_folling=username)
	count_followers = 0
	for i in user_followers:
		print(i.user_username)
		count_followers += 1
	print(count_followers)
	list_of_followers = []
	for z in user_followers:
		list_of_followers.append(z.user_username)
	print(list_of_followers)
	if request.method =='POST':

		following_user = Followers(username_for_filter_foll=user.username, user_username=current_user.username)
		save_following = Following(username_for_filter_folling=current_user.username, user_username_foll=user.username)
		db.session.add(following_user)
		db.session.add(save_following)
		db.session.commit()
		return redirect(request.url)
	return render_template('user_info.html', image_file=image_file,	user=user, form=form,
											user_followers=user_followers, user_followings=user_followings,
											count_followers=count_followers, list_of_followers=list_of_followers)

@app.route('/userinfo/<string:username>/unfollow', methods=['GET','POST'])
@login_required
def unfollow_user(username):
	unfollow = Followers.query.filter_by(username_for_filter_foll=username,user_username=current_user.username)

	current_user_list = []
	for user_username_unfollow in unfollow:
		current_user_list.append(user_username_unfollow.user_username)
	print(current_user_list)
	if request.method == 'POST':
		if current_user.username not in current_user_list:
			abort(403)

	unfollow = Followers.query.filter_by(username_for_filter_foll=username,user_username=current_user.username).delete()
	db.session.commit()
	return redirect(url_for('user_info', username=username))

@app.route('/store')
def store():
	data = DataApi.query.all()

	return render_template('store.html', data=data)


@app.route('/fruit_info/<string:fruit_name>', methods=['GET', 'POST'])
def fruit_info(fruit_name):
	fruit = DataApi.query.filter_by(title=fruit_name).first_or_404()
	form = AdminForm()
	if request.method == 'POST':
		fruit.to_admin = False
		db.session.commit()
		return redirect(url_for('store'))

	return render_template('fruit_info.html', fruit=fruit, form=form)

@app.route('/fruit_info/<string:fruit_name>/delete', methods=['GET', 'POST'])
def delete_fruit(fruit_name):
	fruit = DataApi.query.filter_by(title=fruit_name).first_or_404()
	if request.method == 'POST':
		db.session.delete(fruit)
		db.session.commit()
		return redirect(url_for('home'))

@app.route('/api/', methods=['GET'])
def get_api():
	api_data = DataApi.query.all()
	list_of_data = []
	for data in api_data:
		json_data = {'title': data.title,
						'place': data.place,
						'category': data.category,
						'image_link':data.image_link,
						'land': data.land,
						'depth':data.depth,
						'distance_from':data.distance_from,
						'width':data.width,
						'watering':data.watering,
						'time':data.time,
						'fertiizer':data.fertiizer}
		#json_data = json.dumps(json_data, ensure_ascii=False).encode('utf8')
		list_of_data.append(json_data)
		return jsonify({'item':list_of_data})


# @app.route('/postapidata', methods=['GET', 'POST'])
# def post_data():
# 	form = PostFormAdmin()
# 	if request.method == 'POST':
# 		save_api = DataApi(title=form.title.data, place=form.place.data, category=form.category.data, land=form.land.data, 
# 							depth=form.depth.data, width=form.width.data, distance_from=form.distance_form.data,
# 							 watering=form.watering.data, time=form.time.data, fertiizer=form.fertiizer.data,
# 							  image_link=form.image_link.data)
# 		db.session.add(save_api)
# 		db.session.commit()
# 		return redirect(url_for('home'))

# 	return render_template('post_api_data.html', form=form)

@app.route('/items/api')
def get_all_item():
	get_data = DataApi.query.all()
	json_data = []
	for data in get_data:
		json_data_dict = {
							"title": data.title,
							"image": data.image_link
						}
		json_data.append(json_data_dict)

	return jsonify({'items':json_data})


@app.route('/requests', methods=['GET', 'POST'])
def user_requests():
	form = PostFormAdmin()
	if request.method == 'POST':
		save_data = DataApi(title=form.title.data, place=form.place.data, category=form.category.data, land=form.land.data, 
							depth=form.depth.data, width=form.width.data, distance_from=form.distance_form.data,
							watering=form.watering.data, time=form.time.data, fertiizer=form.fertiizer.data,
							image_link=form.image_link.data)
		
		db.session.add(save_data)
		db.session.commit()
		return redirect(url_for('home'))
	return render_template('post_api_data.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
	data_for_admin = DataApi.query.filter_by(to_admin=True)

	return render_template('admin.html', data_for_admin=data_for_admin)

@app.route('/map', methods=['GET', 'POST'])
def map():
	form = MapForm()
	number = 5	

		# if form.validate_on_submit():
		# get_number = form.Number.data
		# get_number = get_number // 5
		# number_lst.append(get_number)
		# redirect(request.url)
	return render_template('map.html', form=form, number=number)

@app.route('/likes/<int:post_id>/', methods=['GET', 'POST'])
@login_required
def post_like(post_id):
	likes = Like.query.filter_by(post_id=post_id)

	if request.method == 'POST':
		save_like = Like(username=current_user.username, post_id=post_id, likes=1)
		db.session.add(save_like)
		db.session.commit()
	return redirect(url_for('post', post_id=post_id))

@app.route('/likes/<int:post_id>/unlike', methods=['GET', 'POST'])
@login_required
def post_unlike(post_id):
	if request.method == 'POST':
		filter_like = Like.query.filter_by(post_id=post_id, username=current_user.username).delete()
		db.session.commit()

	return redirect(url_for('post', post_id=post_id))
