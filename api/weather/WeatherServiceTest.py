from WeatherService import WeatherService

def main():
    ws = WeatherService()
    coords = ws._locate_coordinates('Stave Lake, BC, Canada')
    print(coords.latitude, coords.longitude)

if __name__ == '__main__':
    main()