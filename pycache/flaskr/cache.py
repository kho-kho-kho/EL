import os
import requests

from flask import Blueprint, current_app
from flaskr.db import get_db

CACHE = {} # TODO populate from db on startup ??

bp = Blueprint('cache', __name__)

@bp.route('/dapi/json/<word>')
def dapi_get(word):
    # TODO how to handle plurals IE: word vs words etc ??
    if word in CACHE:
        return CACHE[word]

    # does word exist in persistent storage?
    db = get_db()
    result = db.execute(
        'SELECT * FROM dapi WHERE word = ?', (word,)
    ).fetchone()

    # fetch from web if word does not exist in cache or db
    persisted = False
    if result is None:
        key = os.environ['DAPI_COLLEGIATE'] # os.getenv(k, default) ??
        pre = os.environ['DAPI_REFERENCES']
        url = f'{pre}/collegiate/json/{word}'

        # TODO check for multiple results
        json = requests.get(url, params = { 'key': key }).json()

        definitions = json[0]['shortdef']
        if len(definitions) > 0:
            result = { 'def': definitions[0] }
        else:
            result = { 'def': 'NA' }

        try:
            db.execute(
                'INSERT INTO dapi (word, def) VALUES (?, ?)',
                (word, result['def']),
            )
            db.commit()
            persisted = True
        except db.IntegrityError:
            return f'Word {word} already exists.'

    CACHE[word] = result['def']
    current_app.logger.info(
        'Persisted: %d; Cache: %d', persisted, len(CACHE)
    )

    return result['def']
