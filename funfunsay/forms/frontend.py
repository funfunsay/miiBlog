# -*- coding: utf-8 -*-

from flaskext.wtf import (Form, HiddenField, BooleanField, TextField,
                          PasswordField, SubmitField, TextField,
                          ValidationError, required, equal_to, email,
                          length)
from flask import (Flask, g)
import time
from flaskext.babel import gettext, lazy_gettext as _

from funfunsay.models import User

PASSLEN_MIN = 1
PASSLEN_MAX = 16

class LoginForm(Form):
    next = HiddenField()
    remember = BooleanField(_('Remember me'))
    login = TextField(_('Username or email address'), [required()])
    password = PasswordField(_('Password'), [required(), length(min=PASSLEN_MIN, max=PASSLEN_MAX)])
    submit = SubmitField(_('Login'))


class SignupForm(Form):
    next = HiddenField()
    name = TextField(_('Username'), [required()])
    password = PasswordField(_('Password'), [required(), length(min=PASSLEN_MIN, max=PASSLEN_MAX)])
    password_again = PasswordField(_('Password again'), [required(), length(min=PASSLEN_MIN, max=PASSLEN_MAX), equal_to('password')])
    email = TextField(_('Email address'), [required(), email(message=_('A valid email address is required'))])
    submit = SubmitField(_('Signup'))

    def validate_name(self, field):
        if g.db.users.find_one({"_id":field.data}) is not None:
            raise ValidationError, gettext('This username is taken')

    def validate_email(self, field):
        if g.db.users.find_one({"email":field.data}) is not None:
            raise ValidationError, gettext('This email is taken')


class RecoverPasswordForm(Form):
    email = TextField(_('Your email'), validators=[
                      email(message=_('A valid email address is required'))])
    submit = SubmitField(_('Send instructions'))


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField('Password', validators=[
                             required(message=_('Password is required'))])
    password_again = PasswordField(_('Password again'), validators=[
                                   equal_to('password', message=\
                                            _("Passwords don't match"))])
    submit = SubmitField(_('Save'))


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [required(), length(min=PASSLEN_MIN, max=PASSLEN_MAX)])
    submit = SubmitField(_('Reauthenticate'))
