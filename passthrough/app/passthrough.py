import os
import requests

from flask import abort, Blueprint, current_app, json, jsonify
from markupsafe import escape
from threading import Lock

from time import sleep

CACHE = {}
LOCKE = Lock()

bp = Blueprint('passthrough', __name__, url_prefix='/dapi')

def parse_blob(blob):
    fls = [] # fl: 'functional label' per dapi spec
    parsed = json.loads(blob)

    # 0: list empty []
    # 1: list of strings ["cam..", "cap.."] (absquatulate)
    # 2: list of dicts [{ "meta": .. }, { "meta": .. }]

    if type(parsed) == type([]) and len(parsed) > 0:
        fls += [
            d['fl'] + ': ' + ';\n'.join(d['shortdef'])
            for d in parsed
            if type(d) == type({}) and 'fl' in d and 'shortdef' in d
        ]

    # TODO plurals ?? use (entry > meta > stems) for x-referencing

    return json.dumps('\n\n'.join(fls))

@bp.route('/json/<word>')
def dapi_word(word):
    word = word.lower()

    with LOCKE:
        if word in CACHE:
            return jsonify(CACHE[word])

    # below 'xcollegiate' > 200, but 'xjson' > 404
    url = f"{os.environ['DAPI_REFERENCES']}/collegiate/json/{word}"
    r = requests.get(url, params = { 'key': os.environ['DAPI_COLLEGIATE'] })

    # IE: misspelling collegiate > 200 with text = "invalid reference name"
    # IE: misspelling json > 404 with text = some html page
    if r.status_code != requests.codes.ok or len(r.text) < 50:
        current_app.logger.warn('%s;%d;%s', word, r.status_code, r.text)
        abort(500, f"Issue fetching '{escape(word)}'")

    parsed = parse_blob(r.content)
    with LOCKE:
        CACHE[word] = parsed
        count = len(CACHE)

    current_app.logger.info('Cache(%d)', count)
    return jsonify(parsed)

@bp.route('/a')
def loop_a():
    i = 0
    while True:
        current_app.logger.info('a %d', i)
        i += 1
        # with LOCKE:
        CACHE['word'] = 'parsed0'
        sleep(0.01)
        current_app.logger.info('%s', CACHE['word'])
        sleep(0.01)
        CACHE['word'] = 'parsed1'
        sleep(0.01)
        current_app.logger.info('%s', CACHE['word'])
        sleep(0.01)
        CACHE['word'] = 'parsed2'
        sleep(0.01)
        current_app.logger.info('%s', CACHE['word'])
        sleep(0.01)
    return 'OK'

@bp.route('/b')
def loop_b():
    i = 0
    while True:
        current_app.logger.info('b %d', i)
        i += 1
        # with LOCKE:
        CACHE['word'] = 'parsed3'
        sleep(0.01)
        current_app.logger.info('%s', CACHE['word'])
        sleep(0.01)
        CACHE['word'] = 'parsed4'
        sleep(0.01)
        current_app.logger.info('%s', CACHE['word'])
        sleep(0.01)
        CACHE['word'] = 'parsed5'
        sleep(0.01)
        current_app.logger.info('%s', CACHE['word'])
        sleep(0.01)
    return 'OK'
