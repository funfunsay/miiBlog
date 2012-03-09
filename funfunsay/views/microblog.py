# -*- coding: utf-8 -*-
"""
    FunFunSay
    ~~~~~~~~

    A micronoting application written with Flask and MongoDB.

    :copyright: (c) 2010 by Brent Jiang.
"""
import sys
import time
from contextlib import closing
from flask import (current_app, Blueprint, request, session, url_for, redirect, \
     render_template, abort, g, flash, jsonify)
from pymongo.objectid import ObjectId
import jinja2
import pymongo
from funfunsay.config import PER_PAGE
from flaskext.babel import gettext as _
from flaskext.login import (login_required, login_user, current_user,
                            logout_user, confirm_login, fresh_login_required,
                            login_fresh)

from funfunsay.models import User
from funfunsay.extensions import cache, login_manager

microblog = Blueprint('microblog', __name__, url_prefix='/m')


@microblog.route('/')
def timeline():
    """
    Index for FunFunSay Microblog.
    Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    We need to use client-side linking since MongoDB doesn't support
    join operation (DBRefs is not a good choice here). Method get_username()
    is provided for such purpose.
    """
    if not current_user.is_authenticated():
        #print url_for('microblog.public_timeline')
        return redirect(url_for('microblog.public_timeline'))
    followers = []
    for f in g.db.followers.find({"who_id":session['user_id']},{"whom_id":1, "_id":0}):
        followers.append(f['whom_id'])
    messages = g.db.messages.find({"$or" : [{"author_id" : session['user_id']}, 
                                            {"author_id": {"$in" : followers}}], "host_id":None}, sort=[("pub_date",pymongo.DESCENDING)]).limit(PER_PAGE)
    return render_template('microblog/timeline.html', messages=messages)


@microblog.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    messages = g.db.messages.find({"host_id":None}, sort=[('pub_date',pymongo.DESCENDING)]).limit(PER_PAGE)
    return render_template('microblog/timeline.html', messages=messages)


