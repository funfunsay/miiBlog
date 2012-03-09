# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime
import time

from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, g, abort)
from jinja2 import TemplateNotFound
from werkzeug import check_password_hash, generate_password_hash
from funfunsay.forms import (SignupForm, LoginForm, RecoverPasswordForm,
                         ChangePasswordForm, ReauthForm)
from flaskext.babel import gettext as _
from flaskext.login import (login_required, login_user, current_user,
                            logout_user, confirm_login, fresh_login_required,
                            login_fresh)

from funfunsay.models import User
from funfunsay.extensions import cache, login_manager


homesite = Blueprint('homesite', __name__
                       #, url_prefix='/pl'
                       #,static_folder='/static'
                       )

@homesite.route('/')
def home():
    if g.user:
        return render_template('index.html')

    login_form = signup_form = None
    if not g.user:
        login_form= LoginForm(next=request.args.get('next'))
        signup_form = SignupForm(nex=request.args.get('next'))
    return render_template('index.html', login_form=login_form,
                           signup_form=signup_form)


@homesite.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(login=request.args.get('login', None),
                     next=request.args.get('next', None))

    if form.validate_on_submit():
        #print "111 validate_on_submit: "
        user, authenticated, error = User.authenticate(form.login.data,
                                    form.password.data)
        #print "111 user: ", user
        #print "111 authenticated: ", authenticated
        #print "111 error: ", error

        if user and authenticated:
            #print "111 if: ", request.form.get('remember')
            remember = request.form.get('remember') == 'y'
            #print "111 remember: ", remember
            if login_user(user, remember=remember):
                flash("Logged in!", 'success')
                session['user_id'] = user.id
            return redirect(form.next.data or url_for('homesite.home'))
        else:
            flash(_('Sorry, invalid login'), 'error')

    #print "comeljdkj"
    return render_template('login.html', form=form)


@homesite.route('/register', methods=['GET', 'POST'])
def register():
    login_form= LoginForm(next=request.args.get('next'))
    form = SignupForm(next=request.args.get('next'))

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)

        user_doc = {"_id":form.name.data,
                    "email":form.email.data,
                    "pw_hash":generate_password_hash(form.password.data),
                    "copyrights":"user",
                    "reg_date":int(time.time())}
        g.db.users.insert(user_doc, safe=True)
        #todo: check fail
        flash('You were successfully registered and can login now')

        if login_user(user):
            return redirect(form.next.data or url_for('homesite.login'))

    return render_template('register.html', form=form, login_form=login_form)

@homesite.route('/logout')
def logout(): 
    """Logs the user out."""
    logout_user()
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('homesite.home'))

@homesite.route('/search')
def search():
    return render_template('search.html')

@homesite.route('/user_profile')
def user_profile():
    return render_template('uprofile.html')