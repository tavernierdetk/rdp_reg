from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import feedparser
import credentials
import json
import datetime
import requests
from google_alerts import GoogleAlerts
from article_scrapper import SearchTerm
from datetime import timedelta
from GoogleNews import GoogleNews
from newspaper import Article
import spacy

class Extractor:
    def __init__(self, connection_creds, start_time, end_time, lang='fr', page_range=1):
        self.creds = connection_creds
        # data structure for connection_creds:
        #   {
        #     "SHEET_ID" : googleSheetId
        #   }
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.sheet_id = connection_creds["SHEET_ID"]
        # data structure for feed_tuples:
        # [
        #   { "region" : region_name,
        #     "feed_tuples": [ ( keyword, feed_url), (...) ]
        #   },
        # {...}
        # ]
        self.filters_domain = [
            "necrocanada",
            "stockhouse",
            "Suttonquebec",
            "Manufacturejobs",
            "arrondissement.com",
            "canadanews24.ca/",
            "poleposition.ca",
            'pcq.qc.ca',
            'meteomedia.com/',
            'lequotidien.com',
            'kamloopsthisweek.com',
            'singtao.ca',
            'nightlife.ca',
            'rcinet.ca',
            'rockville'
        ]

        self.feeds_by_region = []
        self.responses = []
        self.start_time = start_time
        self.end_time = end_time
        self.lang = lang
        self.page_range = page_range
        # self.create_feeds()
        self.update_feeds()
        self.extract_articles()

    def extract_articles_GNews(self):
        self.articles = []
        start_date_string = str(self.start_time.month) + "/" + str(self.start_time.day) + "/" + str(
            self.start_time.year)
        end_date_string = str(self.end_time.month) + "/" + str(self.end_time.day) + "/" + str(
            self.end_time.year)
        googlenews = GoogleNews(start=start_date_string, end=end_date_string)
        googlenews.set_lang(self.lang)

        print("Start search")

        now = datetime.datetime.now()
        print(now)

        for regions_feed in self.feeds_by_region:
            if regions_feed["region"] == "Tests":
                continue
            for feed in regions_feed["feed_tuples"]:
                keyword = feed[0]
                print("Running search")
                print(keyword)

                newtime = datetime.datetime.now()
                googlenews.search(keyword)
                print(newtime-now)
                now = newtime

                print("Getting articles...")

                for i in range(1, self.page_range):
                    googlenews.getpage(i)
                    for link in googlenews.get_links():
                        try:
                            article = Article(link, language='fr')
                            article.download()
                            article.parse()
                            article.nlp()

                            flag = False

                            for formatted_article in self.articles:
                                if article.title == formatted_article['title']:
                                    if regions_feed["region"] not in formatted_article["categories"]:
                                        formatted_article["categories"].append(regions_feed["region"])
                                    flag = True
                            if flag:
                                continue
                            else:
                                self.articles.append({
                                                      "title": article.title,
                                                      "article_object": article,
                                                      "categories": [regions_feed["region"]],
                                                      "domain": self.extract_domain(article.url)
                                                      })
                                print("Added:")
                                print(article.title)
                        except:
                            continue


    def extract_articles(self):
        self.articles = []

        for regions_feed in self.feeds_by_region:
            if regions_feed["region"] == "Tests":
                continue
            for feed in regions_feed["feed_tuples"]:
                keyword = feed[0]

                if feed[1]  == None:
                    continue
                print(feed[1])
                feed_content = feedparser.parse(feed[1])
                for item in feed_content['items']:
                    title = item.title
                    link = item.link

                    start = link.find('&url=')+5
                    end = link.find('&ct=')
                    short_link = link[start:end]
                    link = short_link

                    description = item.description
                    date = item.date
                    flag = False
                    for article in self.articles:
                        if article["link"] == link or article['title'] == title:
                            #TODO check whether article is already in that category
                            if regions_feed["region"] not in article["categories"]:
                                article["categories"].append(regions_feed["region"])
                            flag = True
                    if flag:
                        continue
                    else:
                        self.articles.append({"link": link[:400],
                                              "title": title,
                                              "description": description,
                                              "date": date,
                                              "keyword": keyword,
                                              "categories": [regions_feed["region"]],
                                              "domain":  self.extract_domain(link),
                                              "short_link": short_link
                                              })

    def fetch_full_articles(self, nlp):
        texts = []
        for article in self.articles:
            try:
                analyzed_article = Article(article['short_link'], language='fr')
                analyzed_article.download()
                analyzed_article.parse()

                delattr(analyzed_article, 'html')
                delattr(analyzed_article, 'doc')
                delattr(analyzed_article, 'clean_doc')
                delattr(analyzed_article, 'clean_top_node')
                delattr(analyzed_article, 'top_node')

                doc = nlp(analyzed_article.text)

                if analyzed_article.meta_lang == 'fr':
                    texts.append(analyzed_article.text)

                article['topics'] = doc.cats

                # res_linker = requests.post(self.creds["API_ENDPOINT_LINKER"], json=analyzed_article.text)
                # article['ents'] = res_linker['actors']


                print(article)
                article['analyzed_article'] = analyzed_article
            except:
                continue
        pickle.dump(texts, open('raw_texts.pickle', 'wb'))

    def convert_multiple_cats(self):
        for article in self.articles:
            print("Old:")
            print(article)
            old_cats = article['categories']
            new_cats = []
            for region in old_cats:
                new_cats.append({"name": region, "type": "region"})
            try:
                for topic in article['topics']:

                    if article['topics'][topic] > .4:
                        if topic == "Sante":
                            topic_formatted = "Santé"
                        elif topic == "Economie":
                            topic_formatted = "Économie"
                        elif topic == "Education":
                            topic_formatted = "Éducation"
                        elif topic == "Politique federale":
                            topic_formatted = "Politique fédérale"
                        else:
                            topic_formatted = topic
                        new_cats.append({"name": topic_formatted, "type": "topic"})
                article.pop('topics', None)
                article.pop('analyzed_article', None)
            except:
                article['categories'] = new_cats
                continue
            article['categories'] = new_cats
            print("New:")
            print(article)

    def filter_articles(self, article):
        for domain in self.filters_domain:
            if article['link'].find(domain) != -1:
                return False

        return True

    def create_feeds(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        ga = GoogleAlerts(creds["GOOGLE_ACCOUNT"], creds["GOOGLE_PASSWORD"])
        ga.authenticate()

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../JSONFiles/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet_metadata = service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        for sheet in sheets:
            title = sheet.get("properties", {}).get("title", "Sheet1")

            result = service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=title+"!A1:B100").execute()
            rows = result.get('values', [])
            for row in rows:
                if len(row) == 1:
                    print('run rss creation', row[0])
                    ga.create(row[0], {'delivery': 'RSS', 'language': 'all'})[0]['rss_link']


    def update_feeds(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../JSONFiles/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet_metadata = service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        for sheet in sheets:
            title = sheet.get("properties", {}).get("title", "Sheet1")
            region_feeds = {
                "region": title,
                "feed_tuples": []
            }
            result = service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=title+"!A1:B100").execute()
            rows = result.get('values', [])
            for row in rows:
                if len(row) == 1:
                    continue
                region_feeds["feed_tuples"].append((row[0], row[1]))
            self.feeds_by_region.append(region_feeds)

    def extract_domain(self, string):
        start = string.find('&url=')+13
        end = string[start:].find('/')+start
        return string[start:end]

    def output_articles_to_db(self):
        self.convert_multiple_cats()
        for article in self.articles:
            if self.filter_articles(article):
                endpoint = self.creds["API_ENDPOINT"]
                headers = {"Authorization": "Bearer " + self.creds["API_TOKEN"] }

                article["analyzed_article"] = ''
                try:
                    res = requests.post(endpoint, json=article, headers=headers).json()
                    print(res)
                    self.responses.append(res)
                except:
                    print("error")

    def output_articles_to_db_dev(self):
        self.convert_multiple_cats()
        for article in self.articles:
            if self.filter_articles(article):
                endpoint = self.creds["API_ENDPOINT_DEV"]
                headers = {"Authorization": "Bearer " + self.creds["API_TOKEN_DEV"] }

                print(article)
                article["analyzed_article"] = ''
                try:
                    res = requests.post(endpoint, json=article, headers=headers).json()
                    print(res)
                    self.responses.append(res)
                except:
                    print("error")


if __name__ == "__main__":

    creds = credentials.get_creds()
    now = datetime.datetime.now()

    nlp = spacy.load('ModelFiles/model-CAT-u-06-05-2021')

    start = now - timedelta(days=1)

    extractor = Extractor(creds, start, now)

    # pickle.dump(extractor, open('extractor_test.pickle', 'wb'))
    # extractor = pickle.load(open('extractor.pickle', 'rb'))
    # extractor.creds = creds
    extractor.fetch_full_articles(nlp)

    extractor.output_articles_to_db()
    pickle.dump(extractor, open('extractor_test.pickle', 'wb'))




