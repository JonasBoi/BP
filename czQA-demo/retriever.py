class Retriever():

    def __init__(self, wiki_abstracts, wiki_titles, dita_file, index_file, download_ner_model=False):
        # set wiki api language to search the Czech Wikipedia
        wikipedia.set_lang("cs")

        # save the most common czech words (stop words)
        common = "kdy být a se v na ten on že s z který mít do já o k i jeho ale svůj jako za moci pro tak po tento co když všechen už jak aby od nebo říci jeden jen můj jenž ty stát u muset chtít také až než ještě při jít pak před však ani vědět hodně podle další celý jiný mezi dát tady tam kde každý takový protože nic něco ne sám bez či dostat nějaký proto"
        self.common = common.split()

        # save punctuation to be removed
        punctuation = ". , ? ! ... \" ( ) ; - /"
        self.punctuation = punctuation.split()

        print("Loading lemmatizer")
        # morphodita lemmatizer
        self.tagger = Tagger(dita_file)
        print("Lemmatizer loaded")

        print("Building titles index")
        # load wiki titles and build index for search
        self.bm25_articles_index, self.titles = self.get_title_search_index(wiki_titles)
        print("Titles index done")

        print("Building articles index")
        # load wiki abstracts and build index for search
        self.bm25_abstract_index, self.abstract_titles, self.abstracts = self.get_abstract_search_index(wiki_abstracts,
                                                                                                        index_file)
        print("articles index done")

        print("Loading tokenizer")
        # load tokenizer to split text into sentences
        self.tokenizer = nltk.data.load('tokenizers/punkt/czech.pickle')
        print("Tokenizer loaded")

        print("Building ner model")
        # Download and load model (set download=False to skip download phase)
        self.ner = build_model(configs.ner.ner_ontonotes_bert_mult, download=download_ner_model)
        print("Ner model loaded")

        print("Retriever initialized")

    def get_title_search_index(self, wiki_titles):
        """
        Build index for searching through relevant title names on czech wiki:

        """

        # load all the titles from the file
        f = open(wiki_titles, "r")
        titles = []

        for line in f:
            title = ((" ").join(line.split("_"))).strip()
            title = title.strip('\n')
            titles.append(title)
        f.close()

        # tokenize for bm25
        tok_titles = []
        for title in titles:

            tok_tit = re.split(" ", title.lower())
            for tok in tok_tit:
                if tok == "":
                    tok_tit.remove("")

            tok_titles.append(tok_tit)

        # build index
        bm25 = BM25Okapi(tok_titles)

        return bm25, titles

    def get_abstract_search_index(self, saved_abstracts, index_file):
        """
        Build index for searching through relevant abstracts on czech wiki:

        """
        # load abstracts and titles from preprocessed JSON file
        with open(saved_abstracts, "r") as f:
            wiki_abstracts = json.load(f)

        titles = []
        for idx in wiki_abstracts:
            titles.append(wiki_abstracts[idx]['title'])

        abstracts = []
        for idx in wiki_abstracts:
            abstracts.append(wiki_abstracts[idx]['abstract'])

        # if index saved, load it with pickle and return
        if os.path.isfile(index_file):
            with open(index_file, "rb") as fd:
                print("loading from pickle")
                bm25 = pickle.load(fd)
                return bm25, titles, abstracts

        # process for creating bm25 index
        tok_abstracts = []
        for abstract in abstracts:
            tok_abstract = self.delete_common(self.lemmatize_morphodita(abstract.lower()))
            tok_abstracts.append(tok_abstract)

        # build index
        bm25 = BM25Okapi(tok_abstracts)

        # save index with pickle
        with open(index_file, "wb") as fd:
            pickle.dump(bm25, fd, pickle.HIGHEST_PROTOCOL)

        return bm25, titles, abstracts

    def search_titles(self, question):
        """
        Search with bm25 among the wiki titles

        """
        tokenized_query = self.delete_common(self.lemmatize_morphodita(question.lower()))
        results = self.bm25_articles_index.get_top_n(tokenized_query, self.titles, n=5)

        return results

    def search_abstracts(self, question):
        """
        Search with bm25 among the wiki abstracts

        """
        tokenized_query = self.delete_common(self.lemmatize_morphodita(question.lower()))
        results = self.bm25_abstract_index.get_top_n(tokenized_query, self.abstract_titles, n=5)

        return results

    def get_named_entities(self, question):
        """
        Extracts named entities from the question.

        """
        # tag the questions
        ner_tags = self.ner([question])

        # extracts the named entities
        named_entities = ""
        for idx, tag in enumerate(ner_tags[1][0]):
            if tag != 'O':
                named_entities += ner_tags[0][0][idx] + " "

        # save NEs in a list
        NEs = []
        if len(named_entities.strip()) != 0:
            NEs.append(named_entities.strip())

        return NEs

    def iscommon(self, x):
        """
        decides if query token is common

        """
        if x in self.common or x in self.punctuation:
            return True
        else:
            return False

    def delete_common(self, tokens):
        """
        Remove the most common czech words from the query tokens (low information value)

        """
        tokens = [x for x in tokens if not self.iscommon(x)]

        return tokens


    def lemmatize_morphodita(self, text):
        """
        Returns lemma of each token in a list of lemmatized tokens

        """
        # tokenize and join again
        # (this works better with morphodita which sometimes fails to tokenize the
        #  text correctly if it wasnt split before like this - it just works)
        text = re.split("\W", text)
        text = (" ").join(text)

        tokens = list(self.tagger.tag(text, convert='strip_lemma_id'))

        lemmas = []
        for token in tokens:
            lemmas.append(token.lemma)

        return lemmas


    def search_again(self, tokens):
        """
        Performs repeated search in case wiki api didnt find any documents

        """
        # join the searched tokens and try to use wiki search
        searched_term = (' ').join(tokens)
        if searched_term.strip() != "":
            doc_list = wikipedia.search(searched_term, results=1)

        # if no tokens left, end
        if len(tokens) == 0:
            return []
        # if nothing was found, strip the first searched token
        # and perform the search recursivly like this
        if len(doc_list) == 0:
            del tokens[0]
            return self.search_again(tokens)
        # return the found article
        return doc_list


    def get_doc_list(self, question):
        """
        Returns top 1-3 wiki arcitles that might answer the question topic

        """

        # get names entities if present
        named_ERs = self.get_named_entities(question)
        # get relevant article title names
        relevant_titles = self.search_titles(question)
        # get article titles from relevant abstracts search
        relevant_abstracts = self.search_abstracts(question)

        # search for documents - 1 article for each search method
        max_docs = 1
        doc_list = []

        # search based on recognised named entity
        if len(named_ERs) > 0:
            article = wikipedia.search(named_ERs[0], results=max_docs)
            if len(article) > 0:
                doc_list.append(article[0])
        # search based on best wiki title match
        if len(relevant_titles) > 0:
            article = wikipedia.search(relevant_titles[0], results=max_docs)
            if len(article) > 0:
                doc_list.append(article[0])
        # search based on best wiki abstract match
        if len(relevant_abstracts) > 0:
            article = wikipedia.search(relevant_abstracts[0], results=max_docs)
            if len(article) > 0:
                doc_list.append(article[0])

        # basic search for the non-processed question
        article = wikipedia.search(question, results=max_docs)
        # simplify the search if its too bad and search recursively
        if len(article) == 0:
            # extract important for wiki
            tokens = self.delete_common(self.lemmatize_morphodita(question.lower()))
            article = self.search_again(tokens)
        if len(article) > 0:
            doc_list.append(article[0])

        return doc_list


    def normalize_length(self, par):
        """
        Splits too long paragraph into smaller ones

        """

        # split long paragraph into sentences
        sentences = self.tokenizer.tokenize(par)

        normalized_pars = []
        new_paragraph = ""

        # iterate over sentences
        for idx, sentence in enumerate(sentences):
            # if max paragraph length was reached, save the created paragraph
            # and start appending to a new one
            if len(new_paragraph) + len(sentence) > 2500:
                normalized_pars.append(new_paragraph)
                new_paragraph = ""
                # make some overlap by taking some sentences from the previous paragraph
                for k, trailing in enumerate(sentences[idx - 2:idx]):
                    new_paragraph += trailing
            else:
                new_paragraph += sentence

        return normalized_pars


    def get_wiki_page(self, doc):
        """
        Get the Wikipedia page content

        """
        # note: wikipedia api throws some errors that are hard to deal with
        # that is the reason for this unusual structure
        try:
            doc = wikipedia.page(doc, auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            s = e.options[0]
            try:
                doc = wikipedia.page(s, auto_suggest=False)
            except wikipedia.DisambiguationError or wikipedia.PageError:
                return "not_found"

        return doc


    def split_documents(self, doc_list):
        """
        Splits each retrieved wiki article into paragraphs and normalizes its lengths

        """

        pars = []  # the final paragraphs that will be ranked and retrieved
        lemm_pars = []  # processed paragraphs for building the index

        # iterate over articles and process each one
        for doc in doc_list:
            # get whole page content
            try:
                doc = self.get_wiki_page(doc)
            except wikipedia.PageError:
                continue
            # check if actual page was found
            # page is of Wikipedia instance
            # if not found, string "not found" is returned
            if isinstance(doc, str):
                continue

            # remove the references part of the page
            result = re.split('=== Reference ===|== Reference ==', doc.content)[0]
            # split article into paragraphs
            # this regular expression catches the headings of paragraphs
            result = re.split('== .*. ==|\\n\\n', result)

            # save stripped paragraphs
            for par in result:
                par = ((((par.strip()).strip('=')).strip('\n')).strip('\n\n')).strip('\r\n')

                # remove some trash -- dont know, how to do this better
                # its something like the references part
                # usually contains a lot of searched terms but not the answer,
                # so its removed to not end high in the bm25 ranking
                if par == '' or par == '\n' or par.strip().startswith("Obrázky, zvuky či videa k tématu"):
                    continue

                # for albert, the max paragraph length shall be shorter due to translation limits
                if self.model_type == 'mbert':
                    max_len = 3000
                else:
                    max_len = 1500

                # check max paragraph length
                if len(par) > max_len:
                    # split into smaller paragraphs - normalize lengths
                    normalized_paragraphs = self.normalize_length(par)
                    # append each smaller paragraph
                    for norm_par in normalized_paragraphs:
                        # append paragraph
                        pars.append(norm_par)
                        # get lemmas and append
                        lemm_pars.append((' ').join(self.delete_common(self.lemmatize_morphodita(norm_par.lower()))))
                else:
                    # append paragraph
                    pars.append(par)
                    # get lemmas and append
                    lemm_pars.append((' ').join(self.delete_common(self.lemmatize_morphodita(par.lower()))))

        return pars, lemm_pars


    def retrieve(self, question, max_docs):
        """
        Returns the top 3 paragraphs for the given question

        """
        # check max question length - just set something
        if len(question) > 250:
            return ""

        # strip questionmark - its not necessary i guess
        question = question.strip('?')

        # get relevant wiki article names
        doc_list = self.get_doc_list(question)

        # convert from list to set -- only work with unique article names
        doc_list = set(doc_list)

        # split docs into paragraphs -- this is the slowest part of the process
        # might need optimalization
        pars, lemm_pars = self.split_documents(doc_list)

        # if we didnt find anything using the wiki api -- we need to get atleast something
        # so we just take the reelvant abstracts and hope the answer is there
        if len(pars) == 0:
            # tokenize the query and get the top 5 abstracts
            tokenized_query = self.delete_common(self.lemmatize_morphodita(question.lower()))
            results = self.bm25_abstract_index.get_top_n(tokenized_query, self.abstracts, n=5)

            # perform the paragraph normalization similar to the one in split_documents()
            # get the paragraphs and their processed versions to build its search index
            for par in results:
                par = par.strip()
                # check max paragraph length
                max_len = 3000
                if len(par) > max_len:
                    # split into smaller paragraphs
                    normalized_paragraphs = self.normalize_length(par)
                    # append each smaller paragraph
                    for norm_par in normalized_paragraphs:
                        pars.append(norm_par)
                        lemm_pars.append((' ').join(self.delete_common(self.lemmatize_morphodita(norm_par.lower()))))
                else:
                    # append paragraph
                    pars.append(par)
                    # get lemmas and append
                    lemm_pars.append((' ').join(self.delete_common(self.lemmatize_morphodita(par.lower()))))
        ##############################################################################################

        # tokenize for bm25
        tok_text = []
        for par in lemm_pars:
            tok_par = re.split("\W", par)
            for tok in tok_par:
                if tok == "":
                    tok_par.remove("")
            tok_text.append(tok_par)

        # finally build the index from the processed paragraphs
        bm25 = BM25Plus(tok_text)
        # either BM25 function can be used - the results are similar
        # bm25 = BM25Okapi(tok_text)

        # tokenize and lemmatize the query
        tokenized_query = (' ').join(self.delete_common(self.lemmatize_morphodita(question.lower())))
        tokenized_query = re.split("\W", tokenized_query)

        # get top n results
        results = bm25.get_top_n(tokenized_query, pars, n=max_docs)

        return results, doc_list
