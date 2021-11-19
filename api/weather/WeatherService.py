import re
import time

from geopy.geocoders import Nominatim
from datetime import datetime
from meteostat import Point, Daily
from WeatherServiceExceptions import WeatherServiceFailedToLocateException
from WeatherServiceExceptions import WeatherServiceFailedToRetrieveException

API_WAIT_INTERVAL = 0.5
API_APP_DESCRIPTION = 'CADORS: Civil Aviation Safety Research - Simon Fraser University, BC, Canada'

class WeatherService:
    def __init__(self):
        """[Instantiates a WeatherService object]
        """        
        
        """ Uses OpenMaps Nominatim API
            Limitation: 60 calls per minute
        """    
        self.geolocator = Nominatim(user_agent=API_APP_DESCRIPTION)
        
        """ This regular expression removes all extraneous information in parantheses
            Example: Vancouver International  (CYVR) => Vancouver International
        """ 
        self.parantheses_pattern = re.compile(r'\([^)]*\)')
        
        """ This regular expression removes the province as it is already a field
            Example: Vancouver International BC => Vancouver International
        """ 
        self.province_pattern = re.compile(r'([A-Z]{2})')

    def get_weather(self, date, aerodrome_id, occurence_location, province, country):
        """[Returns a weather dataframe relating to the date and location of the occurence]

        Args:
            date ([string]): [date in YYYY-MM-DD format]
            aerodrome_id ([string]): [4-letter ICAO identifier, e.g. CYVR]
            occurence_location ([string]): [General description of the occurence location]
            province ([string]): [2-letter province code, e.g. BC]
            country ([string]): [Full country name, e.g. Canada]

        Raises:
            WeatherServiceFailedToLocateException: [when the location cannot be matched]
            WeatherServiceFailedToRetrieveException: [when there is no weather information available near this coordinate]

        Returns:
            [Weather]: [Dataframe with  the following weather attributes]
            tavg: average temperature in C
            tmin: minimum temperature in C
            tmax: maximum temperature in C
            prcp: amount of precepitation in mm
            snow: snow depth in mm
            wdir: average wind direction in degrees
            wspd: average wind speed in kph
            wpgt: peak wind gust speed in kph
            pres: average sea-level pressure in hPa
            tsun: total daily sunshine in minutes
        """        
        
        # Clean the location string, remove province, airport code
        occurence_location = self.parantheses_pattern.sub('', occurence_location)
        occurence_location = self.province_pattern.sub('', occurence_location)
        query_string = occurence_location + ', ' + province + ', ' + country
        
        coordinates = self._locate_coordinates(query_string)    
        
        # If the address string is too specific, use the airport as an approximation
        if not coordinates:
            time.sleep(2 * API_WAIT_INTERVAL)
            coordinates = self._locate_coordinates(aerodrome_id)
        
        if not coordinates:
            raise WeatherServiceFailedToLocateException(date + query_string)
        
        date_time = datetime.strptime(date, '%Y-%m-%d')
        point = Point(coordinates.latitude, coordinates.longitude)
        weather = Daily(point, date_time, date_time)
        
        weather_data = weather.fetch()
        
        if weather_data.empty:
            raise WeatherServiceFailedToRetrieveException(date + query_string)
        
        time.sleep(API_WAIT_INTERVAL)
        
        return weather_data

    # consider also using mapbox or photon
    def _locate_coordinates(self, location):
        """[Given a location string, attempt to return an object with the coodinates]

        Args:
            location ([string]): [a full location string: e.g. Stave Lake, BC, Canada]

        Returns:
            [Object]: [Object with Latitude and Longitude, or None if it cannot be found]
        """        
        return self.geolocator.geocode(location)
