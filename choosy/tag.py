"""HTTP Handlers for /tag/* calls"""
from flask import (
    abort, Blueprint, current_app, flash, g, redirect, render_template, request,
    url_for
)
import giphy_client
from werkzeug.exceptions import abort

from choosy.auth import login_required
from choosy import db

bp = Blueprint("tag", __name__)

@bp.route("/tag/<tag_name>")
@login_required
def index(tag_name):
    gifs = []
    error = None
    more = True

    try:
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        error = "Invalid offset"
    if offset < 0:
        offset = 0

    # NOTE: we are getting 7 rows so that we can know if there is more
    # data to load
    gif_ids = db.get_gifs_for_tag(g.user["id"], tag_name, 7, offset)

    current_app.logger.info("ids: %s" % gif_ids)
    if len(gif_ids) < 7:
        # There are no more items to load
        more = False
    else:
        # We only need the first 6
        gif_ids = gif_ids[:-1]

    for gif_id in gif_ids:
        try:
            giphy = giphy_client.DefaultApi()
            giphy_key = current_app.config["GIPHY_KEY"]
            # TODO: do this async
            resp = giphy.gifs_gif_id_get(giphy_key, gif_id)
            gifs.append(resp.data)
        except Exception as e:
            current_app.logger.error("Error loading gif from giphy: %s" % e)
            return abort(500)

    return render_template("tag/index.html",
                           gifs=gifs, offset=offset, more=more,
                           tag_name=tag_name)
