#!/usr/bin/env python

import json
import random
import requests

from lxml import etree

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '"%s" and date within "01-01-%s 31-12-%s"'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=10'
SRU_QUERY += '&startRecord=%s'

start_period = 1869
end_period = 1900

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

wanted_sample = 1000
per_place = int(wanted_sample / len(place_names))

sample = {}

for i in range(0, len(place_names)):
    for j in range(0, per_place):
        rnd_year = random.randint(start_period, end_period)

        query = SRU_QUERY % (place_names[i],
                             str(rnd_year),
                             str(rnd_year + 1),
                             '0')
        sru_data = requests.get(query)
        print(query+'<br>')
        sru_data = etree.fromstring(sru_data.content)

        for item in sru_data.iter():
            if item.tag.endswith('numberOfRecords'):
                rnd_record = random.randint(0, int(int(item.text) / 10))
                break

        query = SRU_QUERY % (place_names[i],
                             str(rnd_year),
                             str(rnd_year + 1),
                             str(rnd_record))
        sru_data = requests.get(query)
        sru_data = etree.fromstring(sru_data.content)

        rnd_nr = random.randint(0, 10)
        c = 0
        for item in sru_data.iter():
            if item.tag.endswith('identifier'):
                ocr = item.text
                if rnd_nr == c:
                    break
                c += 1
        if not place_names[i] in sample:
            sample[place_names[i]] = [ocr]
        else:
            sample[place_names[i]].append(ocr)

from pprint import pprint
import operator

for item in sample:
    for ocr in sample[item]:
        r = requests.get('http://kbresearch.nl/topics/?url=%s' % ocr)
        topics = r.json().get('topics')
        topics = sorted(topics.items(), key=operator.itemgetter(1), reverse=True)

        print('%s<a href="%s">%s</a>%s<br><br>' % (item, ocr, ocr, str(topics)))
