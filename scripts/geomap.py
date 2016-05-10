import numpy as np
from geopy.geocoders import Nominatim


class GeoMap(object):

    dlat = 110.574

    def __init__(self, ulatitude, dlatitude, llongitude, rlongitude, precision=0.3):
        self.precision = precision
        self.geolocator = Nominatim()
        self.dlatitude = np.array(dlatitude)
        self.llongitude = np.array(llongitude)
        # Calculate kilometers from longitude and latitude
        c_size = self.coords2idx(ulatitude, rlongitude)
        self.country_map = np.zeros(c_size)

    # Convert geo coordinates to array index
    def coords2idx(self, latitude, longitude):
        angle = (latitude + self.dlatitude) / 2
        norm_lati = latitude - self.dlatitude
        norm_long = longitude - self.llongitude
        latt_km = norm_lati * GeoMap.dlat
        dlong = abs(111.320 * np.cos(np.pi * angle / 180))
        long_km = norm_long * dlong
        idx = (int(latt_km / self.precision), int(long_km / self.precision))
        return idx

    # Convert city name to array coords
    def citi2idx(self, city):
        location = self.geolocator.geocode(city)
        return self.coords2idx(location.latitude, location.longitude)

    # Set city position
    def set_position(self, position, votes):
        if position < self.country_map.shape and position > (0, 0):
            self.country_map[position[0], position[1]] = votes

    # Clean country map
    def clean(self):
        self.country_map = np.zeros(self.country_map.shape)



