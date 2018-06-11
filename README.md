hxarc
===============================

web version of https://github.com/Colin-Fredericks/hx_util


quickstart
==========

    # clone this repo
    $> git clone https://github.com/nmaekawa/hxarc
    
    # create and activate virtualenv
    $> cd hxarc
    $hxarc> virtualenv -p python3 venv
    $hxarc> source venv/bin/activate
    $(venv) hxarc>
    
    # install pip requirements
    $(venv) hxarc> pip install -r requirements/dev.txt
    
    # turn on debug mode
    $(venv) hxarc> export FLASK_DEBUG=1
    
    # run migration; it creates a dev.db sqlite file
    $(venv) hxarc> FLASK_APP=./hxarc/wsgi.py flask db upgrade
    
    # create a user
    $(venv) hxarc> FLASK_APP=./hxarc/wsgi.py flask create_user --usr user --pwd password --email user@user.com
    
    # start webapp
    $(venv) hxarc> FLASK_APP=./hxarc/wsgi.py flask run
    
    # access webapp on http://localhost:5000
    # login as user:password


Deployment
----------

To deploy::

    export FLASK_DEBUG=0
    npm run build   # build assets with webpack
    flask run       # start the flask server

In your production environment, make sure the ``FLASK_DEBUG`` environment
variable is unset or is set to ``0``, so that ``ProdConfig`` is used.


Shell
-----

To open the interactive shell, run ::

    flask shell

By default, you will have access to the flask ``app``.


Running Tests
-------------

To run all tests, run ::

    flask test


Migrations
----------

Whenever a database migration needs to be made. Run the following commands ::

    flask db migrate

This will generate a new migration script. Then run ::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.


Asset Management
----------------

Files placed inside the ``assets`` directory and its subdirectories
(excluding ``js`` and ``css``) will be copied by webpack's
``file-loader`` into the ``static/build`` directory, with hashes of
their contents appended to their names.  For instance, if you have the
file ``assets/img/favicon.ico``, this will get copied into something
like
``static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico``.
You can then put this line into your header::

    <link rel="shortcut icon" href="{{asset_url_for('img/favicon.ico') }}">

to refer to it inside your HTML page.  If all of your static files are
managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in your ``settings.py``::

    SEND_FILE_MAX_AGE_DEFAULT = 31556926  # one year
