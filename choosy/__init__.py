"""Choosy App instantiation"""
import os

from flask import Flask

def create_app(test_config=None):
    # Try to load the giphy key
    GIPHY_KEY = os.environ.get("GIPHY_KEY", "")
    # Try to load the secret key
    # The secret key is used for password hashing
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    # Create and config the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        GIPHY_KEY=GIPHY_KEY,
        DATABASE=os.path.join(app.instance_path, "choosy.sqlite"),
    )

    if test_config is not None:
        # Load the test config
        app.config.from_mapping(test_config)
    else:
        # Load the instance config
        app.config.from_pyfile("config.py", silent=True)

    # Make sure the instanace folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Init the DB
    from . import db
    db.init_app(app)

    # Register blueprints
    from . import search
    app.register_blueprint(search.bp)
    app.add_url_rule("/", endpoint="index")

    # /auth/*
    from . import auth
    app.register_blueprint(auth.bp)

    # /gif/*
    from . import gif
    app.register_blueprint(gif.bp)

    # /tag/*
    from . import tag
    app.register_blueprint(tag.bp)

    # /stars/*
    from . import star
    app.register_blueprint(star.bp)

    return app
