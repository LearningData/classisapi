# classisapi

Classis API, built in Flask Python framework. Uses fabric for deployment and MySQL as a database.

The API acts as a router to different remote database. It connects to a remote db remotely with credentials assigned specifically to the API.

The API, itself, contains two models: School and User.

School contains the details about the connections to different school databases and User is used for giving credentials to a specific school, user and token being randomly generated.

It runs with the Apache module WSGI on production, a sample of the configuration can be found in the samples directory.

All environment variables for the configuration have to be added to a file called settings.yaml (only if apache is used, otherwise environment variables can be used), sample in the samples directory, and for production or staging: settings_production.yaml or settings_staging.yaml, can be created in the root directory and uploaded using fabric.

Server has to be prepared before deployment, installing dependencies, adding a virtual environment, database created and apache configuration added.

manage.py can be used to migrate the database: python manage.py db upgrade (uses alembic), to test with python manage.py test or to run a development server with python manage.py run_server.

Tests using unittest have been added for the all services methods and api endpoints. Endpoints using remote database or remote db models have no tests.

fabfile.py also contains a method to download remote school files to the API server, report pdfs or profile icons can be downloaded using epf_configs.yaml file, an example can be found in the samples directory. These files will then be encoded in base64 when returned in a request.

A administrator account will be generated when the app starts. With this account credentials can be generated for schools using register endpoint.

There is a /help endpoint which lists all the available endpoints for the API with docstrings added to each view and the required arguments.

A Javascript client has been built as a frontend for the API using Bootstrap and JQuery, this makes easy to POST request.
