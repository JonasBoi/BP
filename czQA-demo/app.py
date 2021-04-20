import numpy as np
import warnings
import nltk
import jsonschema as js

from reader import Reader
from retriever import Retriever

warnings.filterwarnings("ignore")
nltk.download('punkt')


def find_answer(question, reader, retriever, max_docs):
    """
    Finds the answer to the question - connects everything

    """

    # retrieve the relevant paragraphs of context
    documents, article_list = retriever.retrieve(question, max_docs=max_docs)

    # for saving the best results
    bestAnswers = []
    bestDocs = []
    bestScores = []

    # delete null strings
    documents = [x for x in documents if len(x.strip())]

    # iterate over retrieved paragraphs
    for idx, document in enumerate(documents):
        # strip whitespaces
        document = document.strip()
        # chceck if any document has been found for the question
        if document == "":
            continue

        # get answer -------------------------------------------
        answers = reader.get_answers(question, document)
        log_conf = 0

        # choose the first valid answer - which is not empty
        answer = ''
        for answer in answers:
            if answer['text'] != '':
                log_conf = answer['score']
                answer = answer['text']
                break
        #######################################################
        if type(answer) is not str:
            continue  # this is just to make sure that the answer is really ok

        # save probs and answer
        bestAnswers.append(answer)
        bestScores.append(log_conf)
        # save retrieved doc
        bestDocs.append(documents[idx])

    ############################################################
    # check if any answer was found
    if len(bestScores) == 0 or bestAnswers[np.argmax(bestScores, axis=0)] == '':
        return ""

    # get the best doc
    # get best answer from retriever according to reader
    document = bestDocs[np.argmax(bestScores, axis=0)]
    answer = bestAnswers[np.argmax(bestScores, axis=0)]

    return answer, document, bestAnswers, bestScores, article_list, bestDocs


def run():
    # saved reader model
    model_checkpoint = "./data/bert_finetuned_czech_squad2"
    # files with additional saved data
    dita_file = "./data/czech-morfflex-pdt-161115/czech-morfflex-pdt-161115.tagger"
    wiki_titles = "./data/cswiki-latest-all-titles-in-ns0"
    wiki_abstracts = "./data/wiki_abstracts_processed.json"
    index_file = "./data/abstracts_index.pkl"

    # create reader and retriever
    reader = Reader(model_checkpoint)
    retriever = Retriever(wiki_abstracts, wiki_titles, dita_file, index_file, download_ner_model=False)

    while True:
        print("Položte otázku:")
        question = input()

        try:
            answer, document, best_answers, best_scores, article_list, best_docs = find_answer(question,
                                                                                               reader, retriever, 5)
        except ValueError:
            print("odpověď nenalezena")
            continue


        print(answer)
        print()
        print(best_answers)
        print(best_scores)
        print(article_list)
        print()
        print(document)
        print()
        print()
