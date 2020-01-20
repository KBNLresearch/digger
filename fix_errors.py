#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-


import sys
import codecs
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)
#sys.stderr = codecs.getwriter('utf8')(sys.stderr)
print((u'aap'))
import time
import random
import requests
import codecs
from lxml import etree

print('aap')

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '"%s" and ppn exact "%s" '
SRU_QUERY += 'and date within "01-01-%s 31-12-%s" '
SRU_QUERY += 'and type exact "%s"'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=10'
SRU_QUERY += '&startRecord=%s'

START_STOP = {}

NER = "http://ner.kbresearch.nl/?url=%s"

WANTED_TOPICS = []
WANTED_PLACES = []
WANTED_PPNS = []
WANTED_RANGES = []
WANTED_TYPES = ["illustratie met onderschrift",
		"artikel",
		"advertentie", 
		"familiebericht"]

def exec_ner(identifier, target='son'):

    retry = 100

    place_found = False

    while retry > 0:
        try:
            r = requests.get(NER % identifier)
            assert r.status_code == 200
            retry = -1
        except:
            retry -= 1
            time.sleep(random.random())


    all_txt = []
    all_txt1 = r.json().get('text')

    for item in r.json().get('entities'):
        if item.get('ne').lower() == target.lower():
            if item.get('type') == 'location':
                place_found = True
    return place_found


def sru_fetch(sru):
    print(sru)
    retry = 100
    data = False

    while retry > 0:
        try:
            data = requests.get(sru)
            data = etree.fromstring(data.content)
            retry = -1
        except:
            retry -= 1
            time.sleep(random.random())
    return data

def exec_query_count(place, ppn, idate, atype, start=0):
    date_start = date_end = idate
    sru = SRU_QUERY % (place, ppn, date_start, date_end, atype, str(start))
    data = sru_fetch(sru)

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
            result_count = int(item.text)
            return result_count



def exec_query(place, ppn, idate, atype, start=0):
    date_start = date_end = idate
    sru = SRU_QUERY % (place, ppn, date_start, date_end, atype, str(start))
    data = sru_fetch(sru)

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
            result_count = int(item.text)
            break

    identifiers = []
    for record in range(0, result_count, 10):
        sru = SRU_QUERY % (place, ppn, date_start, date_end, atype, str(record))
        print(sru, result_count)
        data = sru_fetch(sru)
        for item in data.iter():
            if item.tag.endswith('identifier'):
                identifiers.append(item.text)
    return identifiers

with open('freq.csv', 'r') as fh:
    for line in fh.read().strip().split('\n'):

        if not line.strip():
            continue
        exp_nr = int(line.split(':')[-2].split(',')[0].strip())
        print("excpected: ", int(line.split(':')[-2].split(',')[0].strip()))


        type_name = line.split(':')[1].strip().split(',')[0]
        ppn = line.split(':')[2].strip().split(',')[0]
        place_name = line.split(':')[3].strip().split(',')[0]
        year = line.split(':')[4].strip().split(',')[0]

        total = {}
        found = False

        wok = False
        result_count = exec_query_count(place_name, ppn, year, type_name)
        print(result_count, exp_nr)

        if result_count not in  range(exp_nr -1, exp_nr + 1):
            print("DDIFFF", result_count, exp_nr)
            ids = exec_query(place_name, ppn, year, type_name)
            if not ids is None:
                print(len(ids), exp_nr)
                if not len(ids) == exp_nr:
                    wok = True
                count = 0

                if wok:
                    for id in ids:
                        found = exec_ner(id, place_name)
                        if found:
                             count += 1
                    print("WRITEOUT")
                    with codecs.open('errors_fix.txt', 'a', encoding='utf-8') as fh:
                        fh.write(line+ u", string_match: "+ str(len(ids)) + u",ner_match:" + str(count) + u"\n")
