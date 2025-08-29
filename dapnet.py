import logging
import sys, os, json, time
import requests
import schedule
from dotenv import load_dotenv
from datetime import datetime

import config

logger = logging.getLogger(__name__)

def setupLogging():
    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', filename="dapnet.log", level=logging.DEBUG)
    stdout_format = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_format)
    logging.getLogger().addHandler(stdout_handler)

def loadAuthFromEnv():
    if os.path.exists(".env"):
        load_dotenv()
        CALL = os.getenv('CALL')
        PASSWORD = os.getenv('PASSWORD')
        if CALL is not None and PASSWORD is not None:
            logger.info("Loaded authentication credentails from .env file.")
            return (CALL, PASSWORD)
        else:
            raise ValueError("No CALL or PASSWORD values in .env.")
    else:
        raise FileExistsError("No .env file present.")

def postMessage(message, auth):
    full_message = config.messagePrefix + message

    logger.info(f"Full message (len: {len(full_message)}): {full_message}")

    if len(full_message) > 80:
        logger.warning(f"Message too long ({len(full_message)}), shortening to 80...")
        full_message = full_message[:80]

    expiration_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+%Z")

    postData = config.postDataLambda(full_message, expiration_date)

    postDataJson = json.dumps(postData).encode('utf-8')
    
    logger.debug(f"Post data object: {postDataJson}")

    if config.enableTX:
        logger.info("Posting data to server...")

        response = requests.post(config.service_uri, headers={'Content-type': 'application/json'}, auth=auth, data=postDataJson, timeout=config.postTimeout)

        if response.status_code == 201:
            logger.info("Data sent, response OK.")
            logger.debug(f"Response: {response.text}")
        else:
            raise Exception(f"Got non-OK response from server, code {response.status_code}: {response.text}")
    else:
        logger.info("TX disabled, not sending.")

def runModule(module, auth):
    logger.info(f"Running module {module.__class__.__name__}...")
    try:
        messages = module.getMessages()
    except Exception as e:
        logger.error(f"Error while running module {module.__class__.__name__}: {e}")
    else:
        if messages == []:
            logger.info("No messages received from module, not sending.")
        else:
            logger.info(f"Number of messages to send: {len(messages)}")
            for i, message in enumerate(messages):
                logger.info(f"Sending message {i+1}/{len(messages)}...")
                try:
                    postMessage(message, auth)
                except Exception as e:
                    logger.error(f"Error while sending message {i+1}/{len(messages)}: {e}")
                else:
                    logger.info(f"Sending message {i+1}/{len(messages)} from module {module.__class__.__name__} succesful.")

if __name__ == '__main__':
    setupLogging()

    logger.info("Starting...")

    auth = loadAuthFromEnv()

    for module_obj in config.modules:
        module, schedule_time = module_obj
        if schedule_time == None:
            runModule(module, auth)
        else:
            logger.info(f"Scheduling module {module.__class__.__name__}: {schedule_time}")
            schedule_time.do(runModule, module, auth)

    logger.info("Starting main loop...")
    while True:
        schedule.run_pending()
        time.sleep(config.mainLoopSleep)