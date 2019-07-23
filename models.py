from app import db

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def add_new_user(username, password):
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()

def add_new_post(title, body, owner):
    new_post = Blog(title, body, owner)
    db.session.add(new_post)
    db.session.commit()
    return new_post