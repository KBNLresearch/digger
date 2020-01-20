#!/usr/bin/env python3.5

import requests
import json
from lxml import etree
import time
import random

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '"%s" and ppn exact "%s" '
SRU_QUERY += 'and date within "01-01-%s 31-12-%s" '
SRU_QUERY += 'and type exact "%s"'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=10'
SRU_QUERY += '&startRecord=%s'

NER = "http://ner.kbresearch.nl/?url=%s"

WANTED_PLACES = []
WANTED_PPNS = []
WANTED_RANGES = []
WANTED_TYPES = ["illustratie met onderschrift",
                "artikel",
                "advertentie",
                "familiebericht"]

CLEAN = "http://kbresearch.nl/remove_leading_place/?url=%s&query=%s"

def read_ppns(filename='corpus.csv'):
    global WANTED_PPNS

    with open(filename) as fh:
        data = fh.read()

    i = 0

    for line in data.split('\n'):
        if line.find(',') > -1:
            i += 1
            ppn = line.split(',')[1][1:-1]
            WANTED_PPNS.append(ppn)
            if i > 2: # LIMIT NR OF PPNS
                return

def read_places(filename='places_exceptions.csv'):
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

def exec_clean(identifier, target='Dordrecht'):
    r = requests.get(CLEAN % (identifier, target))
    return r.json()


def exec_query(ppn, place, idate, atype, start=0, identifiers=[]):
    done = False

    while not done:
        try:
            date_start = date_end = idate
            sru = SRU_QUERY % (place, ppn, date_start, date_end, atype, str(start))
            data = requests.get(sru)
            data = etree.fromstring(data.content)
            done = True
        except:
            time.sleep(random.random())

    for item in data.iter():
        #print(item.tag, item.attrib, item.text)
        if item.tag.endswith('numberOfRecords'):
            result_count = int(item.text)
        if item.tag.endswith('identifier'):
            identifiers.append(item.text)


    if start + 10 < result_count and result_count > 0:
        identifier = exec_query(ppn, place, idate, atype, start + 10, identifiers)
        return identifiers
    else:
        return identifiers
    #return ("akaakaka")



if __name__ == '__main__':
    read_ppns()
    read_places()
    read_years()

    result = []

    for ppn in WANTED_PPNS:
        for place in WANTED_PLACES:
            for date in WANTED_RANGES:
                atype = "artikel"
                result = exec_query(ppn, place, date, atype, 0, [])

                total_hits = len(result)
                total_verified_hits = 0

                for i in result:
                    if exec_clean(i, place.lower()):
                        total_verified_hits += 1
                print("atype: %s, ppn: %s, place: %s, date: %s, hits_string: %s, hits_clean: %s" % (atype, ppn, place, date, total_hits, total_verified_hits))

'''
    with open('freq.json', 'w') as fh:
        fh.write(json.dumps(result))

output:

    37631091X Eindhoven 1900 1909 2068

    ppn, place, start_date, end_date, freq

'''
