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
        app.config['ADMINISTRATOR_NAME'] = 'administrator'
        app.config['USERNAME_LENGTH'] = 50
        app.config['TOKEN_LENGTH'] = 100

        self.app = app.test_client()
        db_session = connect_db()

        self.post_headers = headers = [('Content-Type', 'application/json')]
        self.register_json = '{"school_name": "test_school",' \
            '"client_id": "test_client_id",' \
            '"host": "test_host", "db": "test_db_remote" }'

    def tearDown(self):
        os.unlink('test.db')

    def assertCountEqual(self, result, count):
        return self.assertEqual(len(result), count)

    def test_app_running_root_query_returns_status_200(self):
        self.assertEqual(self.app.get('/').status_code, 200)

    def test_generate_random_string_default_returns_string_default_length(self):
        self.assertCountEqual(generate_random_string(), 20)

    def test_generate_random_string_length_returns_string_passed_length(self):
        self.assertCountEqual(generate_random_string(100), 100)

    def test_generate_username_config_length_returns_config_length(self):
        self.assertCountEqual(generate_username(), 50)

    def test_generate_token_config_length_returns_config_length(self):
        self.assertCountEqual(generate_token(), 100)

    def test_without_init_db_returns_no_admins_or_schools(self):
        admins = User.query.filter(User.user=='administrator').all()
        schools = School.query.filter(School.name=='Admin School').all()
        self.assertCountEqual(admins, 0)
        self.assertCountEqual(schools, 0)

    def test_init_db_creates_administrator_and_school(self):
        init_db()
        admins = User.query.filter(User.user=='administrator').all()
        schools = School.query.filter(School.name=='Admin School').all()
        self.assertCountEqual(schools, 1)
        self.assertCountEqual(admins, 1)

    def test_create_school_required_args_creates_school(self):
        school = create_school('test_name', 'test_clid', 'test_host', 'test_db')
        self.assertEqual(school.name, 'test_name')
        self.assertEqual(school.client_id, 'test_clid')
        self.assertEqual(school.host, 'test_host')
        self.assertEqual(school.db, 'test_db')

    def test_create_school_optional_args_creates_school(self):
        school = create_school('test_name', 'test_clid', 'test_host',
                               'test_db', 'test_port', 'test_city')
        self.assertEqual(school.port, 'test_port')
        self.assertEqual(school.city, 'test_city')

    def test_create_api_user_required_args_creates_user(self):
        school = create_school('test', 'test', 'test', 'test')
        user = create_api_user(school.id, 'email@test.com')
        self.assertEqual(user.school_id, school.id)
        self.assertEqual(user.email, 'email@test.com')

    def test_create_api_user_generates_token_and_username(self):
        school = create_school('test', 'test', 'test', 'test')
        user = create_api_user(school.id, 'email@test.com')
        self.assertNotEqual(user.token, '')
        self.assertNotEqual(user.user, '')

    def test_app_get_help_query_returns_status_200(self):
        self.assertEqual(self.app.get('/help').status_code, 200)

    def test_app_get_register_query_without_admin_returns_status_401(self):
        self.assertEqual(self.app.get('/register').status_code, 401)

    def test_app_get_register_query_with_admin_returns_status_405(self):
        init_db()
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        self.assertEqual(self.app.get(url).status_code, 405)

    def test_app_post_register_query_with_admin_without_json_returns_status_415(self):
        init_db()
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        self.assertEqual(self.app.post(url).status_code, 415)

    def test_app_post_register_query_with_admin_without_json_with_content_type_returns_status_400(self):
        init_db()
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        headers = self.post_headers
        self.assertEqual(self.app.post(url, headers=headers).status_code, 400)

    def test_app_post_register_query_with_admin_with_json_without_content_type_returns_status_415(self):
        init_db()
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        json = self.register_json
        self.assertEqual(self.app.post(url, data=json).status_code, 415)

    def test_app_post_register_query_with_admin_with_json_with_content_type_returns_status_201(self):
        init_db()
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        headers = self.post_headers
        json = self.register_json
        self.assertEqual(self.app.post(url, headers=headers, data=json).status_code, 201)

    def test_app_get_register_query_with_valid_user_other_than_admin_returns_status_401(self):
        school = create_school('test', 'test', 'test', 'test')
        user = create_api_user(school.id, 'email@test.com')
        url = '/register?user=' + user.user + '&token=' + user.token
        self.assertEqual(self.app.post(url).status_code, 401)

    def test_app_post_register_full_query_with_admin_with_json_with_content_type_returns_status_201(self):
        init_db()
        json = '{"school_name": "test_school",' \
            '"client_id": "test_client_id",' \
            '"port": "3307",' \
            '"city": "test_city",' \
            '"email": "test_email@email.com",' \
            '"host": "test_host", "db": "test_db_remote" }'
        admin = User.query.filter(User.user=='administrator').first()
        url = '/register?user=' + admin.user + '&token=' + admin.token
        headers = self.post_headers
        self.assertEqual(self.app.post(url, headers=headers, data=json).status_code, 201)

if __name__ == '__main__':
    unittest.main()
