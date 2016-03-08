import os
import json
import unicodedata
from settings import settings

class TweetFilter(object):

    __TWEETPREF = "./Tweets/tweet"
    __TWEETSUFF = ".txt"
    aval_types = [ "user", "tweet"]


    ## Clas constructor
    def __init__(self):
        tweet_list = os.listdir(settings["file_path"])
        tweet_list = [ int(x[5:-4]) for x in tweet_list ]
        if tweet_list:
            self.tweet_num = max(tweet_list)
        else:
            self.tweet_num = 0


    ## Filter method, maches records in tweets json files and returns
    ## list of tweets found and number of mached records
    ## Method need to specify type of required information, it could be "user" account
    ## information or single tweet info 
    def filter(self, atr="location", info_type="tweet", validate=True):

        # Throw value exception if type is not valid
        if not info_type in self.aval_types:
            raise ValueError('Not valid information type...')

        num_mat = 0
        # iterate over tweets
        for number in range(0, self.tweet_num):
            with open(self.__TWEETPREF + str(number) + self.__TWEETSUFF) as json_file:
                json_data = json.load(json_file)
                if info_type == self.aval_types[0]:
                    json_data = json_data["user"]
                if json_data.get(atr):
                    value = str(unicodedata.normalize('NFD', json_data[atr]).encode('ascii', 'ignore'))
                    # If validation set as True
                    if validate and atr == "location" :
                        if not self.validate_location(value):
                            continue
                    num_mat = num_mat + 1
                    print "matches: " + str(num_mat) + " value: " + value
                    
        return num_mat

    ## Method to verify location status
    def validate_location(self, pcity):
        pcity = pcity.lower()
        with open(settings["cities_path"], 'r') as citi_file:
            for line in citi_file:
                if line[:-1].lower() in pcity:
                    return line[:-1]
        return None







def main():
    tw = TweetFilter()
    print tw.filter(info_type="user")
    # print tw.filter(atr="geo")
    # print tw.validate_location("wroclaw")





if __name__ == '__main__':
    main()



