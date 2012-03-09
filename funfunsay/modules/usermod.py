"""
user module (usermod) defines some utility functions
"""
import pymongo
from flask import g
from pymongo.objectid import ObjectId


def get_latest_liferule(userid):
    return g.db.liferules.find_one({"author_id":userid}, sort=[("pub_date", pymongo.DESCENDING)])

def my_vote(liferuleid):
    """
    return 0 if not voted, -1 means vote down, 1 means vote up
    """
    if g.user is None:
        return 0

    vote_doc = g.db.votes.find_one({'liferule_id':liferuleid, 'user_id':g.user['_id']})
    if vote_doc is None:
        return 0

    print vote_doc
    return vote_doc['vote']


def do_vote(liferuleid, voteval):
    """
    return 0 if not voted, -1 means vote down, 1 means vote up
    liferule_id: an ObjectId of liferule, voteval should be integer
    """
    #print liferuleid
    #print voteval
    if g.user is None:
        return 0

    liferule_doc = g.db.liferules.find_one({'_id':liferuleid})

    # cannot vote self!
    if g.user['_id'] == liferule_doc['author_id']:
        return 0, int(liferule_doc['score'])

    vote_doc = g.db.votes.find_one({'liferule_id':liferuleid, 'user_id':g.user['_id']})
    print vote_doc
    if vote_doc is None:
        vote_doc = {'user_id':g.user['_id'],
                    'liferule_id':liferuleid,
                    'vote':voteval
                    }
        g.db.votes.insert(vote_doc, safe=True)
        if voteval==1:
            liferule_doc['vote_up_count'] = liferule_doc['vote_up_count'] + 1
            liferule_doc['score'] = liferule_doc['score'] + 1
        else:
            liferule_doc['vote_down_count'] = liferule_doc['vote_down_count'] + 1
            liferule_doc['score'] = liferule_doc['score'] - 1
        g.db.liferules.save(liferule_doc, safe=True)
        return voteval, int(liferule_doc['score'])

    if vote_doc['vote']<>voteval:
        if vote_doc['vote']==1:
            liferule_doc['vote_up_count'] = liferule_doc['vote_up_count'] - 1
            liferule_doc['vote_down_count'] = liferule_doc['vote_down_count'] + 1
            liferule_doc['score'] = liferule_doc['score'] - 2
        elif vote_doc['vote']==-1:
            liferule_doc['vote_up_count'] = liferule_doc['vote_up_count'] + 1
            liferule_doc['vote_down_count'] = liferule_doc['vote_down_count'] - 1
            liferule_doc['score'] = liferule_doc['score'] + 2

        vote_doc['vote'] = voteval
        g.db.votes.save(vote_doc, safe=True)
    else:
        if vote_doc['vote']==1:
            liferule_doc['vote_up_count'] = liferule_doc['vote_up_count'] - 1
            liferule_doc['score'] = liferule_doc['score'] - 1
        else:
            liferule_doc['vote_down_count'] = liferule_doc['vote_down_count'] - 1
            liferule_doc['score'] = liferule_doc['score'] + 1
        voteval = 0
        g.db.votes.remove(vote_doc, safe=True)

    g.db.liferules.save(liferule_doc, safe=True)

    return voteval, int(liferule_doc['score'])