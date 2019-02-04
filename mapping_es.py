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
            "status":           {"type": "keyword"},
            "cnpj":             {"type": "keyword"},
            "place_rating":     {"type": "float"},
            "rating_ponderado": {"type": "float"},
            "location":         {"type": "geo_point"},
        }
    }
}
]
