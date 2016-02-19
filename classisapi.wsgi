import os
import yaml
import sys

activate_this = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".env/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
	with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.yaml')) as settings_file:
		ENV_VARS = json.load(settings_file)
except:
	ENV_VARS = {}

for key, value in ENV_VARS.iteritems():
    try:
        os.environ[key] = value
    except KeyError:
        pass

from classisapi import app as application
