import schedule

service_uri = 'http://www.hampager.de:8080/calls' # DAPNET REST-API server

postTimeout = 5 # request post timeout

enableTX = False

messagePrefix = "SQ2IPS WX: "

subscribers = ["sq2ips"]
transmitters = ["sr2uvg"]
transmitter_groups = ["sp-all"]

postDataLambda = lambda full_message : { "text": full_message, "callSignNames": subscribers, "transmitterGroupNames": transmitter_groups, "emergency": False }

mainLoopSleep = 1

from modules.startup import Startup
startup = Startup(
    startup_message = lambda startup_time: f"System startup, time: {startup_time}."
)

from modules.sun import SunriseSunset
sunrisesunset = SunriseSunset(
    lat='54.5206',
    lon='18.5392',
    localtime=True
)

from modules.radiation_paa import RadiationPaa
radiation_paa = RadiationPaa(
    service_uri="https://monitoring.paa.gov.pl/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=paa:kcad_siec_pms_moc_dawki_mapa&outputFormat=application/json",
    sensor_id="d2e87d20-28e2-47ea-860d-98a4e98d8726"
)

from modules.meteoalert_imgw import MeteoalertIMGW
meteoalert_imgw = MeteoalertIMGW(
    service_url="https://meteo.imgw.pl/api/meteo/messages/v1/",
    city_ids=["2262"],
    hydro_ids=["W_G_6_PM", "Z_G_22_PM"],
    service_url_baltic="https://baltyk.imgw.pl/getdata/forecast.php?type=sea&lang=pl",
    baltic_region="SOUTHEASTERN", # options: WESTERN, SOUTHERN, SOUTHEASTERN, CENTRAL, NORTHERN, refer to https://baltyk.imgw.pl/
    no_warns_text=True
)

from modules.airpolution_gios import AirPolutionGIOS
airpolution_gios = AirPolutionGIOS(
    service_url="http://api.gios.gov.pl/pjp-api/rest/",
    sensor_id=732)

modules = [
    (startup, None),
    (sunrisesunset, None),
    (radiation_paa, None),
    (meteoalert_imgw, None)
#    (testsendermodule, schedule.every(3).seconds),
#    (sunrisesunset, schedule.every(3).seconds)
#    (radiation_paa, None)
#    (meteoalert_imgw, None)
]