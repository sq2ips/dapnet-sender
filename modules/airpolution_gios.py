import logging

import requests

from utils import trim_pl

class AirPolutionGIOS:
    def __init__(self, service_url, sensor_id):
        self.__logger = logging.getLogger(__name__)
        self.__service_url = service_url
        self.__sensor_id = sensor_id
    
    def getMessages(self):
        data = requests.get(self.__service_url + "")

# https://api.gios.gov.pl/pjp-api/rest/station/sensors/732
# https://api.gios.gov.pl/pjp-api/rest/data/getData/4712
# https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/4714