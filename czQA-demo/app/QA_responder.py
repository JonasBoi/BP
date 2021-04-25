from .reader import Reader
from .retriever import Retriever
import warnings
import re
import numpy as np


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
        # delete null strings
        paragraphs = [x for x in paragraphs if len(x.strip())]

        # for saving the results
        answers = []
        char_offsets = []
        passage_indeces = []
        scores = []

        # iterate over retrieved paragraphs
        for idx, document in enumerate(paragraphs):
            # strip whitespaces and document title
            document = document.strip().split("######")[1]

            # get answer -------------------------------------------
            all_answers = self.reader.get_answers(question, document)

            # for saving answers and data from this paragraph
            par_answers = []
            par_char_offsets = []
            par_scores = []
            par_passage_indeces = []

            # choose the valid answers
            for answer in all_answers:
                if (answer['text'] != '') and (len(re.split("\W", answer['text'])) <= max_tokens):
                    if type(answer['text']) is not str:
                        continue  # this is just to make sure that the answer is really ok

                    # save probs and answer
                    par_answers.append(answer['text'])
                    answer_start = document.find(answer['text'])
                    par_char_offsets.append([answer_start, answer_start+len(answer['text'])])
                    par_scores.append(answer['score'])
                    par_passage_indeces.append(idx)

            # save x answers - dependent on configuration["extractive_reader"]["reader_top_k_answers"]
            for i, ans in enumerate(par_answers):
                if i >= int(max_answers):
                    break
                answers.append(ans)
                char_offsets.append(par_char_offsets[i])
                scores.append(par_scores[i])
                passage_indeces.append(par_passage_indeces[i])

        ############################################################

        # not mandatory
        ids = [0 for x in paragraphs]
        reranked_scores = [0 for x in paragraphs]
        aggregated_scores = [0 for x in paragraphs]

        titles = [x.split("######")[0] for x in paragraphs]  # get paragraph titles
        paragraphs = [x.split("######")[1] for x in paragraphs]  # strips the title from the beggining

        # get best answer from retriever according to reader
        # answer = answers[np.argmax(scores, axis=0)]

        # convert to string because of json
        paragraph_scores = [str(x) for x in paragraph_scores]
        scores = [str(x) for x in scores]

        # create response json
        response = {
            "question": question,
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
