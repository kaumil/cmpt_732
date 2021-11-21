import re
import time

from geopy.geocoders import Photon, Nominatim
from datetime import datetime
from meteostat import Point, Daily
from GeoWeatherExceptions import GeoWeatherServiceFailedToLocateException
from GeoWeatherExceptions import GeoWeatherServiceFailedToRetrieveException

API_WAIT_INTERVAL = 0.75
API_APP_DESCRIPTION = 'CADORS: Civil Aviation Safety Research - Simon Fraser University, BC, Canada'

class GeoWeatherService:
    """[A  class to provide a Weather Service to locate and return
       weather information for a given location, date and time.]
    """
        
    def __init__(self):
        """[Instantiates a WeatherService object]
        """        
        
        """ This geocoder uses OpenMaps Photon API
            Limitation: No limitation on API Calls
        """    
        self.primary_geolocator = Photon(user_agent=API_APP_DESCRIPTION)
        
        """ This geocoder uses OpenMaps Nominatim API
            Limitation: 60 calls per minute
        """    
        self.secondary_geolocator = Nominatim(user_agent=API_APP_DESCRIPTION)
        
        """ This regular expression removes all extraneous information in parantheses
            It use used by the remove_province_code() function
        """ 
        self.parantheses_pattern = re.compile(r'\([^)]*\)')


    def retrieve_data(self, date, aerodrome_id, occurence_location, province, country):
        """[Returns a location and weather object based on the date and location of the occurence
            Note: this method can be used in parallel with no sleep time in between calls]

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
            ([Location]: [Location object with latitude and longitude fields],
            [Weather]: [Dataframe with the following weather attributes])
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
        occurence_location = self._remove_aerodrome_code(occurence_location)
        occurence_location = self._remove_province_code(occurence_location)
        occurence_location = occurence_location.strip()
        query_string = occurence_location + ', ' + province + ', ' + country
        
        date_time = datetime.strptime(date, '%Y-%m-%d')
        exact_coordinates = self._locate_coordinates(query_string)    
        
        # Try the exact coordinates. If the exact coordinates cannot be located,
        # or the weather cannot be loaded for that location, try the airport location
        # if nothing else works, try searching weather by province and country only
        
        if exact_coordinates:
            point = Point(exact_coordinates.latitude, exact_coordinates.longitude)
            weather = Daily(point, date_time, date_time).fetch()
            
            if weather.empty:
                approximate_coordinates = self._locate_coordinates_alternate(aerodrome_id)
                
                if not approximate_coordinates:
                    region_coordinates = self._locate_coordinates_alternate('Downtown ' + province + ', ' + country)
                   
                    if not region_coordinates:
                        raise GeoWeatherServiceFailedToLocateException(province + country)
                
                    point = Point(region_coordinates.latitude, region_coordinates.longitude)
                    weather = Daily(point, date_time, date_time).fetch()
                
                else:   
                    point = Point(approximate_coordinates.latitude, approximate_coordinates.longitude)
                    weather = Daily(point, date_time, date_time).fetch()
                    
                    if weather.empty:
                        region_coordinates = self._locate_coordinates_alternate('Downtown ' + province + ', ' + country)
                   
                        if not region_coordinates:
                            raise GeoWeatherServiceFailedToLocateException(province + country)
                    
                        point = Point(region_coordinates.latitude, region_coordinates.longitude)
                        weather = Daily(point, date_time, date_time).fetch()
        
        else:
                approximate_coordinates = self._locate_coordinates_alternate(aerodrome_id)
            
                if not approximate_coordinates:
                    region_coordinates = self._locate_coordinates_alternate('Downtown ' + province + ', ' + country)
                   
                    if not region_coordinates:
                        raise GeoWeatherServiceFailedToLocateException(province + country)
                
                    point = Point(region_coordinates.latitude, region_coordinates.longitude)
                    weather = Daily(point, date_time, date_time).fetch()
                
                else:   
                    point = Point(approximate_coordinates.latitude, approximate_coordinates.longitude)
                    weather = Daily(point, date_time, date_time).fetch()
                    
                    if weather.empty:
                        region_coordinates = self._locate_coordinates_alternate('Downtown ' + province + ', ' + country)
                   
                        if not region_coordinates:
                            raise GeoWeatherServiceFailedToLocateException(province + country)
                    
                        point = Point(region_coordinates.latitude, region_coordinates.longitude)
                        weather = Daily(point, date_time, date_time).fetch()
            
        # If weather is still empty after primary, secondary, and tertiary searches, throw an exception
        if weather.empty:
            raise GeoWeatherServiceFailedToRetrieveException('Weather primary and secondary and provincial search failed', aerodrome_id, query_string)


        # Return the most specific coordinates as the first value of the tuple,
        # Regardless of whether or not weather was available at this location
        
        location = exact_coordinates 
        
        if not location:
            location = approximate_coordinates
            
        if not location:
            location = region_coordinates
            
        if not location:
            raise GeoWeatherServiceFailedToLocateException(query_string)

        return (location, weather)


    def _locate_coordinates(self, location):
        """[Given a location string, attempt to return an object with the coodinates
            Note: this can be called in parallel, no API request limit is specified]

        Args:
            location ([string]): [a full location string: e.g. Stave Lake, BC, Canada]

        Returns:
            [Location]: [Object with Latitude and Longitude, or None if it cannot be found]
        """
        
        coordinates = self.primary_geolocator.geocode(location)
        
        return coordinates


    def _locate_coordinates_alternate(self, location):
        """[Given a location string, attempt to return an object with the coodinates
            Note: this method will cause a delay of 1s due to API limitation of 60 requests/min]

        Args:
            location ([string]): [a full location string: e.g. Stave Lake, BC, Canada]

        Returns:
            [Location]: [Object with Latitude and Longitude, or None if it cannot be found]
        """
        
        coordinates = self.secondary_geolocator.geocode(location)
        time.sleep(API_WAIT_INTERVAL)
        
        return coordinates


    def _remove_aerodrome_code(self, location):
        """[Removes the aerodrome code from a location string
           Example: Vancouver BC (CYVR) => Vancouver BC]

        Args:
            location ([string]): [full location string]

        Returns:
            [string]: [location with province code removed]
        """        
        
        return self.parantheses_pattern.sub('', location)


    def _remove_province_code(self, location):
        """[Removes the province code from a location string
            Example: Vancouver BC (CYVR) => Vancouver (CYVR)]

        Args:
            location ([string]): [full location string]

        Returns:
            [string]: [location with province code removed]
        """
                
        self.codes = ['NL', 'PE', 'NS', 'NB', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'YT', 'NT', 'NU']
    
        for code in self.codes:
            location = location.replace(code, '')
            
        return location
