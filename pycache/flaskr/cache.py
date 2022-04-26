import os
import requests

from flask import (
    abort, Blueprint, current_app, flash, json, jsonify, redirect, url_for
)
from flaskr.db import get_db
from markupsafe import escape
from werkzeug.exceptions import HTTPException

CACHE = {}

bp = Blueprint('cache', __name__, url_prefix='/dapi')

def get_dapi_bulk():
    words = []
    for word in words:
        get_dapi_word(word)

# 0: list empty []
# 1: list of strings ["campanulate", "capitulate"] (absquatulate)
# 2: list of dicts [{ "meta": .. }, { "meta": .. }]

def parse_blob(blob):
    fls = [] # fl: 'functional label' per dapi spec
    parsed = json.loads(blob)
    if type(parsed) == type([]) and len(parsed) > 0:
        fls += [
            d['fl'] + ': ' + ';\n'.join(d['shortdef'])
            for d in parsed
            if type(d) == type({}) and 'fl' in d and 'shortdef' in d
        ]

    # TODO plurals ?? use (entry > meta > stems) for x-referencing

    return json.dumps('\n\n'.join(fls))

@bp.before_app_first_request
def init_dapi():
    # db = get_db()
    # result = db.execute(
    #     'SELECT * FROM dapi WHERE word = ?', (word,)
    # ).fetchone()
    db = get_db()
    for row in db.execute('SELECT * FROM dapi').fetchall():
        CACHE[row['word']] = parse_blob(row['def'])
    current_app.logger.info('Cache(%d) warm ..', len(CACHE))

@bp.route('/<word>', methods=['PUT'])
def put_dapi_word(word):
    word = word.lower()

    url = f"{os.environ['DAPI_REFERENCES']}/collegiate/json/{word}"
    # url = f"{os.environ['DAPI_REFERENCES']}/collegiate/xjson/{word}"
    r = requests.get(url, params = { 'key': os.environ['DAPI_COLLEGIATE'] })
    if r.status_code != requests.codes.ok:
        abort(r.status_code, f"Issue fetching '{word}'")

    try:
        db = get_db()
        db.execute(
            'INSERT INTO dapi (word, defs) VALUES (?, ?)' +
            ' ON CONFLICT (word) DO UPDATE SET def=excluded.def',
            (word, r.content),
        )
        db.commit()
    except:
        abort(500, f"Issue adding '{word}'")

    CACHE[word] = parse_blob(r.content)
    current_app.logger.info('Cache(%d)', len(CACHE))
    return jsonify(CACHE[word])

# GET (SAFE & IDEMPOTENT & CACHEABLE)
# The GET method requests a representation of the specified resource.
# Requests using GET should only retrieve data.

@bp.route('/json/<word>', methods=['GET'])
def get_dapi_word(word):
    word = word.lower()

    if word in CACHE:
          return jsonify(CACHE[word])

    return put_dapi_word(word)

@bp.route('/test')
def test_dapi():
    # render_template('500.html')
    abort(401, 'NOBODY IS AUTHORIZED')

# @bp.errorhandler(Exception)
# def handle_exception(e):
#     return (jsonify(error=str(e)),
#         e.code if isinstance(e, HTTPException) else 500)
