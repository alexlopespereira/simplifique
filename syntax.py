# -*- coding: utf-8 -*-

import json
import requests


def postObj(url, data):
    print url
    headers = {'Content-Type': 'application/json; charset=utf-8',
               'Accept': 'application/xml, text/javascript, */*; q=0.01',
               'Content-Language':'pt'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    resp = json.dumps(r.json(), indent=4)
    print resp
    return r.json()


data={
   "strings": [u"Meu deus do céu, quero fazer atualização cadastral pra pagar guia do INSS e não consigo agendamento. Quero pagar e não consigo, ja pensou se eu estivesse querendo receber, estaria F..........".encode('utf8')],
   "tree": False
}
url='http://localhost:9000/api/v1/query'
init_url = 'http://localhost:9000/api/v1/use/Portuguese-BR'
r = requests.get(init_url)

postObj(url, data)

