#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
import sys



#----------------------------------------------------------------------------#
# Application Configuration.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# connect to a local  database
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)



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



def getLocations():
  registeredLocations = Venue.query.with_entities(Venue.state, Venue.city, Venue.name, Venue.phone).distinct().all()  
  return registeredLocations

def formatLocation():
  return
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.

  data = []
  registeredLocations = getLocations()
  city = None
  state = None
  venues = None

  
  for registeredLocation in registeredLocations:
    city = registeredLocation.city
    state = registeredLocation.state
    venues = Venue.query.filter_by(city=city, state=state).all()

    venuesDetails = []
    for venue in venues:
      venueDetail = {
        'id': venue.id,
        'name': venue.name,
      }
      venuesDetails.append(venueDetail)

    details = {
      "city": city,
      "state": state,
      "venues": venuesDetails,
      "num_upcoming_shows": 1
    }

    data.append(details)
  
  return render_template('pages/venues.html', areas=data);
 
def returnSerchVenueresult(search_term):
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  return venues
  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  

      search_term = request.form.get('search_term', '').strip()
      venues = returnSerchVenueresult(search_term)

      data = []
      for venue in venues:
        venueDet = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": venue.num_upcoming_shows
        }
        data.append(venueDet)

      response = {
        "count": len(data),
        "data": data
      }


  
      # return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
      return render_template('pages/search_venues.html', results=response, search_term=search_term)

def getVenueById(venue_id):
  return Venue.query.get(venue_id) 

def getArtistById(artist_id):
  return Artist.query.get(artist_id)

def getSearchDetailForVenue(venue, pastEvents, upcoming_shows):
  return  {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "past_shows": pastEvents,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": venue.num_past_shows,
      "upcoming_shows_count": venue.num_upcoming_shows,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "past_shows": pastEvents,
      "upcoming_shows": upcoming_shows,
      "facebook_link": venue.facebook_link,
      "seeking_talent": True if venue.seeking_talent in (True, 't', 'True', 'y') else False,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link if venue.image_link else "",
      "upcoming_shows_count": venue.num_upcoming_shows,
      
    }


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
    venue = getVenueById(venue_id)

    if not venue:
      flash("Given venue with the given Id does not exist", category='error')
      return redirect(url_for('venues'))

    pastEvents = []
    for show in venue.past_shows:
      artist = getArtistById(show.artist_id)
      artistInfo = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
      }
      pastEvents.append(artistInfo)
      
    upcoming_shows = []
    for show in venue.upcoming_shows:
      artist = getArtistById(show.artist_id)
      artistInfo = {
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "artist_id": show.artist_id,
        "start_time": str(show.start_time)
      }
      upcoming_shows.append(artistInfo)

    data = getSearchDetailForVenue(venue, pastEvents, upcoming_shows)
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

