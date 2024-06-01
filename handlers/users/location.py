from geopy.geocoders import Nominatim
from geopy.distance import geodesic


def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.reverse((latitude, longitude), language="uz")

    location_name = location.address
    return location_name.split(",")

def get_location_name_ru(latitude, longitude):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.reverse((latitude, longitude), language="ru")

    location_name = location.address
    return location_name.split(",")


def calculate_distance(longitude, latitude):
    if float(latitude) == 41.334416 and float(longitude) == 69.214577:
        return "Error"
    else:
        location1 = (41.3334416, 69.214577)
        location2 = (latitude, longitude)
        distance = geodesic(location1, location2).kilometers
        return distance

