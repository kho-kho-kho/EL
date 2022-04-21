import os

from flask import abort, Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # TODO randomize key
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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

    @app.route('/dapi/<type>/json/<word>')
    def dapiGet(type, word):
        if type == 'collegiate':
            key = os.environ['DAPI_COLLEGIATE'] # os.getenv(k, default) ??
        else:
            key = os.environ['DAPI_THESAURUS']

        pre = os.environ['DAPI_REFERENCES']
        url = f'{pre}{type}/json/{word}?key={key}'
        return url

    return app
