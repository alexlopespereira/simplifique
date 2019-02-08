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

import sys
reload(sys)
sys.setdefaultencoding('utf8')

google_places = GooglePlaces(YOUR_API_KEY)

capitais = [#["SP", "Guarulhos", "-46.5333", "-23.4538"],
            #["SP", "Campinas", "-47.0659", "-22.9053"],
            #["MA", "São Luís", "-44.2825", "-2.53874"],
            #["RJ", "São Gonçalo", "-43.0634", "-22.8268"],
            #["RJ", "Duque de Caxias", "-43.3049", "-22.7858"],
            #["RJ", "Nova Iguaçu", "-43.4603", "-22.7556"],
            #["SP", "São Bernardo do Campo", "-46.5646", "-23.6914"],
            #["SP", "Santo André", "-46.5432", "-23.6737"],
            ["SP", "Osasco", "-46.7916", "-23.5324"],
            ["PE", "Jaboatão Dos Guararapes", "-35.015", "-8.11298"],
            ["SP", "São José Dos Campos", "-45.8841", "-23.1896"],
            ["SP", "Ribeirão Preto", "-47.8099", "-21.1699"],
            ["MG", "Contagem", "-44.0539", "-19.9321"],
            ["MG", "Uberlândia", "-48.2749", "-18.9141"],
            ["SP", "Sorocaba", "-47.4451", "-23.4969"],
            ["BA", "Feira de Santana", "-38.9663", "-12.2664"],
            ["MG", "Juiz de Fora", "-43.3398", "-21.7595"],
            ["SC", "Joinville", "-48.8487", "-26.3045"],
            ["PR", "Londrina", "-51.1691", "-23.304"],
            ["RJ", "Niterói", "-43.1034", "-22.8832"],
            ["PA", "Ananindeua", "-48.3743", "-1.36391"],
            ["RJ", "Belford Roxo", "-43.3992", "-22.764"],
            ["RJ", "Campos Dos Goytacazes", "-41.3181", "-21.7622"],
            ["RJ", "São João de Meriti", "-43.3729", "-22.8058"],
            ["GO", "Aparecida de Goiânia", "-49.2469", "-16.8198"],
            ["RS", "Caxias do Sul", "-51.1792", "-29.1629"],
            ["SC", "Florianópolis", "-48.5477", "-27.5945"],
            ["SP", "Santos", "-46.335", "-23.9535"],
            ["SP", "Mauá", "-46.4613", "-23.6677"],
            ["ES", "Vila Velha", "-40.2875", "-20.3417"],
            ["ES", "Serra", "-40.3074", "-20.121"],
            ["SP", "São José do Rio Preto", "-49.3758", "-20.8113"],
            ["SP", "Mogi Das Cruzes", "-46.1854", "-23.5208"],
            ["SP", "Diadema", "-46.6205", "-23.6813"],
            ["PB", "Campina Grande", "-35.8731", "-7.22196"],
            ["MG", "Betim", "-44.2008", "-19.9668"],
            ["PE", "Olinda", "-34.8545", "-8.01017"],
            ["SP", "Jundiaí", "-46.8974", "-23.1852"],
            ["SP", "Carapicuíba", "-46.8407", "-23.5235"],
            ["SP", "Piracicaba", "-47.6476", "-22.7338"],
            ["MG", "Montes Claros", "-43.8578", "-16.7282"],
            ["PR", "Maringá", "-51.9333", "-23.4205"],
            ["ES", "Cariacica", "-40.4165", "-20.2632"],
            ["SP", "Bauru", "-49.0871", "-22.3246"]]


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


def read_csv(file):
    with open(file, 'rb') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        currlist = list(reader)

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



first_query = True
csv_file = read_csv('./inssof.csv')
first_city = u'Cocal'
first_iter = True
for c in csv_file:
    municipio = c[9].strip().encode('utf-8')
    if municipio != first_city and first_iter:
        continue

    first_iter = False
    print(c[9])
    addr = '{0} {1} CEP {2}, {3}, {4}'.format(c[7].strip(), c[0].strip(), c[1].strip(), municipio, c[13].strip()).encode('utf-8')
    worked = False
    tries = 1
    while not worked:
        try:
            query_result = google_places.text_search(
                language=lang.PORTUGUESE_BRAZIL,
                #lat_lng={'lat': c[3], 'lng': c[2]},
                location=addr,
                query='inss',
                radius=3000
            )
            worked = True
            n = random.uniform(0, 1)*5
            sleep(5 * (pow(tries + n, 2)))
        except:
            tries = tries + 1
            print("tries {0}".format(tries))
            pass

    # n2 = random.uniform(0, 1)*5
    # sleep(10 * n2)
    get_data(query_result.places, c)

    while query_result.has_next_page_token:
        n2 = random.uniform(0, 1) * 5
        sleep(10 * n2)
        if not first_query:
            query_result = google_places.nearby_search(
                pagetoken=query_result.next_page_token)
            get_data(query_result.places, c)
        else:
            first_query = False
            get_data(query_result.places, c)



# write_csv('./review_inss.csv', full_dict.values())
