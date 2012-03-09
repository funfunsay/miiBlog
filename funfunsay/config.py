# -*- coding: utf-8 -*-

APP_NAME = 'funfunsay'
PER_PAGE = 30

class BaseConfig(object):

    DEBUG = False
    TESTING = False
    FEATURE = 0 #0: funfunsay, 1:miiBlog

    # os.urandom(24)
    SECRET_KEY = 'secret key'


class DefaultConfig(BaseConfig):

    DEBUG = True
    SECRET_KEY = 'development key'

    # configuration
    DATABASE = 'localhost'
    DBPORT = 27017
    DBNAME = 'ffsdb'
    DEBUG = True



class TestConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False
