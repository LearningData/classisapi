import os

from classisapi import app
from classis import classis

app.register_blueprint(classis)

app.run(host='0.0.0.0',
        port=os.environ.get('PORT', 5000),
        debug=os.environ.get('DEBUG', False))

