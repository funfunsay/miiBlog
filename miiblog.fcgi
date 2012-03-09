#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from funfunsay import create_app

if __name__ == '__main__':
    WSGIServer(app).run()