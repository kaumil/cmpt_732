from GeoWeather import GeoWeatherService
from GeoWeatherExceptions import GeoWeatherServiceFailedToLocateException, GeoWeatherServiceFailedToRetrieveException

ws = GeoWeatherService()


try:
    coords, weather_data = ws.retrieve_data('2021-05-05', 'rtwrwerwerewrwerwerwe', 'stavwerwerwerwerewrwerwerwerfsdfsdfsdfe lwerewrwerwerewrwerake', 'sdfsdfdsfsdfwerwerewrwerbc', 'cawerwerwerwerwerewrwerwernada')
except GeoWeatherServiceFailedToLocateException:
    print('failed to locate')
except GeoWeatherServiceFailedToRetrieveException:
    print('failed to get weather')


#print(coords.latitude, coords.longitude, '\n', weather_data)