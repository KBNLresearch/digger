#!/usr/bin/env python3.5

import requests
import json
from lxml import etree
import time
import random
import threading

OUTPUT_DIR = "result"

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '"%s" and "%s" and ppn exact "%s" '
SRU_QUERY += 'and date within "01-01-%s 31-12-%s" '
SRU_QUERY += 'and type exact "%s"'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=1'
SRU_QUERY += '&startRecord=%s'

START_STOP = {}
WANTED_TOPICS = []
WANTED_PLACES = []
WANTED_PPNS = []
WANTED_RANGES = []
WANTED_TYPES = ["illustratie met onderschrift",
                "artikel",
                "advertentie",
                "familiebericht"]

def read_ppns(filename='ppn.csv'):
    global WANTED_PPNS

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        ppn = line[1:-1]
        if ppn:
            WANTED_PPNS.append(ppn)


def read_startstop(filename='start_stop.csv'):
    global START_STOP

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        if line.strip():
            line = line.split(',')
            ppn = line[0]
            start = line[1]
            stop = line[2]
        if int(start) > int(stop):
            t = start
            start = stop
            stop = t
        START_STOP[ppn] = [int(start), int(stop)]

def read_places(filename='places.csv'):
    global WANTED_PLACES

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        place = line.split(',')[0][1:-1]
        if place:
            WANTED_PLACES.append(place)
        else:
            print(line)

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

def exec_query(topic, ppn, place, date, atype):
    done = False

    while not done:
        sru = SRU_QUERY % (topic, place, ppn, date, date, atype, '0')
        try:
            data = requests.get(sru)
            data = etree.fromstring(data.content)
            done = True

        except:
            time.sleep(random.random())

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
            return item.text

def read_topics(fname='categories.txt'):
    global WANTED_TOPICS
    cat = {}
    all_topics = []
    with open(fname, 'r') as fh:
        for line in fh.read().split('\n'):
            if not line:
                continue
            name = line.split(',')[0]
            if not line.split(',')[1].isupper():
                if not name in cat:
                    cat[name] = []
                cat[name].append(line.split(',')[1])
                all_topics.append(line.split(',')[1])
    WANTED_TOPICS = all_topics

def do_one_topic(topic, outfile, start_stop):
    result = []

    WANTED_RANGES = range(start_stop[0], start_stop[1])

    for place in WANTED_PLACES:
        for date in WANTED_RANGES:
            for atype in WANTED_TYPES:
                print(topic, place, date, ppn, atype)
                result.append((topic,
                               ppn,
                               place,
                               date,
                               atype,
                               exec_query(topic,
                                          ppn,
                                          place,
                                          date,
                                          atype,
                                          )
                               ))
                out = str(result[-1])[1:-1] + '\n'
                outfile.write(out)

if __name__ == '__main__':
    read_ppns()
    read_places()
    read_years()
    read_topics()
    read_startstop()

    uk = []

    for ppn in WANTED_PPNS:
        for topic in WANTED_TOPICS:
            with open(OUTPUT_DIR + "/" + topic + ".csv", 'a') as fh:
                do_one_topic(topic, fh, START_STOP[ppn])
