# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 15:39:16 2020

@author: KHO
"""

import random
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

INPUT = 'AAPL,'

URL_BASE = 'https://finance.yahoo.com/quote/'

random.seed()

options = Options()
options.add_argument("--incognito")
options.headless = True
driver = webdriver.Chrome(options=options)

args = [(x, f'{URL_BASE}{x}') for x in INPUT.split(',') if x]

for ticker, url in args:
    driver.get(url)
    src = driver.page_source

    match = re.search(r'"summaryProfile"\s*:\s*{(.*?)}', src, re.DOTALL)
    if match and match.group(1):
        txt = match.group(1)
        err = re.search(r'"err"\s*:\s*{', txt, re.S)
        if err:
            print(f'{ticker}|ERR')
            continue
        emp = re.search(r'"fullTimeEmployees"\s*:\s*(\d*)', txt, re.S).group(1)
        ind = re.search(r'"industry"\s*:\s*"(.*?)"', txt, re.S).group(1)
        sec = re.search(r'"sector"\s*:\s*"(.*?)"', txt, re.S).group(1)
        print(f'{ticker}|{sec}|{ind}|{emp}')

    time.sleep(random.randint(5, 9))

driver.quit()

def main():
    """ xxx """

if __name__ == "__main__":
    main()
