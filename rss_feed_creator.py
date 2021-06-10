from google_alerts import GoogleAlerts
import credentials

listed_words = ["site:www.radio-canada.ca/nouvelle"]
words_rss_tuple = []

creds = credentials.get_creds()


# Create an instance
ga = GoogleAlerts(creds["GOOGLE_ACCOUNT"], creds["GOOGLE_PASSWORD"])

# # Authenticate your user
ga.authenticate()

# Add a new monitor
for term in listed_words:

    words_rss_tuple.append((term,  ga.create(term, {'delivery': 'RSS', 'language': 'all'})[0]['rss_link']))

print(words_rss_tuple)
