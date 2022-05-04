from os import environ as env

from passthrough.passthrough import dapi_key, dapi_path

PATH_GOOD = '/dapi/json/antimacassar'
PATH_PING = '/dapi/ping'

def test_environ():
    assert 'DAPI_REFERENCES' in env and len(env['DAPI_REFERENCES']) == 47
    assert 'DAPI_COLLEGIATE' in env and len(env['DAPI_COLLEGIATE']) == 36
    assert len(dapi_key()) == 36
    assert len(dapi_path()) == 63

def test_ping(client):
    r = client.get(PATH_PING, follow_redirects=True)
    assert r.status_code == 200
    assert b'pong' in r.data

def test_bad_path(client, monkeypatch):
    monkeypatch.setenv('DAPI_REFERENCES', env['DAPI_REFERENCES'] + 'z')
    r = client.get(PATH_GOOD, follow_redirects=True)
    assert r.status_code == 503
    assert b'Possibly malformed request' in r.data

def test_bad_key(client, monkeypatch):
    monkeypatch.setenv('DAPI_COLLEGIATE', 'abc')
    r = client.get(PATH_GOOD, follow_redirects=True)
    assert r.status_code == 503
    assert b'Invalid API key' in r.data

def test_bad_format(client):
    r = client.get('/dapi/xml/antimacassar', follow_redirects=True)
    assert r.status_code == 404
    assert b'requested URL was not found on the server' in r.data

def test_word_imaginary(client):
    r = client.get('/dapi/json/zzzzzzzzzz', follow_redirects=True)
    assert r.status_code == 404
    assert b'Cannot find definition' in r.data

def test_word_simple(client):
    r = client.get(PATH_GOOD, follow_redirects=True)
    assert b'noun: a cover to protect the back or arms of furniture' in r.data
