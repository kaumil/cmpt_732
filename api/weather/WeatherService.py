from geopy.geocoders import Nominatim
from datetime import datetime
from meteostat import Point, Daily
from WeatherServiceExceptions import WeatherServiceFailedToLocateException

APP_DESCRIPTION = 'CADORS: Civil Aviation Safety Research - Simon Fraser University, BC, Canada'

class WeatherService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent=APP_DESCRIPTION)

    def get_weather(self, date, aerodrome_id, occurence_location, province, country):
        address = occurence_location + ', ' + province + ', ' + country
        coordinates = self._locate_coordinates(address)
        
        # If occurence location is not sensitive enough, default to aerodrome location
        if not coordinates:
            coordinates = self._locate_coordinates(aerodrome_id + ', ' + country)
            
        if not coordinates:
            raise WeatherServiceFailedToLocateException(date + address)
        
        point = Point(coordinates.latitude, coordinates.longitude)
        weather = Daily(point, date, date)
        
        return weather.fetch()

    def _locate_coordinates(self, location):
        return self.geolocator.geocode(location)
