#!/usr/bin/env python

from app import Review, Place, db, es, ES_HOST, reviewindex, placesindex
from mapping_es import mapping
import json
import requests


def refresh_eq_index():
    es.indices.refresh(index=reviewindex)


def index_reviews(catalog_url, pindex, rindex, RESET_PLACE=False, RESET_REVIEW=False, limit=None):
    s = requests.session()
    headers = {'content-type': 'application/json'}
    rurl = catalog_url + "/" + rindex
    purl = catalog_url + "/" + pindex

    if RESET_REVIEW:
        s.delete(rurl)
        r = s.put(rurl, data=json.dumps(mapping[0]), headers=headers)
        resp = json.dumps(r.json(), indent=4)
        print(resp)
        urlmappingreviews = rurl + '/_mapping/review'
        r = s.put(urlmappingreviews, data=json.dumps(mapping[1]), headers=headers)
        resp = json.dumps(r.json(), indent=4)
        print(resp)
        q = db.session.query(Review).all()

        for i in q:
            i.add_index_to_es()

    if RESET_PLACE:
        s.delete(purl)
        r = s.put(purl, data=json.dumps(mapping[0]), headers=headers)
        resp = json.dumps(r.json(), indent=4)
        print(resp)
        urlmappingplace = purl + '/_mapping/place'
        r = s.put(urlmappingplace, data=json.dumps(mapping[2]), headers=headers)
        resp = json.dumps(r.json(), indent=4)
        print(resp)

        p = db.session.query(Place).all()

        for i in p:
            i.add_index_to_es()

    refresh_eq_index()



catalogurl = 'http://{0}:7000'.format(ES_HOST)
index_reviews(catalogurl, placesindex, reviewindex, RESET_PLACE=True, RESET_REVIEW=True)

