import os

from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # implement http security headers via external libs
    CORS(app, origins=['http://localhost:*']) # add some pytests
    Talisman(app) # forces https redirect in production (waitress-serve)

    from . import db
    db.init_app(app)

    from . import passthrough
    app.register_blueprint(passthrough.bp)

    return app
