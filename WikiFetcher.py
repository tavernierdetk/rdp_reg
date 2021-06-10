from __future__ import unicode_literals, print_function

import requests
import spacy
import json
import wikipedia

class Wikifetcher:
    def __init__(self, language):
        #two letter code from wiki doc
        self.language = language
        wikipedia.set_lang(self.language)

    def get_pageid(self, term):
        res = requests.get(f'https://{self.language}.wikipedia.org/w/api.php?action=query&prop=pageprops&titles=' + term +'&format=json').json()
        # print(res)
        try:
            pages = list(res["query"]["pages"].keys())
            if pages[0] == -1:
                return "No Page"
            return pages[0]
        except:
            return "No_page"

    def wiki_clear_cache(self):
        for cached_func in (wikipedia.search, wikipedia.suggest, wikipedia.summary):
            cached_func.clear_cache()

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

    def wiki_get_page_from_term(self, term):
        try:
            page = wikipedia.page(term)
            return page
        except:
            # print(wikipedia.search(term)[0])
            self.wiki_get_page_from_term(wikipedia.search(term)[0])

    def get_wiki_page(self, term):
        try:
            # print("Trying straight load...")
            page = wikipedia.page(title=term)
            # print("Straight load succeeded")
        except wikipedia.exceptions.DisambiguationError as error:
            # print("Disambiguations complete")
            page = wikipedia.page(title=error.options[0], auto_suggest=False)
            #
            # # wikivert.wiki_clear_cache()
            # page_id = self.get_pageid(top_contender)
            # print(page_id)
            # print("Disambiguations complete")
            # if page_id == -1:
            #     page = None
            # else:
            #     page = wikipedia.page(pageid=self.get_pageid(error.options[0]))
        except wikipedia.exceptions.PageError as error:
            # print(error)
            page = None

        return page

    def get_wiki_tuple(self, page):
        if page == None:
            return (None, None, None)
        manual_summary = page.summary[:page.summary.find('.')+1]
        return(self.get_qid_from_title(page.title, self.language, manual_summary, page.url))

if __name__ == "__main__":

    # term = 'RDI'
    # language = 'fr'
    # wikivert = Wikifetcher(language)
    # print(wikivert.get_wiki_page(term))
    #
    #
    print("Loading dataset...")
    with open("./JSONFiles/sample_article.json", 'rb') as file:
        sample_article = json.load(file)

    # print(sample_article['text'])

    # Load models
    language = 'fr'
    nlp = spacy.load('./new_model')

    wikivert = Wikifetcher(language)

    doc = nlp(sample_article['text'])

    doc.ents
    for ent in doc.ents:
        full_ent = ""
        for token in ent:
            full_ent = full_ent + token.text + " "
        full_ent = full_ent[:-1]
        print(full_ent)
        print(ent.label_)
        page = wikivert.get_wiki_page(full_ent)
        print(wikivert.get_wiki_tuple(page))
        print()


