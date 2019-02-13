# coding=utf-8
# encoding=utf8
import datetime
import re
import random
from time import sleep
from googleplaces import GooglePlaces, lang, GooglePlacesError
from app import Place, db, Review
from config import YOUR_API_KEY
import csv
from sqlalchemy import func
from unidecode import unidecode

import sys
reload(sys)
sys.setdefaultencoding('utf8')

google_places = GooglePlaces(YOUR_API_KEY)

capitais = [["Rondônia","RO","Porto Velho",-63.899902,-8.760772],
["Amapá","AP","Macapa",-51.069395,0.034934],
["Roraima","RR","Boa Vista",-60.675328,2.823842],
["Amazonas","AM","Manaus",-60.02123,-3.118662],
["Pará","PA","Belem",-48.489756,-1.455396],
["Acre","AC","Rio Branco",-67.824348,-9.97499],
["Tocantins","TO","Palmas",-48.355751,-10.239973],
["Mato Grosso","MT","Cuiaba",-56.097397,-15.600979],
["Mato Grosso do Sul","MS","Campo Grande",-54.629463,-20.448589],
["Goiás","GO","Goiania",-49.264346,-16.686439],
["Distrito Federal","DF","Brasilia",-47.929657,-15.779522],
["Paraná","PR","Curitiba",-49.264622,-25.419547],
["Santa Catarina","SC","Florianopolis",-48.547696,-27.594486],
["Rio Grande do Sul","RS","Porto Alegre",-51.206533,-30.031771],
["Maranhão","MA","Sao Luis",-44.282513,-2.538742],
["Ceará","CE","Fortaleza",-38.542298,-3.716638],
["Rio Grande do Norte","RN","Natal",-35.198604,-5.793567],
["Paraíba","PB","Joao Pessoa",-34.864121,-7.11509],
["Pernambuco","PE","Recife",-34.877065,-8.046658],
["Alagoas","AL","Maceio",-35.73496,-9.665985],
["Sergipe","SE","Aracaju",-37.06766,-10.909133],
["Bahia","BA","Salvador",-38.501068,-12.97178],
["Piauí","PI","Teresina",-42.803364,-5.091944],
["São Paulo","SP","Sao Paulo",-46.63952,-23.532905],
["Rio de Janeiro","RJ","Rio de Janeiro",-43.200295,-22.912897],
["Minas Gerais","MG","Belo Horizonte",-43.926572,-19.910183],
["Espírito Santo","ES","Vitoria",-40.312806,-20.315472]]


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


def read_csv(file, skip=None):
    with open(file, 'rb') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        currlist = list(reader)

    if skip:
        currlist = currlist[skip-1:]
    return currlist


def write_csv(filepath, data):
    with open(filepath, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(data)

def get_city_state(address_components):
    city = None
    state = None
    for c in address_components:
        if u'administrative_area_level_1' in c['types']:
            state = c['short_name']
        elif u'administrative_area_level_2' in c['types']:
            city = c['long_name']

    return city, state

def get_data(places, c):
    for place in places:
        nlow = place.name.lower()
        lterms = ['inss', u'previdência social', u'instituto nacional seguro social', u'instituto nacional do seguro social', u'previdencia social',
                  u'instituto nacional seguro social.']
        found = False
        for text in lterms:
            if text in nlow:
                found = True

        if not found:
            print("descartou {0}".format(nlow))
            continue

        p = db.session.query(Place).filter_by(id=place.place_id).first()
        if not p:
            place.get_details()
            # city = place.details['address_components'][2]['short_name']
            # state = place.details['address_components'][3]['short_name']
            city, state = get_city_state(place.details['address_components'])
            p = Place(id=place.place_id, address=place.formatted_address, lat=place.geo_location['lat'],
                      lng=place.geo_location['lng'], name=place.name, local_phone_number=place.local_phone_number,
                      rating=place.rating, city=city, state=state,
                      endereco=c[7], bairro=c[0], municipio=c[9], cep=c[1], cnpj=c[2], cod_unid_gestora=c[3], cod_uo_inss=c[4],
                      gex=c[8], sigla_uo_inss=c[10], telefone='{0}{1}'.format(c[6], c[11]), tipo=c[12], status_ativo=c[14]
                      )

            db.session.add(p)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                pass

            print(u'added place: {0}'.format(place.formatted_address))

            if 'reviews' in place.details:
                for i in place.details['reviews']:
                    dt_object = datetime.datetime.fromtimestamp(i['time'])
                    rev = Review(author_name=i['author_name'], author_url=i['author_url'],  # language=i['language'],
                                 profile_photo_url=i['profile_photo_url'], rating=i['rating'],
                                 relative_time_description=i['relative_time_description'], text=i['text'],
                                 time=i['time'], date=dt_object.date())

                    p.reviews.append(rev)
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
                        pass

                    print(u'added review: {0}'.format(i['text']))
        else:
            print(u'updated place: {0}'.format(c[9]))
            p.bairro = c[0]
            p.municipio = c[9]
            p.cep = c[1]
            p.cnpj = c[2]
            p.cod_unid_gestora = c[3]
            p.cod_uo_inss = c[4]
            p.gex = c[8]
            p.sigla_uo_inss = c[10]
            p.telefone = '{0}{1}'.format(c[6], c[11])
            p.tipo = c[12]
            p.status_ativo = c[14]
            p.endereco = c[7]

            db.session.add(p)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                pass


def get_data2(places, c):
    city_name = unidecode(u'{0}'.format(c[3])).lower()
    selected_places = []
    for place in places:
        nlow = unidecode(u'{0}'.format(place.vicinity)).lower()
        if city_name in nlow:
            selected_places.append(place)

    selected = None
    if len(selected_places)==0:
        print('skiping {0}'.format(c[3]))
        return

    for place in selected_places:
        nlow = place.name.lower()
        if city_name in nlow:
            selected = place

    for place in selected_places:
        nlow = place.name.lower()
        if 'agência' in nlow or 'agencia' in nlow:
            selected = place

    if not selected:
        selected = places[0]
    p = db.session.query(Place).filter_by(cod_aps="{:08d}".format(int(c[0]))).first()
    selected.get_details()
    city, state = get_city_state(selected.details['address_components'])
    p.address = selected.formatted_address
    p.id=selected.place_id
    p.lat=selected.geo_location['lat']
    p.lng=selected.geo_location['lng']
    p.name=selected.name
    p.local_phone_number=selected.local_phone_number
    p.rating=selected.rating
    p.city=city
    p.state=state
    db.session.add(p)
    db.session.commit()

    #print(u'updated place: {0}, {1}'.format(c[0], selected.formatted_address))



first_query = True
csv_file = read_csv('./data/inssof3.csv', skip=91)
first_city = None
first_iter = True
for c in csv_file:
    first_iter = False
    print(c[3])
    addr = unidecode(u'{0}, {2}, {3}, Brasil'.format(c[6], c[7], c[3], c[4])).encode('utf-8')

    worked = False
    tries = 1
    while not worked:
        try:
            query_result = google_places.nearby_search(
                language=lang.PORTUGUESE_BRAZIL,
                #lat_lng={'lat': c[3], 'lng': c[2]},
                location=addr,
                name='inss',
                radius=3000
            )
            worked = True
            n = random.uniform(0, 1)*5
            sleep(5 * (pow(tries + n, 2)))
        except Exception as e:
            tries = tries + 1
            print("tries {0}".format(tries))
            pass

    # n2 = random.uniform(0, 1)*5
    # sleep(10 * n2)
    get_data2(query_result.places, c)


