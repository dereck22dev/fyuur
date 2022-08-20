# ----------------------------------------------------------------------------#
# Imports.
# ----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY


# ----------------------------------------------------------------------------#
# init.
# ----------------------------------------------------------------------------#
db = SQLAlchemy()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(ARRAY(db.String()))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String())
    show = db.relationship("Show", backref="Venue", cascade="all, delete", lazy=True)


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String())
    show = db.relationship("Show", backref="Artist", cascade="all, delete", lazy=True)


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue = db.Column(
        db.Integer, db.ForeignKey("Venue.id", ondelete="cascade"), nullable=False
    )
    artist = db.Column(
        db.Integer, db.ForeignKey("Artist.id", ondelete="cascade"), nullable=False
    )