def createVenueRecord(
          name, 
          city,
          state,
          address,
          phone,
          genres,
          facebook_link,
          image_link,
          website_link,
          seeking_talent,
          seeking_description):
    error = False
    try:
        venue = Venue(
          name=name, 
          city=city,
          state=state,
          address=address,
          phone=phone,
          genres=genres,
          facebook_link=facebook_link,
          image_link=image_link,
          website_link=website_link,
          seeking_talent=seeking_talent,
          seeking_description=seeking_description,
          )
        db.session.add(venue)    
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        abort(400)
    finally:
        db.session.close()
        if error:
            abort (400)
        else:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    name=request.form['name']
    city=request.form['city']
    state=request.form['state']
    address=request.form['address']
    phone=request.form['phone']
    genres=request.form['genres']
    facebook_link=request.form['facebook_link']
    image_link=request.form['image_link']
    website_link=request.form['website_link']
    seeking_talent=request.form['seeking_talent']
    seeking_description=request.form['seeking_description']

    return createVenueRecord(  
          name, 
          city,
          state,
          address,
          phone,
          genres,
          facebook_link,
          image_link,
          website_link,
          seeking_talent,
          seeking_description
        )

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # replace with real data returned from querying the database
  allArtist = Artist.query.with_entities(Artist.id, Artist.name).all()
  data = [dict(zip(artist.keys(), artist)) for artist in allArtist]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
 
    search_term = request.form.get('search_term', '').strip()

    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))

    data = []
    for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": artist.num_upcoming_shows
      })

    count = len(data)
    response = {
      "count": count,
      "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)

    if not artist:
      flash("Artist "+ str(artist_id) +"  not found!", category='error')
      return redirect(url_for('artists'))

    pastEvents = []
    for show in artist.past_shows:    
      venue = Venue.query.get(show.venue_id)
      pastEvents.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
      })

    upcomingEvents = []
    for show in artist.upcoming_shows:
      venue = Venue.query.get(show.venue_id)
      upcomingEvents.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
      })

    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "seeking_venue": True if artist.seeking_venue in ('y', True, 't', 'True') else False,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "facebook_link": artist.facebook_link,
      "website": artist.website_link,
      "past_shows_count": artist.num_past_shows,
      "upcoming_shows_count": artist.num_upcoming_shows,
      "past_shows": pastEvents,
      "upcoming_shows": upcomingEvents,
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)

    if not artist: 
      flash('Artist with Id ' + str(artist_id) + '  not found!', category='error')
      return redirect(url_for('artists'))
    
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)
  


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  status = False

  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  if not artist: 
    flash(' Artist with Id ' + str(artist_id) + '  not found!', category='error')
    return redirect(url_for('artists'))

  try:
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
    status = True
  except:
    db.session.rollback()
    status = False
    print(sys.exc_info())
  finally:
    db.session.close()

  if not status:
    # on unsuccessful db insert, flash an error instead.
    flash('Error occurred, Artist ' + request.form['name'] + ' was not edited.', category='error')
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + '  Edited successfully!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  # TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm()

    # populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)

    if not venue: 
      flash('An error occurred. Venue with ID ' + str(venue_id) + ' was not found!', category='error')
      return redirect(url_for('venues'))

    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.name.data = venue.name
    form.city.data = venue.city
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    # take values from the form submitted, and update existing
  status = False

  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  if not venue: 
    flash('Error occurred. Venue Id ' + str(venue_id) + ' not found', category='error')
    return redirect(url_for('venues'))

  try:
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.state = request.form['state']
    venue.genres = request.form.getlist('genres')
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
    status = True
  except:
    db.session.rollback()
    status = False
    print(sys.exc_info())
  finally:
    db.session.close()

  if not status:
    # on unsuccessful db insert, flash an error instead.
    flash('Error occurred, venue ' + request.form['name'] + ' was not edited.', category='error')
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was edited successfully')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    error = False

    try:
        artist = Artist(
          name=request.form['name'], 
          city=request.form['city'],
          state=request.form['state'],
          phone=request.form['phone'],
          genres=request.form['genres'],
          facebook_link=request.form['facebook_link'],
          image_link=request.form['image_link'],
          website_link=request.form['website_link'],
          seeking_venue=request.form['seeking_venue'],
          seeking_description=request.form['seeking_description'],
          )
        db.session.add(artist)    
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        abort(400)
    finally:
        db.session.close()
        if error:
            abort (400)
        else:
            
          # called upon submitting the new artist listing form
          # TODO: insert form data as a new Venue record in the db, instead
          # TODO: modify data to be the data object returned from db insertion

          # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
          # TODO: on unsuccessful db insert, flash an error instead.
          # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
          return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = db.session.query(Show).join(Venue, (Venue.id == Show.venue_id)).join(Artist, (Artist.id == Show.artist_id)).with_entities(Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time).all()

  def formatData(result):
    result = dict(zip(result.keys(), result))
    result['start_time'] = str(result['start_time'])
    return result

  data = [formatData(result) for result in data]
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
    error = False
    try:
      
        show = Show(
          venue_id=request.form['venue_id'], 
          artist_id=request.form['artist_id'],
          start_time=request.form['start_time'],
          )
        db.session.add(show)    
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        abort(400)
    finally:
        db.session.close()
        if error:
            abort (400)
        else:  
            # on successful db insert, flash success
            flash('Show was successfully listed!')
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
