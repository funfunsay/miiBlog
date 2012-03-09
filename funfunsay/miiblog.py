# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
import sys
from datetime import datetime

from hashlib import md5
from flask import Flask, request, render_template, g, session
from flaskext.babel import Babel
from funfunsay.config import DefaultConfig, APP_NAME
from funfunsay.views import homesite, microblog
from funfunsay.extensions import cache, login_manager
import pymongo
from pymongo import Connection
from pymongo.errors import ConnectionFailure
from flaskext.login import login_user, current_user, logout_user
from funfunsay import utils
from funfunsay.models import User

# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    homesite,
    microblog
)

MAX_LEN_P = 100 #max text length for a principle

def connect_db(app):
    """Returns a new connection to the database."""
    try:
        c = Connection(host=app.config['DATABASE'], port=app.config['DBPORT'])
        return c[app.config['DBNAME'] ]
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)


#由于init_db()函数可以单独用于调用，所以里面有一个connect_db的调用。
#而全局g对象中保存的数据库连接是另外调用connect_db生成的。
def init_db(app):
    """There is no need to create the collection in advance."""
    with closing(connect_db(app)) as db:
        """force to drop all existing collections"""
        db.followers.drop()
        db.messages.drop()
        db.users.drop()


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = APP_NAME
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    #configure_logging(app)
    configure_template_filters(app)
    #configure_error_handlers(app)


    # add some filters to jinja
    app.jinja_env.filters['datetimeformat'] = utils.format_datetime
    app.jinja_env.filters['gravatar'] = utils.gravatar_url
    app.jinja_env.filters['user'] = User.get_user
    app.jinja_env.filters['myvote'] = User.my_vote
    app.jinja_env.filters['scoreformat'] = int

    #print "app created"
    return app



def configure_app(app, config):
    """Configure app from object, parameter and env."""

    app.config.from_object(DefaultConfig)
    if config is not None:
        app.config.from_object(config)
    # Override setting by env var without touching codes.
    app.config.from_envvar('FUNFUNSAY_CONFIG', silent=True)


def configure_extensions(app):
    # pymongo

    # cache
    cache.init_app(app)

    # babel
    #print "create babel object"
    babel = Babel(app)
    #@babel.localeselector
    #def get_locale():
    #    accept_languages = app.config.get('ACCEPT_LANGUAGES')
    #    return request.accept_languages.best_match(accept_languages)

    # login.
    login_manager.login_view = 'homesite.login'
    login_manager.refresh_view = 'homesite.reauth'
    @login_manager.user_loader
    def load_user(id):
        #print "####: loaduser ", id
        return User.get_user(id)
    login_manager.setup_app(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):
    @app.template_filter()
    def format_datetime(value):
        """Format a timestamp for display."""
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def configure_hook(app):
    @app.before_request
    def before_request():
        """Make sure we are connected to the database each request and look
        up the current user so that we know he's there.
        """
        g.db = connect_db(app)
        g.user = None
        g.MAX_LEN_P = MAX_LEN_P
        if 'user_id' in session:
            g.user = User.get_user(session['user_id'])


    @app.teardown_request
    def teardown_request(exception):
        """Closes the database again at the end of the request."""
        if hasattr(g, 'db'):
            g.db.connection.close()
