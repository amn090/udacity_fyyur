#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import ge
import psycopg2
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
connection = psycopg2.connect(user="postgres", password="postgres", database="fyyur", host="192.168.1.14", port="5432")
print("Successfully connected!")


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    venue_name = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    artist_name = db.Column(db.String(), nullable=False)
    artist_image_link = db.Column(db.String(120))
    start_time = db.Column(db.String(), nullable=False)

#db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = Venue.query.all()

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchTerm = request.form.get('search_term', '')
  searchT = "%{}%".format(searchTerm)

  response = Venue.query.filter(Venue.name.like(searchT))

  response.data = response.all()
  response.count = response.count()
  
  return render_template('pages/search_venues.html', results = response, search_term = searchTerm)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  data = Venue.query.filter_by(id=venue_id).first()
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  name = request.form.get('name', '')
  genres = request.form.get('genres', '')
  city = request.form.get('city', '')
  state = request.form.get('state', '')
  address = request.form.get('address', '')
  phone = request.form.get('phone', '')
  image_link = request.form.get('image_link', '')
  facebook_link = request.form.get('facebook_link', '')
  seeking_talent = request.form.get('seeking_talent', 'y')
  seeking_description = request.form.get('seeking_description', '')
  website = request.form.get('website', '')


  if (seeking_talent == 'y') : s_talent = 1
  else : s_talent = 0

  try:
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = image_link, facebook_link = facebook_link,
    seeking_description = seeking_description, seeking_talent = s_talent, website = website, genres = genres)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
 
  searchTerm = request.form.get('search_term', '')
  searchT = "%{}%".format(searchTerm)

  response = Artist.query.filter(Artist.name.like(searchT))

  response.data = response.all()
  response.count = response.count()

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 
  data = Artist.query.get(artist_id)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
 
  # TODO: populate form with fields from artist with ID <artist_id>
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = request.form.get('genres', '')
    artist.image_link = request.form.get('image_link', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website = request.form.get('website', '')
    seeking_venue = request.form.get('seeking_venue', 'y')
    artist.seeking_description = request.form.get('seeking_description', '')
    if (seeking_venue == 'y') : s_venue = 1
    else : s_venue = 0

    artist.seeking_venue = s_venue
    db.session.commit()
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()






  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = request.form.get('genres', '')
    artist.image_link = request.form.get('image_link', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website = request.form.get('website', '')
    seeking_venue = request.form.get('seeking_venue', 'y')
    artist.seeking_description = request.form.get('seeking_description', '')

    if (seeking_venue == 'y') : s_venue = 1
    else : s_venue = 0

    artist.seeking_venue = s_venue
    db.session.commit()
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.filter_by(id=venue_id).first()
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.phone = request.form.get('phone', '')
    venue.genres = request.form.get('genres', '')
    venue.image_link = request.form.get('image_link', '')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.website = request.form.get('website', '')
    seeking_venue = request.form.get('seeking_venue', 'y')
    venue.seeking_description = request.form.get('seeking_description', '')

    if (seeking_venue == 'y') : s_venue = 1
    else : s_venue = 0

    venue.seeking_venue = s_venue

    db.session.commit()
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website = request.form.get('website', '')
    seeking_venue = request.form.get('seeking_venue', 'y')
    seeking_description = request.form.get('seeking_description', '')

    if (seeking_venue == 'y') : s_venue = 1
    else : s_venue = 0

    artist = Artist(name = name, city = city, state = state, genres = genres, phone = phone, image_link = image_link, facebook_link = facebook_link, website = website,
    seeking_description = seeking_description, seeking_venue = s_venue)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()



  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
 
  data = Show.query.all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
    venue_id = request.form.get('venue_id', '')
    artist_id = request.form.get('artist_id', '')
    start_time = request.form.get('start_time', '')
    print(start_time)

    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    artist = Artist.query.get(artist_id)
    artist_image_link = artist.image_link
    artist_name = artist.name

    show = Show(venue_id = venue_id, venue_name = venue_name, artist_id = artist_id, artist_name = artist_name, artist_image_link = artist_image_link, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.rollback()
    flash('An error occurred.')
  finally:
    db.session.close()



  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
