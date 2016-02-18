import os
import unittest
import tempfile

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from classisapi import app, db_session
from services import *
from admin import User, School
from database import Base, connect_db, init_db

class MainTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DB_URL'] = 'sqlite:///test.db'
        app.config['USERNAME_LENGTH'] = 50
        app.config['TOKEN_LENGTH'] = 100

        self.app = app.test_client()
        db_session = connect_db()

    def tearDown(self):
        os.unlink('test.db')

    def test_app_running_root_query_returns_status_200(self):
        assert self.app.get('/').status_code == 200

    def test_generate_random_string_default_returns_string_default_length(self):
        assert len(generate_random_string()) == 20

    def test_generate_random_string_length_returns_string_passed_length(self):
        assert len(generate_random_string(100)) == 100

    def test_generate_username_config_length_returns_config_length(self):
        assert len(generate_username()) == 50

    def test_generate_token_config_length_returns_config_length(self):
        assert len(generate_token()) == 100

    def test_without_init_db_returns_no_admins_or_schools(self):
        admins = User.query.filter(User.user=='administrator').all()
        schools = School.query.filter(School.name=='Admin School').all()
        assert len(admins) == 0 and len(schools) == 0

    def test_init_db_creates_administrator_and_school(self):
        init_db()
        admins = User.query.filter(User.user=='administrator').all()
        schools = School.query.filter(School.name=='Admin School').all()
        assert len(schools) == 1 and len(admins) == 1

    def test_create_school_required_args_creates_school(self):
        school = create_school('test_name', 'test_clid', 'test_host', 'test_db')
        assert school.name == 'test_name' and school.client_id == 'test_clid' \
                and school.host == 'test_host' and school.db == 'test_db'

    def test_create_api_user_required_args_creates_user(self):
        school = create_school('test', 'test', 'test', 'test')
        user = create_api_user(school.id, 'email@test.com')
        assert user.school_id == school.id and user.email == 'email@test.com'

    def test_create_api_user_generates_token_and_username(self):
        school = create_school('test', 'test', 'test', 'test')
        user = create_api_user(school.id, 'email@test.com')
        assert user.token != '' and user.user !=''

    def test_app_get_help_query_returns_status_200(self):
        assert self.app.get('/help').status_code == 200

    def test_app_get_register_query_without_admin_returns_status_401(self):
        assert self.app.get('/register').status_code == 401

    def test_app_get_register_query_with_admin_returns_status_405(self):
        init_db()
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        assert self.app.get(url).status_code == 405

if __name__ == '__main__':
    unittest.main()
