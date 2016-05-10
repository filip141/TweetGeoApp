import json
from settings import settings
from geopy.geocoders import Nominatim

cities = []
geolocator = Nominatim()

with open(settings["cities_path"], 'r') as citi_file:
    for line in citi_file:
        cities.append(line[:-1])
city_coords = []
cities = cities[:3]
for city in cities:
    coords = geolocator.geocode(city)
    city_coords.append((city, (coords.latitude, coords.longitude)))
    print city
city_coords = dict(city_coords)
with open("../data/coords.json", 'w') as coords_file:
    json.dump(city_coords, coords_file)