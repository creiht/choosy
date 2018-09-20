"""HTTP Handlers for /gif/* calls"""
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request,
    url_for
)
import giphy_client
from werkzeug.exceptions import abort

from choosy.auth import login_required
from choosy import db

bp = Blueprint("gif", __name__)

@bp.route("/gif/<gif_id>", methods=("GET", "POST"))
@login_required
def index(gif_id):
    gifs = []
    tags = []
    error = None
    user_id = g.user["id"]

    if request.method == "POST":
        star = request.form.get("star")
        unstar = request.form.get("unstar")
        add_tag = request.form.get("add_tag")
        if star != None:
            # User has clicked the star button to add star
            db.add_star(user_id, gif_id)
        elif unstar != None:
            # User has clicked the star button to remove star
            db.remove_star(user_id, gif_id)
        elif add_tag != None:
            # User is adding a tag to the starred gif
            tag_name = request.form.get("tag")
            if tag_name is None or tag_name == "":
                error = "Tag name required."
            elif tag_name in db.get_tags_for_star(user_id, gif_id):
                error = "Tag already exists."
            else:
                if not db.is_starred(user_id, gif_id):
                    error = "Gif must be starred to add a tag."
                else:
                    db.create_tag_for_gif(user_id, tag_name, gif_id)

    if error:
        flash(error)

    starred = db.is_starred(user_id, gif_id)
    tags = db.get_tags_for_star(user_id, gif_id)

    gif = None
    try:
        giphy = giphy_client.DefaultApi()
        giphy_key = current_app.config["GIPHY_KEY"]
        resp = giphy.gifs_gif_id_get(giphy_key, gif_id)
        gif = resp.data
    except Exception as e:
        current_app.logger.error("Error loading gif from giphy: %s" % e)
        return abort(500)

    return render_template("gif/index.html",
                           gif=gif, starred=starred, tags=tags)
