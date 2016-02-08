from flask import Flask

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config.from_object('config')

import classis
import classisapi.views
from classisapi.database import init_db

import logging
logging.basicConfig(filename='/tmp/classisapi.log',level=logging.DEBUG)

init_db()
