#!/usr/bin/env python3 

import os
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



data = []

ok = 0
nok = 0 

ppn = '37631091X'
place = 'amsterdam'

for line in open('amsterdam_old', 'r').read().split('\n'):
    if not line.find('37631091X') > -1 or not line:
        continue
    atype = line.split(',')[3].replace("'", "").strip()
    date = line.split(',')[2].replace("'", "").strip()
    hits = int(line.split(',')[-1].replace("'",''))


    response = requests.get(SRU_QUERY % (place, ppn, date, date, atype, "0"))
    data= etree.fromstring(response.content)

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
                if not hits == int(item.text):
                        print("MISSS")


#from pprint import pprint
#pprint(data)
