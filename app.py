from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from models import db, Ad, User 
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

login_manager = LoginManager(app)
login_manager.login_view = 'login'

db.init_app(app)
with app.app_context():
    db.create_all()

@login_manager.user_loader  
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import *

if __name__ == '__main__':
    app.run(debug=True)