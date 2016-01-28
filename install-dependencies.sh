!#/bin/sh
apt-get update
apt-get -y install python-pip python-dev build-essential
apt-get -y install libmysqlclient-dev
pip install virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv classisapi
workon classisapi
