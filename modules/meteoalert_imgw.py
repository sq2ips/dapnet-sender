import logging

import requests

from utils import trim_pl

class MeteoalertIMGW:
    def __init__(self, service_url, city_ids, hydro_ids, service_url_baltic, baltic_region, no_warns_text):
        self.__logger = logging.getLogger(__name__)
        self.__service_url = service_url
        self.__city_ids = city_ids
        self.__hydro_ids = hydro_ids
        self.__service_url_baltic = service_url_baltic
        self.__baltic_region = baltic_region
        self.__no_warns_text = no_warns_text

    def getInternalIds(self, alerts, komets):
        id_alerts = []
        id_komets = []

        for id in self.__city_ids:
            if id in alerts["teryt"]:  # Alerty
                for i in alerts["teryt"][id]:
                    id_alerts.append(i)
            if id in komets["teryt"]:  # Komunikaty
                for i in komets["teryt"][id]:
                    id_komets.append(i)
        return id_alerts, id_komets

    def processKomets(self, id_komets, komets, warnings_used):
        messages = []
        for i in id_komets:
            komet = komets["komets"][i]
            code = komet["Phenomenon"][0]["Code"]
            if code in warnings_used:
                self.__logger.info("Warning duplicate: " + kod)
            else:
                warnings_used.append(code)
                messages.append(f'IMGW Info: {trim_pl(komet["Phenomenon"][0]["Name"])} do: {komet["ValidTo"][5:]} LT')

        return messages

    def processAlerts(self, id_alerts, alerts, warnings_used):
        messages = []
        for i in id_alerts:
            alert = alerts["warnings"][i]
            code = alert["PhenomenonCode"]
            if code in warnings_used:
                self.__logger.warning("Warning duplicate: " + kod)
            else:
                warnings_used.append(code)
                messages.append(f'IMGW Alert: {trim_pl(alert["PhenomenonName"])}/{alert["Level"]} od {alert["ValidFrom"][5:]} do {alert["ValidTo"][5:]} LT')

        return messages

    def processHydro(self, hydro_ids, alerts_hydro):
        hydro_used = []
        messages = []
        for alert_hydro in alerts_hydro["warnings"]:
            for zlewnia in alert_hydro["Zlewnie"]:
                if zlewnia["Code"] in hydro_ids:
                    warn_hydro = alert_hydro["WarnHydro"]
                    code = warn_hydro["Phenomena"]
                    if code in hydro_used:
                        self.__logger.warning("Warning duplicate: " + kod)
                    else:
                        hydro_used.append(code)
                        if code in ["GWSW", "W_PSO", "W_PSA"]:
                            messages.append(f'IMGW Hydro: Wezbranie/{warn_hydro["Level"]} od {warn_hydro["ValidFrom"][5:]} do {warn_hydro["ValidTo"][5:]} LT')
                        elif code == "SH":
                            messages.append(f'IMGW Hydro: Susza Hydrologiczna of {warn_hydro["ValidFrom"][5:]} LT do odwolania')
                        else:
                            self.__logger.warning(f"Unknown code {code}")

        return messages
    
    def processBaltic(self, baltic):
        valid_text = baltic["validity"].split() # format: Ważność od 06:00 UTC 29.08.2025 do 18:00 UTC 29.08.2025
        valid_time = valid_text[6]
        valid_date = valid_text[8].split('.')
        valid = f"{valid_date[1]}-{valid_date[0]} {valid_time} Z"

        alert_level = baltic["regions"][f"{self.__baltic_region} BALTIC"]["alert_level"]

        if alert_level == "0": # no warnings
            return []
        elif alert_level == "1": # silny wiatr
            alert_text = "Silny wiatr"
        elif alert_level == "2":
            alert_text = "Sztorm"
        elif alert_level == "3":
            alert_text = "Silny sztorm"
        elif alert_level == "4":
            alert_text = "Silny wiatr, huraganowe porywy"
        else:
            self.__logger.error(f"Unknown warning level for Baltic: {alert_level}")
            return []
        
        return [f"IMGW Baltyk: {alert_text}, do {valid}"]
    
    def getMessages(self):

        uri_komets = self.__service_url + "osmet/latest/komet-teryt"
        uri_alerts = self.__service_url + "osmet/latest/osmet-teryt"
        uri_alerts_hydro = self.__service_url + "warnhydro/latest/warn"

        self.__logger.info("Requesting live meteo warnings...")
        komets = requests.get(uri_komets).json() # komunikaty
        self.__logger.info("Requesting meteo warnings...")
        alerts = requests.get(uri_alerts).json() # alerty
        self.__logger.info("Requesting hydro warnings...")
        alerts_hydro = requests.get(uri_alerts_hydro).json() # alerty hydro


        self.__logger.info("Getting internal IDs...")
        id_alerts, id_komets = self.getInternalIds(alerts, komets)

        messages = []
        warnings_used = []

        self.__logger.info("Parsing warnings data...")
        messages += self.processKomets(id_komets, komets, warnings_used)
        messages += self.processAlerts(id_alerts, alerts, warnings_used)
        messages += self.processHydro(self.__hydro_ids, alerts_hydro)

        self.__logger.info("Requesting warnings for Baltic sea...")
        baltic = requests.get(self.__service_url_baltic).json() # Bałtyk

        self.__logger.info("Parsing warnings for Baltic sea...")
        messages += self.processBaltic(baltic)

        if messages == []:
            self.__logger.info("No weather warnings.")
            if self.__no_warns_text:
                self.__logger.info("Sending info about no warnings.")
                messages.append("No weather warnings.")
        return messages