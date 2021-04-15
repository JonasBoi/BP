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
          "maximum": 10,
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
          "maximum": 10,
          "default": 5
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
  "Which robot does a weee sound in Star Wars?",
  "What is the answer to life, the universe, and everything?",
  "Who was the first president of USA?",
  "What is equal to pi?",
  "Which animal is a reservoir of SARS?",
  "Which flooded cave pit is the deepest in the world?",
  "What does the term \"corpus\" mean in latine?",
  "What is symbol of electrical resistance?",
  "How many inches are in one feet?"
]

# Predefined first ten questions from EfficientQA validation dataset
FAKE_PREDEFINED_QUESTIONS = [
  "the last time la dodgers won the world series",
  "who sings ain't nothing but a good time",
  "where does the movie the sound of music take place",
  "statue coming out of the ground in washington dc",
  "field hockey is the national sport of which country",
  "who governs in america\u2019s representative democracy (republic) system",
  "who is the song you're my best friend about",
  "where was the church of latter day saints founded",
  "who os the father of bridget jones baby",
  "who is the nationalist leader associated with the american revolution"
]

# Example:
#
# {
#   "question": "the last time la dodgers won the world series",
#   "configuration": {
#     "retriever_model": "dpr-pruned",
#     "retriever_top_k": 100,
#     "retriever_reranking": true,
#     "reranker_model": "concat",
#     "extractive_reader_model": "electra",
#     "abstractive_reader_model": "fusion-in decoder",
#     "reader_top_k_answers": 100,
#     "reader_max_tokens_for_answer": 5,
#     "reranking_and_fusion": true,
#     "reranking_and_fusion_type": "readers fusion"
#   }
# }
#
REQUEST_JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "question": {"type": "string"},
    "configuration": CONFIGURATION_JSON_SCHEMA
  },
  "required": ["question", "configuration"],
  "additionalProperties": False
}


# Example:
#
# {
#   "question": "the last time la dodgers won the world series",
#   "answer": "1988",
#   "passages": {
#     "paragraphs": ["in the west in the early 6th century. The system ...", ...],
#     "titles": ["Julian calendar", ...],
#     "ids": [62451, ...],
#     "scores": [47.797794342041016, ...],
#     "reranked_scores": [4.303440570831299, ...],
#   },
#   "extractive_reader": {
#     "answers": ["1988", ...],
#     "passage_indices": [0, ...],
#     "char_offsets": [[269,273], ...],
#     "scores": [-0.00048680813051760197, ...],
#     "reranked_scores": [-0.1050909012556076, ...],
#     "aggregated_scores": [-0.12190021140611282]
#   },
#   "abstractive_reader": {
#     "answers": ["1988"],
#     "scores": [1]
#   }
# }
#
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
