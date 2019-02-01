# coding=utf-8
import datetime
import re
from googleplaces import GooglePlaces, types, lang, GooglePlacesError
from app import Place, db, Review
from config import YOUR_API_KEY
import csv

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


def convert_date():
    review = Review.query.all()
    for r in review:
        dt_object = datetime.datetime.fromtimestamp(r.time)
        r.date = dt_object.date()
        db.session.add(r)
        db.session.commit()


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


def fill_city():
    places = Place.query.all()
    for p in places:
        if len(p.state) > 2:
            addr = p.address.split(',')[-2].split('-')
            city = addr[0].strip()
            if hasNumbers(city):
                addr = p.address.split(',')[0].split(' - ')
                if len(addr) < 2:
                    addr = p.address.split(',')[2].split(',')
                    if len(addr) < 2:
                        addr = addr[0].split(' - ')
                        if len(addr) < 2:
                            continue

            city = addr[0].strip()
            state = addr[1].strip()
            p.city = city
            p.state = state
            db.session.add(p)
            db.session.commit()


def delete_rows():
    places = Place.query.all()
    for p in places:
        lterms = ['CAP']
        name = p.name.lower()
        found = False
        for text in lterms:
            if text in name:
                found = True

        if found:
            print(u"delete {0}".format(name))
            db.session.delete(p)
            db.session.commit()


def read_csv(file):
    with open(file, 'rb') as f:
        reader = csv.reader(f)
        currlist = list(reader)

    return currlist


def write_csv(filepath, data):
    with open(filepath, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(data)


def get_data(places):
    for place in places:
        nlow = place.name.lower()
        lterms = ['inss', u'previdência social', u'instituto nacional seguro social', u'instituto nacional do seguro social', u'previdencia social',
                  u'instituto nacional seguro social.']
        found = False
        for text in lterms:
            if text in nlow:
                found = True

        if not found:
            print(nlow)
            continue

        p = db.session.query(Place).filter_by(id=place.place_id).first()
        if not p:
            place.get_details()
            # addr = place.formatted_address.split(',')[-3].split('-')
            city = place.details['address_components'][2]['short_name']
            state = place.details['address_components'][3]['short_name']
            # if len(addr) == 1:
            #     addr = place.formatted_address.split('-')[-2].split(',')
            #     city = addr[0].strip()
            #     state = addr[1].strip()
            # else:
            #     city=addr[0].strip()
            #     state = addr[1].strip()

            p = Place(id=place.place_id, address=place.formatted_address, lat=place.geo_location['lat'],
                      lng=place.geo_location['lng'], name=place.name, local_phone_number=place.local_phone_number,
                      rating=place.rating, city=city, state=state)
            db.session.add(p)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                pass
        else:
            continue

        print(u'added place: {0}'.format(place.formatted_address))

        if 'reviews' in place.details:
            for i in place.details['reviews']:
                rev = Review(author_name=i['author_name'], author_url=i['author_url'],  # language=i['language'],
                             profile_photo_url=i['profile_photo_url'], rating=i['rating'],
                             relative_time_description=i['relative_time_description'], text=i['text'], time=i['time'])

                p.reviews.append(rev)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    pass

                print(u'added review: {0}'.format(i['text']))


# fill_city()
# convert_date()
# full_list = []
# header =['place_id', 'formatted_address', 'lat', 'lng', 'name', 'local_phone_number', 'rating', 'user_ratings_total',
#          'author_name', 'author_url', 'language', 'profile_photo_url', 'user_rating', 'relative_time_description', 'text', 'time']
# full_list.append(list(header))
# full_dict = {}
# full_dict['header'] = header

first_query = True
csv_file = read_csv('./inssof.csv')
for c in capitais:
    print(c[1])
    query_result = google_places.text_search(
        language=lang.PORTUGUESE_BRAZIL,
        lat_lng={'lat': c[3], 'lng': c[2]},
        # locationbias='rectangle:-15.834343,-47.947989|-15.725664,-47.835764',
        location='Brasil',
        query='inss',
        radius=50000
    )

    get_data(query_result.places)

    while query_result.has_next_page_token:
        if not first_query:
            query_result = google_places.nearby_search(
                pagetoken=query_result.next_page_token)
            get_data(query_result.places)
        else:
            first_query = False
            get_data(query_result.places)



# write_csv('./review_inss.csv', full_dict.values())
