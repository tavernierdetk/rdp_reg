from newspaper import Article
from GoogleNews import GoogleNews
import datetime
from datetime import timedelta
import pickle



class SearchTerm:
    def __init__(self, term_params, date_range, page_range):


        #personnal_info is an object shaped with the following structure:
        # {  "name": name,
        #    "language": <Two letter code, legend found here: https://sites.google.com/site/opti365/translate_codes >
        # }

        #date_range is a tuple of datetime object, (beginning, end_date)

        self.page_range = page_range
        self.date_range = date_range
        self.term_params = term_params
        self.articles = []
        self.collect_articles()



    def collect_articles(self):
        start_date_string = str(self.date_range[0].month) + "/" + str(self.date_range[0].day) + "/" + str(self.date_range[0].year)
        end_date_string = str(self.date_range[1].month) + "/" + str(self.date_range[1].day) + "/" + str(self.date_range[1].year)
        googlenews = GoogleNews(start=start_date_string, end=end_date_string)
        googlenews.set_lang(self.term_params['language'])
        googlenews.search(self.term_params["term"])
        print("Getting articles...")

        for i in range(1, self.page_range):
            googlenews.getpage(i)
            for link in googlenews.get_links():
                try:
                    article = Article(link, language='fr')
                    article.download()
                    article.parse()
                    article.nlp()
                except:
                    continue
                self.articles.append(article)


if __name__ == "__main__":
    test_term = {"term": "Simon Allaire",
                   "language" : 'fr' }

    start = datetime.datetime.now()
    beginning = start - timedelta(days=1)

    date_range = (beginning,start)

    person = SearchTerm(test_term, date_range, 3)
    print(person)
    for article in person.articles:
        # delattr(article, 'html')
        # delattr(article, 'doc')
        # delattr(article, 'clean_doc')
        # delattr(article, 'clean_top_node')
        # delattr(article, 'top_node')
        # article.parse()
        print(article.title)
        print(article.canonical_link)
        print(article.keywords)
        print(article.meta_keywords)
        print(article.tags)
        # print(article.meta_data)
    #
    #
    # pickle.dump(person, open("pickleFiles/test_person.pickle", 'wb'))

    # person = pickle.load(open('pickleFiles/test_person.pickle', 'rb'))
    # print(person.articles)