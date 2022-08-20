# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import dateutil.parser
from datetime import timezone, datetime
import babel
import logging
from logging import Formatter, FileHandler
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
    abort,
)
from flask_moment import Moment
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from forms import *
from models import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
csrf = CSRFProtect(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
        if format == "full":
            format = "EEEE MMMM, d, y 'at' h:mma"
        elif format == "medium":
            format = "EE MM, dd, y h:mma"
    else:
        date = value
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():

    # on recupères les différentes villes et Etats et on les filtres
    distinct_city_state = (
        Venue.query.distinct(Venue.city, Venue.state)
        .order_by(Venue.city, Venue.state)
        .all()
    )

    # data est une liste qui contiendra les valeurs à renvoyer à la vue
    data = []

    # Pour chaque Villes et Etats ajoutons à @data les données à renvoyer à la vue
    for i in distinct_city_state:
        data.append(
            {
                "city": i.city,
                "state": i.state,
                "venues": Venue.query.filter(
                    Venue.city == i.city, Venue.state == i.state
                ).all(),
            }
        )
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # on récupère le mot recherché
    search_term = request.form.get("search_term")
    # recherchons la dans notre database
    venues_founds = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    # renvoyons le résultat sous forme d'objet
    response = {"count": len(venues_founds), "data": venues_founds}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue_found = Venue.query.filter(Venue.id == venue_id).one_or_none()
    if venue_found is None:
        abort(404)
    else:

        # --------restructurons les données trouvées

        # liste de genres valide
        genres_enabled = [
            "Alternative",
            "Blues",
            "Classical",
            "Country",
            "Electronic",
            "Folk",
            "Funk",
            "Hip-Hop",
            "Heavy Metal",
            "Instrumental",
            "Jazz",
            "Musical Theatre",
            "Pop",
            "Punk",
            "R&B",
            "Reggae",
            "Rock n Roll",
            "Soul",
            "Other",
        ]

        # va contenir la liste de genres sous forme de string
        stringfy_genres_list = ""

        # convetissons le tuple en chaine
        for genre in venue_found.genres:
            stringfy_genres_list += genre

        # va contenir la liste de genres qui sera renvoyé à la vue
        genres_reformated = []

        # remplissons la liste qui sera envoyé à la vue
        for genre in genres_enabled:

            # on vérifie si la liste de genres valide à des correspondances dans notre liste parsé en string
            # si il y a correspondance  on remplie la nouvelle liste
            if re.search(genre, stringfy_genres_list):

                genres_reformated.append(genre)

        # -------créons maintenant l'objet qui sera rendu
        data = {
            "id": venue_found.id,
            "name": venue_found.name,
            "city": venue_found.city,
            "genres": genres_reformated,
            "state": venue_found.state,
            "phone": venue_found.phone,
            "address": venue_found.address,
            "image_link": venue_found.image_link,
            "facebook_link": venue_found.facebook_link,
            "website": venue_found.website_link,
            "seeking_talent": venue_found.seeking_talent,
            "seeking_description": venue_found.seeking_description,
            "upcoming_shows": [
                show
                for show in Show.query.filter(
                    Show.start_time > datetime.now(), Show.venue == venue_found.id
                ).all()
            ],
            "past_shows": [
                show
                for show in Show.query.filter(
                    Show.start_time < datetime.now(timezone.utc),
                    Show.venue == venue_found.id,
                ).all()
            ],
            "upcoming_shows_count": len(
                Show.query.filter(
                    Show.start_time > datetime.now(timezone.utc),
                    Show.venue == venue_found.id,
                ).all()
            ),
            "past_shows_count": len(
                Show.query.filter(
                    Show.start_time < datetime.now(timezone.utc),
                    Show.venue == venue_found.id,
                ).all()
            ),
        }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    csrf.protect()
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    csrf.protect()
    form = VenueForm()

    errors_occurred = False

    if form.validate_on_submit():

        # traitons les données récupérées
        name = form.name.data.strip()
        genres = form.genres.data
        address = form.address.data
        city = form.city.data.strip()
        state = form.state.data
        phone = form.phone.data.strip()
        facebook_link = form.facebook_link.data.strip()
        image_link = form.image_link.data.strip()
        website_link = form.website_link.data.strip()
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data.strip()

        print(f"genres before:{genres}")
    else:
        errors_occurred = True
        for error in form.errors:
            flash("please enter a valid data...check (" + error + ") input")

        return redirect(url_for("create_venue_submission"))

    if not errors_occurred:
        try:
            new_venue = Venue(
                name=name,
                genres=genres,
                address=address,
                city=city,
                state=state,
                phone=phone,
                facebook_link=facebook_link,
                image_link=image_link,
                website_link=website_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description,
            )
            db.session.add(new_venue)
            db.session.commit()

            # on successful db insert, flash success
            flash("Venue " + request.form["name"] + " was successfully listed!")

        except Exception as e:
            db.session.rollback()
            print(f'Exception "{e}" in create_venue_submission()')
            flash(
                "An error occurred. Venue "
                + request.form["name"]
                + " could not be listed."
            )

        finally:
            db.session.close()

    return render_template("pages/home.html")


#  Update  Venue
#  ----------------------------------------------------------------
@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    csrf.protect()

    venue = Venue.query.get(venue_id)

    form = VenueForm(obj=venue)

    venue = {
        "id": venue_id,
        "name": venue.name,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
    }
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    csrf.protect()

    form = VenueForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website_link = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate_on_submit():
        flash(form.errors)
        return redirect(url_for("edit_venue_submission", venue_id=venue_id))

    else:
        error_an_occured = False

        try:
            venue = {
                "name": name,
                "city": city,
                "genres": genres,
                "state": state,
                "phone": phone,
                "website_link": website_link,
                "facebook_link": facebook_link,
                "seeking_talent": seeking_talent,
                "seeking_description": seeking_description,
                "image_link": image_link,
            }

            db.session.query(Venue).filter(Venue.id == venue_id).update(venue)
            db.session.commit()

        except Exception as e:
            error_an_occured = True
            print(f'Exception "{e}" in edit_venue_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_an_occured:
            flash("Venue " + request.form["name"] + " was successfully updated!")
        else:
            print("Error in edit_venue_submission()")
            flash("An error occurred. Venue " + name + " could not be updated.")
    return redirect(url_for("show_venue", venue_id=venue_id))


#  DELETE Venue
#  ----------------------------------------------------------------
@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash("Venue is deleted succesfuly")
        return jsonify({"success": True})
    except:
        db.session.rollback()
        flash("ERROR Venue is not deleted! ")
        return jsonify({"success": False})
    finally:
        db.session.close()


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artist_found = Artist.query.all()
    data = []
    for artist in artist_found:
        data.append({"id": artist.id, "name": artist.name})

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():

    search_term = request.form.get("search_term")
    artist_founds = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {"count": len(artist_founds), "data": artist_founds}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    artist_found = Artist.query.filter(Artist.id == artist_id).one_or_none()
    if artist_found is None:
        abort(404)
    else:
        # --------restructurons les données trouvées

        # liste de genres valide
        genres_enabled = [
            "Alternative",
            "Blues",
            "Classical",
            "Country",
            "Electronic",
            "Folk",
            "Funk",
            "Hip-Hop",
            "Heavy Metal",
            "Instrumental",
            "Jazz",
            "Musical Theatre",
            "Pop",
            "Punk",
            "R&B",
            "Reggae",
            "Rock n Roll",
            "Soul",
            "Other",
        ]

        # va contenir la liste de genres sous forme de string
        stringfy_genres_list = ""

        # convetissons le tuple en chaine
        for genre in artist_found.genres:
            stringfy_genres_list += genre

        # va contenir la liste de genres qui sera renvoyé à la vue
        genres_reformated = []

        # remplissons la liste qui sera envoyé à la vue
        for genre in genres_enabled:

            # on vérifie si la liste de genres valide à des correspondances dans notre liste parsé en string
            # si il y a correspondance  on remplie la nouvelle liste
            if re.search(genre, stringfy_genres_list):

                genres_reformated.append(genre)
        data = {
            "id": artist_found.id,
            "name": artist_found.name,
            "genres": genres_reformated,
            "city": artist_found.city,
            "state": artist_found.state,
            "phone": artist_found.phone,
            "image_link": artist_found.image_link,
            "facebook_link": artist_found.facebook_link,
            "website": artist_found.website_link,
            "seeking_venue": artist_found.seeking_venue,
            "seeking_description": artist_found.seeking_description,
            "upcoming_shows": [
                show
                for show in Show.query.filter(
                    Show.start_time > datetime.now(), Show.artist == artist_found.id
                ).all()
            ],
            "past_shows": [
                show
                for show in Show.query.filter(
                    Show.start_time < datetime.now(), Show.artist == artist_found.id
                ).all()
            ],
            "upcoming_shows_count": len(
                Show.query.filter(
                    Show.start_time > datetime.now(), Show.artist == artist_found.id
                ).all()
            ),
            "past_shows_count": len(
                Show.query.filter(
                    Show.start_time < datetime.now(), Show.artist == artist_found.id
                ).all()
            ),
        }
    data = list(filter(lambda d: d["id"] == artist_id, [data]))[0]
    return render_template("pages/show_artist.html", artist=data)


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    csrf.protect()
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    csrf.protect()

    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website_link = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate_on_submit():
        flash(form.errors)
        return redirect(url_for("create_artist_submission"))

    else:
        error_an_occured = False

        # Insérons les données dans la BD
        try:

            new_artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description,
                image_link=image_link,
                website_link=website_link,
                facebook_link=facebook_link,
            )

            db.session.add(new_artist)
            db.session.commit()

        except Exception as e:
            error_an_occured = True
            print(f'Exception "{e}" in create_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_an_occured:
            # on successful db insert, flash success
            flash("Artist " + request.form["name"] + " was successfully listed!")
            return redirect(url_for("index"))
        else:
            flash("An error occurred. Artist " + name + " could not be listed.")
            print("Error in create_artist_submission()")
            abort(500)


#  Update Artist
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    csrf.protect()

    artist = Artist.query.get(artist_id)

    form = ArtistForm(obj=artist)

    artist = {
        "id": artist_id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
    }
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    csrf.protect()

    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website_link = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate_on_submit():
        flash(form.errors)
        return redirect(url_for("edit_artist_submission", artist_id=artist_id))

    else:
        error_an_occured = False

        try:
            artist = {
                "name": name,
                "city": city,
                "genres": genres,
                "state": state,
                "phone": phone,
                "website_link": website_link,
                "facebook_link": facebook_link,
                "seeking_venue": seeking_venue,
                "seeking_description": seeking_description,
                "image_link": image_link,
            }

            db.session.query(Artist).filter(Artist.id == artist_id).update(artist)
            db.session.commit()

        except Exception as e:
            error_an_occured = True
            print(f'Exception "{e}" in edit_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_an_occured:
            # on successful db update, flash success
            flash("Artist " + request.form["name"] + " was successfully updated!")
        else:
            flash("An error occurred. Artist " + name + " could not be updated.")

    return redirect(url_for("show_artist", artist_id=artist_id))


#  DELETE Artist
#  ----------------------------------------------------------------
@app.route("/artist/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):

    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
        flash("Artist is deleted succesfuly")
        return jsonify({"success": True})
    except:
        db.session.rollback()
        flash("ERROR Artist is not deleted! ")
        return jsonify({"success": False})
    finally:
        db.session.close()


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    show_founds = Show.query.all()
    data = []

    for show in show_founds:

        data.append(
            {
                "show_id": show.id,
                "venue_id": show.Venue.id,
                "venue_name": show.Venue.name,
                "artist_id": show.Artist.id,
                "artist_name": show.Artist.name,
                "artist_image_link": show.Artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/show/search", methods=["POST"])
def search_show():

    search_term = request.form.get("search_term")
    error_occurs = False
    try:
        show_founds = Show.query.filter_by(id=search_term).all()
    except:
        error_occurs = True
        flash("show can only be searched by id")
        return redirect(url_for("shows"))
    finally:
        if not error_occurs:
            response = {"count": len(show_founds), "data": show_founds}
    return render_template(
        "pages/show.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


#  CREATE  Shows
#  ----------------------------------------------------------------


@app.route("/shows/create", methods=["GET"])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm()

    artist = form.artist_id.data.strip()
    venue = form.venue_id.data.strip()
    start_time = form.start_time.data

    error_an_occured = False

    try:
        new_show = Show(start_time=start_time, artist=artist, venue=venue)
        db.session.add(new_show)
        db.session.commit()
    except Exception as e:
        error_an_occured = True
        db.session.rollback()
        print(f'Exception "{e}" in create_show_submission()')
    finally:
        db.session.close()

    if error_an_occured:
        flash(f"An error occurred.  Show could not be listed.")
    else:
        flash("Show was successfully listed!")

    return render_template("pages/home.html")


# ERROR Handler.
# ----------------------------------------------------------------------------#


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
