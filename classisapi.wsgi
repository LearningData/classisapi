activate_this = "/home/vagrant/.virtualenvs/classisapi/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from classisapi import app as application
