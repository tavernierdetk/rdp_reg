import pickle
import spacy
from spacy.kb import KnowledgeBase
import extractor
from newspaper import Article
from NLP_module import EntityLinker
import json
import requests




if __name__ == '__main__':


    sample = "Face à une flambée des cas de COVID-19 dans la région de Québec, le cabinet du premier ministre François Legault annonce la tenue d’une nouvelle conférence de presse, jeudi, à 17 h.\n\nLes détails de l’annonce n’ont pas été précisés, mais cette plage horaire est d’ordinaire réservée aux restrictions sanitaires. La forte hausse du nombre de cas de COVID-19 à Québec et dans Chaudière-Appalaches laisse entrevoir un prolongement des mesures spéciales d’urgence.\n\nPour la région de la Capitale-Nationale seulement, le bilan de mercredi fait état de 400 à 500 nouveaux cas, selon nos informations. La veille, ce chiffre était de 250.\n\nLa semaine dernière, le gouvernement avait ordonné un confinement strict dans ces régions, ce qui inclut un couvre-feu à 20 h, la fermeture des commerces non essentiels et l’enseignement à distance pour tous les élèves. Ce resserrement devait initialement durer jusqu’au 12 avril.\n\nLors du plus récent point de presse, mardi dernier, le directeur national de santé publique, le Dr Horacio Arruda avait déclaré que la possibilité de voir ces régions repasser en zone orange relevait du « miracle »."
    res = requests.post('http://127.0.0.1:8000/entity_linker', json=sample)


    print(res)
    entities = json.loads(res.content)
    print(entities['actors'])