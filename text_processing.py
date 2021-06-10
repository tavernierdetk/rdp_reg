import json
import sklearn
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import pickle
import article_scrapper as AS
import datetime
from datetime import timedelta

class Corpus:
    def __init__(self, replacement_dictionary=[], valence_dictionary=[], stopwords=[], target_words=[]):
        self.replacement_dictionary = replacement_dictionary
        self.valence_dictionary = valence_dictionary
        self.target_words = target_words
        self.stopwords = stopwords
        self.texts = []
        self.term_values = []
        self.total_values_by_term = []

    def add_text(self, text):
        self.texts.append(Text(text))

    def compute_tf_idf_matrix(self):
        print("Processing texts...")
        self.tf_idf_matrix = []
        vectorizer = TfidfVectorizer(stop_words=self.stopwords)
        vectors = vectorizer.fit_transform(text.text for text in self.texts)
        feature_names = vectorizer.get_feature_names()
        dense = vectors.todense()
        denselist = dense.tolist()
        df = pd.DataFrame(denselist, columns=feature_names)
        listed_terms = list(df.columns)
        for term in listed_terms:
            non_zero_count = df[term].astype(bool).sum(axis=0)
            self.total_values_by_term.append(

                (term, df[term].sum()/non_zero_count)
            )
        self.total_values_by_term = sorted(self.total_values_by_term, key=lambda x: x[1], reverse=True)
        zipped_list = []
        for index, term in enumerate(self.total_values_by_term):
            if index == 100:
                break
            zipped_list.append((term[0], index+1))
        self.zipped_list = zipped_list

    def compute_delta_terms(self, previous_list):
        final_list = []
        for term in self.zipped_list:
            flag = 0
            for term_prior_period in previous_list:
                if term[0] == term_prior_period[0]:
                    final_list.append((term[0], term[1], term_prior_period[1] - term[1]))
                    flag = 1
            if flag == 1:
                continue
            final_list.append((term[0], term[1], 100 - term[1]))
        return final_list

    def give_context(self, word):
        for text in self.texts:
            print(text.give_self_context(word))



class Text:
    def __init__(self, text):
        self.text = text
        self.tokenize()

    def tokenize(self):
        self.tokenized = self.text.split()
        for index, word in enumerate(self.tokenized):
            self.tokenized[index] = word.lower()


    def give_self_context(self, word, range_length=15):
        listed_context = []
        for index, token in enumerate(self.tokenized):
            if token == word:
                matched_index = index
                start = 0 if matched_index < range_length else matched_index - range_length
                stop = len(self.tokenized)-1 if (len(self.tokenized) - matched_index) < range_length else matched_index + range_length
                context_string = ""
                for i in range(start, stop):
                    context_string += " " + self.tokenized[i]
                listed_context.append(context_string)
        return listed_context


def update_temporary_stopword(filepath, listed_words):
    with open(filepath,'rb') as file:
        stopwords = json.load(file)
    for word in listed_words:
        stopwords.append(word)
    with open(filepath,'w') as file:
        json.dump(stopwords, file, indent=3)


if __name__ == "__main__":

    test_person = {"name": "Julie Payette",
                   "language" : 'en' }

    # start = datetime.datetime.now()
    # start = start.replace(day=1,month=1,year=2013)
    # beginning = start - timedelta(weeks=104)

    # start = datetime.datetime.now()
    # beginning = start - timedelta(weeks=402)

    start = datetime.datetime.now()
    start = start.replace(day=1,month=1,year=2011)
    beginning = start - timedelta(weeks=608)

    date_range = (beginning,start)

    person = AS.Person(test_person, date_range, 5)
    corpus = Corpus()
    for article in person.articles:
        corpus.add_text( article['text'])

    corpus.compute_tf_idf_matrix()


    pickle.dump(corpus, open("pickleFiles/corpus.pickle", 'wb'))
    pickle.dump(person, open("pickleFiles/person2013-fr.pickle", 'wb'))

    # corpus = pickle.load(open("pickleFiles/corpus.pickle", 'rb'))
    # person = pickle.load(open("pickleFiles/person.pickle", 'rb'))

    for term in corpus.zipped_list:
        print(term[0])

    print(corpus.texts[1].text)
