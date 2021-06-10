import spacy
import pickle
from spacy.kb import KnowledgeBase
from spacy.vocab import Vocab
import gensim
import datetime
import WikiFetcher



class ModelExtender:
    def __init__(self, language_model):
        self.language_model = language_model

class TextOutput:
    def __init__(self, doc):
        self.doc = doc
        self.actors = []
        self.relationships = []

    def extract_actors(self):
        for ent in self.doc.ents:
            self.actors.append(ent)
            print(ent)
            print(ent.kb_id_)

    def find_adjectives(self):
        for actor in self.actors:
            print(actor)

def timer_reset(prev):
    now = datetime.datetime.now()
    delta = now-prev
    print("Time taken: ", delta)
    return datetime.datetime.now()

if __name__ == "__main__":
    prev = datetime.datetime.now()

    print("Loading dataset...")
    #Load dataset
    from article_scrapper import Person
    person = pickle.load(open('pickleFiles/test_person.pickle', 'rb'))


    prev = timer_reset(prev)
    print("Loading models...")

    #Load models and initialize kb
    language_model = spacy.load('fr_core_news_md')





