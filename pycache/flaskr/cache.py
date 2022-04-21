import os
import requests

from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)

from flaskr.db import get_db

MEM_CACHE = {}

bp = Blueprint('cache', __name__)

@bp.route('/dapi/<type>/json/<word>')
def dapiGet(type, word):
    # does word exist in-memory?
    if word in MEM_CACHE:
        return MEM_CACHE[word]

    # does word exist in persistent storage?
    db = get_db()
    result = db.execute(
        'SELECT * FROM dapi WHERE word = ?', (word,)
    ).fetchone()

    # fetch from web if word does not exist in cache or db
    if result is None:
        if type == 'collegiate':
            key = os.environ['DAPI_COLLEGIATE'] # os.getenv(k, default) ??
        else:
            key = os.environ['DAPI_THESAURUS']

        pre = os.environ['DAPI_REFERENCES']
        url = f'{pre}{type}/json/{word}?key={key}'
        json = requests.get(url).json() # TODO check for multiple results

        definitions = json[0]['shortdef']
        if len(definitions) > 0:
            result = { 'def': definitions[0] }
        else:
            result = { 'def': 'NA' }

        try:
            db.execute(
                'INSERT INTO dapi (word, definition) VALUES (?, ?)',
                (word, result['def']),
            )
            db.commit()
        except db.IntegrityError:
            return f'Word {word} already exists.'

    MEM_CACHE[word] = result['def']
    return MEM_CACHE[word]
