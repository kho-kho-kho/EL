import json
import os
import requests

from flask import Blueprint, current_app
from flaskr.db import get_db

CACHE = {}

bp = Blueprint('cache', __name__)

def parse_blob(blob):
    fls = [] # fl: 'functional label' per MW spec
    parsed = json.loads(blob)
    if type(parsed) == type([]) and len(parsed) > 0:
        fls += [
            d['fl'] + ': ' + ';\n'.join(d['shortdef'])
            for d in parsed
            if type(d) == type({}) and 'fl' in d and 'shortdef' in d
        ]

    # 0: list empty []
    # 1: list of strings ["campanulate", "capitulate"] (absquatulate)
    # 2: list of dicts [{ "meta": .. }, { "meta": .. }]

    # TODO plurals ?? use (entry > meta > stems) for x-referencing

    return json.dumps('\n\n'.join(fls))

def init_dapi():
    db = get_db()
    for row in db.execute('SELECT * FROM dapi').fetchall():
        CACHE[row['word']] = parse_blob(row['def'])
    current_app.logger.info('Cache: %d', len(CACHE))

@bp.route('/dapi/json/<word>')
def get_dapi_word(word):
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
        url = f"{os.environ['DAPI_REFERENCES']}/collegiate/json/{word}"
        r = requests.get(url, params = { 'key': key })
        result = { 'def': r.content }

        try:
            db.execute(
                'INSERT INTO dapi (word, def) VALUES (?, ?)',
                (word, result['def']),
            )
            db.commit()
            persisted = True
        except db.IntegrityError:
            return f'Word {word} already exists.'

    CACHE[word] = parse_blob(result['def'])

    current_app.logger.info('P%d; Cache: %d', persisted, len(CACHE))

    return CACHE[word]
