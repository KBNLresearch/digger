#!/usr/bin/env python3.5

import requests
import json
from lxml import etree
import time
import random

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += 'ppn exact "%s" '
SRU_QUERY += 'and date within "01-01-%s 31-12-%s" '
SRU_QUERY += 'and type exact "%s"'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=1'
SRU_QUERY += '&startRecord=%s'

WANTED_PLACES = []
WANTED_PPNS = []
WANTED_RANGES = []
WANTED_TYPES = ["illustratie met onderschrift",
                "artikel",
                "advertentie",
                "familiebericht"]

def read_ppns(filename='corpus.csv'):
    global WANTED_PPNS

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        if line.find(',') > -1:
            ppn = line.split(',')[1][1:-1]
            WANTED_PPNS.append(ppn)

def read_places(filename='places.csv'):
    global WANTED_PLACES

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        if line.find(',') > -1 and not line.find('naam') > -1:
            place = line.split(',')[1][1:-1]
            WANTED_PLACES.append(place)

def read_years(filename='years.txt'):
    global WANTED_RANGES
    years = []


    '''
    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        if not line == 'Years':
            years.append(str(line))

    for i in range(0, len(years)-1):
        if i >0:
            WANTED_RANGES.append([str(int(years[i]) + 1), years[i + 1]])
        else:
            WANTED_RANGES.append([years[i], years[i+1]])
    '''

    for i in range(1865, 1995):
        WANTED_RANGES.append(str(i))

def exec_query(ppn, date, atype):
    done = False

    while not done:
        try:
            date_start = date_end = date
            sru = SRU_QUERY % (ppn, date_start, date_end, atype, '0')
            data = requests.get(sru)
            data = etree.fromstring(data.content)
            done = True
        except:
            time.sleep(random.random())

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
            return item.text

if __name__ == '__main__':
    read_ppns()
    #read_places()
    read_years()

    result = []

    for ppn in WANTED_PPNS:
        #for place in WANTED_PLACES:
        for date in WANTED_RANGES:
            for atype in WANTED_TYPES:
                result.append((ppn, date, atype, exec_query(ppn, date, atype)))
                print(str(result[-1])[1:-1])

'''
    with open('freq.json', 'w') as fh:
        fh.write(json.dumps(result))

output:

    37631091X Eindhoven 1900 1909 2068

    ppn, place, start_date, end_date, freq

'''
