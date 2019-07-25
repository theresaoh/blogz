from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from app import app, db
from models import User, Blog, add_new_user, add_new_post

app.secret_key = 'pcEwO1Nlx7'

def get_all_blog_posts():
    return Blog.query.all()  

def get_all_users():
    return User.query.all()

# Page displaying all Blogz users
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', users=get_all_users())

@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect("/blog")

@app.route('/login', methods=['POST', 'GET'])
def login():
    # If a user is attempting to log in
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # If the user doesn't exist, or their password is incorrect, flash error messages
        if not user:
            flash('Username invalid', 'username-error')
            return render_template('login.html')
        if password != user.password:
            flash('Password incorrect', 'password-error')
            return render_template('login.html', username=username)
        # Otherwise, log them in and redirect them to the blog page
        session['username'] = username
        return redirect('/blog')
    # Display the login template plainly if the user hasn't yet attempted login
    return render_template('login.html')

# A helper function to determine if passwords or usernames meet length criteria
def is_invalid(username_or_password):
    if len(username_or_password) < 3 or len(username_or_password) > 20:
        return True
    if username_or_password == "":
        return True
    return False

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    # If a user is attempting to sign up
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        # If the username entered matches that of an existing user, flash error
        if existing_user:
            flash('Username already exists', 'username-error')
            return render_template('signup.html')
        # If username or password are invalid, flash error
        if is_invalid(username):
            flash('Username invalid - usernames must be between 5 and 20 characters.', 'username-error')
            return render_template('signup.html')
        if is_invalid(password):
            flash('Password invalid - passwords must be between 5 and 20 characters.', 'password-invalid-error')
            return render_template('signup.html', username=username)
        # If the passwords entered don't match, flash error
        if password != verify:
            flash('Passwords don\'t match, please enter again', 'password-match-error')
            return render_template('signup.html', username=username)
        # Otherwise, enter new user into database with the information provided and add them to session
        add_new_user(username, password)
        session['username'] = username
        # Redirect them to add their first Blogz post
        return redirect('/newpost')
    # If user has not yet attempted to sign up, render signup template plainly
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
    # If a user is not currently logged in, do not display any pages other than those in this list:
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if not('username' in session or request.endpoint in allowed_routes):
        # Instead, redirect them to log in
        return redirect("/login")

if __name__ == '__main__':
    app.run()