# coding=utf-8
import datetime
import re
from googleplaces import GooglePlaces, types, lang, GooglePlacesError
import csv
from app import Place, db, Review
from config import YOUR_API_KEY

google_places = GooglePlaces(YOUR_API_KEY)

capitais = [
    ["RO","Porto Velho",-63.899902,-8.760772],
["AP","Macapa",-51.069395,0.034934],
["RR","Boa Vista",-60.675328,2.823842],
["AM","Manaus",-60.02123,-3.118662],
["PA","Belem",-48.489756,-1.455396],
["AC","Rio Branco",-67.824348,-9.97499],
["TO","Palmas",-48.355751,-10.239973],
["MT","Cuiaba",-56.097397,-15.600979],
["MS","Campo Grande",-54.629463,-20.448589],
["GO","Goiania",-49.264346,-16.686439],
["DF","Brasilia",-47.929657,-15.779522],
["PR","Curitiba",-49.264622,-25.419547],
["SC","Florianopolis",-48.547696,-27.594486],
["RS","Porto Alegre",-51.206533,-30.031771],
["MA","Sao Luis",-44.282513,-2.538742],
["CE","Fortaleza",-38.542298,-3.716638],
["RN","Natal",-35.198604,-5.793567],
["PB","Joao Pessoa",-34.864121,-7.11509],
["PE","Recife",-34.877065,-8.046658],
["AL","Maceio",-35.73496,-9.665985],
["SE","Aracaju",-37.06766,-10.909133],
["BA","Salvador",-38.501068,-12.97178],
["PI","Teresina",-42.803364,-5.091944],
["SP","Sao Paulo",-46.63952,-23.532905],
["RJ","Rio de Janeiro",-43.200295,-22.912897],
["MG","Belo Horizonte",-43.926572,-19.910183],
["ES","Vitoria",-40.312806,-20.315472]]

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




def write_csv(filepath, data):
    with open(filepath, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(data)

def get_data(places):
    for place in places:
        nlow = place.name.lower()
        lterms = ['inss', u'previdência social',u'instituto nacional do seguro social',u'previdencia social',u'instituto nacional seguro social.']
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
                rev = Review(author_name=i['author_name'], author_url=i['author_url'], #language=i['language'],
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

for c in capitais:
    query_result = google_places.text_search(
            language=lang.PORTUGUESE_BRAZIL,
            lat_lng={'lat': c[3], 'lng': c[2]},
            #locationbias='rectangle:-15.834343,-47.947989|-15.725664,-47.835764',
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


