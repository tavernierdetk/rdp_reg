from __future__ import unicode_literals, print_function

import requests
import spacy
from spacy.tokens import Span
import json
import wikipedia
import pickle
from spacy.kb import KnowledgeBase


class Wikifetcher:
    def __init__(self, language):
        #two letter code from wiki doc
        self.language = language
        wikipedia.set_lang(self.language)

        self.kb_ents_tba = []


    def update_kb(self, kb):
        for ent in self.doc.ents:
            if ent._.wiki_page == None:
                continue

            if ent.kb_id_ == "":

                wiki_tuple = self.get_wiki_tuple(ent._.wiki_page)

                vector = nlp(wiki_tuple[1]).vector
                kb.add_entity(entity=wiki_tuple[0], freq=32, entity_vector=vector)
                kb.add_alias(alias=ent.text, entities=[wiki_tuple[0]], probabilities=[1])


    def get_qid_from_title(self, title, language, manual_summary, link):
        protocol = 'https'
        language = language
        base_url = '.wikipedia.org/w/api.php'
        params = f'action=query&prop=pageprops&format=json&titles={title}'
        url = f'{protocol}://{language}{base_url}?{params}'

        response = requests.get(url)
        json = response.json()
        for pages in json['query']['pages'].values():
            wikidata_id = pages['pageprops']['wikibase_item']
            try:
                wikidata_desc = pages['pageprops']['wikibase-shortdesc']
            except:
                wikidata_desc = manual_summary
        return wikidata_id, wikidata_desc, link

    def get_wiki_page(self, ent):
        term = ""
        for token in ent:
            term = term + token.text + " "
        term = term[:-1]
        try:
            page = wikipedia.page(title=term)
        except wikipedia.exceptions.DisambiguationError as error:
            # print("Disambiguations complete")
            best_suggestion = error.options[0]
            try:
                page = wikipedia.page(title=best_suggestion, auto_suggest=False)
            except:
                return None
        except wikipedia.exceptions.PageError:
            page = None

        return page

    def get_wiki_tuple(self, page):
        if page == None:
            return (None, None, None)
        manual_summary = page.summary[:page.summary.find('.')+1]
        return(self.get_qid_from_title(page.title, self.language, manual_summary, page.url))

    def update_ents(self, doc):
        self.doc = doc
        for ent in self.doc.ents:
            print("Next? ([Y]es/[N]o:")
            if input() == 'N':
                break
            print(ent.text)
            print(ent.kb_id_)
            if ent.kb_id_ == "":
                try:
                    ent._.set('wiki_page', self.get_wiki_page)
                    ent = self.human_verification(ent)
                    self.kb_ents_tba.append((ent))
                except:
                    ent._.set('wiki_page', None)
                    ent = self.human_verification(ent)

    def human_verification(self, ent):
            context = self.context_retrieval(ent)
            print('Context: ', context)
            print('Suggested page: ', ent._.wiki_page)
            if ent._.wiki_page is not None:
                print('Suggested page URL:', ent._.wiki_page.url)
            print('Action ([a]pprove, [c]hange, [n]o page: ')
            action = input()

            if action == "c":
                print('Proper page title:')
                new_title = input()
                page = wikipedia.page(new_title, redirect=False, auto_suggest=False)
                print(page)
                ent._.set('wiki_page', page)
            elif action == "n":
                ent._.set('wiki_page', None)



    def context_retrieval(self, ent):
        for sentence in self.doc.sents:
            if ent.start > sentence.start and ent.end < sentence.end:
                return sentence.text



if __name__ == "__main__":
    articles = pickle.load(open('/Users/alex/PycharmProjects/RevueDePresseRegions/raw_texts.pickle', 'rb'))

    language = 'fr'
    kb_path = "/Users/alex/PycharmProjects/RevueDePresseRegions/ModelFiles/kb"
    nlp = spacy.load('fr_core_news_lg')

    wikivert = Wikifetcher('fr')
    Span.set_extension("wiki_page", getter=wikivert.get_wiki_page)
    vocab = nlp.vocab
    kb = KnowledgeBase(vocab=vocab, entity_vector_length=300)


    # TODO comment out to build kb from scratch
    kb.from_disk(kb_path)
    print(kb.get_entity_strings())

    for article in articles:
        if input("Un autre? (o/n") == 'o':
            doc = nlp(article)
            wikivert.update_ents(doc)
        else:
            break
    wikivert.update_kb(kb)



    print(kb.get_entity_strings())

    kb.to_disk("/Users/alex/PycharmProjects/RevueDePresseRegions/ModelFiles/kb")


