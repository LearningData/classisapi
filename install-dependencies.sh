!#/bin/sh
apt-get update
apt-get -y install python-pip python-dev build-essential
apt-get -y install libmysqlclient-dev
apt-get -y install libapache2-mod-wsgi
apt-get -y install libjpeg8-dev
a2enmod wsgi
pip install virtualenvwrapper
