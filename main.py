from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG'] = True
project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "build-a-blog.db"))
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'pcEwO1Nlx7'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def display_blogs():
    blog_posts = Blog.query.filter_by().all()
    return render_template('blog.html', blog_posts=blog_posts)

# This route displays all blog posts, as well as individual blog posts
@app.route('/blog', methods=['POST', 'GET'])
def index():
    # Access the id of the blog clicked
    blog_id = request.args.get('id')
    # Access all blog posts
    blog_posts = Blog.query.filter_by().all()
    if blog_id != None:
        # If a blog title was clicked, show just that blog title and body on the blog page with the id as a query parameter in the URL
        post_to_display = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', post_to_display=post_to_display)
    # Otherwise display all blog posts
    return render_template('blog.html', blog_posts=blog_posts)


@app.route('/add-post', methods=['POST', 'GET'])
def add_post():
    blog_posts = Blog.query.filter_by().all()
    if request.method == 'POST': 
        # Access the title and body of the blog post submitted
        title = request.form['title']
        body = request.form['body']
        #Displaying relevant error messages
        #I legitimately couldn't figure out a more efficient way to do this, please help me
        if title == "" and body == "":
            flash("Please fill in the title", 'title_error')
            flash("Please fill in the body", 'body_error')
            return render_template('add-post.html', title=title, body=body)
        if body == "" and title != "":
            flash("Please fill in the body", 'body_error')
            return render_template('add-post.html', title=title, body=body)
        if body != "" and title == "":
            flash("Please fill in the title", 'title_error')
            return render_template('add-post.html', title=title, body=body)
        # Create a new post using the title and body submitted and the Blog class
        new_post = Blog(title, body)
        # Add the new blog post to the database and redirect to that blog post's page
        db.session.add(new_post)
        db.session.commit()
        blog_id = new_post.id
        post_to_display = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', post_to_display=post_to_display)
    # If the title or body aren't filled out properly, re-render the add-post page with relevant error messages
    return render_template('add-post.html')

if __name__ == '__main__':
    app.run()