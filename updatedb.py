# coding=utf-8
# encoding=utf8
import datetime
import re
from app import Place, db, Review
import csv
from sqlalchemy import func
import sys
from sentiment import *

reload(sys)
sys.setdefaultencoding('utf8')

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


def fill_state():
    places = Place.query.all()
    for p in places:
        if len(p.state) > 2 or len(p.city)==2:
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


def rating_acumulado(city):
    if city:
        count = db.session.query(Place.id, Place.city, Place.rating_ponderado, func.count(Review.rating).label("qtd")) \
            .join(Review, Place.id == Review.place_id) \
            .filter(Place.city == city) \
            .group_by(Place.id).order_by(Place.id.desc()).all()
    else:
        count = db.session.query(Place.id, Place.rating_ponderado, func.count(Review.rating).label("qtd"))\
                        .join(Review, Place.id == Review.place_id)\
                        .group_by(Place.id).order_by(Place.id.desc()).all()
    for p in count:
        place = Place.query.filter(Place.id == p.id).first()
        place.qtd_avaliacaoes = p.qtd
        db.session.add(place)
        db.session.commit()


def get_sentiment():
    reviews = Review.query.all()
    for r in reviews:
        # r.sentiment_google = google_sentment(r.text)
        # r.sentiment_gotitai = gotitai_sentment(r.text)
        print(r.text)
        try:
            r.sentiment_amazon = amazon_sentment(r.text)
        except:
            pass
            continue
        db.session.add(r)
        db.session.commit()

def media_ponderada(city=None):
    if city:
        count = db.session.query(Place.id, Place.city, Place.rating_ponderado, Review.rating, func.count(Review.rating).label("qtd")) \
            .join(Review, Place.id == Review.place_id) \
            .filter(Place.city == city) \
            .group_by(Place.id, Review.rating).order_by(Place.id.desc()).all()
    else:
        count = db.session.query(Place.id, Place.rating_ponderado, Review.rating, func.count(Review.rating).label("qtd"))\
                        .join(Review, Place.id == Review.place_id)\
                        .group_by(Place.id, Review.rating).order_by(Place.id.desc()).all()
    sum = 0
    qtd = 0
    key = count[0].id
    rating_dict = {1:0, 2:0, 3:0, 4:0, 5:0}
    for p in count:

        if key == p.id:
            # sum = sum + p.rating*p.qtd
            # qtd = qtd + p.qtd
            rating_dict[p.rating] = p.qtd
        else:
            place = Place.query.filter(Place.id == key).first()
            place.rating_ponderado = fiveStarRating(rating_dict)
            rating_dict = {1:0, 2:0, 3:0, 4:0, 5:0}
            rating_dict[p.rating] = p.qtd
            # sum = p.rating*p.qtd
            # qtd = p.qtd

            key = p.id
            db.session.add(place)
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
        next(reader, None)  # skip the headers
        currlist = list(reader)

    return currlist


def write_csv(filepath, data):
    with open(filepath, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(data)


# get_sentiment()
# fill_state()
# media_ponderada()
convert_date()