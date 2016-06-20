#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import numpy as np
from word_stats import CityStats
from word_stats import WordStats
from sklearn.cluster import KMeans
from settings import settings
import warnings


warnings.filterwarnings("ignore")


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
                               for x in line[:-1].split(';')[0].split(',')]
                parameters.append(word_params)
        parameters = np.array(parameters)
        dim2array = zip(parameters[:, 1], parameters[:, 2])
        return dim2array

    def predict(self, params):
        centroid_test = self.kmeans.predict((0.1, 0.1))[0]
        if centroid_test == 1:
            self.word_scope = ['local', 'global']
        return self.word_scope[self.kmeans.predict(params)[0]]


def main():
    wc = WordCluster()
    ws = WordStats(punfile=settings["punfile_name"], stopfile=settings["stopfile_name"])
    info_str = "molo sopot było Gdynia Gdańsk Sopot trójmiasto morze #gdynia opener #darmłodzierzy"
    tweet_words = ws.divide_tweet(unicode(info_str, "utf-8"))
    ct = CityStats(db_addr=settings["db_addr"], punfile=settings["punfile_name"]
                   , stopfile=settings["stopfile_name"])
    words, citi_dict = ct.get_words(stjson_path=settings["statistic_json"])
    local_coords = []
    for word in tweet_words:
        pred = ct.word_prediction_params(word, citi_dict)
        if pred:
            pred_result = wc.predict(pred[0][1:])
            print "Slowo: " + word
            print "Zaklasyfikowane jako : " + pred_result
            print "Z wynikami: " + str(pred[0][1:])
            print "Wspolrzedne: " + str(pred[1])
            print "--------------------------------------------------"
            if pred_result == "local":
                local_coords.append(pred[1])
    if local_coords:
        print "Found local words, Please wait..."
        time.sleep(2)
        local_mean = np.sum(local_coords, axis=0) / len(local_coords)
        ct.geo_map.set_position((local_mean[0], local_mean[1]), 100)
        print "Znalezione kordyntaty to: " + str(ct.geo_map.idx2cords(local_mean))


if __name__ == '__main__':
    main()
