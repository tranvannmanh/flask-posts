import os
import redis
from flask import Flask
from dotenv import load_dotenv
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from . import config
from . import database

db = database.db
migrate = Migrate()

load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.environ["SECRET_KEY"],
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        SQLALCHEMY_ECHO = True,
        SQLALCHEMY_DATABASE_URI = 'sqlite:///recommend_system.sqlite',
        SESSION_TYPE="redis",
        SESSION_USE_SIGNER=True,
        SESSION_REDIS=redis.from_url("redis://127.0.0.1:6379")
    )
    # app.config.from_object(config.ApplicationConfig())
    CORS(app, supports_credentials=True)
    Bcrypt(app)
    Session(app)

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth
    app.register_blueprint(auth.bp)

    from . import category
    app.register_blueprint(category.bp)

    # from . import blog
    # app.register_blueprint(blog.bp)
    
    app.add_url_rule('/', endpoint='index')

    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()

    return app