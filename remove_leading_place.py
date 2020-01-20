#!/usr/bin/env python3

import json
import lxml.html
import requests

from flask import request, Response, Flask
from lxml import etree

application = Flask(__name__)
application.debug = True

@application.route('/')
def index():
    url = request.args.get('url')
    query = request.args.get('query')

    if not url:
        return("Invoke example ?url=http://resolver.kb.nl/resolve?urn=ddd:110586084:mpeg21:a0065:ocr&query='Den Haag'")
    if not query:
        return("Invoke example ?url=http://resolver.kb.nl/resolve?urn=ddd:110586084:mpeg21:a0065:ocr&query='Den Haag'")

    query = query.lower()

    parsed_text = ocr_to_dict(url)
    response = is_in_text(parsed_text, query)

    resp = Response(response=json.dumps(response),
		    mimetype='application/json; charset=utf-8')

    return resp

def is_in_text(parsed_text, query):
    for item in parsed_text:
        for word in parsed_text[item].split():
            if word.lower() == query:
                return True
    return False


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
            txt = " ".join([i for i in item.text.split()[:10] if not i.isupper()])
            if len(item.text.split()) > 10:
                for i in item.text.split()[10:]:
                    txt += " " + i
            if "p" not in parsed_text:
                parsed_text["p"] = []
            parsed_text["p"].append(txt)

    for part in parsed_text:
        parsed_text[part] = "".join(parsed_text[part])

    return parsed_text

if __name__ == '__main__':
    data = ocr_to_dict('http://resolver.kb.nl/resolve?urn=ddd:110586084:mpeg21:a0065:ocr')
    print(is_in_text(data, "vlag"))
    print(is_in_text(data, "den haag"))
