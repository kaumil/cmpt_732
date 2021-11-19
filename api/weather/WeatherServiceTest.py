from Weather import WeatherService

def main():
    ws = WeatherService()
    
    print('=== COORDS ===')
    coords = ws._locate_coordinates('Stave Lake, BC, Canada')
    print(coords.latitude, coords.longitude, '\n')
    
    print('=== CYVR === ')
    print(ws.retrieve_weather('2005-11-13', 'cyvr', 'richmond BC (CYVR)', 'BC', 'Canada'), '\n')
    
    print('=== WEMINDJI QC (CYNC) === ')
    print(ws.retrieve_weather('2021-11-13', 'cync', 'WEMINDJI QC (CYNC)', 'QC', 'Canada'), '\n')
    
    print('=== KANGIQSUALUJJUAQ (GEORGES RIVER) QC (CYLU) === ')
    print(ws.retrieve_weather('2021-11-13', 'cylu', 'KANGIQSUALUJJUAQ (GEORGES RIVER) QC', 'QC', 'Canada'), '\n')
    
    print('=== 15NM W QUÉBEC / JEAN LESAGE INTL QC (CYQB) === ')
    print(ws.retrieve_weather('2021-11-13', 'cyqb', '15NM W QUÉBEC / JEAN LESAGE INTL QC (CYQB)', 'QC', 'Canada'), '\n')
    
    
if __name__ == '__main__':
    main()