# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 15:39:16 2020

@author: KHO
"""

import random
import re
import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

INPUT = 'AMZN,'
OUTPUT = 'output.csv'

WAIT_MIN = 5
WAIT_MAX = 9

URL_BASE = 'https://finance.yahoo.com/quote/'
YNA = 'N/A' # for matching missing values

def _parse_stats(src, out):
    """Regex routines to parse out statistics from summary section"""

    cap = bet = per = div = yld = -1.0
    mc_units = {'B': 1, 'M': 0.001, 'T': 1000, }

    regex = r'<table.*?>(.*?)</table>.*<table.*?>(.*?)</table>'
    match = re.search(regex, src, re.S)
    if match and match.group(1) and match.group(2):
        tb2 = match.group(2)

        reg = r'<span.*?>Market Cap</span>.*?<td.*?>(.*?)</td>'
        mat = re.search(reg, tb2, re.S)
        if mat and mat.group(1) and mat.group(1) != YNA:
            cap = float(mat.group(1)[:-1]) * mc_units[mat.group(1)[-1:]]

        reg = r'<span.*?>Beta.*?</span>.*?<td.*?>(.*?)</td>'
        mat = re.search(reg, tb2, re.S)
        if mat and mat.group(1) and mat.group(1) != YNA:
            bet = mat.group(1)

        reg = r'<span.*?>PE Ratio.*?</span>.*?<td.*?>(.*?)</td>'
        mat = re.search(reg, tb2, re.S)
        if mat and mat.group(1) and mat.group(1) != YNA:
            per = mat.group(1)

        reg = r'<span.*?>Forward Dividend.*?</span>.*?<td.*?>(.*?) \((.*?)%\)</td>'
        mat = re.search(reg, tb2, re.S)
        if mat and mat.group(1) and mat.group(1) != YNA and mat.group(2):
            div = mat.group(1)
            yld = mat.group(2)

    out['M.Cap(1b)'] = cap
    out['Beta(5ym)'] = bet
    out['PER(TTM)'] = per
    out['Fwd.Div$'] = div
    out['Div.yld%'] = yld

def _parse_profile(src, out):
    """Regex routines to parse out fields from company profile section"""

    emp = -1.0
    ind = sec = ''

    match = re.search(r'"summaryProfile"\s*:\s*{(.*?)}', src, re.S)
    if match and match.group(1):
        pro = match.group(1)

        if not re.search(r'"err"\s*:\s*{', pro, re.S):
            mat_emp = re.search(r'"fullTimeEmployees"\s*:\s*(\d*)', pro, re.S)
            if mat_emp and mat_emp.group(1):
                emp = mat_emp.group(1)

            mat_ind = re.search(r'"industry"\s*:\s*"(.*?)"', pro, re.S)
            if mat_ind and mat_ind.group(1):
                ind = mat_ind.group(1)

            mat_sec = re.search(r'"sector"\s*:\s*"(.*?)"', pro, re.S)
            if mat_sec and mat_sec.group(1):
                sec = mat_sec.group(1)

    out['Emp(1k)'] = float(emp) / 1000
    out['Sector'] = sec
    out['Indus.'] = ind

def main():
    """
    Selenium-based yahoo finance parser for "quotes"
    Includes configurable range-bound randomized throttle between web hits
    If webdriver/browser version becomes mismatched:
    https://chromedriver.chromium.org/downloads/version-selection
    """

    random.seed()

    options = Options()
    options.add_argument('--headless')
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    rows = []
    for name, url in [(x, f'{URL_BASE}{x}') for x in INPUT.split(',') if x]:
        driver.get(url)

        row = {'Name': name}
        _parse_profile(driver.page_source, row)
        _parse_stats(driver.page_source, row)
        rows.append(row)

        print('|'.join([str(x) for x in row.values()]))
        time.sleep(random.randint(WAIT_MIN, WAIT_MAX))

    fpath = '\\'.join([str(Path(__file__).parents[0]), OUTPUT])
    pd.DataFrame(rows).to_csv(fpath)

    driver.quit()

if __name__ == "__main__":
    main()
