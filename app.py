# coding=utf-8

from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost:5432/inss'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

ES_HOST = '191.235.87.46'
es = Elasticsearch(
        hosts=[{'host': ES_HOST, 'port': 7000}],
        use_ssl=False,
        verify_certs=False
)
urlgrammar = 'http://localhost:9000/api/v1/query'
reviewindex = 'greviews'
placesindex = 'aps'
agendamentoindex = 'agendamento'


def days_between(d1, d2):
    # d1 = datetime.strptime(d1, "%Y-%m-%d")
    # d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


class Place(db.Model):
    __tablename__ = 'place'

    id = db.Column(db.String)
    address = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    rating = db.Column(db.Float)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    local_phone_number = db.Column(db.String)
    reviews = db.relationship('Review', backref=db.backref('place', lazy='joined'), lazy='dynamic')

    bairro = db.Column(db.String)
    municipio = db.Column(db.String)
    uf = db.Column(db.String)
    cep = db.Column(db.String)
    cnpj = db.Column(db.String)
    cod_aps = db.Column(db.String, primary_key=True)
    cod_unid_gestora = db.Column(db.String)
    cod_uo_inss = db.Column(db.String)
    tipo = db.Column(db.String)
    endereco = db.Column(db.String)
    complemento = db.Column(db.String)
    rating_ponderado = db.Column(db.Float)
    stddev = db.Column(db.Float)
    qtd_avaliacaoes = db.Column(db.Integer)


    def add_index_to_es(self):
        es.index(placesindex, 'place', self.to_json())


    def to_json(self):
        json = {
            'place_id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'municipio': self.municipio,
            'uf': self.uf,
            'cnpj': self.cnpj,
            'place_rating': self.rating,
            # 'location': {'lat': self.lat, 'lon': self.lng},
            'rating_ponderado': self.rating_ponderado,
            'qtd_avaliacoes': self.qtd_avaliacaoes,
            'stddev': self.stddev,
            'cod_aps': self.cod_aps,
            'cod_uo_inss': self.cod_uo_inss,
        }

        return json


    def __repr__(self):
        return "<Place(name='%s', address='%s')>" % (self.name, self.address)


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer)
    author_name = db.Column(db.String)
    rating = db.Column(db.Float)
    author_url = db.Column(db.String, primary_key=True)
    language = db.Column(db.String)
    profile_photo_url = db.Column(db.String)
    text = db.Column(db.String)
    time = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    relative_time_description = db.Column(db.String)
    cod_aps = db.Column(db.String, db.ForeignKey('place.cod_aps'))
    sentiment_google = db.Column(db.JSON)
    sentiment_gotitai = db.Column(db.JSON)
    sentiment_amazon = db.Column(db.JSON)
    sentiment_spacy = db.Column(db.JSON)

    def add_index_to_es(self):
        es.index(reviewindex, 'review', self.to_json())

    def postObj(self, urlgrammar, data):
        headers = {'Content-Type': 'application/json; charset=utf-8',
                   'Accept': 'application/xml, text/javascript, */*; q=0.01',
                   'Content-Language': 'pt'}
        r = requests.post(urlgrammar, data=json.dumps(data), headers=headers)
        return r.json()

    def to_json(self):
        place = db.session.query(Place).filter_by(id=self.cod_aps).first()
        json = {
            'place_id': self.place_id,
            'address': place.address,
            'city': place.city,
            'state': place.state,
            'place_rating': place.rating,
            'review_rating': self.rating,
            'text': self.text,
            'date': self.date,
            'author_name': self.author_name,
            'location': {'lat': place.lat, 'lon': place.lng},
            'rating_ponderado': place.rating_ponderado,
            'amazon_sentiment': self.sentiment_amazon
        }

        return json

    def __repr__(self):
        return "<Review(author_name='%s', text='%s')>" % (self.author_name, self.text)


class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    cod_agendamento = db.Column(db.String, primary_key=True)
    nome_requerente = db.Column(db.String)
    data_agendamento = db.Column(db.Date)
    data_solicitacao_agendamento = db.Column(db.Date)
    servico = db.Column(db.String)
    celular = db.Column(db.String)
    telefone_fixo = db.Column(db.String)
    email = db.Column(db.String)
    cod_aps = db.Column(db.String, db.ForeignKey('place.cod_aps'))

    def add_index_to_es(self):
        es.index(agendamentoindex, 'agendamento', self.to_json())

    def to_json(self):
        place = db.session.query(Place).filter_by(cod_aps=self.cod_aps).first()
        json = {
            'cod_agendamento': self.cod_agendamento,
            'nome_requerente': self.nome_requerente,
            'data_agendamento': self.data_agendamento,
            'data_solicitacao_agendamento': self.data_solicitacao_agendamento,
            'servico': self.servico,
            'celular': self.celular,
            'telefone_fixo': self.telefone_fixo,
            'email': self.email,
            'municipio': place.municipio,
            'uf': place.uf,
            'location': {'lat': place.lat, 'lon': place.lng},
            'delay': days_between(self.data_agendamento, self.data_solicitacao_agendamento),
            'dia_sem_solic_agendamento': self.data_solicitacao_agendamento.weekday(),
            'dia_sem_agendamento': self.data_agendamento.weekday(),
            'dia_mes_solic_agendamento': self.data_solicitacao_agendamento.day,
            'dia_mes_agendamento': self.data_agendamento.day,
            'cod_uo_inss': place.cod_uo_inss.replace(u'Agência da Previdência Social ',''),
        }

        return json

    def __repr__(self):
        return "<Review(author_name='%s', text='%s')>" % (self.author_name, self.text)



