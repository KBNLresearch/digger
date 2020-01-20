#!/usr/bin/env python3

import os
import json
import random
import requests
import topic

from lxml import etree

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '%s'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=100'

START_STRING = "industrie"
OUTPUT_LDA = "lda_" + START_STRING




def create_dataset():
    query = SRU_QUERY % (START_STRING)
    sru_data = requests.get(query)
    sru_data = etree.fromstring(sru_data.content)

    remove = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<text>', '</text>',
              '<p>', '</p>',
              '<title>', '</title>']

    data_set = []


    for item in sru_data.iter():
        if not item.tag.endswith('identifier'):
            continue
        req = requests.get(item.text)
        text = req.text
        for r in remove:
            text = text.replace(r, '').strip()
        text = text.replace('\n', ' ').strip()

        if text in data_set:
            continue

        if text.find('>') > -1 and text.find('<') > -1:
            continue

        data_set.append(text)
    return data_set

data_set = create_dataset()
lda = topic.gen_topics(data_set, START_STRING.split())
from pprint import pprint
lda.save("lda_industrie")
print("===RES===")
result = (lda.print_topics(num_topics=10, num_words=10))

for r in result:
    print(r)
