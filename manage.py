import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Command
from flask_migrate import Migrate, MigrateCommand

from classisapi import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['DB_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy()
db.app = app
db.init_app(app)

migrate = Migrate(app, db)
migrate.init_app(app, db, directory='classisapi/migrations')

manager = Manager(app)

from classisapi import app, config
import classis
from classisapi.admin import *

#app.register_blueprint(classis)

class ServerCommand(Command):
    def run(self):
        app.run(host=config['HOST'],
                port=config['PORT'],
                debug=config['DEBUG'])

class TestCommand(Command):
    def run(self):
        test_loader = unittest.defaultTestLoader
        test_runner = unittest.TextTestRunner()
        test_suite = test_loader.discover('.')
        test_runner.run(test_suite)

manager.add_command('db', MigrateCommand)
manager.add_command('run_server', ServerCommand)
manager.add_command('test', TestCommand)

if __name__ == '__main__':
    manager.run()
