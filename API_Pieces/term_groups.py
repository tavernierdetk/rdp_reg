import pickle
import credentials

if __name__ == '__main__':
    creds = credentials.get_creds()
    filepath = ''
    object = pickle.load(open(filepath, 'rb'))

    #TODO write script

    pickle.dump(object, open(filepath, 'wb'))