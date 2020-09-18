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

WAIT_MIN = 5
WAIT_MAX = 9

URL_BASE = 'https://finance.yahoo.com/quote/'

def main():
    """ xxx """

    random.seed()

    options = Options()
    options.add_argument("--incognito")
    options.headless = True
    driver = webdriver.Chrome(options=options)

    args = [(x, f'{URL_BASE}{x}') for x in INPUT.split(',') if x]

    for ticker, url in args:
        driver.get(url)
        src = driver.page_source

        res = 'OK'
        cap = bet = per = div = emp = ind = sec = ''

        match = re.search(r'<table.*?>(.*?)</table>.*<table.*?>(.*?)</table>', src, re.S)
        if match and match.group(1) and match.group(2):
            tb2 = match.group(2)

            cap = re.search(r'<span.*?>Market Cap</span>.*?<span.*?>(.*?)</span>', tb2, re.S).group(1)
            bet = re.search(r'<span.*?>Beta.*?</span>.*?<span.*?>(.*?)</span>', tb2, re.S).group(1)
            per = re.search(r'<span.*?>PE Ratio.*?</span>.*?<span.*?>(.*?)</span>', tb2, re.S).group(1)
            div = re.search(r'<span.*?>Forward Dividend.*?</span>.*?<td.*?>(.*?)</td>', tb2, re.S).group(1)

        match = re.search(r'"summaryProfile"\s*:\s*{(.*?)}', src, re.S)
        if match and match.group(1):
            pro = match.group(1)

            if re.search(r'"err"\s*:\s*{', pro, re.S):
                res = 'ERR'
            else:
                emp = re.search(r'"fullTimeEmployees"\s*:\s*(\d*)', pro, re.S).group(1)
                ind = re.search(r'"industry"\s*:\s*"(.*?)"', pro, re.S).group(1)
                sec = re.search(r'"sector"\s*:\s*"(.*?)"', pro, re.S).group(1)

        print(f'{ticker}|{res}|{sec}|{ind}|{emp}|{cap}|{bet}|{per}|{div}')
        time.sleep(random.randint(WAIT_MIN, WAIT_MAX))

    driver.quit()

if __name__ == "__main__":
    main()
