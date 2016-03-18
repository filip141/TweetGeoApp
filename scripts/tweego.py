import sys

import tweepy
from database import MongoBase
from settings import settings


class CustomStreamListener(tweepy.StreamListener):

    def __init__(self):
        super(CustomStreamListener, self).__init__()
        # Initialize mongo object
        try:
            self.db = MongoBase(settings['db_addr'])
        except Exception:
            print "Problem with database"
            raise

    def on_status(self, status):
        print status.text
        self.db.insert_Tweet(status._json)

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


class Tweego(object):

    ## Tweego construcotr
    def __init__(self):

        ## User Authentication
        self.auth = tweepy.OAuthHandler(settings["consumer_key"], settings["consumer_secret"])
        self.auth.set_access_token(settings["access_token"], settings["access_token_secret"])

        ## API init
        self.api = tweepy.API(self.auth)


    ## Method helps to find tweets
    ## from specified localization
    def findTweetsIn(self):
        sapi = tweepy.streaming.Stream(self.auth, CustomStreamListener())
        sapi.filter(languages=["pl"], track=self.read_lang()[settings["START"]:settings["END"]])


    ## Read file with common polish words
    def read_lang(self, fname=settings['langfile_name']):
        with open(fname, 'r') as lang_file:
            lang_list = lang_file.read().split(",")
            lang_list = [ x.replace(" ", "") for x in lang_list ]
            return lang_list


def main():
    while True:
        try:
            tw = Tweego()
            tw.findTweetsIn()
        except KeyboardInterrupt:
            ## ctrl + c presset
            print "Stream disconected, Leaving..."
            break
        except Exception:
            ## Connection broken
            print "Connection broken"
            continue




if __name__ == '__main__':
    main()







