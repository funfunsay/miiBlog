# -*- coding: utf-8 -*-

from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, g, abort)
from werkzeug import (generate_password_hash, check_password_hash,
                      cached_property)
from flaskext.login import UserMixin
import pymongo
from pymongo.objectid import ObjectId

from funfunsay.utils import get_current_time, VARCHAR_LEN_128


class User(UserMixin):
    def __init__(self, pymongodoc=None, **kwargs):
        self.document = pymongodoc
        if self.document is not None:
            self.id = self.name = pymongodoc['_id']
            self.email = pymongodoc['email']
            self.reg_date = pymongodoc['reg_date']
    
    document = None
    id = None
    name = None
    email = None
    _password = None
    activation_key = None
    followers = None
    following = None
    reg_date = None


    def __repr__(self):
        return '<User %r>' % self.name

    #def _get_password(self):
    #    return self._password

    #def _set_password(self, password):
    #    self._password = generate_password_hash(password)

    # Hide password encryption by exposing password field only.
    #password = property(_get_password, _set_password)

    #def check_password(self, password):
    #    if self.password is None:
    #        return False
    #    return check_password_hash(self.password, password)

    #@property
    #def num_followers(self):
    #    if self.followers:
    #        return len(self.followers)
    #    return 0

    #@property
    #def num_following(self):
    #    return len(self.following)

    #def follow(self, user):
    #    user.followers.add(self.id)
    #    self.following.add(user.id)

    #def unfollow(self, user):
    #    if self.id in user.followers:
    #        user.followers.remove(self.id)
    #
    #    if user.id in self.following:
    #        self.following.remove(user.id)

    #def get_following_query(self):
    #    return User.query.filter(User.id.in_(self.following or set()))

    #def get_followers_query(self):
    #    return User.query.filter(User.id.in_(self.followers or set()))

    def is_authenticated(self):
        return False if (self.document == None) else True

    @classmethod
    def authenticate(cls, login, password):
        #print ": authenticate(cls, login, password):"
        error = None
        #print "g.db: ", g.db
        user_doc = g.db.users.find_one({"$or": [{"_id":login}, {"email":login}]})

        if user_doc:
            authenticated = check_password_hash(user_doc['pw_hash'], password)
            if not authenticated:
                error = 'Invalid password'
        else:
            error = 'Invalid username'
            authenticated = False

        #print user_doc
        #print authenticated
        #print error
        user = User(user_doc)
        return user, authenticated, error

    def is_active(self):
        return True

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_user(cls, user_id):
        """Return a user document."""
        user_doc = g.db.users.find_one({"_id":user_id})
        user = User(user_doc)
        return user

    @classmethod
    def get_latest_message(cls, userid):
        return g.db.messages.find_one({"author_id":userid}, sort=[("pub_date", pymongo.DESCENDING)])

    @classmethod
    def my_vote(cls, messageid):
        """
        return 0 if not voted, -1 means vote down, 1 means vote up
        """
        if g.user is None:
            return 0

        vote_doc = g.db.votes.find_one({'message_id':messageid, 'user_id':g.user['_id']})
        if vote_doc is None:
            return 0

        #print vote_doc
        return vote_doc['vote']


    @classmethod
    def do_vote(cls, messageid, voteval):
        """
        return 0 if not voted, -1 means vote down, 1 means vote up
        message_id: an ObjectId of message, voteval should be integer
        """
        #print messageid
        #print voteval
        if g.user is None:
            return 0

        message_doc = g.db.messages.find_one({'_id':messageid})

        # cannot vote self!
        if g.user['_id'] == message_doc['author_id']:
            return 0, int(message_doc['score'])

        vote_doc = g.db.votes.find_one({'message_id':messageid, 'user_id':g.user['_id']})
        #print vote_doc
        if vote_doc is None:
            vote_doc = {'user_id':g.user['_id'],
                        'message_id':messageid,
                        'vote':voteval
                        }
            g.db.votes.insert(vote_doc, safe=True)
            if voteval==1:
                message_doc['vote_up_count'] = message_doc['vote_up_count'] + 1
                message_doc['score'] = message_doc['score'] + 1
            else:
                message_doc['vote_down_count'] = message_doc['vote_down_count'] + 1
                message_doc['score'] = message_doc['score'] - 1
            g.db.messages.save(message_doc, safe=True)
            return voteval, int(message_doc['score'])

        if vote_doc['vote']<>voteval:
            if vote_doc['vote']==1:
                message_doc['vote_up_count'] = message_doc['vote_up_count'] - 1
                message_doc['vote_down_count'] = message_doc['vote_down_count'] + 1
                message_doc['score'] = message_doc['score'] - 2
            elif vote_doc['vote']==-1:
                message_doc['vote_up_count'] = message_doc['vote_up_count'] + 1
                message_doc['vote_down_count'] = message_doc['vote_down_count'] - 1
                message_doc['score'] = message_doc['score'] + 2

            vote_doc['vote'] = voteval
            g.db.votes.save(vote_doc, safe=True)
        else:
            if vote_doc['vote']==1:
                message_doc['vote_up_count'] = message_doc['vote_up_count'] - 1
                message_doc['score'] = message_doc['score'] - 1
            else:
                message_doc['vote_down_count'] = message_doc['vote_down_count'] - 1
                message_doc['score'] = message_doc['score'] + 1
            voteval = 0
            g.db.votes.remove(vote_doc, safe=True)

        g.db.messages.save(message_doc, safe=True)

        return voteval, int(message_doc['score'])