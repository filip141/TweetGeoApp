#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os

ROOTPATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

## Twitter settings
settings = dict(
    consumer_key='ilKfff3MnScncmsvlHBqwx2LC',
    consumer_secret='nzaANk2HIjzOmfSrxvcQqEwH49fWbA5enHB6SruRL6dJ3vueGy',
    access_token='705527560868859904-34pSO4nzBkyYelULqwyi7u3YIT2DIgz',
    access_token_secret='L1VADfcaurQYFLcMA2hFrebxkgM4DDttw6kwEp2YmMmNQ',
    abs_path=ROOTPATH,
    db_addr='oxygen.engine.kdm.wcss.pl:27017',
    cities_path=ROOTPATH + "/data/cities.txt",
    langfile_name=ROOTPATH + "/data/lang.txt",
    statfile_name=ROOTPATH + "/data/statfile.dat",
    punfile_name=ROOTPATH + "/data/punctation.txt",
    stopfile_name=ROOTPATH + "/data/stopwords.txt",
    statistic_json=ROOTPATH + "/data/words_statistic.json",
    START=0,
    END=399
    )

