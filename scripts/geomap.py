import json
import numpy as np
from surf import surf


class GeoMap(object):

    dlat = 110.574

    def __init__(self, ulatitude, dlatitude, llongitude, rlongitude, precision=0.3):
        self.precision = precision
        with open("../data/coords.json", 'r') as coords_file:
            coords = json.loads(coords_file.read())
        self.citi_coords = coords
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
        coords_dict = self.citi_coords
        for mcity, value in coords_dict.iteritems():
            # City found
            if mcity == city:
                idx_tuple = self.coords2idx(value[0], value[1])
                # Tuple is not correct index
                if idx_tuple[0] > 0 and idx_tuple[1] > 0:
                    return idx_tuple
        return None

    # Set city position
    def set_position(self, position, votes):
        if self.country_map.shape > position > (0, 0):
            self.country_map[position[0], position[1]] = votes

    # Clean country map
    def clean(self):
        self.country_map = np.zeros(self.country_map.shape)

    # Distance between two points
    @staticmethod
    def distance(point_one, point_two):
        return np.sqrt((point_one[0] - point_two[0])**2 + (point_one[1] - point_two[1])**2)

    def multi_exp(self, cmass, c_coeff, alpha):
        cshape = self.country_map.shape
        x = np.arange(0, cshape[1])
        y = np.arange(0, cshape[1])
        meshx, meshy = np.meshgrid(x, y)
        dist = np.sqrt((meshx - cmass[0])**2 + (meshy - cmass[1])**2)
        exp_surf = c_coeff * dist**-alpha
        surf(exp_surf, x, y)


# if __name__ == '__main__':
#     poland_latitude = (54.83, 49.0)
#     poland_longitude = (14.12, 24.15)
#     gm = GeoMap(poland_latitude[0], poland_latitude[1],
#                               poland_longitude[0], poland_longitude[1], precision=2)
#     gm.multi_exp()

