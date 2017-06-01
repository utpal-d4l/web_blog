from flask import Flask, render_template, request, session, flash, redirect, url_for
from src.models.user import User
from src.models.blog import Blog
from src.models.post import Post
from src.models.userdata import UserData
from src.common.database import Database
from src.forms import EditProfile, LoginForm, RegisterForm
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = uuid.uuid4().hex


@app.before_first_request
def initialize_database():
    Database.initialize()
    session['email'] = None


@app.route('/')
def hello_method():
    if session['email'] is not None:
        return render_template('home.html', user=session['email'])
    else:
        return render_template('home.html', user='User')


@app.route('/login/')
def log_tmp():
    form = LoginForm()
    return render_template('login.html', user=session['email'] if not None else None, form=form)


@app.route('/register/')
def reg_tmp():
    form = RegisterForm()
    return render_template('register.html', user=session['email'] if not None else None, form=form)


@app.route('/auth/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is not None:
            if check_password_hash(user.password, form.password.data):
                User.login(form.email.data)
                return redirect(url_for('user_profile'))
            else:
                flash('Invalid Password.')
                return redirect(url_for('log_tmp'))
        else:
            flash('Invalid Email.')
            return redirect(url_for('log_tmp'))
    else:
        flash('Enter Valid Data.')
        return redirect(url_for('log_tmp'))


@app.route('/auth/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        if User.register(email, generate_password_hash(form.password.data)):
            flash('User registered successfully. Login to continue.')
            return redirect(url_for('log_tmp'))
        else:
            flash('User already exists. Login Instead.')
            return redirect(url_for('log_tmp'))
    else:
        flash('Enter valid email and password.')
        return redirect(url_for('reg_tmp'))


@app.route('/user/ep', methods=['GET', 'POST'])
def ep():
    if session['email'] is not None:
        form = EditProfile()
        if form.validate_on_submit():
            user_data = UserData.find_user_data(session['email'])
            if user_data is not None:
                Database.delete(collection='user_data', query={'email': session['email']})
            user_data = UserData(session['email'],
                                 form.first_name.data,
                                 form.last_name.data,
                                 form.dob.data,
                                 form.profession.data)
            user_data.save_user_data()
            flash('Your profile has been updated.')
            return redirect(url_for('user_profile'))
        else:
            flash('Enter Valid Details.')
            return redirect(url_for('edit_profile'))
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/edit_profile')
def edit_profile():
    if session['email'] is not None:
        form = EditProfile()
        return render_template('proedit.html', user=session['email'], form=form)
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/profile')
def user_profile():
    if session['email'] is not None:
        user_data = UserData.find_user_data(session['email'])
        blog_count = Blog.count_blogs(session['email'])
        post_count = Post.count_posts(session['email'])
        return render_template('pro.html',
                               user=session['email'],
                               user_data=user_data,
                               blog_count=blog_count,
                               post_count=post_count)
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/logout')
def logout():
    if session['email'] is not None:
        User.logout()
        flash('You have been logged out successfully.')
        return redirect(url_for('hello_method'))
    else:
        flash('You must Login first.')
        return redirect(url_for('log_tmp'))


@app.route('/user/cb', methods=['GET', 'POST'])
def create_blog():
    if session['email'] is not None:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            blog = Blog(session['email'], title, description)
            blog.save_blog()
            flash('Your Blog has been created.')
            return redirect(url_for('created_blog'))
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/create_blog')
def created_blog():
    if session['email'] is not None:
        return render_template('profile.html', user=session['email'])
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/view_blogs')
def view_blogs():
    if session['email'] is not None:
        blogs = Blog.find_blogs(session['email'])
        return render_template('profile1.html', user=session['email'], blogs=blogs)
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/cp', methods=['GET', 'POST'])
def create_post():
    if session['email'] is not None:
        blog_id = request.form['blog_id']
        title = request.form['title']
        content = request.form['content']
        post = Post(blog_id, title, content, session['email'])
        post.save_post()
        flash('Post successfully created.')
        return redirect(url_for('created_post'))
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/create_post')
def created_post():
    if session['email'] is not None:
        blogs = Blog.find_blogs(session['email'])
        return render_template('profile2.html', user=session['email'], blogs=blogs)
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/user/view_posts/<blog_id>')
def view_posts(blog_id):
    if session['email'] is not None:
        posts = Post.find_posts(blog_id)
        return render_template('profile3.html', user=session['email'], posts=posts)
    else:
        flash('Please Log In to access your account.')
        return redirect(url_for('log_tmp'))


@app.route('/search')
def search_form():
    return render_template('search.html', user=session['email'])


@app.route('/search/blogs', methods=['GET', 'POST'])
def search_blog():
    users = request.form['user1']
    if User.get_by_email(users) is not None:
        blogs = Blog.find_blogs(users)
        return render_template('search_blog.html', user=session['email'], users=users, blogs=blogs)
    else:
        flash('No such user found.')
        return redirect(url_for('search_form'))


@app.route('/search/posts', methods=['GET', 'POST'])
def search_post():
    users = request.form['user2']
    if User.get_by_email(users) is not None:
        posts = Post.find_post_author(users)
        return render_template('search_post.html', user=session['email'], users=users, posts=posts)
    else:
        flash('No such user found.')
        return redirect(url_for('search_form'))


if __name__ == '__main__':
    app.run(debug=True)