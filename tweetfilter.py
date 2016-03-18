import os
import sys
import json
import unicodedata
from settings import settings
from database import MongoBase

class TweetFilter(object):

    aval_types = [ "user", "tweet"]

    ## Clas constructor
    def __init__(self):
        try:
            self.db = MongoBase(settings['db_addr'])
            self.data_cursor = self.db.get_dataset("user_tweets")
        except Exception:
            print "Problem with databse occured when trying get access to data..."
            sys.exit(1)

    ## Filter method, maches records in tweets jsons
    def filter(self, atr="location", info_type="tweet", validate=True, save=True):

        # Throw value exception if type is not valid
        if not info_type in self.aval_types:
            raise ValueError('Not valid information type...')

        num_mat = 0
        # iterate over tweets
        for tweet in self.data_cursor:
                # Check information type
                if info_type == self.aval_types[0]:
                    res_data = tweet["user"]
                else:
                    res_data = tweet
                if res_data.get(atr):
                    # Remove polish characters if string is unicode
                    if isinstance(res_data[atr], unicode):
                        value = unicodedata.normalize('NFD', res_data[atr]).encode('ascii', 'ignore')
                    else:
                        value = str(res_data[atr])
                    # Increment match counter
                    num_mat = num_mat + 1
                    # If validation set as True
                    if validate and atr == "location" :
                        city = self.validate_location(value)
                        if not city:
                            continue
                        else:
                            tweet["user"]["location"] = city
                    if save:
                        self.db.insert_Tweet(tweet, atr)
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


    def gen_statfile(self, match_num, atr, sfile="statfile.dat"):
        stats = {}
        json_data = {}
        with open(settings["abs_path"] + "/" + sfile, 'a+') as stat_file:
            stats["matches"] = match_num
            stats["percent"] = str((100*match_num*1.0)/self.db.tweet_num) + "%"
            stats["path"] = "/" + atr
            json_data[atr] = stats
            json.dump(json_data, stat_file)

    def rm_statfile(self, sfile="statfile.dat"):
        try:
            os.remove('./' + sfile)
        except:
            pass

def main():
    tw = TweetFilter()
    tw.rm_statfile()
    user = tw.filter(info_type="user")
    geo = tw.filter(atr="geo")
    tw.gen_statfile(user, "user")
    tw.gen_statfile(geo, "geo")



if __name__ == '__main__':
    main()



