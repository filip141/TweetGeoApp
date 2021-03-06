import os
import json
import sys
import unicodedata
from database import MongoBase
from settings import settings


class TweetFilter(object):
    ''' Separate tweets with geo and correct
    localization inserted to separate
    database collecions '''

    aval_types = ["user", "tweet"]

    # Class constructor
    def __init__(self):
        try:
            self.db = MongoBase(settings['db_addr'])
            self.data_cursor = self.db.get_dataset("user_tweets")
        except Exception:
            print "Problem with databse occured when trying get access to data..."
            sys.exit(1)

    # Filter method, matches records in tweets jsons
    def filter(self, atr="location", info_type="tweet", validate=True, save=True):

        # Throw value exception if type is not valid
        if info_type not in self.aval_types:
            raise ValueError('Not valid information type...')

        num_mat = 0
        # iterate over tweets
        for tweet in self.data_cursor:
            # Check information type
            short_text = unicodedata.normalize('NFD', tweet['text'])\
                .encode('ascii', 'ignore')[:20]
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
                num_mat += 1
                # If validation set as True
                if validate and atr == "location":
                    city = self.validate_location(value)
                    if not city:
                        continue
                    else:
                        tweet["user"]["location"] = city
                if save:
                    self.db.insert_in_col(tweet, atr)
                print "[" + short_text + "...]" + "matches: " + str(num_mat) \
                      + " value: " + value
        return num_mat

    # Method to verify location status
    @staticmethod
    def validate_location(pcity):
        with open(settings["cities_path"], 'r') as citi_file:
            for line in citi_file:
                if line[:-1] in pcity:
                    return line[:-1]
        return None

    def gen_statfile(self, match_num, atr, sfile=settings["statfile_name"]):
        stats = {}
        json_data = {}
        with open(sfile, 'a+') as stat_file:
            stats["matches"] = match_num
            stats["percent"] = str((100 * match_num * 1.0) / self.db.tweet_num) + "%"
            stats["path"] = "/" + atr
            json_data[atr] = stats
            json.dump(json_data, stat_file)

    @staticmethod
    def rm_statfile(sfile=settings["statfile_name"]):
        try:
            os.remove(sfile)
        except OSError:
            print "Error occurred while removing statefile"
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
