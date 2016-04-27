#!/bin/bash
# Sort Tweet Script v1

#  Warning:
#  -------
# This script could erse your database
# It's highly recommended to use this script with
# Cron support

# Export data
export LC_ALL=C

# Find mongo response
MONGO_QUERRY_RESPONSE="$(mongo Tweets --host oxygen.engine.kdm.wcss.pl:27017 --eval "db.user_tweets.count()")"
LOCATION_COUNT="$(echo "${MONGO_QUERRY_RESPONSE}" | tail -n 1)"

# File properties
SCRIPT_PATH="$(pwd)"
TWEETFILTER_PATH="$SCRIPT_PATH/tweetfilter.py"
TWEETNUM="tweetnum.dat"
FILE_PATH="$(python -c "print '/'.join('$SCRIPT_PATH'.split('/')[:-1])+'/data/$TWEETNUM'")"

if [ "$LOCATION_COUNT" -gt "0" ]; then
    if [ -f $FILE_PATH ]; then
        echo "File found"
        OLD_TWEETNUM="$(cat "$FILE_PATH")"
        if [ "$LOCATION_COUNT" -eq "$OLD_TWEETNUM" ]; then
            echo "Nothing changed ! "
            exit 1
        fi
    else
        echo "File not found!, creating new file"
        touch $FILE_PATH
    fi
fi

# Start script
mongo Tweets --host oxygen.engine.kdm.wcss.pl:27017 --eval "db.location.drop()"
python $TWEETFILTER_PATH > /dev/null
echo "$LOCATION_COUNT" | tee $FILE_PATH > /dev/null



