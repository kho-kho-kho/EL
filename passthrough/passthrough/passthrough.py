import os
import requests

from flask import abort, Blueprint, current_app, json, jsonify
from json import JSONDecodeError
from threading import Lock

AB404_NO_DEFINITION = 'Cannot find definition'
AB500_ERR_PARSING = 'Blob parsing failed'
AB500_NON_200 = 'Non-200 response received'
AB503_SERVICE_DOWN = 'Service unavailable'
AB503_BAD_REQUEST = 'Possibly malformed request'
AB503_BAD_API_KEY = 'Invalid API key'

CACHE = {}
LOCKE = Lock()

bp = Blueprint('passthrough', __name__, url_prefix='/dapi')

def dapi_key():
    return os.getenv('DAPI_COLLEGIATE')

def dapi_path(type = 'collegiate'):
    # misspell collegiate > 200 with text = "invalid reference name"

    return f"{os.getenv('DAPI_REFERENCES')}/{type}/json"

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

def log_request(r, length = 50):
    current_app.logger.warning(
        '%s;%d;%s', r.url, r.status_code, r.content[0:length]
    )

@bp.route('/json/<word>')
def dapi_word(word):
    word = word.lower()

    with LOCKE:
        if word in CACHE:
            return jsonify(CACHE[word])

    try:
        p = { 'key': dapi_key() }
        r = requests.get(f"{dapi_path()}/{word}", params = p)
    except requests.exceptions.RequestException as err:
        current_app.logger.warning('word;%s', err)
        abort(503, AB503_SERVICE_DOWN)

    if r.status_code != requests.codes.ok or len(r.text) < 50:
        log_request(r)
    if r.status_code == 404:
        abort(503, AB503_BAD_REQUEST)
    if r.content == b'[]':
        abort(404, AB404_NO_DEFINITION)

    try:
        parsed = parse_blob(r.content)
    except JSONDecodeError:
        log_request(r)
        if b'Invalid API key' in r.content:
            abort(503, AB503_BAD_API_KEY)
        abort(500, AB500_ERR_PARSING)

    with LOCKE:
        CACHE[word] = parsed
        count = len(CACHE)

    current_app.logger.info('Cache(%d)', count)
    return jsonify(parsed)

@bp.route('/ping')
def dapi_ping():
    try:
        r = requests.get(dapi_path() + '/')
    except requests.exceptions.RequestException as err:
        current_app.logger.warning('ping;%s', err)
        abort(503, AB503_SERVICE_DOWN)

    if r.status_code == 200:
        return 'pong'

    log_request(r)
    abort(500, AB500_NON_200)
