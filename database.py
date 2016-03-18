import pymongo
from abc import ABCMeta, abstractmethod

## Database interface, usefull in case
## changing databse
class DataBase(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def insert_Tweet(self, tweet_json):
        pass

    @abstractmethod
    def insert_Tweet(self, tweet_json, col):
        pass

    @abstractmethod
    def get_dataset(self, col, find_arg=""):
        pass

## MongoDb object, inherits
## Database and implements methods
class MongoBase(DataBase):

    def __init__(self, addr):
        try:
            # Init Mongo client
            dbcli = pymongo.MongoClient(addr)
            self.__serv_info =  dbcli.server_info()
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print err
            raise
        self.db = dbcli.Tweets
        self.tweet_num = self.db.user_tweets.count()

    ## Insert tweet in MongoDb
    def insert_Tweet(self, tweet_json):
        self.db.user_tweets.insert(tweet_json)

    ## Insert tweet in specified collection
    def insert_Tweet(self, tweet_json, col):
        dbcol = self.db[col]
        if not dbcol.find_one(tweet_json):
            dbcol.insert(tweet_json)



    ## Get cursor to specific data
    def get_dataset(self, col, find_arg=""):
        # Check collection existence
        if col in self.db.collection_names():
            dbcol = self.db[col]
            if not find_arg:
                return dbcol.find()
            else:
                return dbcol.find(find_arg)
        else:
            raise pymongo.errors.CollectionInvalid


