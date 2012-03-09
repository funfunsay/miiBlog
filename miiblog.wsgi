# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    Deploy with apache2 wsgi.
"""

import sys, os
#import pwd
os.environ['FUNFUNSAY_CONFIG'] = ''
# http://code.google.com/p/modwsgi/wiki/ApplicationIssues#User_HOME_Environment_Variable
#os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir

#activate_this = '/var/www/funfunsay/env/bin/activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))

#BASE_DIR = os.path.join(os.path.dirname(__file__))
BASE_DIR = "c:/inetpub/wwwroot/"
#print BASE_DIR
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from funfunsay import create_app
application = create_app()

