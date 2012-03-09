# -*- coding: utf-8 -*-

from setuptools import setup
import os

APP_TYPE = 'FUNFUNSAY'

# @faq Conditional Import
# see SO:2259382
# for FUNFUNSAY
try:
	from funfunsay.ffsapp import create_app
	APP_TYPE = 'FUNFUNSAY'
except ImportError:
	from funfunsay.miiblog import create_app
	APP_TYPE = 'MIIBLOG'

if APP_TYPE is 'MIIBLOG':
	print 'setup MIIBLOG'
	setup(
		name='miiBLOG',
		version='0.1',
		description='miiBLOG: a Fun-Fun-Say Project',
		author='Brent Jiang',
		author_email='sanyi0127@sina.com',
		packages=['funfunsay'],
		include_package_data=True,
		zip_safe=False,
		install_requires=[
			'Flask',
			'pymongo',
			'Flask-WTF',
			'Flask-Script',
			'Flask-Babel',
			'Flask-Cache',
			'Flask-Login',
		]
	)
else: # 'FUNFUNSAY'
	print 'setup FUNFUNSAY'
	setup(
		name='funfunsay',
		version='0.1',
		description='Fun-Fun-Say Project',
		author='Brent Jiang',
		author_email='sanyi0127@sina.com',
		packages=['funfunsay'],
		include_package_data=True,
		zip_safe=False,
		install_requires=[
			'Flask',
			'pymongo',
			'Flask-WTF',
			'Flask-Script',
			'Flask-Babel',
			'Flask-Cache',
			'Flask-Login',
		]
	)
