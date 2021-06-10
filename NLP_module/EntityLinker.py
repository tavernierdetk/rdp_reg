import spacy
import pickle
from spacy.kb import KnowledgeBase
from spacy.vocab import Vocab
import datetime
import json
from spacy.util import filter_spans
from spacy.tokens import Span

class Actor:
    def __init__(self, token):
        #re-tokenized after NER tagging so the token has kb_id_, etc... properties
        self.token = token

class Relationship:
    def __init__(self, language_model):
        self.language_model = language_model

class ModelExtender:
    def __init__(self, language_model):
        self.language_model = language_model

class AnnotatedText:
    def __init__(self, doc):
        self.doc = doc
        self.actors = {}
        self.relationships = []
        # self.retokenize()

        self.extract_actors()


    def extract_actors(self):
        for ent in self.doc.ents:
            if ent.kb_id_ not in self.actors:
                #TODO remove the contingency for nil once the internal DB entity creation is complete
                if ent.kb_id_ == "NIL":
                    self.actors["Unidentified"] = {
                        "count": 1,
                    }
                self.actors[ent.kb_id_] = {
                    "ent": ent,
                    "kb_id_": ent.kb_id_,
                    "label": ent.label_,
                    "count": 1,
                }
            else:
                self.actors[ent.kb_id_]['count'] +=1

    def context_retrieval(self, ent):
        if isinstance(ent, spacy.tokens.token.Token):
            for sentence in self.doc.sents:
                if ent.i > sentence.start and ent.i < sentence.end:
                    return sentence.text

        if isinstance(ent, spacy.tokens.span.Span):
            for sentence in self.doc.sents:
                if ent.start > sentence.start and ent.end < sentence.end:
                    return sentence.text

    def retokenize(self):
        spans = list(self.doc.ents) + list(self.doc.noun_chunks)
        spans = filter_spans(spans)
        with self.doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)

    def parser_output(self):
        self.chunk_heads = []
        for ent in self.doc.ents:
            head = ent.root.head
            if head not in self.chunk_heads:
                self.chunk_heads.append(head)

        self.dep_list_full = []
        for chunk_head in self.chunk_heads:
            context = self.context_retrieval(chunk_head)

            dep_list = {"root": chunk_head,
                        "dependants": []}
            for idx, child in enumerate(chunk_head.children):
                print(child)
                print(child.dep_)
                print(type(child))
                try:
                    dep_list['dependants'].append((idx, child.dep_, child, child.ent_kb_id_))
                except:
                    dep_list['dependants'].append((idx, child.dep_, child, 'no_id'))

            self.dep_list_full.append(dep_list)



def timer_reset(prev):
    now = datetime.datetime.now()
    delta = now-prev
    print("Time taken: ", delta)
    return datetime.datetime.now()



if __name__ == "__main__":
    print('Running Entity Linker Main')

    kb_path = "/Users/alex/PycharmProjects/Entity_linker_builder/output/my_kb"
    nlp_path = "/Users/alex/PycharmProjects/Entity_linker_builder/output/my_nlp_el"
    articles_path = "/Users/alex/PycharmProjects/Entity_linker_builder/output/my_nlp_el"

    nlp = spacy.load(nlp_path)
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=1)
    kb.load_bulk(kb_path)

    articles = pickle.load(open(articles_path, 'rb'))

    for article in articles:
        print(article)




