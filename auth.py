import datetime

from functools import wraps
from flask import Response, request, abort
from sqlalchemy import or_, and_

from admin import User
from database import db_session

client_id = None

def check_auth(user, token):
    return db_session.query(User). \
            filter(and_(User.user == user, User.token == token)). \
            first()

def requires_auth(api_method):
    @wraps(api_method)
    def authenticate(*args, **kwargs):
        checked_user = None
        if(request.endpoint != 'index' and request.endpoint != 'help'):
            auth = request.args
            checked_user = check_auth(auth.get('user'), auth.get('token'))

            if not auth or not checked_user:
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
        if checked_user.user != 'administrator':
            abort(401)

        return api_method(*args, **kwargs)
    return is_administrator
