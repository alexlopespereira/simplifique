#!/usr/bin/env python

from app import Review, Place, db, es, ES_HOST, currindex
from mapping_es import mapping
import json
import requests


def refresh_eq_index():
    es.indices.refresh(index=currindex)


def index_reviews(catalog_url, index, RESET_CATALOG=False, limit=None):
    s = requests.session()
    headers = {'content-type': 'application/json'}
    equrl = catalog_url + "/" + index

    if RESET_CATALOG:
        s.delete(equrl)
        r = s.put(equrl, data=json.dumps(mapping[0]), headers=headers)
        resp = json.dumps(r.json(), indent=4)
        print(resp)
        urlmappingreviews = equrl + '/_mapping/review'
        r = s.put(urlmappingreviews, data=json.dumps(mapping[1]), headers=headers)
        resp = json.dumps(r.json(), indent=4)
        print(resp)

    q = db.session.query(Review).all()

    for i in q:
        i.add_index_to_es()

    refresh_eq_index()



catalogurl = 'http://{0}:7000'.format(ES_HOST)
init_url = 'http://localhost:9000/api/v1/use/Portuguese-BR'
r = requests.get(init_url)
index_reviews(catalogurl, currindex, RESET_CATALOG=True)

