import logging

import requests

from utils import trim_pl

class RadiationPaa:
    def __init__(self, service_uri, sensor_id):
        self.__logger = logging.getLogger(__name__)
        self.__service_uri = service_uri
        self.__sensor_id = sensor_id

    def getMessages(self):
        self.__logger.info(f"Requesting radioactivity data...")
        sensors_json = requests.get(self.__service_uri).json()

        sensor_data = None
        for sensor in sensors_json["features"]:
            if sensor["properties"]["id"] == self.__sensor_id:
                sensor_data = sensor["properties"]
                self.__logger.info(f"Sensor with id {self.__sensor_id} found, station name: {sensor_data["stacja"]}, value: {sensor_data["tip_value"]}")
        
        if sensor_data == None:
            raise ValueError(f"No sensor with id {self.__sensor_id} found")

        return [f'Radiation level ({trim_pl(sensor_data["stacja"])}, {sensor_data["tip_date"][11:]}): {sensor_data["tip_value"].replace("µ", "u")}']
