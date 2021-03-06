import os
import string
import random
import base64

from datetime import datetime

from classisapi import config
from admin import User, School

def generate_random_string(length=20):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_username():
    username = generate_random_string(config['USERNAME_LENGTH'])
    if User.query.filter(User.user==username).first():
        username = generate_username()
    return username

def generate_token():
    token = generate_random_string(config['TOKEN_LENGTH'])
    if User.query.filter(User.token==token).first():
        token = generate_token()
    return token

def create_api_user(school_id, email, username=''):
    user = User.query.filter(User.user==username).first()
    if not user:
        user = User()
    user.user = username
    if username == '':
        user.user = generate_username()
    user.token = generate_token()
    user.school_id = school_id
    user.email = email

    return user

def create_school(name, client_id, host, db, port='', city=''):
    school = School.query.filter(School.db==db).first()
    if not school:
        school = School()
    school.name = name
    school.client_id = client_id
    school.host = host
    school.db = db
    if port != '':
        school.port = port
    if city != '':
        school.city = city

    return school