@microblog.route('/following')
@login_required
def my_following():
    """Displays the users or medias that i am following."""
    return render_template('microblog/timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))

@microblog.route('/plaza')
def plaza():
    """Displays latest reviews, newly created media or users, hotest contents."""
    """latest messages"""
    messages = g.db.messages.find({"host_id":None}, sort=[("pub_date",pymongo.DESCENDING)]).limit(PER_PAGE)
    """newly created medias"""
    medias = g.db.users.find({"copyrights":{ "$ne":"user"}, "host_id":None}, sort=[("reg_date",pymongo.DESCENDING)]).limit(PER_PAGE)
    return render_template('plaza.html', messages=messages,medias=medias)

@microblog.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user_doc = g.db.users.find_one({"_id":username})
    if profile_user_doc is None:
        abort(404)
    followed = False
    if current_user.is_authenticated():
        followed = g.db.followers.find_one({"who_id":session['user_id'], "whom_id":username}) is not None
    messages = g.db.messages.find({"author_id":username, "host_id":None}, sort=[("pub_date",pymongo.DESCENDING)]).limit(PER_PAGE)
    return render_template('microblog/timeline.html', messages=messages, followed=followed,
            profile_user=profile_user_doc)


@microblog.route('/media/<medianame>')
def media(medianame):
    """Display's a medias tweets."""
    media_doc = g.db.users.find_one({"_id":medianame})
    if media_doc is None:
        abort(404)
    followed = False
    if current_user.is_authenticated():
        followed = g.db.followers.find_one({"who_id":session['user_id'], "whom_id":media_doc['_id']}) is not None
    contents = []
    for b in g.db.contents.find({"book_id":medianame}, {"_id":1}):
        contents.append(b['_id'])
    messages = g.db.messages.find({"content_id": {"$in":contents}, "host_id":None}, 
                                  sort=[("pub_date",pymongo.DESCENDING)]).limit(PER_PAGE)
    return render_template('media.html', messages=messages, 
                           followed=followed,
                           profile_media=media_doc)

			
@microblog.route('/<username>/follow')
@login_required
def follow_user(username):
    """Adds the current user as follower of the given user."""
    whom_id = username
    if whom_id is None:
        abort(404)
    follower_doc = {"who_id":session['user_id'], 
                    "whom_id":whom_id }
    g.db.followers.insert(follower_doc, safe=True)
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@microblog.route('/<username>/unfollow')
@login_required
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    whom_id = username
    if whom_id is None:
        abort(404)
    g.db.followers.remove({"who_id":session['user_id'], 
                           "whom_id":whom_id }, safe=True)
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@microblog.route('/add_message', methods=['POST'])
@login_required
def add_message():
    """Registers a new message for the user."""
    if request.form['text'] and request.form['text']<>'':
        #print request.form['text']
        message_doc = {"author_id":session['user_id'], 
                       "text":request.form['text'],
                       "pub_date":int(time.time()),
                       "content_id":None,
                       "host_id":None,
                       "score":0,
                       "vote_up_count":0,
                       "vote_down_count":0
                       }
        g.db.messages.insert(message_doc)
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@microblog.route('/reply_message', methods=['POST'])
@login_required
def reply_message():
    """Reply to a message(id=hostid)."""
    if request.form['text']:
        message_doc = {"author_id":session['user_id'], 
                       "text":request.form['text'],
                       "pub_date":int(time.time()),
                       "content_id":None,
                       "host_id":request.form['hostid'],
                       "score":0,
                       "vote_up_count":0,
                       "vote_down_count":0
                       }
        g.db.messages.insert(message_doc)
        flash('Your reply was recorded')
    return redirect(url_for('timeline'))

	
@microblog.route('/create', methods=['GET', 'POST'])
@login_required
def create_media():
    """Create a media is like registers the user."""
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['copyrights']:
            error = 'You have to enter copyrights information'
        elif g.db.users.find_one({'_id':request.form['username']}) is not None:
            error = 'The media is already existing.'
        else:
            user_doc = {"_id":request.form['username'],
                        "email":request.form['email'],
                        "pw_hash":generate_password_hash("default"),
                        "copyrights":request.form['copyrights'],
                        "reg_date":int(time.time())}
            g.db.users.insert(user_doc, safe=True)
            #todo: check fail
            flash('Media creation application was successfully applied and can now to be remarked')
            return redirect(url_for('media', medianame=request.form['username']))
    return render_template('create.html', error=error)


@microblog.route('/_get_replies')
def get_replies():
    messageid = request.args.get('messageid')
    messages = g.db.messages.find({"host_id":messageid}, sort=[("pub_date", pymongo.DESCENDING)]).limit(PER_PAGE)
    return jsonify(result=jinja2.Markup(render_template("replies_widget.html", replies=messages, hostid=messageid)))

@microblog.route('/m/_get_new_message')
@login_required
def get_new_message():
    if not current_user.is_authenticated():
        g.my_new_message = None
        return jsonify(messageid="", messagepubdate="", imgsrc="")
    else:
        g.my_new_message = get_latest_message(current_user.id)
        #print g.my_new_message
        return jsonify(messageid="%s"%g.my_new_message['_id'], messagepubdate=format_datetime(g.my_new_message['pub_date']),
                       imgsrc=gravatar_url(current_user.email, 48))

# get the new reply that current user posted
@microblog.route('/_get_new_reply')
@login_required
def get_new_reply():
    g.my_new_message = get_latest_message(current_user.id)
    #print g.my_new_message
    return jsonify(hostid="%s"%g.my_new_message['host_id'],
                    messageid="%s"%g.my_new_message['_id'], messagepubdate=format_datetime(g.my_new_message['pub_date']),
                    imgsrc=gravatar_url(current_user.email, 48))

@microblog.route('/_vote')
@login_required
def vote():
    messageid = ObjectId(request.args.get('messageid'))
    voteval = int(request.args.get('voteval'))
    if not current_user.is_authenticated():
        return jsonify(result=0)

    voteresult, score = User.do_vote(messageid, voteval)
    return jsonify(result=1, voteresult=voteresult, score=score, messageid = request.args.get('messageid'))
