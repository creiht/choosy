"""DB calls"""
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def get_db():
    """Helper function to get the database"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
    return g.db

def close_db(e=None):
    """Removes database object from the environment and closes it"""
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    """Initialize and wipe the database"""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

def init_app(app):
    """Register db with the app"""
    # Ensure that the db is closed after a response
    app.teardown_appcontext(close_db)
    # Register cli commands
    app.cli.add_command(init_db_command)

# TODO: This is a very simple abstraction.  If I wanted to take this
# further, I would look into using an ORM
# TODO: Add exception handling to db calls

# User functions
def get_user_by_name(username):
    """Returns a user dict if the username is found, otherwise None."""
    db = get_db()
    user_row = db.execute(
        "SELECT id, password FROM user WHERE username=?", (username, )
    ).fetchone()
    if not user_row:
        return None
    else:
        return {
            "id": user_row[0],
            "username": username,
            "password": user_row[1],
        }

def get_user_by_id(user_id):
    """Returns a user dict if the user id is found, otherwise None."""
    db = get_db()
    user_row = db.execute(
        "SELECT username, password FROM user WHERE id=?", (user_id, )
    ).fetchone()
    if not user_row:
        return None
    else:
        return {
            "id": user_id,
            "username": user_row[0],
            "password": user_row[1],
        }

def create_user(username, password):
    """Creates a user with the given username and password and returns
    the new user's ID."""
    db = get_db()
    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        (username, generate_password_hash(password))
    )
    db.commit()
    user_row = db.execute(
        "SELECT id FROM user WHERE username = ?", (username, )
    ).fetchone()
    if not user_row:
        return None
    else:
        return user_row[0]

# Star Functions
def add_star(user_id, gif_id):
    """Adds a star to a given gif for the user."""
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO star (user_id, giffy_id) VALUES (?, ?)",
        (user_id, gif_id)
    )
    db.commit()

def remove_star(user_id, gif_id):
    """Remove a star from a given gif for the user."""
    db = get_db()
    star_id = get_star_id(user_id, gif_id)
    db.execute(
        "DELETE FROM star WHERE id=?",
        (star_id, )
    )
    db.execute(
        "DELETE FROM tag_to_star WHERE star_id=?",
        (star_id, )
    )
    db.commit()

def get_star_id(user_id, gif_id):
    """Returns the star id if the gif is starred by the user, None otherwise."""
    db = get_db()
    star_row = db.execute(
        "SELECT id FROM star WHERE user_id=? AND giffy_id=?",
        (user_id, gif_id)
    ).fetchone()
    if star_row is None:
        return None
    else:
        return star_row[0]

def is_starred(user_id, gif_id):
    """Returns True if the gif is starred by the user, False otherwise."""
    star_id = get_star_id(user_id, gif_id)
    return star_id is not None

# Tag Functions
def create_tag_for_gif(user_id, tag_name, gif_id):
    """Creates a tag and maps it to a the given gif"""
    db = get_db()
    # create the tag
    db.execute(
        "INSERT OR IGNORE INTO tag (user_id, name) "
        "VALUES (?, ?)",
        (user_id, tag_name)
    )
    #TODO: Fix a slight chance of race here if the tag is deleted between
    # these two statements
    # get the tag id
    tag_row = db.execute(
        "SELECT id FROM tag WHERE user_id=? AND name=?",
        (user_id, tag_name)
    ).fetchone()
    # get the star id
    star_row = db.execute(
        "SELECT id FROM star WHERE user_id=? AND giffy_id=?",
        (user_id, gif_id)
    ).fetchone()
    # link the tag to the star
    db.execute(
        "INSERT INTO tag_to_star (tag_id, star_id) "
        "VALUES (?, ?)",
        (tag_row[0], star_row[0])
    )
    db.commit()

def get_tag_id_by_name(user_id, tag_name):
    """Returns a tag id for a given tag name and user."""
    db = get_db()
    tag_row = db.execute(
        "SELECT id FROM tag WHERE user_id=? AND name=?",
        (user_id, tag_name)
    ).fetchone()
    if tag_row is None:
        return None
    else:
        return tag_row[0]

def get_tags_for_star(user_id, gif_id):
    """Returns a list of tags for the given starred gif for a user."""
    db = get_db()
    star_id = get_star_id(user_id, gif_id)
    if star_id is None:
        return []
    else:
        return [t[0] for t in db.execute(
            "SELECT tag.name "
            "FROM tag_to_star INNER JOIN tag ON tag_to_star.tag_id = tag.id "
            "WHERE tag_to_star.star_id=?",
            (star_id,)
        )]

# Gif Functions
def get_gifs_for_tag(user_id, tag_name, limit, offset):
    """Returns a list of gif ids for a given tag and user."""
    db = get_db()
    tag_id = get_tag_id_by_name(user_id, tag_name)
    if tag_id is None:
        return []
    else:
        return [g[0] for g in db.execute(
            "SELECT star.giffy_id "
            "FROM tag_to_star INNER JOIN star ON tag_to_star.star_id=star.id "
            "WHERE tag_to_star.tag_id=? "
            "LIMIT ? offset ?",
            (tag_id, limit, offset)
        )]

def get_starred_gifs(user_id, limit, offset):
    """Returns a list of starred gif ids for a user."""
    db = get_db()
    return [g[0] for g in db.execute(
        "SELECT giffy_id FROM star WHERE user_id=? "
        "LIMIT ? offset ?",
        (user_id, limit, offset)
    )]


# Custom CLI commands

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create the DB (will re-create if it already exists)."""
    init_db()
    click.echo("DB Initialized.")

