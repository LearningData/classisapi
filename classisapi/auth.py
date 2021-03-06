import datetime

from functools import wraps
from flask import Response, request, abort
from sqlalchemy import or_, and_

from classisapi import config, db_session
from admin import User

client_id = None

def check_auth(user, token):
    return User.query. \
            filter(and_(User.user == user, User.token == token)). \
            first()

def requires_auth(api_method):
    @wraps(api_method)
    def authenticate(*args, **kwargs):
        checked_user = None
        if(request.endpoint != 'index' and request.endpoint != 'help'
                and 'assets' not in request.path):
            auth = request.args
            checked_user = check_auth(auth.get('user'), auth.get('token'))

            if not auth or not checked_user or checked_user is None:
                abort(401)

            checked_user.requests_count += 1
            checked_user.last_request = datetime.datetime.now()
            db_session.commit()

        return api_method(checked_user, *args, **kwargs)
    return authenticate

def restrict_administrator(api_method):
    @wraps(api_method)
    @requires_auth
    def is_administrator(checked_user, *args, **kwargs):
        if checked_user.user != config['ADMINISTRATOR_NAME']:
            abort(401)

        return api_method(*args, **kwargs)
    return is_administrator
