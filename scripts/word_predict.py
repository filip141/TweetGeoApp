#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from word_stats import CityStats
from word_stats import WordStats
from sklearn.cluster import KMeans
from settings import settings


class WordCluster(object):

    def __init__(self):
        self.train_list = self.build_training_set()
        # Initialize Kmeans
        self.kmeans = KMeans(n_clusters=2)
        self.kmeans.fit(self.train_list)
        self.centroids = self.kmeans.cluster_centers_
        self.labels = self.kmeans.labels_
        self.word_scope = ['global', 'local']

    @staticmethod
    def build_training_set():
        parameters = []
        with open('../data/local_params.dat', 'r') as fp:
            for line in fp:
                word_params = [float(x.replace(" ", "").replace(")", "").replace("(", ""))
                               for x in line[:-1].split(',')]
                parameters.append(word_params)
        parameters = np.array(parameters)
        dim2array = zip(parameters[:, 1], parameters[:, 2])
        return dim2array

    def predict(self, params):
        return self.word_scope[self.kmeans.predict(params)[0]]


def main():
    wc = WordCluster()
    ws = WordStats(punfile=settings["punfile_name"], stopfile=settings["stopfile_name"])
    str = "Pyrkon mega impreza w Poznań :)"
    tweet_words = ws.divide_tweet(unicode(str, "utf-8"))
    ct = CityStats(db_addr=settings["db_addr"], punfile=settings["punfile_name"]
                   , stopfile=settings["stopfile_name"])
    words, citi_dict = ct.get_words(stjson_path=settings["statistic_json"])
    for word in tweet_words:
        pred = ct.word_prediction_params(word, citi_dict)
        if pred:
            print wc.predict(pred[1:]), word

if __name__ == '__main__':
    main()
