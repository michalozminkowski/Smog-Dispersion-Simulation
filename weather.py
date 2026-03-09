import requests
import os
from datetime import datetime, timedelta

api_key = os.environ.get("OPENWEATHER_API_KEY")

def get_wind():
    try:
        data = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={'q': 'Poznań,PL', 'appid': api_key, 'units': 'metric'},
            timeout=3
        ).json()

        # daty za 3 i 4 dni
        target1 = (datetime.now() + timedelta(days=3)).date()
        target2 = (datetime.now() + timedelta(days=4)).date()

        def convert(wind):
            speed = min(wind['speed'] * 3.6 / 50, 1.0)
            deg = wind.get('deg', 225)

            if 337.5 <= deg or deg < 22.5:
                d = (0, -1)  # N
            elif 22.5 <= deg < 67.5:
                d = (1, -1)  # NE
            elif 67.5 <= deg < 112.5:
                d = (1, 0)  # E
            elif 112.5 <= deg < 157.5:
                d = (1, 1)  # SE
            elif 157.5 <= deg < 202.5:
                d = (0, 1)  # S
            elif 202.5 <= deg < 247.5:
                d = (-1, 1)  # SW
            elif 247.5 <= deg < 292.5:
                d = (-1, 0)  # W
            else:
                d = (-1, -1)  # NW

            return {'speed': speed, 'dir_x': d[0], 'dir_y': d[1]}

        # przekonwertuj dane
        day1 = [convert(item['wind']) for item in data['list']
                if datetime.fromtimestamp(item['dt']).date() == target1]
        day2 = [convert(item['wind']) for item in data['list']
                if datetime.fromtimestamp(item['dt']).date() == target2]

        return {
            'Monday': day1 or [{'speed': 0.45, 'dir_x': -1, 'dir_y': 1}],
            'Tuesday': day2 or [{'speed': 0.45, 'dir_x': -1, 'dir_y': 1}]
        }

    except:
        return {
            'Monday': [{'speed': 0.45, 'dir_x': -1, 'dir_y': 1}],
            'Tuesday': [{'speed': 0.45, 'dir_x': -1, 'dir_y': 1}]
        }
print(get_wind())
WIND_DATA = get_wind()