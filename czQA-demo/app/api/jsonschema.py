SUPPORTED_MODELS_DICTIONARY = {
  "retriever": ["bm25"],
  "passage_reranker": [],
  "extractive_reader": ["m-BERT"],
  "abstractive_reader": []
}

# Example:
#
# {
#   "retriever_model": "dpr-pruned",
#   "retriever_top_k": 100,
#   "retriever_reranking": true,
#   "reranker_model": "concat",
#   "extractive_reader_model": "electra",
#   "abstractive_reader_model": "fusion-in decoder",
#   "reader_top_k_answers": 100,
#   "reader_max_tokens_for_answer": 5,
#   "reranking_and_fusion": true,
#   "reranking_and_fusion_type": "readers fusion"
# }
#
CONFIGURATION_JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "retriever": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string",
          "enum": SUPPORTED_MODELS_DICTIONARY["retriever"]
        },
        "top_k": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20,
          "default": 5
        }
      },
      "required": ["model"]
    },
    "passage_reranker": {
      "type": "object",
      "properties": {
        "model": {
          "type": ["string", "null"],
          "enum": SUPPORTED_MODELS_DICTIONARY["passage_reranker"] + [None],
          "default": None
        }
      }
    },
    # extractive reader model type
    "extractive_reader": {
      "type": "object",
      "properties": {
        "model": {
          "type": ["string", "null"],
          "enum": SUPPORTED_MODELS_DICTIONARY["extractive_reader"] + [None],
          "default": None
        },
        # reader returns top k answers
        "reader_top_k_answers": {
          "type": "integer",
          "minimum": 1,
          "maximum": 30,
          "default": 10
        },
        # maximum answer length in tokens
        "reader_max_tokens_for_answer": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10,
          "default": 10
        },
        # generative reranking of extractive asnwer spans by the abstractive reader
        "generative_reranking": {
          "type": "boolean",
          "default": False
        }
      }
    },
    # extractive reader model type
    "abstractive_reader": {
      "type": "object",
      "properties": {
        "model": {
          "type": ["string", "null"],
          "enum": SUPPORTED_MODELS_DICTIONARY["abstractive_reader"] + [None],
          "default": None
        }
      }
    },
    # aggregation of readers answer span scores and/or rankers passage score
    "score_aggregation": {
      "type": "boolean",
      "default": False      
    }
  },
  "anyOf": [
    {"required": ["retriever", "extractive_reader"]},
    {"required": ["retriever", "abstractive_reader"]}
  ],
  "additionalProperties": False
}

PREDEFINED_QUESTIONS = [
  "Kdy se slaví svátek Cyrila a Metoděje v česku a Slovensku?",
  "Dokdy řádil Velký požár Londýna?",
  "Jak se jmenuje německý automobilový závodník a sedminásobný mistr světa ve Formuli 1?",
  "Kdo napsal komedii Lakomec?",
  "Kdy se společnosti SpaceX poprvé podařilo vyslat na orbitu stroj a pak s ním přistát ve vodách Tichého oceánu?",
  "Co se kromě tenisu hraje na antuce?",
  "Ve které opeře zpívá Královna noci tón f3?",
  "Jaký je stavový číselný kód vrácený serverem, když nenalezne požadovaný soubor?",
  "Co patří mezi Edisonovy nejznámější vynálezy?"
]

REQUEST_JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "question": {"type": "string"},
    "configuration": CONFIGURATION_JSON_SCHEMA
  },
  "required": ["question", "configuration"],
  "additionalProperties": False
}

RESPONSE_JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "question": {"type": "string"},
    "ranker": {
      "type": "object", 
      "properties": {
        "paragraphs": {"type": "array", "items": {"type": "string"}},
        "titles": {"type": "array", "items": {"type": "string"}},
        "ids": {"type": "array", "items": {"type": "number"}},
        "scores": {"type": "array", "items": {"type": "number"}},
        "reranked_scores": {"type": "array", "items": {"type": "number"}}
      },
      "required": ["paragraphs", "titles", "ids", "scores"]
    },
    "extractive_reader": {
      "type": "object",
      "properties": {
        "answers": {"type": "array", "items": {"type": "string"}},
        "passage_indices": {"type": "array", "items": {"type": "number"}},
        "char_offsets": {
          "type": "array", 
          "items": {
            "type": "array",
            "items": [{"type": "number"}, {"type": "number"}]
          }
        },
        "scores": {"type": "array", "items": {"type": "number"}},
        "reranked_scores": {"type": "array", "items": {"type": "number"}},
        "aggregated_scores": {"type": "array", "items": {"type": "number"}}
      },
      "required": ["answers", "passage_indices", "char_offsets", "scores"]
    },    
    "abstractive_reader": {
      "type": "object",
      "properties": {
        "answers": {"type": "array", "items": {"type": "string"}},
        "scores": {"type": "array", "items": {"type": "number"}},
      },
      "required": ["answers", "scores"]
    }
  },
  "anyOf": [
    {"required": ["question", "ranker", "extractive_reader"]},
    {"required": ["question", "ranker", "abstractive_reader"]}
  ],
  "additionalProperties": False
}
