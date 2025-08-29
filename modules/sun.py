import logging

import ephem
from datetime import datetime, timezone

class SunriseSunset:
    def __init__(self, lat, lon, localtime):
        self.__logger = logging.getLogger(__name__)
        self.__lat = lat
        self.__lon = lon
        self.__localtime = localtime

    def getMessages(self):
        self.__logger.info("Calculating sunrise and sunset...")
        home = ephem.Observer()
        home.date = datetime.now(timezone.utc)
        home.lat = self.__lat
        home.lon = self.__lon

        sun = ephem.Sun()

        sun.compute(home)

        if self.__localtime:
            rising = ephem.localtime(home.next_rising(sun)).strftime("%H:%M")
            setting = ephem.localtime(home.next_setting(sun)).strftime("%H:%M")
            tz = "LT"
        else:
            rising = home.next_rising(sun).datetime().strftime("%H:%M")
            setting = home.next_setting(sun).datetime().strftime("%H:%M")
            tz = "Z"

        self.__logger.info(f"Calculated times: rising, {rising} setting, {setting}")

        return [f"Sunrise: {rising}, Sunset: {setting} {tz}"]