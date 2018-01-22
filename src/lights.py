#!/usr/bin/env python3

import os, sys
import pyHS100
import asyncio
import random
import time
from time import sleep
from multiprocessing.connection import Listener
import logging



lights = []
config = {
    "MAX_BRIGHTNESS": os.getenv("MAX_BRIGHTNESS", 40),
    "MIN_BRIGHTNESS": os.getenv("MIN_BRIGHTNESS", 30),
    "HUE_INTERVAL": os.getenv("HUE_INTERVAL", 30),
    "SATURATION_INTERVAL": os.getenv("SATURATION_INTERVAL", 10),
    "MIN_SATURATION": os.getenv("MIN_SATURATION", 70),
    "MAX_SATURATION": os.getenv("MAX_SATURATION", 100),
    "TRANSITION_MS": os.getenv("TRANSITION_MS", 1633),
    "TRANSITION_DIVISOR": os.getenv("TRANSITION_DIVISOR", 1000)
}

ON=False
FIXED=False

state = None
listener = None

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


def setup():
    # listener = Listener( ('localhost', 6780), authkey=b'secret')
    rcfile = open(os.environ['HOME'] + os.sep + '.lightsrc')
    for line in rcfile.read().splitlines():
        config.update({line.split('=')[0]: line.split('=')[1].split(',')})
    if config.get('lights'):
        for ip_address in config.get('lights'):
            try:
                lights.append(pyHS100.SmartBulb(ip_address))
            except:
                logging.info("Failed setting {ip_address} as bulb")
                break
        return

    devices = pyHS100.Discover().discover()
    for ip, obj in devices.items():
        if obj.__class__ == pyHS100.SmartBulb:
            lights.append(obj)

#def setup_params():
#    for key, value in config.items():
#       #

def change_light_state(light, data, refresh_state=False):
    global state, FIXED, ON
    if FIXED or not ON:
        state = light.get_light_state()
        return state
    if not state or state == None or refresh_state == True:
        state = light.get_light_state()

    for prop, value in data.items():
        state[prop] = value

    light.set_light_state(state)

def prepare_light_data(data={}):
    global ON, FIXED, config
    ON = data.get('power', ON)
    FIXED = data.get('fixed', FIXED)
    prepped_data = {}
    prepped_data["hue"] = data.get("hue", random.choice(range(0,360)))
    prepped_data["saturation"] = data.get("saturation", random.choice(range(config["MIN_SATURATION"],config["MAX_SATURATION"])))
    prepped_data["brightness"] = data.get("brightness", random.choice(range(config["MIN_BRIGHTNESS"],config["MAX_BRIGHTNESS"])))
    prepped_data["transition_period"] = data.get("transition_period", config.get('TRANSITION_MS'))
    prepped_data["ignore_default"] = "1"
    return prepped_data

global timestamp
timestamp = None
# def animate(range)
#     global timestamp
#     if not timestamp: timestamp = DateTime.now


def main(setup_lights=lights, args=None):
    logging.info("Beginning setup")
    setup()
    logging.info("Setup complete")
    global ON
    global config

    for setting, value in config.items():
        if args:
            if setting is not "lights" and args.get("{setting}"):
                config["{setting}"] = args.get("{setting}",value)

    ON = True


    # conn = listener.accept()
    start_time = time.time()
    frame_counter = 0
    while True:
        #if frame_counter % 5 == 0: logging.info("FPS:" + str(frame_counter / float(time.time() - start_time)))
        # if conn.poll():
        #     data = prepare_light_data(conn.recv())
        #     print(data)
        # else:
        data = prepare_light_data()

        transition_period = data.get('transition_period', config["TRANSITION_MS"])
        if ON:
            for light in setup_lights:
                change_light_state(light, data)
        frame_counter += 1
        sleep(transition_period / config["TRANSITION_DIVISOR"])


if __name__ == '__main__':
    try:
        setup()
        main(lights)
    except KeyboardInterrupt:
        sys.exit(0)
