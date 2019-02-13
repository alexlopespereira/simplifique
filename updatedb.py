# coding=utf-8
# encoding=utf8
import datetime
import re
import math
from app import Place, db, Review, Agendamento
import csv
from sqlalchemy import func
import sys
from sentiment import *
import numpy as np

reload(sys)
sys.setdefaultencoding('utf8')

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


def findUF(name):
    for c in capitais:
        if c[0] == name:
            return c[1]
    return None


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


def update_qtd(city=None):
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
    reviews = Review.query.filter(Review.sentiment_amazon == None, Review.text != '').all()
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


def update_stddev():
    places = Place.query.all()
    for p in places:
        lrating = []
        for r in p.reviews:
            lrating.append(r.rating)

        npa = np.asarray(lrating, dtype=np.float32)
        stddev = float(np.std(npa))

        if math.isnan(stddev):
            stddev = None

        p.stddev = stddev
        db.session.add(p)
        db.session.commit()


def update_cod_aps():
    csv_file = read_csv('./email_aps.csv')
    for c in csv_file:
        cod_aps = c[0].split('@')[0][3:]
        siglauoinss = c[1]
        if cod_aps=='':
            continue

        place = Place.query.filter(Place.sigla_uo_inss==siglauoinss).first()
        if place:
            place.cod_aps = cod_aps
            db.session.add(place)
            db.session.commit()


def delete_rows():
    places = Place.query.all()
    for p in places:
        lterms = ['aadj','trabalho','fusesc','antt','futebol','prevplan','tribunal','promoover','iprev','dataprev','manaus previdência','amprev','sint','providencia','senaprev','cristina','sind','futura','cras ','agu','perícia','inps','neves','justiça','tcu','bomba','aposentado','quiterio']
        name = p.name.lower()
        found = False
        for text in lterms:
            if text in name:
                found = True

        if found:
            print(u"delete {0}".format(name))
            db.session.delete(p)
            db.session.commit()


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



def create_places():
    csv_file = read_csv('./data/inssof3.csv')
    for c in csv_file:
        uf = findUF(c[4].encode('utf8'))
        if uf is None:
            print(c[4])

        p = Place(cod_aps="{:08d}".format(int(c[0])), uf=uf,
              endereco=c[6], bairro=c[2], municipio=c[3], cep=c[7], cnpj=c[8], cod_unid_gestora=c[3], cod_uo_inss=c[1],
              tipo=c[12], complemento=c[5])

        db.session.add(p)
        db.session.commit()


def populate_agendamento():
    csv_file = read_csv('./data/agendamentos.csv', skip=None)
    for c in csv_file:
        a = Agendamento(cod_agendamento=c[2], nome_requerente=c[7], data_agendamento=c[4],
                        data_solicitacao_agendamento=c[5], servico=c[6],
                        celular=c[9], telefone_fixo=c[8], email=c[10], cod_aps="{:08d}".format(int(c[0])))
        db.session.add(a)
        db.session.commit()




# get_sentiment()
# fill_state()
# media_ponderada()
# convert_date()
# update_qtd()
# update_cod_aps()
# delete_rows()
# create_places()
populate_agendamento()