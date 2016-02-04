import os

from flask import make_response, jsonify

from app import app
from database import init_db
from views import *


@app.errorhandler(400)
def invalid_request(error):
        return make_response(jsonify({'error': 'Invalid request'}), 400)

@app.errorhandler(401)
def invalid_credentials(error):
        return make_response(jsonify({'error': 'Invalid credentials'}), 401)

@app.errorhandler(403)
def forbidden(error):
        return make_response(jsonify({'error': 'Forbidden'}), 403)

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    init_db()

    import logging
    logging.basicConfig(filename='/tmp/classisapi.log',level=logging.DEBUG)

    app.run(host='0.0.0.0',
            port=os.environ.get('PORT', 5000),
            debug=os.environ.get('DEBUG', False))
