from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from blogserver.config import Config
import boto3

db = SQLAlchemy()
aws_config = Config()
dynamo_db= boto3.resource('dynamodb',
                        aws_access_key_id = aws_config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key = aws_config.AWS_SECRET_KEY)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = 'info'

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from blogserver.users.routes import users
    from blogserver.posts.routes import posts
    from blogserver.main.routes import main
    from blogserver.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app