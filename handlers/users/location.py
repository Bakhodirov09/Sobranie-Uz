from geopy.geocoders import Nominatim


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

