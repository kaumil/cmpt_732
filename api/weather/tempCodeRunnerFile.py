from Weather import WeatherService
from meteostat import Point, Daily
from datetime import datetime

ws = WeatherService()

loc = ws._locate_airport_code('cyvr')

#loc = ws._locate_coordinates('KANGIQSUALUJJUAQ, QC, Canada')

print(loc)

pt = Point(loc.latitude, loc.longitude)

day = datetime.strptime('2015-11-13', '%Y-%m-%d')


wx = Daily(pt, day, day).fetch()

print(wx)