from .reader import Reader
from .retriever import Retriever
import warnings
import re
# import numpy as np


class qaResponder:
    def __init__(self):
        warnings.filterwarnings("ignore")

        # saved reader model
        model_checkpoint = "./data/bert_finetuned_czech_squad2"
        # files with additional saved data
        dita_file = "./data/czech-morfflex-pdt-161115/czech-morfflex-pdt-161115.tagger"
        wiki_titles = "./data/cswiki-latest-all-titles-in-ns0"
        wiki_abstracts = "./data/wiki_abstracts_processed.json"
        index_file = "./data/abstracts_index.pkl"

        # create reader and retriever
        self.reader = Reader(model_checkpoint)
        self.retriever = Retriever(wiki_abstracts, wiki_titles, dita_file, index_file, download_ner_model=False)

    def find_answer(self, question, configuration):
        """
        Finds the answer to the question - connects everything

        """
        max_docs = configuration["retriever"]["top_k"]
        max_answers = configuration["extractive_reader"]["reader_top_k_answers"]
        max_tokens = configuration["extractive_reader"]["reader_max_tokens_for_answer"]

        # retrieve the relevant paragraphs of context
        paragraphs, paragraph_scores = self.retriever.retrieve(question, max_docs=max_docs)

        # for saving the best results
        answers = []
        char_offsets = []
        passage_indeces = []
        scores = []
        titles = []

        # not mandatory
        reranked_scores = []
        aggregated_scores = []

        # delete null strings
        paragraphs = [x for x in paragraphs if len(x.strip())]

        # iterate over retrieved paragraphs
        for idx, document in enumerate(paragraphs):
            # strip whitespaces and document title
            title = document.strip().split("######")[0]
            document = document.strip().split("######")[1]

            # check if any document has been found for the question
            if document == "":
                continue

            # get answer -------------------------------------------
            all_answers = self.reader.get_answers(question, document)

            # choose the first valid answer - which is not empty
            paragraph_answers = 0  # answers extracted from paragraph dependent on configuration["reader_top_k_answers"]
            for answer in all_answers:
                if paragraph_answers >= max_answers:
                    break
                if (answer['text'] != '') and (len(re.split("\W", answer)) <= max_tokens):
                    if type(answer['text']) is not str:
                        continue  # this is just to make sure that the answer is really ok

                    # save probs and answer
                    answers.append(answer['text'])
                    answer_start = document.find(answer['text'])
                    char_offsets.append([answer_start, answer_start+len(answer['text'])])
                    scores.append(answer['score'])
                    passage_indeces.append(idx)
                    titles.append(title)
                    # not mandatory
                    reranked_scores.append(0)
                    aggregated_scores.append(0)

        ############################################################

        # not mandatory
        ids = [0 for x in paragraphs]
        # get the best doc
        # get best answer from retriever according to reader
        # answer = answers[np.argmax(scores, axis=0)]

        response = {
            "question": question,
            # "answer": answer,
            "ranker": {
                "paragraphs": paragraphs,
                "titles": titles,
                "ids": ids,
                "scores": paragraph_scores,
                "reranked_scores": reranked_scores,
            },
            "extractive_reader": {
                "answers": answers,
                "passage_indices": passage_indeces,
                "char_offsets": char_offsets,
                "scores": scores,
                "reranked_scores": reranked_scores,
                "aggregated_scores": aggregated_scores
            },
            "abstractive_reader": {
                "answers": [],
                "scores": []
            }
        }

        return response
