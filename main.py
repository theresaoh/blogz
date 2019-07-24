from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from app import app, db
from models import User, Blog, add_new_user, add_new_post

app.secret_key = 'pcEwO1Nlx7'

def get_blog_posts_by_user():
    owner = User.query.filter_by(username=session['username']).first()
    return Blog.query.filter_by(owner_id=owner.id).all()

def get_all_blog_posts():
    return Blog.query.all()  

def get_all_users():
    return User.query.all()

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', users=get_all_users())

@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect("/blog")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username invalid', 'username-error')
            return render_template('login.html')
        if password != user.password:
            flash('Password incorrect', 'password-error')
            return render_template('login.html', username=username)
        session['username'] = username
        return redirect('/blog')
    return render_template('login.html')

def password_invalid(password):
    if len(password) < 3 or len(password) > 20:
        return True
    if password == "":
        return True
    return False

def username_invalid(username):
    if len(username) < 3 or len(username) > 20:
        return True
    if username == "":
        return True
    return False

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'username-error')
            return render_template('signup.html')
        if username_invalid(username):
            flash('Username invalid - usernames must be between 5 and 20 characters.', 'username-error')
            return render_template('signup.html')
        if password_invalid(password):
            flash('Password invalid - passwords must be between 5 and 20 characters.', 'password-invalid-error')
            return render_template('signup.html', username=username)
        if password != verify:
            flash('Passwords don\'t match, please enter again', 'password-match-error')
            return render_template('signup.html', username=username)
        add_new_user(username, password)
        session['username'] = username
        return redirect('/newpost')
    return render_template('signup.html')

# This route displays all blog posts, as well as individual blog posts
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    # Access the id of the blog clicked
    username = request.args.get('user')
    if username:
        user = User.query.filter_by(username=username).first()
        posts_by_user = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('blog.html', posts_by_user=posts_by_user, username=username)
    blog_id = request.args.get('id')
    if blog_id != None:
        # If a blog title was clicked, show just that blog title and body on the blog page with the id as a query parameter in the URL
        post_to_display = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', post_to_display=post_to_display) 
    # Otherwise display all blog posts
    return render_template('blog.html', blog_posts=get_all_blog_posts(), users=get_all_users())


@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    # blog_posts = Blog.query.all()
    if request.method == 'POST': 
        # Access the title and body of the blog post submitted
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        #Displaying relevant error messages
        #I legitimately couldn't figure out a more efficient way to do this, please help me
        if title == "" and body == "":
            flash("Please fill in the title", 'title_error')
            flash("Please fill in the body", 'body_error')
            return render_template('newpost.html', title=title, body=body)
        if body == "" and title != "":
            flash("Please fill in the body", 'body_error')
            return render_template('newpost.html', title=title, body=body)
        if body != "" and title == "":
            flash("Please fill in the title", 'title_error')
            return render_template('newpost.html', title=title, body=body)
        # Create a new post using the title and body submitted and the Blog class
        new_post = add_new_post(title, body, owner)
        post_to_display = Blog.query.filter_by(id=new_post.id).first()
        return render_template('blog.html', post_to_display=post_to_display)
    # If the title or body aren't filled out properly, re-render the  page with relevant error messages
    return render_template('newpost.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup', 'test']
    if not('username' in session or request.endpoint in allowed_routes):
        return redirect("/login")

if __name__ == '__main__':
    app.run()