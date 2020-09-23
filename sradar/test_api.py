# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 15:08:15 2020

@author: KHO
"""

import http.client
from os import environ
from pathlib import Path

API_URL = 'api.sportradar.us'
API_KEY = environ.get('SR_API_KEY')

URI_BASE = '/nba/trial/v7/en/'
URI_MEAT = 'games/fc3dfaed-74b1-48dc-8278-3b808060296c/summary' # 2020 PIT
URI_METHOD = 'GET'

DATA_FORMAT = '.xml' # .json or .xml

def main():
    """Make https calls to RESTful API and save output locally"""

    print(f'CONNECTING {API_URL}')
    conn = http.client.HTTPSConnection(API_URL)

    location = f'{URI_BASE}{URI_MEAT}{DATA_FORMAT}?api_key={API_KEY}'

    print(f'{URI_METHOD} {location}')
    conn.request(URI_METHOD, location)

    data = conn.getresponse().read()
    size = len(data) / 1000
    print(f'FETCHED {size} KB')

    fpath = '\\'.join([str(Path(__file__).parents[0]),
                       URI_MEAT.replace('/', '-') + DATA_FORMAT])

    print(f'SAVING {fpath}')
    with open(fpath, 'w') as file:
        file.write(data.decode('utf-8'))

if __name__ == "__main__":
    main()
