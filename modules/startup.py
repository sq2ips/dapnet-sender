import logging

from datetime import datetime

class Startup:
    def __init__(self, startup_message):
        self.__logger = logging.getLogger(__name__)
        self.__startup_message = startup_message
    
    def getMessages(self):
        startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return [self.__startup_message(startup_time)]