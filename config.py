import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#App host and port
HOST = os.environ.get('API_HOST', '0.0.0.0')
PORT = os.environ.get('API_PORT', 5000)

#Debug should be false on production
DEBUG = os.environ.get('API_DEBUG', False)
#Log file where all the requests will be saved
#Should be changed on production
LOG_FILE = os.environ.get('API_LOG_FILE', '/tmp/classis.log')

#DB url to save the users and schools
#sqlite for development and mysql for production
DB_URL = os.environ.get('API_DB_URL', 'sqlite:///classisapi.db')

#Name and email for the API administrator
#This user will be able to register other users
ADMINISTRATOR_NAME = os.environ.get('API_ADMINISTRATOR_NAME',
                                    'administrator')
ADMINISTRATOR_EMAIL = os.environ.get('API_ADMINISTRATOR_EMAIL',
                                     'classisapi@learningdata.ie')

#Directory used by Fabric to download remote avatars and reports PDFs
AVATARS_DIR = os.environ.get('API_AVATARS_DIR', '/tmp')
REPORTS_DIR = os.environ.get('API_REPORTS_DIR', '/tmp')

#Length of the username and token random generated strings
USERNAME_LENGTH = os.environ.get('API_USERNAME_LENGTH', 16)
TOKEN_LENGTH = os.environ.get('API_TOKEN_LENGTH', 20)

#Authentication for all the remote databases
#Obviously, this should be the same for all of them
#Remember to give remote permissions to this user
REMOTE_DB_AUTH = os.environ.get('API_REMOTE_DB_AUTH', 'classisapi:password')

#Static url path to be shown for static files
STATIC_URL = os.environ.get('API_STATIC_URL', '/assets')
