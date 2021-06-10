import pickle
import spacy
from spacy.kb import KnowledgeBase
import extractor
from newspaper import Article
from NLP_module import EntityLinker
import json




if __name__ == '__main__':
    MODEL_DIR = './ModelFiles/'
    MODEL_LANG = 'fr'

    SAMPLE_TEXT = "CECI EST UN TEXTE À PROPOS DE LA VILLE DE MONTRÉAL"
    EXAMPLES = []


    from extractor import Extractor
    # extractor = pickle.load(open('extractor.pickle','rb'))

    # with open('/Users/alex/PycharmProjects/RevueDePresseRegions/JSONFiles/revuedepresse_annotations.json', 'rb') as file:
    #     json_list = list(file)
    #
    # for json_str in json_list:
    #     EXAMPLES.append(json.loads(json_str))


    # nlp = spacy.load(MODEL_DIR +"nlp_model_"+ MODEL_LANG)

    # Initialize new model
    from spacy.pipeline.textcat_multilabel import DEFAULT_MULTI_TEXTCAT_MODEL

    nlp = spacy.load("fr_core_news_md")
    config = {
        "threshold": 0.5,
        "model": DEFAULT_MULTI_TEXTCAT_MODEL,
    }

    textcat = nlp.add_pipe("textcat_multilabel", config=config)

    textcat.add_label("Politique municipale")
    textcat.add_label("Politique provinciale")
    textcat.add_label("Politique fedérale")
    textcat.add_label("Santé")
    textcat.add_label("Infrastructure")
    textcat.add_label("Éducation")
    textcat.add_label("Culture")
    textcat.add_label("Économie")
    textcat.add_label("Faits divers")


    doc = nlp(SAMPLE_TEXT)


    print(doc)

    nlp.to_disk(MODEL_DIR +"nlp_model_"+ MODEL_LANG)


