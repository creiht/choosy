from flask import (
    abort, Blueprint, current_app, flash, g, redirect, render_template, request,
    url_for
)
import giphy_client
from werkzeug.exceptions import abort

from choosy.auth import login_required
from choosy import db

bp = Blueprint("star", __name__)

@bp.route("/stars")
@login_required
def index():
    gifs = []
    error = None
    more = True

    try:
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        error = "Invalid offset"
    if offset < 0:
        offset = 0
    gif_ids = db.get_starred_gifs(g.user["id"], 7, offset)
    if len(gif_ids) < 7:
        # There are no more items to load
        more = False
    else:
        # We only want the first 6
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

    return render_template("star/index.html",
                           gifs=gifs, offset=offset, more=more)
