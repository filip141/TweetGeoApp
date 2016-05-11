import json
import time
from settings import settings
from geopy.geocoders import Nominatim

cities = []
geolocator = Nominatim()

with open(settings["cities_path"], 'r') as citi_file:
    for line in citi_file:
        cities.append(line[:-1])
city_coords = []
for city in cities:
    if len(city) > 2:
        while True:
            try:
                coords = geolocator.geocode(city)
                print city, "OK"
                city_coords.append((city, (coords.latitude, coords.longitude)))
                break
            except Exception:
                print "Timeout Error, Waiting"
                time.sleep(60 * 5)
print "All Cities saved"
city_coords = dict(city_coords)
with open("../data/coords.json", 'w') as coords_file:
    json.dump(city_coords, coords_file)