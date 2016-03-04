import os
import json
import tweepy
from settings import settings


class CustomStreamListener(tweepy.StreamListener):

    def __init__(self):
    	super(CustomStreamListener, self).__init__()
        self.counter = 0

    def on_status(self, status):
    	fname = '/tweet' + str(self.counter) + '.txt'
    	print status.text
        with open(settings["file_path"] + fname, 'w') as json_file:
    		json.dump(status._json, json_file)
    	self.counter = self.counter + 1

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


class Tweego(object):

	## Tweego construcotr
	def __init__(self):

		## Check tweets dir
		try:
			os.stat(settings["file_path"])
		except:
			os.mkdir(settings["file_path"])

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
	def read_lang(self, fname='lang.txt'):
		lang_file = open(fname, 'r')
		lang_list = lang_file.read().split(",")
		lang_list = [ x.replace(" ", "") for x in lang_list ]
		return lang_list


def main():
	tw = Tweego()
	tw.findTweetsIn()




if __name__ == '__main__':
    main()








