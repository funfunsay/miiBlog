# -*- coding: utf-8 -*-
import os

# @faq Conditional Import
# see SO:2259382
# for FUNFUNSAY
try:
	from ffsapp import create_app
	print "import ffsapp"
except ImportError:
	from miiblog import create_app
	print "import miiblog"
