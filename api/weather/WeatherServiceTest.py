from WeatherService import WeatherService

def main():
    ws = WeatherService()
    coords = ws._locate_coordinates('Stave Lake, BC, Canada')
    print(coords.latitude, coords.longitude)
    
    wx = ws.get_weather('2020-11-13', 'cyvr', 'richmond', 'BC', 'Canada')
    print(wx)

if __name__ == '__main__':
    main()