from .reader import Reader
from .retriever import Retriever
import warnings
import re
from scipy.special import log_softmax


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
        reader_answers = []

        # iterate over retrieved paragraphs
        for idx, document in enumerate(paragraphs):
            # strip whitespaces and document title
            document = document.strip().split("######")[1]

            # get answer -------------------------------------------
            all_answers = self.reader.get_answers(question, document)

            # choose the valid answers
            for answer in all_answers:
                if (answer['text'] != '') and (len(re.split("\W", answer['text'])) <= max_tokens):
                    if type(answer['text']) is not str:
                        continue  # this is just to make sure that the answer is really ok

                    # save answer and info
                    answer_start = document.find(answer['text'])
                    res = {
                        "answer": answer['text'],
                        "char_offset": [answer_start, answer_start+len(answer['text'])],
                        "score": answer['score'],
                        "passage_id": idx
                    }
                    reader_answers.append(res)

        ############################################################

        # sort via scores and get best n dependent on ["extractive_reader"]["reader_top_k_answers"]
        reader_answers = sorted(reader_answers, key=lambda i: i['score'], reverse=True)
        reader_answers = reader_answers[:max_answers]

        # get answers with their info
        answers = []
        scores = []
        passage_indeces = []
        char_offsets = []
        for ans in reader_answers:
            answers.append(ans["answer"])
            scores.append(ans["score"])
            char_offsets.append(ans["char_offset"])
            passage_indeces.append(ans["passage_id"])

        # get paragraph titles and strips the title from the beggining
        titles = [x.split("######")[0] for x in paragraphs]
        paragraphs = [x.split("######")[1] for x in paragraphs]

        # convert to float because of json
        paragraph_scores = log_softmax(paragraph_scores)
        paragraph_scores = [float(x) for x in paragraph_scores]
        scores = log_softmax(scores)  # log softmax
        scores = [float(x) for x in scores]

        # not mandatory - just some unique ids
        ids = [idx for idx, x in enumerate(paragraphs)]

        # create response json
        response = {
            "question": question,
            "ranker": {
                "paragraphs": paragraphs,
                "titles": titles,
                "ids": ids,
                "scores": paragraph_scores
            },
            "extractive_reader": {
                "answers": answers,
                "passage_indices": passage_indeces,
                "char_offsets": char_offsets,
                "scores": scores
            }
        }

        return response
