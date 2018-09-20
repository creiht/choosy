"""HTTP Handlers for /* search calls"""
from flask import (
    abort, Blueprint, current_app, flash, g, redirect, render_template, request,
    url_for
)
import giphy_client
from werkzeug.exceptions import abort

from choosy.auth import login_required

bp = Blueprint("search", __name__)

@bp.route("/")
@login_required
def index():
    gifs = []
    error = None
    search = request.args.get("search", "")
    try:
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        error = "Invalid offset"
    if offset < 0:
        error = "Invalid offset"

    if error:
        flash(error)
    elif search != "":
        try:
            giphy = giphy_client.DefaultApi()
            giphy_key = current_app.config["GIPHY_KEY"]
            # TODO: Make this async
            resp = giphy.gifs_search_get(giphy_key, search,
                                            limit=6,
                                            offset=offset,
                                            rating="g",
                                            lang="en",
                                            fmt="json")
            gifs = resp.data
            current_app.logger.info(gifs[0])
        except Exception as e:
            current_app.logger.error("Error loading gifs from giphy: %s" % e)
            return abort(500)

    return render_template("search/index.html",
                           gifs=gifs, search=search, offset=offset)
