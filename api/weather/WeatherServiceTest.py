from WeatherService import WeatherService
from datetime import datetime

def main():
    ws = WeatherService()
    coords = ws._locate_coordinates('Stave Lake, BC, Canada')
    print(coords.latitude, coords.longitude)
    
    wx = ws.get_weather(datetime(2021, 11, 17), 'cyvr', 'stave lake', 'BC', 'Canada')
    print(wx)

if __name__ == '__main__':
    main()