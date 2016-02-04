import os
import string
import random
import base64

from datetime import datetime

from database import db_session
from admin import User, School

def get_title(title):
    titles = {'': '',
        '0': '',
        '1': 'mr',
        '2': 'mrs',
        '3': 'srd',
        '4': 'srada',
        '5': 'miss',
        '6': 'dr',
        '7': 'ms',
        '8': 'major'
        };
    return str(titles[str(title)])

def get_user_picture(epfusername, images_path = '/tmp'):
    encoded_image = None
    file_name = epfusername + '.jpeg'

    image = {}

    file = images_path + '/' + file_name
    if os.path.exists(file):
        with open(file, 'rb') as image:
            encoded_image = base64.b64encode(image.read())
    else:
        file_name = None

    image = {
        'base64': encoded_image,
        'name': file_name
    }

    return image

def generate_random_string(length=20):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_username():
    username = generate_random_string(16)
    if db_session.query(User).filter(User.user==username).first():
        username = generate_username()
    return username

def generate_token():
    token = generate_random_string(20)
    if db_session.query(User).filter(User.token==token).first():
        token = generate_token()
    return token

def create_api_user(school_id, email, username=''):
    user = db_session.query(User).filter(User.user==username).first()
    if not user:
        user = User()
    user.user = username
    if username == '':
        user.user = generate_username()
    user.token = generate_token()
    user.school_id = school_id
    user.email = email
    db_session.add(user)
    db_session.commit()

    return user

def create_school(name, client_id, host, db, epf_path='', port='', city=''):
    school = db_session.query(School).filter(School.db==db).first()
    if not school:
        school = School()
    school.name = name
    school.client_id = client_id
    school.host = host
    school.db = db
    if epf_path != '':
        school.eportfolio_path = epf_path
    if port != '':
        school.port = port
    if city != '':
        school.city = city
    db_session.add(school)
    db_session.commit()

    return school
