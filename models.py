from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI
from flask_login import UserMixin
from datetime import datetime
import os

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    ads = db.relationship('Ad', backref='author_ref', lazy=True)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.now())
    image = db.Column(db.String(200)) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def generate_filename(self, user_id, filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(filename)
        return f"user_{user_id}/{timestamp}_{name[:10]}{ext}"

