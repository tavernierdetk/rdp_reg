import sheetInterfeace as SI
import json
import credentials
from google_alerts import GoogleAlerts
import pickle
from sheetInterfeace import SheetsUpdater

class KeywordConvertor:
    def __init__(self, category, creds):
        self.category = category
        self.creds = creds
        self.full_alerts = []
        self.alert_tuples = []


    def add_alert(self, alert):
        full_alert = ""
        for index, component in enumerate(alert):
            if index == 0:
                full_alert = component['operator'] + component['term']
            else:
                full_alert = full_alert + " " + component['operator'] + component['term']


        self.full_alerts.append(full_alert)

    def generate_feeds(self):
        ga = GoogleAlerts(self.creds["GOOGLE_ACCOUNT"], self.creds["GOOGLE_PASSWORD"])
        # Authenticate your user
        ga.authenticate()
        for term in self.full_alerts:
            self.alert_tuples.append((term,  ga.create(term, {'delivery': 'RSS', 'language': 'all'})[0]['rss_link']))

def create_alert(term):
    return {"term": term, "operator": ""}

if __name__ == "__main__":
    creds = credentials.get_creds()
    listed_alerts = []

    category = "Tests"
    # listed_sites = [
    #     Megan Perry Malençon, "litteral"),
    #     Joel Arseneau, "litteral"),
    #     Gaspésie, "litteral"),
    #     Iles-de-la-Madeleine, "litteral"),
    #     MRC d’Avignon, "litteral"),
    #     MRC de Bonaventure, "litteral"),
    #     MRC du Rocher-Percé, "litteral"),
    #     MRC Côte-de-Gaspé, "litteral"),
    #     MRC de la Haute-Gaspésie, "litteral"),
    #     Communauté maritime des Iles
    # ]

    alerts = [
        [
            {"term": "Sylvain Roy",
             "operator": 'litt'},
            {"term": "député",
             "operator": ''}
        ],
        [
            {"term": "Sylvain Roy",
             "operator": 'litt'},
            {"term": "député",
             "operator": ''}
        ],
    ]


    converter = KeywordConvertor(category, creds)
    for alert in listed_alerts:
        print(alert)
        converter.add_alert(alert)

    converter.generate_feeds()

    pickle.dump(converter, open('pickleFiles/converter.pkl', 'wb'))

    # converter = pickle.load(open('pickleFiles/converter.pkl', 'rb'))

    print(converter.full_alerts)
    print(converter.alert_tuples)

    updater = SheetsUpdater(creds['SHEET_ID'], category)
    for alert in converter.alert_tuples:
        updater.addDataPoint([alert[0],alert[1]])
    updater.update()





