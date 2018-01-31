#!/usr/bin/env python3

import os
import sys
import socket
import pyHS100
import random
import time
from time import sleep
import logging


lights = []
config = {
    "MAX_BRIGHTNESS": int(os.getenv("MAX_BRIGHTNESS", 40)),
    "MIN_BRIGHTNESS": int(os.getenv("MIN_BRIGHTNESS", 30)),
    "HUE_INTERVAL": int(os.getenv("HUE_INTERVAL", 30)),
    "SATURATION_INTERVAL": int(os.getenv("SATURATION_INTERVAL", 10)),
    "MIN_SATURATION": int(os.getenv("MIN_SATURATION", 70)),
    "MAX_SATURATION": int(os.getenv("MAX_SATURATION", 100)),
    "TRANSITION_MS": int(os.getenv("TRANSITION_MS", 1000)),
    "TRANSITION_DIVISOR": int(os.getenv("TRANSITION_DIVISOR", 1000))
}

ON = False
FIXED = False

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

# def setup_params():
#    for key, value in config.items():
#       #


def change_light_state(light, data, refresh_state=False):
    global state, FIXED, ON
    if FIXED or not ON:
        state = light.get_light_state()
        return state
    if not state or state is None or refresh_state is True:
        state = light.get_light_state()

    for prop, value in data.items():
        state[prop] = value

    light.set_light_state(state)


def get_animated_states():
    global config
    rainbow = list(range(0, 361, 30))
    # rainbow = [
    #     0,
    #     180,
    #     30,
    #     210,
    #     60,
    #     240,
    #     90,
    #     270,
    #     120,
    #     300,
    #     150,
    #     330,
    #     # 360
    # ]
    # random.shuffle(rainbow)
    luminescence = [
        config["MIN_BRIGHTNESS"],
        config["MAX_BRIGHTNESS"],
        config["MIN_BRIGHTNESS"]
    ]
    intensity = list(
        range(config["MIN_SATURATION"], config["MAX_SATURATION"], 2))
    # intensity = intensity + list(
    #   range(config["MAX_SATURATION"], config["MIN_SATURATION"], -2))

    states = []
    last_hue = None
    for saturation in intensity:
        for hue in rainbow:
            # for brightness in luminescence:
                if hue is not last_hue:
                    last_hue = hue
                    transition_period = int(config["TRANSITION_MS"]) * 3
                else:
                    transition_period = config["TRANSITION_MS"]
            # for brightness in luminescence:
                data = {
                    'hue': hue,
                    'brightness': 35,  # brightness,
                    'saturation': saturation,
                    'transition_period': transition_period,
                    'ignore_default': 1
                }
                states.append(data)
    return states


def prepare_light_data(data={}):
    global ON, FIXED, config
    ON = data.get('power', ON)
    FIXED = data.get('fixed', FIXED)
    prepped_data = {}
    prepped_data["hue"] = data.get("hue", random.choice(range(0, 360)))
    prepped_data["saturation"] = data.get(
        "saturation",
        random.choice(
            range(config["MIN_SATURATION"], config["MAX_SATURATION"])
        ))
    prepped_data["brightness"] = data.get(
        "brightness", random.choice(
            range(config["MIN_BRIGHTNESS"], config["MAX_BRIGHTNESS"])))
    prepped_data["transition_period"] = data.get(
        "transition_period", config.get('TRANSITION_MS'))
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
                config["{setting}"] = args.get("{setting}", value)

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', 7777))
    serversocket.listen(5)  # become a server socket, maximum 5 connections
    ON = True
    # conn = listener.accept()
    # start_time = time.time()
    frame_counter = 0
    while True:

        if ON:
            for state in get_animated_states():
                connection, address = serversocket.accept()
                connection.settimeout(0.1)
                buf = connection.recv(64)
                if len(buf) > 0:
                    data = buf.decode()
                    logging.info(data)
                    key, value = data.split(':')
                    if key == "speed":
                        key = "transition_period"
                    state[key] = value
                transition_period = state.get('transition_period')
                for light in setup_lights:
                    change_light_state(light, state)
                sleep(transition_period / config["TRANSITION_DIVISOR"])
        frame_counter += 1


if __name__ == '__main__':
    try:
        setup()
        main(lights)
    except KeyboardInterrupt:
        sys.exit(0)
