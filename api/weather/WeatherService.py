import re

from geopy.geocoders import Nominatim
from datetime import datetime
from meteostat import Point, Daily
from WeatherServiceExceptions import WeatherServiceFailedToLocateException

APP_DESCRIPTION = 'CADORS: Civil Aviation Safety Research - Simon Fraser University, BC, Canada'

class WeatherService:
    def __init__(self):
        """ Uses OpenMaps Nominatim API
            Limitation: 60 calls per minute
        """    
        self.geolocator = Nominatim(user_agent=APP_DESCRIPTION)
        
        """ This regular expression removes all extraneous information in parantheses
            Example: Vancouver International  (CYVR) => Vancouver International
        """ 
        self.parantheses_pattern = re.compile(r'\([^)]*\)')
        
        """ This regular expression removes the province as it is already a field
            Example: Vancouver International BC => Vancouver International
        """ 
        self.province_pattern = re.compile(r'([A-Z]{2})')

    def get_weather(self, date, aerodrome_id, occurence_location, province, country):
        
        # Clean the location string, remove province, airport code
        occurence_location = self.parantheses_pattern.sub('', occurence_location)
        occurence_location = self.province_pattern.sub('', occurence_location)

        address = occurence_location + ', ' + province + ', ' + country
        coordinates = self._locate_coordinates(address)    
        
        # If occurence address string is too specific, try the location only
        if not coordinates:
            coordinates = self._locate_coordinates(occurence_location)
        
        # If that doesn't work, try the airport location only as an approximation
        if not coordinates:
            coordinates = self._locate_coordinates(aerodrome_id + ', ' + country)
        
        if not coordinates:
            raise WeatherServiceFailedToLocateException(date + address)
        
        date_time = datetime.strptime(date, '%Y-%m-%d')
        point = Point(coordinates.latitude, coordinates.longitude)
        weather = Daily(point, date_time, date_time)
        
        return occurence_location #weather.fetch()

    # consider also using mapbox or photon
    def _locate_coordinates(self, location):
        return self.geolocator.geocode(location)
