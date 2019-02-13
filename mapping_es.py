mapping = [
{
    ##0
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "filter": {
        "my_ascii_folding": {
          "type": "asciifolding",
          "preserve_original": "true"
        },
        "brazilian_stop": {
          "type":       "stop",
          "stopwords":  "_brazilian_"
        },
        "brazilian_stemmer": {
          "type":       "stemmer",
          "language":   "brazilian"
        },
        "brazilian_keywords": {
            "type": "keyword_marker",
            "keywords": ["ser", "tem", "tive", "estou"]
        },
      },
      "analyzer": {
        "brazilian": {
          "tokenizer": "standard",
          "filter": [
              "lowercase",
              "brazilian_stop",
              "brazilian_stemmer",
              "brazilian_keywords"
          ]
        }
      }
    }
  }
},
{
    ##1
    "review": {
        "properties": {
            "place_id":         {"type": "keyword"},
            "address":          {"type": "text", "analyzer": "brazilian"},
            "city":             {"type": "keyword"},
            "state":            {"type": "keyword"},
            "place_rating":     {"type": "float"},
            "text":             {"type": "text", "analyzer": "brazilian"},
            "review_rating":    {"type": "float"},
            "date":             {"type": "date"},
            "author_name":      {"type": "text", "analyzer": "brazilian"},
            "location":         {"type": "geo_point"},
            "rating_ponderado": {"type": "float"},
            "amazon_sentiment": {
                        "properties": {
                            "score":  {"type": "float"},
                            "label": {"type": "keyword"},
                            "positive": {"type": "float"},
                            "neutral": {"type": "float"},
                            "negative": {"type": "float"},
                            "mixed": {"type": "float"}
                        }
            }
        }
    }
},
{
    ##2
    "place": {
        "properties": {
            "place_id":         {"type": "keyword"},
            "name":             {"type": "keyword"},
            "address":          {"type": "text", "analyzer": "brazilian"},
            "city":             {"type": "keyword"},
            "state":            {"type": "keyword"},
            "municipio":        {"type": "keyword"},
            "uf":               {"type": "keyword"},
            "cnpj":             {"type": "keyword"},
            "cod_uo_inss":      {"type": "keyword"},
            "place_rating":     {"type": "float"},
            "rating_ponderado": {"type": "float"},
            "qtd_avaliacoes":   {"type": "integer"},
            "cod_aps":          {"type": "integer"},
            "stddev":           {"type": "float"},
            "location":         {"type": "geo_point"},
        }
    }
},
{
    ##3
    "agendamento": {
        "properties": {
            "cod_agendamento":                  {"type": "integer"},
            "nome_requerente":                  {"type": "keyword"},
            "data_agendamento":                 {"type": "date"},
            "data_solicitacao_agendamento":     {"type": "date"},
            "servico":                          {"type": "keyword"},
            "celular":                          {"type": "keyword"},
            "telefone_fixo":                    {"type": "keyword"},
            "email":                            {"type": "keyword"},
            "municipio":                        {"type": "keyword"},
            "uf":                               {"type": "keyword"},
            # "location":                         {"type": "geo_point"},
            # "delay":                            {"type": "integer"},
            # "dia_sem_solic_agendamento":        {"type": "keyword"},
            # "dia_sem_agendamento":              {"type": "keyword"},
            # "dia_mes_solic_agendamento":        {"type": "integer"},
            # "dia_mes_agendamento":              {"type": "integer"},
        }
    }
}
]
