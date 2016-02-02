import datetime

from functools import wraps
from flask import Response, request, abort
from sqlalchemy import or_, and_

from admin import User
from database import db_session

def check_auth(user, token):
    return db_session.query(User). \
            filter(and_(User.user == user, User.token == token)). \
            first()

def requires_auth(api_method):
    @wraps(api_method)
    def authenticate(*args, **kwargs):
        auth = request.args
        checked_user = check_auth(auth.get('user'), auth.get('token'))

        if not auth or not checked_user:
            abort(401)

        checked_user.requests_count += 1
        checked_user.last_request = datetime.datetime.now()
        db_session.commit()

        return api_method(*args, **kwargs)
    return authenticate
