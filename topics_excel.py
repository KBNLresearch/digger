#!/usr/bin/env python3

import xlwt
import os
import json
import sys
import requests
import random
import xml.etree.ElementTree as etree


from pprint import pprint

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '"%s" and date within "01-01-%s 31-12-%s" and ppn exact %s'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=10'
SRU_QUERY += '&startRecord=%s'

start_period = 1865
end_period = 1995

place_names = [
        "Alkmaar",
        "Almere",
        "Alphen aan de Rijn",
        "Amersfoort",
        "Amsterdam",
        "Delft",
        "Den Haag",
        "Dordrecht",
        "Haarlem",
        "Haarlemmermeer",
        "Leyde",
        "Leiden",
        "Rotterdam",
        "Utrecht",
        "Westland",
        "Zaanstad",
        "Zoetermeer",
        ]

COLNAMES = ['url', 'topic', 'criminality', 'transportation/infrastructure', 'industry', 'services', 'science', 'culture', 'politics', 'sports', 'business', 'ocr']

PPNS = []


with open('corpus.csv', 'r') as fh:
    data = fh.read()

for line in data.split('\n'):
    if len(line.split(',')) == 3:
        ppn = line.split(',')[1].replace('"', '')
        PPNS.append(ppn)


def fetch_random_article(place, ppn, record_nr):
    query = SRU_QUERY % (place,
                         str(start_period),
                         str(end_period),
                         ppn,
                         record_nr)
    try:
        sru_data = requests.get(query)
        sru_data = etree.fromstring(sru_data.content)
        for item in sru_data.iter():
            if item.tag.endswith('identifier'):
                return item.text
                break
    except:
        return


def fetch_10_random_articles():
    max_record = 0
    all_articles = []

    while len(all_articles) < 10:
        while max_record < 10:
            ppn = PPNS[random.randint(0, len(PPNS) - 1)]
            place = place_names[random.randint(0, len(place_names)-1)]

            query = SRU_QUERY % (place,
                                 str(start_period),
                                 str(end_period),
                                 ppn,
                                 '0')
            sru_data = requests.get(query)
            sru_data = etree.fromstring(sru_data.content)
            for item in sru_data.iter():
                if item.tag.endswith('numberOfRecords'):
                    max_record = int(int(item.text) / 10)
                    break


        rnd_articles = []
        while len(rnd_articles) < 10:
            nr = random.randint(0, max_record)
            if not nr in rnd_articles:
                rnd_articles.append(nr)

        for nr in rnd_articles:
            article = fetch_random_article(place, ppn, nr)
            if article and not article in all_articles:
                all_articles.append(article)

    return all_articles

def fetch_article(url):
    req = requests.get(url)
    print(url)
    txt = req.text
    txt = txt.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
    txt = txt.replace('<text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="articletext.xsd">', '')
    txt = txt.replace('<p>', '')
    txt = txt.replace('</p>', '')
    txt = txt.replace('<text>', '')
    txt = txt.replace('</text>', '')
    txt = txt.replace('<title>', '')
    txt = txt.replace('</title>', '')
    return txt

def xls_create(filename):
    book = xlwt.Workbook()
    sh = book.add_sheet(filename)

    i = 0
    for colname in COLNAMES:
        sh.write(0, i, colname)
        i+=1

    return(book, sh)

def xls_finish(book):
    book.save("test.xls")

def xls_add_row(sh, rnd_articles, col=1):

    row = ['http://resolver.kb.nl/resolve?urn=KBNRC01:000028240:mpeg21:a0001:ocr',
           '',
           0,
           0,
           0,
           0,
           0,
           0,
           0,
           0,
           0,
           'blaat']
    for i in range(1, len(rnd_articles)):
        row[0] = rnd_articles[i]
        row[-1] = fetch_article(row[0])
        for count, values in enumerate(row):
            sh.write(i, count, values)

def parse_json_files(rnd_articles):
    book, sh = xls_create("test.xsl")
    xls_add_row(sh, rnd_articles)
    xls_finish(book)


rnd_articles = []

while len(rnd_articles) < 1000:
    for article in fetch_10_random_articles():
        if not article in rnd_articles:
            rnd_articles.append(article)

parse_json_files(rnd_articles)
