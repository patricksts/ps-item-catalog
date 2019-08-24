from flask import make_response
from flask import session as login_session
from flask import Flask, render_template, request
from flask import flash, redirect, jsonify, url_for
from dbsetup import Base, Place, Thing, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
import random
import string
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item-Catalog-Project"


# CONNECT
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# CREATE TOKEN
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and(gplus_id == stored_gplus_id):
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '"style = "width: 300px; height: 300px;">'
    flash("Welcome %s" % login_session['username'])
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


class NotFoundError():
    def __init__(self, arg):
        self.args = arg


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        print("User email not found.")


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON ENDPOINTS
@app.route('/place/<int:place_id>/list/JSON')
def placeList_JSON(place_id):
    place = session.query(Place).filter_by(id=place_id).one()
    things = session.query(Thing).filter_by(
        place_id=place_id).all()
    return jsonify(
        things=[i.serialize for i in things], place=[place.serialize])


@app.route('/place/<int:place_id>/list/<int:thing_id>/JSON')
def thing_JSON(place_id, thing_id):
    Json_thing = session.query(Thing).filter_by(id=thing_id).one()
    return jsonify(Json_thing=Json_thing.serialize)


@app.route('/place/JSON')
def places_JSON():
    places = session.query(Place).all()
    return jsonify(places=[r.serialize for r in places])


# ALL PLACES
@app.route('/')
@app.route('/place/')
def showPlaces():
    places = session.query(Place).order_by(asc(Place.name))
    if 'username' not in login_session:
        return render_template('open_places.html', places=places)
    else:
        return render_template('places.html', places=places)


# NEW PLACE
@app.route('/place/new/', methods=['GET', 'POST'])
def newPlace():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newPlace = Place(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newPlace)
        flash('Your place %s is in there!' % newPlace.name)
        session.commit()
        return redirect(url_for('showPlaces'))
    else:
        return render_template('new_place.html')


# EDIT PLACE
@app.route('/place/<int:place_id>/edit/', methods=['GET', 'POST'])
def editPlace(place_id):
    editedPlace = session.query(
        Place).filter_by(id=place_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedPlace.user_id != login_session['user_id']:
        return (
            "<script>function theAlert() {alert('This ain't your place!" +
            "Make your own.');}</script><body onload='theAlert()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedPlace.name = request.form['name']
            flash('Yup. You have changed %s' % editedPlace.name)
            return redirect(url_for('showPlaces'))
    else:
        return render_template('edit_place.html', place=editedPlace)


# DELETE PLACE
@app.route('/place/<int:place_id>/delete/', methods=['GET', 'POST'])
def deletePlace(place_id):
    placeToDelete = session.query(
        Place).filter_by(id=place_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletePlace.user_id != login_session['user_id']:
        return (
            "<script>function theAlert() {alert('This ain't your place!" +
            "Make your own.');}</script><body onload='theAlert()'>")
    if request.method == 'POST':
        session.delete(placeToDelete)
        flash('%s is no more.' % placeToDelete.name)
        session.commit()
        return redirect(url_for('showPlaces', place_id=place_id))
    else:
        return render_template('delete_place.html', place=placeToDelete)


# SHOW LIST
@app.route('/place/<int:place_id>/')
@app.route('/place/<int:place_id>/list/')
def showList(place_id):
    place = session.query(Place).filter_by(id=place_id).one()
    # creator = getUserInfo(place.user_id)
    things = session.query(Thing).filter_by(place_id=place_id).all()
    print("Place: " + place.name)
    for i in things:
        print("thing: " + i.name)

    if 'username' not in login_session:
        #  or creator.id != login_session['user_id']
        return render_template('open_list.html', things=things, place=place)
    else:
        return render_template('list.html', things=things, place=place)


# NEW THING
@app.route('/place/<int:place_id>/list/new/', methods=['GET', 'POST'])
def newThing(place_id):
    if 'username' not in login_session:
        return redirect('/login')
    place = session.query(Place).filter_by(id=place_id).one()
    if request.method == 'POST':
        newThing = Thing(
            name=request.form['name'],
            description=request.form['description'],
            category=request.form['category'],
            place_id=place_id, user_id=place.user_id)
        session.add(newThing)
        session.commit()
        flash('New thing %s is in there' % (newThing.name))
        return redirect(url_for('showList', place_id=place_id))
    else:
        return render_template('new_thing.html', place_id=place_id)


# EDIT THING
@app.route(
    '/place/<int:place_id>/list/<int:thing_id>/edit',
    methods=['GET', 'POST'])
def editThing(place_id, thing_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedThing = session.query(Thing).filter_by(id=thing_id).one()
    place = session.query(Place).filter_by(id=place_id).one()
    if login_session['user_id'] != place.user_id:
        return (
            "<script>function myFunction()" +
            "{alert('This is not your thing!');}</script>" +
            "<body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedThing.name = request.form['name']
        if request.form['description']:
            editedThing.description = request.form['description']
        if request.form['category']:
            editedThing.category = request.form['category']
        session.add(editedThing)
        session.commit()
        flash('Your thing has been changed.')
        return redirect(url_for('showList', place_id=place_id))
    else:
        return render_template(
            'edit_thing.html',
            place_id=place_id,
            thing_id=thing_id, thing=editedThing)


# DELETE THING
@app.route(
    '/place/<int:place_id>/list/<int:thing_id>/delete',
    methods=['GET', 'POST'])
def deleteThing(place_id, thing_id):
    if 'username' not in login_session:
        return redirect('/login')
    place = session.query(Place).filter_by(id=place_id).one()
    thingToDelete = session.query(Thing).filter_by(id=thing_id).one()
    if login_session['user_id'] != place.user_id:
        return (
            "<script>function myFunction()" +
            "{alert('This is not your thing!');}</script>" +
            "<body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(thingToDelete)
        session.commit()
        flash('Your thing is gone.')
        return redirect(url_for('showList', place_id=place_id))
    else:
        return render_template('delete_thing.html', thing=thingToDelete)


# DISCONNECT
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You are out of here.")
        return redirect(url_for('showPlaces'))
    else:
        flash("Um I don't think you ever signed in...")
        return redirect(url_for('showPlaces'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run()
