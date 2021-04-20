import jsonschema as js

config = {
    "retriever_model": "bm25",
    "retriever_top_k": 5,
    "retriever_reranking": False,
    "reranker_model": None,
    "extractive_reader_model": "m-BERT",
    "abstractive_reader_model": None,
    "reader_top_k_answers": 5,
    "reader_max_tokens_for_answer": 5,
    "reranking_and_fusion": False,
    "reranking_and_fusion_type": None
}

request = {
    "question": "the last time la dodgers won the world series",
    "configuration": {
        "retriever_model": "bm25",
        "retriever_top_k": 5,
        "retriever_reranking": False,
        "reranker_model": None,
        "extractive_reader_model": "m-BERT",
        "abstractive_reader_model": None,
        "reader_top_k_answers": 5,
        "reader_max_tokens_for_answer": 5,
        "reranking_and_fusion": False,
        "reranking_and_fusion_type": None
    }
}

response = {
    "question": "the last time la dodgers won the world series",
    "answer": "1988",
    "passages": {
        "paragraphs": best_docs,
        "titles": article_list,
        "ids": [],
        "scores": [best_bm25_scores],
        "reranked_scores": [],
    },
    "extractive_reader": {
        "answers": best_answers,
        "passage_indices": [0, ...],
        "char_offsets": [[269, 273], ...],
        "scores": best_scores,
        "reranked_scores": [],
        "aggregated_scores": []
    },
    "abstractive_reader": {
        "answers": [],
        "scores": []
    }
 }
