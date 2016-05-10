import re
import ast
import json
import numpy as np
import unicodedata
from geomap import GeoMap
from database import MongoBase
from settings import settings
from collections import Counter
from surf import surf

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)'  # anything else
]


class WordTokenizer(object):
    '''
        WordTokenizer divides each string into isolated
        words, this operation is performed using python
        Regular Expression
    '''

    def __init__(self):
        self.tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
        self.emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)
        self.undef_re = re.compile(r'^' + regex_str[-1] + '$', re.VERBOSE | re.IGNORECASE)
        self.men_re = re.compile(r'^' + regex_str[2] + '$', re.VERBOSE | re.IGNORECASE)
        self.url_re = re.compile(r'(' + '|'.join([regex_str[1], regex_str[4]]) + ')',
                                 re.VERBOSE | re.IGNORECASE)

    def tokenize(self, word):
        return self.tokens_re.findall(word)

    def preprocess(self, s, lowercase=False, words_only=False):
        tokens = self.tokenize(s)
        if words_only:
            tokens = [token
                      for token in tokens
                      if not self.emoticon_re.search(token)
                      and not self.url_re.search(token)
                      and not self.undef_re.search(token)
                      and not self.men_re.search(token)
                      ]
        # Lowercase option for words, not emoticon
        if lowercase:
            tokens = [token if self.emoticon_re.search(token) else token.lower() for token in tokens]
        return tokens


class WordStats(object):
    def __init__(self, punfile="punctation.txt", stopfile="stopwords.txt"):
        self.tokenizer = WordTokenizer()
        self.__punfile = punfile
        self.__stopfile = stopfile
        # Load list of punctation characters from file
        with open(self.__punfile) as punf:
            self.punctation = ast.literal_eval(punf.read())
        # Load list of stop words characters from file
        with open(self.__stopfile) as stopf:
            stop = ast.literal_eval(stopf.read())
            self.stop = [unicodedata.normalize('NFD', word).encode('ascii', 'ignore')
                         for word in stop
                         ]

    # Counting word occurrence in tweets
    def word_counter(self, json_base):
        tweets_counter = Counter()
        stop = self.stop + self.punctation + ["rt"]
        for json in json_base:
            json_text = unicodedata.normalize('NFD', json.get("text")).encode('ascii', 'ignore')
            str_words = self.tokenizer.preprocess(json_text, lowercase=True,
                                                  words_only=True)
            str_words = [term for term in str_words if term not in stop]
            tweets_counter.update(str_words)
        return tweets_counter


class CityStats(object):

    poland_latitude = (54.83, 49.0)
    poland_longitude = (14.12, 24.15)

    def __init__(self, db_addr='localhost:27017', punfile="punctation.txt", stopfile="stopwords.txt"):
        self.citi_dict = {}
        self.geo_map = GeoMap(CityStats.poland_latitude[0], CityStats.poland_latitude[1],
                              CityStats.poland_longitude[0], CityStats.poland_longitude[1], precision=2)
        self.mn_db = MongoBase(db_addr)
        self.word_stats = WordStats(punfile=punfile, stopfile=stopfile)

    # get tweets from specified city
    def get_json_list(self, basename, city):
        db_cur = self.mn_db.get_dataset(basename, find_arg={"user.location": city})
        return db_cur

    # Create list of cities base on cities.txt file
    # content
    @staticmethod
    def get_cities_list(city_path):
        cities = []
        with open(city_path, 'r') as citi_file:
            for line in citi_file:
                cities.append(line[:-1])
        return cities

    def get_word_freq(self, city):
        db_cur = self.get_json_list('location', city)
        res = self.word_stats.word_counter(db_cur)
        res = {key: value for (key, value) in res.iteritems() if value > 1}
        return res

    # Count tweet words for specified location
    def count_citywords(self, city_path="cities.txt", stjson_path="words_statistic.json"):
        words_found = []
        cities = self.get_cities_list(city_path)
        for city in cities:
            res = self.get_word_freq(city)
            words_found.append(res)
            print city, res
        citi_dict = dict(zip(cities, words_found))
        with open(stjson_path, 'w') as fp:
            json.dump(citi_dict, fp)
        return citi_dict

    def get_words(self, stjson_path="words_statistic.json"):
        word_list = []
        # Read words dictionary from json file
        with open(stjson_path) as data_file:
            citi_dict = json.load(data_file)
        for city, value in citi_dict.iteritems():
            for word, ntimes in value.iteritems():
                word_list.append(word)
        word_list = set(word_list)
        return word_list, citi_dict

    def local_words(self, stjson="words_statistic.json"):
        # Read word list
        words, citi_dict = self.get_words(stjson_path=stjson)
        # Iterate over words
        for word in words:
            matched_freqs = []
            coords_list = []
            self.geo_map.clean()
            for city, value in citi_dict.iteritems():
                list_element = [ freq for match, freq
                                 in value.iteritems() if match == word
                                 ]
                if list_element:
                    coords = self.geo_map.citi2idx(city)
                    coords_list.append(coords)
                    # self.geo_map.set_position(coords, list_element[0][1])
                    matched_freqs.append(list_element[0])
            c_mass = np.sum([(coord[0] * freq, coord[1] * freq)
                             for coord, freq in zip(coords_list, matched_freqs)],
                            axis=0)
            c_mass /= np.sum(matched_freqs, axis=0)
            print c_mass





def main():
    ct = CityStats(db_addr=settings["db_addr"], punfile=settings["punfile_name"]
                   , stopfile=settings["stopfile_name"])
    # citi_dict = ct.count_citywords(city_path=settings["cities_path"], stjson_path=settings["statistic_json"])
    ct.local_words(stjson=settings["statistic_json"])


if __name__ == '__main__':
    main()
