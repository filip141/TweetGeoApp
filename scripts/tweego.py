import sys
import time
import tweepy
import threading
from database import MongoBase
from settings import settings


class FriendsGetter(threading.Thread):

    '''Object execute breadth-first search
       acquiring hist firends and his followers
        tweets'''

    def __init__(self, api, lock):
        super(FriendsGetter, self).__init__()
        self.api = api
        self.lock = lock

    ## Set database
    def set_db(self, db):
        self.db = db

    ## Store json in updated database
    def store(self, status):
        self.db.insert_Tweet(status)

    ## Find current user
    def peek_at_user(self):
        with self.lock:
            user = CustomStreamListener.user_name
        return user

    ## Collect user friends and followers
    def get_friends_tweets(self, user_name):
        ## Process user friends
        for friend in tweepy.Cursor(self.api.friends, screen_name=user_name).items():
            friend_stuff = self.api.user_timeline(
                    screen_name = friend.screen_name,
                    count = 200,
                    include_rts = True
            )
            for user_status in friend_stuff:
                if user_status.lang == "pl":
                    self.store(user_status._json)

        ## Process user followers
        for follower in tweepy.Cursor( self.api.followers, screen_name=user_name ).items():
            follower_stuff = self.api.user_timeline(
                    screen_name = follower.screen_name,
                    count = 200,
                    include_rts = True
            )
            for user_status in follower_stuff:
                if user_status.lang == "pl":
                    self.store(user_status._json)
    def run(self):
        while True:
            user = self.peek_at_user()
            try:
                self.get_friends_tweets(user)
            except tweepy.TweepError:
                time.sleep(15*60)
                print "------------------\
                ---Time to Find Your Friends :D---\
                ---------------- "


class CustomStreamListener(tweepy.StreamListener):

    user_name = None

    def __init__(self, api, db_addr='localhost:27017'):
        super(CustomStreamListener, self).__init__()
        # Initialize mongo object
        try:
            self.db = MongoBase(db_addr)
        except Exception:
            print "Problem with database"
            raise

        ## Friends Get object
        self.lock = threading.Lock()
        self.friends_get = FriendsGetter(api, self.lock)
        self.friends_get.set_db(self.db)
        self.friends_get.start()

    def on_status(self, status):
        print status.text
        with self.lock:
            CustomStreamListener.user_name = status.user.screen_name
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
        sapi = tweepy.streaming.Stream(self.auth, CustomStreamListener(self.api, db_addr=settings['db_addr']))
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







