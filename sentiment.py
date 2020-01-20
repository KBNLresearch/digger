#!/usr/bin/env python3

import json
import lxml.html
import requests

from flask import request, Response, Flask
from lxml import etree
from pattern import nl
from pattern.nl import sentiment

application = Flask(__name__)
application.debug = True

IR = "http://kbresearch.nl/get_ir/?identifier=%s"
NIR = "http://kbresearch.nl/get_nir/?identifier=%s"
SENTIMENT = "http://sentiment.kbresearch.nl/?url=%s&place=%s"

@application.route('/')
def index():
    url = request.args.get('url')

    if not url:
        return("Invoke example ?url=http://resolver.kb.nl/resolve?urn=ddd:010639198:mpeg21:a0001:ocr")

    parsed_text = ocr_to_dict(url)

    relevant_places =  fetch_ir(url)

    result = {'found': [], 'sentiment': {}}

    for item in relevant_places:
        relevant = []
        for place in item.get('str'):
            result['found'].append(place)
            for sent in extract_part_of_intrest(parsed_text, place):
                if not sent in relevant:
                    relevant.append(sent)

        result['sentiment'][item.get('id')] = sentiment(" ".join(relevant))[0]

    resp = Response(response=json.dumps(result),
		    mimetype='application/json; charset=utf-8')

    return resp


def fetch_ir(identifier):
    url = IR % identifier
    ir = requests.get(url)
    ir = ir.json()

    sentiment_targets = []
    ne = {}
    ids = set()

    for item in ir.get('links'):
        if not item.get('id') in ne:
            ne[item.get('id')] = [item.get('neString')]
        else:
            ne[item.get('id')].append(item.get('neString'))

    for entity in ne.keys():
        url = NIR % entity
        nir = requests.get(url)
        nir = nir.json()

        for entry in nir.get('enrich'):
            if entry.get('latlong'):
                sentiment_targets.append(entity)
                break

    result = []
    for target in sentiment_targets:
        result.append({'id': target, 'str': ne[target]})

    return result

def ocr_to_dict(url):
    req = requests.get(url)
    text = req.content

    parser = lxml.etree.XMLParser(ns_clean=True,
                                  recover=True,
                                  encoding='utf-8')

    xml = lxml.etree.fromstring(text, parser=parser)

    parsed_text = {}

    for item in xml.iter():
        if not item.text:
            continue

        item.text = item.text.replace('&', '&amp;')
        item.text = item.text.replace('>', '&gt;')
        item.text = item.text.replace('<', '&lt;')

        if item.tag == 'title':
            if "title" not in parsed_text:
                parsed_text["title"] = []
            parsed_text["title"].append(item.text)
        else:
            if "p" not in parsed_text:
                parsed_text["p"] = []
            parsed_text["p"].append(item.text)

    for part in parsed_text:
        parsed_text[part] = "".join(parsed_text[part])

    return parsed_text

def extract_part_of_intrest(data, entity='Moskou', distance=2):
    parsed = []
    unwanted = []
    wanted = []

    go = 0
    for part in data:
        seen = False
        for s in nl.tokenize(data[part]):
            parsed.append(s)

    print(entity)

    for part in parsed:
        if go and go <= distance:
            wanted.append(part)
            go += 1
            if go == distance:
                go = 0
        if part.find(entity) > -1:
            for item in unwanted[-distance:]:
                wanted.append(item)
            wanted.append(part)
            go = 1
        else:
            unwanted.append(part)

    return wanted

if __name__ == '__main__':
    data = ocr_to_dict('http://resolver.kb.nl/resolve?urn=ddd:010639198:mpeg21:a0001:ocr')
