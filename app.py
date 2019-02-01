# coding=utf-8

from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import requests

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

currindex = 'ginss'

class Place(db.Model):
    __tablename__ = 'place'
    id = db.Column(db.String, primary_key=True)
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
    cep = db.Column(db.String)
    cnpj = db.Column(db.String)
    cod_unid_gestora = db.Column(db.String)
    cod_uo_inss = db.Column(db.String)
    gex = db.Column(db.String)
    sigla_uo_inss = db.Column(db.String)
    telefone = db.Column(db.String)
    tipo = db.Column(db.String)
    status_ativo = db.Column(db.String)
    endereco = db.Column(db.String)

    # def add_index_to_es(self):
    #     es.index('inss', 'place', self.to_json_index())

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
    place_id = db.Column(db.String, db.ForeignKey('place.id'))

    def add_index_to_es(self):
        es.index(currindex, 'review', self.to_json())

    def postObj(self, urlgrammar, data):
        headers = {'Content-Type': 'application/json; charset=utf-8',
                   'Accept': 'application/xml, text/javascript, */*; q=0.01',
                   'Content-Language': 'pt'}
        r = requests.post(urlgrammar, data=json.dumps(data), headers=headers)
        return r.json()

    def to_json(self):
        place = db.session.query(Place).filter_by(id=self.place_id).first()
        verb = []
        adj = []
        adv = []
        noum = []

        if self.text != '':
            grammar = self.postObj(urlgrammar, {"strings": [self.text], "tree": False})
            for o in grammar[0]['output']:
                if o['pos_tag'] == 'ADJ':
                    adj.append({'value': o['word'].lower()})
                elif o['pos_tag'] == 'ADV':
                    adv.append({'value': o['word'].lower()})
                elif o['pos_tag'] == 'NOUN':
                    noum.append({'value': o['word'].lower()})
                elif o['pos_tag'] == 'VERB':
                    verb.append({'value': o['word'].lower()})

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
            'location': {"lat": place.lat, "lon": place.lng},
            'verb': verb,
            'adj': adj,
            'adv': adv,
            'noum': noum
        }

        return json

    def __repr__(self):
        return "<Review(author_name='%s', text='%s')>" % (self.author_name, self.text)

