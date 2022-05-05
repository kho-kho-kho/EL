from os import environ as env
from passthrough.passthrough import (dapi_key, dapi_path,
    AB404_NO_DEFINITION, AB500_ERR_PARSING, AB500_NON_200,
    AB503_SERVICE_DOWN, AB503_BAD_REQUEST, AB503_BAD_API_KEY
)

PATH_WORD = '/dapi/json/antimacassar'
PATH_WORD_DEF = b'noun: a cover to protect the back or arms of furniture'
PATH_WORD_BAD = '/dapi/json/zzzzzzzzzz'
PATH_WORD_XML = '/dapi/xml/antimacassar'
PATH_PING = '/dapi/ping'

def b_lit(str, enc = 'utf-8'):
    return bytes(str, enc)

def test_environ():
    assert 'DAPI_REFERENCES' in env and len(env['DAPI_REFERENCES']) == 47
    assert 'DAPI_COLLEGIATE' in env and len(env['DAPI_COLLEGIATE']) == 36
    assert len(dapi_key()) == 36
    assert len(dapi_path()) == 63

def test_ping(client):
    r = client.get(PATH_PING, follow_redirects=True)
    assert r.status_code == 200
    assert b'pong' in r.data

def test_bad_ping_req(client, monkeypatch):
    ref = env['DAPI_REFERENCES'].replace('api', 'apiz')
    monkeypatch.setenv('DAPI_REFERENCES', ref)
    r = client.get(PATH_PING, follow_redirects=True)
    assert r.status_code == 503
    assert b_lit(AB503_SERVICE_DOWN) in r.data

def test_bad_ping_path(client, monkeypatch):
    ref = env['DAPI_REFERENCES'] + 'z'
    monkeypatch.setenv('DAPI_REFERENCES', ref)
    r = client.get(PATH_PING, follow_redirects=True)
    assert r.status_code == 500
    assert b_lit(AB500_NON_200) in r.data

def test_bad_req(client, monkeypatch):
    ref = env['DAPI_REFERENCES'].replace('api', 'apiz')
    monkeypatch.setenv('DAPI_REFERENCES', ref)
    r = client.get(PATH_WORD, follow_redirects=True)
    assert r.status_code == 503
    assert b_lit(AB503_SERVICE_DOWN) in r.data

def test_bad_path(client, monkeypatch):
    ref = env['DAPI_REFERENCES'] + 'z'
    monkeypatch.setenv('DAPI_REFERENCES', ref)
    r = client.get(PATH_WORD, follow_redirects=True)
    assert r.status_code == 503
    assert b_lit(AB503_BAD_REQUEST) in r.data

def test_bad_key(client, monkeypatch):
    monkeypatch.setenv('DAPI_COLLEGIATE', 'abc')
    r = client.get(PATH_WORD, follow_redirects=True)
    assert r.status_code == 503
    assert b_lit(AB503_BAD_API_KEY) in r.data

def test_bad_format(client):
    r = client.get(PATH_WORD_XML, follow_redirects=True)
    assert r.status_code == 404
    assert b'requested URL was not found on the server' in r.data

def test_word_imaginary(client):
    r = client.get(PATH_WORD_BAD, follow_redirects=True)
    assert r.status_code == 404
    assert b_lit(AB404_NO_DEFINITION) in r.data

def test_word_simple(client):
    r = client.get(PATH_WORD, follow_redirects=True)
    assert PATH_WORD_DEF in r.data
