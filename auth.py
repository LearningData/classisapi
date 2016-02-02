from functools import wraps
from flask import Response, request
from sqlalchemy import or_, and_

from admin import User
from database import db_session

def check_auth(user, token):
    return db_session.query(User). \
            filter(and_(User.user == user, User.token == token)). \
            first()

def authenticate():
    return Response(
            'Could not verify your credentials.', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.args
        checked_user = check_auth(auth.get('user'), auth.get('token'))
        if not auth or not checked_user:
            return authenticate()
        return f(*args, **kwargs)
    return decorated
