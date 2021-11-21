import unittest
from GeoWeather import GeoWeatherService

class GeoWeatherServiceTest(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super(GeoWeatherServiceTest, self).__init__(*args, **kwargs)
        self.ws = GeoWeatherService()
    
    def test_coordinate_retrieval(self):
        data = self.ws._locate_coordinates('Stave Lake, BC, Canada')
        self.assertIsNotNone(data[0])
    
    def test_specific_data_retrieval(self):
        data = self.ws.retrieve_data('2005-11-13', 'cyvr', 'richmond BC (CYVR)', 'BC', 'Canada')
        self.assertIsNotNone(data[0])
        self.assertIsNotNone(data[1])
        
    def test_specific_data_retrieval2(self):
        data = self.ws.retrieve_data('2019-11-13', 'cync', 'WEMINDJI QC (CYNC)', 'QC', 'Canada')
        self.assertIsNotNone(data[0])
        self.assertIsNotNone(data[1])
    
    def test_approximate_data_retrieval(self):
        data = self.ws.retrieve_data('2018-11-13', 'cylu', 'KANGIQSUALUJJUAQ (GEORGES RIVER) QC', 'QC', 'Canada')
        self.assertIsNotNone(data[0])
        self.assertIsNotNone(data[1])
        
    def test_region_data_retrieval(self):
        data = self.ws.retrieve_data('2021-11-13', 'cyqb', '15NM W QUÉBEC / JEAN LESAGE INTL QC (CYQB)', 'QC', 'Canada')
        self.assertIsNotNone(data[0])
        self.assertIsNotNone(data[1])
        
    def test_multiple_successive_retrivals(self):
        locations = ['Downtown Vancouver', 'Vancouver International Airport', 'Metrotown Mall', 'Richmond', 'Howe Sound', \
            'Whistler Mountain', 'Grouse Mountain', 'Harrison Mills', 'Harrison Lake', 'Abbotsford International']
        
        for location in locations:
            data = self.ws.retrieve_data('2021-11-05', 'cyvr', location, 'BC', 'Canada')
            self.assertIsNotNone(data[0])
            self.assertIsNotNone(data[1])
        
        
if __name__ == '__main__':
    unittest.main()