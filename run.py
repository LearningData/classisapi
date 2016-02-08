import os

from classisapi import app, config
from classis import classis

app.register_blueprint(classis)

app.run(host=config['HOST'],
        port=config['PORT'],
        debug=config['DEBUG'])

