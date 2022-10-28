from datetime import datetime
from blogserver import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    

class User(db.Model, UserMixin):
    """Model for storing users"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    documents = db.relationship('Document', back_populates = 'owner')
    posts = db.relationship('Post', back_populates='author', lazy=True)
    password = db.Column(db.String(60), nullable = False)
    

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
        
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"
    

class Post(db.Model):
    """Model for storing posts"""
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default= datetime.utcnow)
    content=db.Column(db.Text, nullable=False)
    documents = db.relationship("Document", secondary='post_documents', back_populates='posts')
    author = db.relationship("User", back_populates = "posts")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

class Document(db.Model):
    """Model for storing documents"""
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable = True)
    read_time = db.Column(db.Integer, nullable = False)
    presigned_url = db.Column(db.String(300), nullable=True, default = None)
    owner = db.relationship("User", back_populates = "documents")
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posts = db.relationship("Post", secondary='post_documents', back_populates='documents')

    def __repr__(self):
        return f"Document('{self.id}','{self.name}')"


class PostDocument(db.Model):
    """Model for linking posts and documents"""
    __tablename__ = 'post_documents'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id') )
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    



