import os
import json
import sys
import csv
import numpy as np
from collections import Counter
from geopy.geocoders import Nominatim
import unicodedata
from database import MongoBase
from settings import settings
import plotly.plotly as py
import plotly.graph_objs as go
py.sign_in('obama', 'sgseve5yrj')
import pandas as pd


# connect to the database
try:
   db = MongoBase(settings['db_addr'])
   data_cursor = db.get_dataset("location")
except Exception:
   print "Problem with databse occured when trying get access to data..."
   sys.exit(1);

loc_counter = Counter()

# #get cities and write them to the file
for location in data_cursor:
    loclist = [location["user"]["location"].lower()]
    loc_counter.update(loclist)

# count number of city occureences and write to .csv file with coordinates
with open("data.csv", 'w') as f:
    fieldnames = ['counter', 'lat', 'lon', 'city']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for city,counter in  loc_counter.most_common(3000):
        try:
            geolocator = Nominatim()
            location = geolocator.geocode(city)
        except Exception:
            print "Couldn't find location"
            continue
        city = city.strip("\n")
        writer.writerow({'counter': counter, 'lat': location.latitude, 'lon': location.longitude, 'city': city })

df = pd.read_csv('data.csv')
df.head()

#display data on bar graph
data2 = [
    go.Bar(
        x=df['city'],
        y=df['counter']
    )
]
plot_url = py.plot(data2, filename='basic-bar')

#display data on map
df['text'] = df['city'] + ' , ' + df['counter'].astype(str) +' Twitts'
limits = [(0,2),(3,10),(11,20),(21,50)]
colors = ["rgb(0,116,217)","rgb(255,65,54)","rgb(133,20,75)","rgb(255,133,27)"]
cities = []

for i in range(len(limits)):
    lim = limits[i]
    df_sub = df[lim[0]:lim[1]]
    city = dict(
        type = 'scattergeo',
        lon = df_sub['lon'],
        lat = df_sub['lat'],
        text = df_sub['text'],
        marker = dict(
            size = df_sub['counter'],
            color = colors[i],
            line = dict(width=0.5, color='rgb(40,40,40)'),
            sizemode = 'area'
        ),
        name = '{0} - {1}'.format(lim[0],lim[1]) )
    cities.append(city)

layout = dict(
        title = 'Twitter users in Poland',
        showlegend = True,
        geo = dict(
            resolution = 50,
            scope = 'europe',
            showframe = False,
            showcoastlines = True,
            showland = True,
            landcolor = "rgb(229, 229, 229)",
            countrycolor = "rgb(255, 255, 255)" ,
            coastlinecolor = "rgb(255, 255, 255)",
            projection = dict(
                type = 'Mercator'
            ),
            lonaxis = dict( range= [ 14.0, 25.0 ] ),
            lataxis = dict( range= [ 49.0, 55.0 ] ),
        ),
    )

fig = dict( data=cities, layout=layout )
url = py.plot( fig, validate=False, filename='twitter_Poland' )