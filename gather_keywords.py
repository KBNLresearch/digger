#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#atype: artikel, ppn: 400337266, place: Dieren, date: 1924, hits_string: 142, hits_ner: 5

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
import time
import random
import requests
import codecs
from lxml import etree

OUTPUT_DIR = "result"

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '%s and "%s" and ppn exact "%s" '
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

WANTED_KW = ["handel", "industrie", "fabriek", "toerisme", "bank", "verzekering",
             "detailhandel", "informatica", "electronica", "eletrionika", "paard", "vee",
             "spoorweg", "autoweg", "snelweg", "ringweg", "vliegveld", "haven", "trein",
             "boot", "schip", "auto", "vrachtwagen", "vliegtuig", "staal", "zijde", "katoen",
             "hout", "staal", "veen", "olie", "elektriciteit", "kolen", "chemisch", "misdaad",
             "slachtoffer", "moord", "ongeluk", "brand", u"industrieën", "fabrieken", "banken",
             "verzekeringen", "paarden", "spoorwegen", "autowegen", "snelwegen", "ringwegen", "vliegvelden",
             "havens", "treinen", "boten", "schepen", "autos", "vrachtwagens", "vliegtuigen", "slachtoffers",
             "moorden", "ongelukken", "branden"]

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

    print(NER % identifier)
    print(r.json().keys())


    all_txt = []
    all_txt1 = r.json().get('text')

    seen = []

    for item in r.json().get('entities'):
        if item.get('ne').lower() == target.lower():
            if item.get('type') == 'location':
                place_found = True


    if place_found:
        for i in all_txt1:
            for item in all_txt1[i].replace('.', ' ').replace(',', ' ').replace(';', ' ').split():
                item = item.lower()
                if not item[-1].isalpha():
                    item = item[:-1]

                for kw in WANTED_KW:
                    if item == kw and not kw in seen:
                        seen.append(kw)
            #
            #item in WANTED_KW1 and not item in seen:
            #    seen.append(item)

    return place_found, seen


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



def exec_query(kw, place, ppn, idate, atype, start=0):
    date_start = date_end = idate
    sru = SRU_QUERY % (orq, place, ppn, date_start, date_end, atype, str(start))
    data = sru_fetch(sru)

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
            result_count = int(item.text)

    identifiers = []
    for record in range(0, result_count, 10):
        sru = SRU_QUERY % (orq, place, ppn, date_start, date_end, atype, str(record))
        print(sru, result_count)
        data = sru_fetch(sru)
        for item in data.iter():
            #print(item)
            if item.tag.endswith('identifier'):
                identifiers.append(item.text)
                #print(item.text)
    return identifiers


with open('freq.csv', 'r') as fh:
    for line in fh.read().strip().split('\n'):
        line = 'atype: artikel, ppn: 37631091X, place: Kampen, date: 1938, hits_string: 100, hits_ner: 58'
        #line = 'atype: artikel, ppn: 37631091X, place: Kampen, date: 1938, hits_string: 100, hits_ner: 58'
        #line = 'atype: artikel, ppn: 37631091X, place: Kampen, date: 1938, hits_string: 1150, hits_ner: 421'
        #line = 'atype: familiebericht, ppn: 37631091X, place: Putten, date: 1914, hits_string: 37, hits_ner: 7'
        #line = 'atype: artikel, ppn: 37631091X, place: Best, date: 1918, hits_string: 1036, hits_ner: 59'

        print(line)

        exp_nr = int(line.split(':')[-2].split(',')[0].strip())
        print("excpected: ", int(line.split(':')[-2].split(',')[0].strip()))


        type_name = line.split(':')[1].strip().split(',')[0]
        ppn = line.split(':')[2].strip().split(',')[0]
        place_name = line.split(':')[3].strip().split(',')[0]
        year = line.split(':')[4].strip().split(',')[0]

        orq = ""

        for item in WANTED_KW:
            orq += '"' + item + '"' + " OR "

        total = {}
        found = False

        org = orq.strip()
        orq = orq[:-3].strip()

        ids = exec_query(orq, place_name,ppn, year, type_name)


        if not ids is None:
            print(len(ids), exp_nr)
            if not len(ids) == exp_nr:
                print("WAARRRNINGGGG, expected does not equal current")
            count = 0

            '''

            for id in ids:
                print(id)
                found, seen  = exec_ner(id, place_name)
                if found:
                     count += 1
                     for item in seen:
                         if not item in total:
                             total[item] = 1
                         else:
                             total[item] += 1 

            from pprint import pprint
            pprint(total)
            total = {}


            for kw in total:
                with codecs.open('output_ner/'+ kw + '.txt', 'a', encoding='utf-8') as fh:
                    fh.write(unicode(line)+ ", "+ unicode(kw) + ": " + unicode(total[kw]) + "\n")
            total = {}
            '''
