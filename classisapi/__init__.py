from flask import Flask

app = Flask(__name__, static_url_path='/assets', static_folder='static')

app.config.from_object('config')
config = app.config

from classisapi.database import init_db, connect_db

db_session = connect_db()

import classis
import classisapi.views

import logging
logging.basicConfig(filename=config['LOG_FILE'],level=logging.DEBUG)

init_db()
