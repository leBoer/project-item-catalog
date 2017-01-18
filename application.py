from flask import (Flask, render_template, request, redirect,
                   jsonify, url_for, flash)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# For time stamping print statements
from datetime import datetime

# Imports for credentials
from flask import session as login_session
from flask import make_response
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import random
import string
import requests

# CLIENT_ID = json.loads(
#     open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
                       encoding='utf8')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON API's to view information
@app.route('/catalog/users/json')
def usersJSON():
    users = session.query(User).all()
    return jsonify(users=[u.serialize for u in users])


@app.route('/catalog/categories/json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/items/json')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/item/<int:item_id>/json')
def itemJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


# Gives the full catalog with categories and items in one JSON
@app.route('/catalog/json')
def catalogJSON():
    categories = session.query(Category).all()
    serializedCategories = []
    for c in categories:
        new_category = c.serialize
        items = session.query(Item).filter_by(category_id=c.id).all()
        serializedItems = []
        for i in items:
            serializedItems.append(i.serialize)
        new_category['items'] = serializedItems
        serializedCategories.append(new_category)
    return jsonify(categories=[serializedCategories])


# Front page with all categories and latest item
@app.route('/')
def showFront():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).order_by(desc(Item.created)).limit(10).all()
    if 'username' not in login_session:
        return render_template('front.html',
                               categories=categories,
                               items=items)
    else:
        return render_template('front.html',
                               categories=categories,
                               items=items,
                               username=login_session['username'])


# Shows items within a category
@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).filter_by(category_id=category.id).all()
    if 'username' not in login_session:
        return render_template('category.html',
                               category=category,
                               categories=categories,
                               items=items)
    else:
        return render_template('category.html',
                               category=category,
                               categories=categories,
                               items=items,
                               username=login_session['username'])


# Shows a description of a specific item.
# Note that I would have preferred to include the unique ID's in the route,
# but this choice seemed to be a requirement for the project. I will have
# to make sure that the names are unique as well.
@app.route('/catalog/<category_name>/<item_name>/')
def showItem(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return render_template('item.html',
                               item=item)
    else:
        return render_template('item.html',
                               item=item,
                               username=login_session['username'])


# Lets a logged in user create a new item
@app.route('/newitem', methods=['GET', 'POST'])
def newItem():
    if 'username' in login_session:
        if request.method == 'POST':
            category = session.query(Category).filter_by(
                name=request.form['category']).one()
            item = Item(name=request.form['name'],
                        description=request.form['description'],
                        category=category,
                        user_id=login_session['user_id'])
            session.add(item)
            session.commit()
            flash("New item %s successfully created" % item.name)
            return redirect(url_for('showItem',
                                    category_name=item.category.name,
                                    item_name=item.name))
        else:
            return render_template('newitem.html')
    else:
        flash("You must be logged in to create a new item")
        return redirect(url_for('showFront'))


# Lets the creator of an item edit the item
@app.route('/catalog/<item_name>/edit/', methods=['GET', 'POST'])
def editItem(item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    if 'username' in login_session:
        user_id = getUserId(login_session['email'])
        if user_id != item.user_id:
            flash('You are not the creator of this item')
            return redirect(url_for('showFront'))
        if request.method == 'POST' and user_id == item.user_id:
            category = session.query(Category).filter_by(
                name=request.form['category']).one()
            item.name = request.form['name']
            item.description = request.form['description']
            item.category = category
            session.add(item)
            session.commit()
            flash('Item has been successfully edited')
            return redirect(url_for('showItem',
                                    category_name=request.form['category'],
                                    item_name=item.name,
                                    item=item))
        else:
            return render_template('edititem.html',
                                   item_name=item.name,
                                   item=item)
    else:
        return render_template('item.html',
                               item=item,
                               item_name=item.name,
                               category_name=item.category.name)


@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    if 'username' in login_session:
        user_id = getUserId(login_session['email'])
        if user_id != item.user_id:
            flash('You are not the creator of this item')
            return redirect(url_for('showFront'))
        if request.method == 'POST' and user_id == item.user_id:
            session.delete(item)
            session.commit()
            flash("Item has been successfully deleted")
            return redirect(url_for('showFront'))
        else:
            return render_template('deleteitem.html',
                                   item=item)
    else:
        return redirect(url_for('showFront'))

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # Render the login template
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s" % access_token

    # Exchange client token for long-lived server-side token with GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.2/me"
    # Strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s" % url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split('=')[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # See if user exists
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output





# Disconnect functions
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        # if login_session['provider'] == 'google':
            # gdisconnect()
            # del login_session['gplus_id']
            # del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showFront'))
    else:
        flash("You were not logged in to begin with!")
        redirect(url_for('showFront'))


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    print access_token
    print facebook_id
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    print str(datetime.now()) + "Processing h.request"
    result = h.request(url, 'DELETE')[1]
    print str(datetime.now()) + "Finished processing h.requst"
    return "You have been logged out"


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
