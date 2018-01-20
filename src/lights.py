#!/usr/bin/env python3

import os, sys
import pyHS100
import asyncio
import random
from time import sleep
from multiprocessing.connection import Listener

lights = []
MAX_BRIGHTNESS = os.getenv("MAX_BRIGHTNESS", 40)
MIN_BRIGHTNESS = os.getenv("MIN_BRIGHTNESS", 30)
HUE_INTERVAL = os.getenv("HUE_INTERVAL", 33)
SATURATION_INTERVAL = os.getenv("SATURATION_INTERVAL", 10)
MIN_SATURATION = os.getenv("MIN_SATURATION", 30)
MAX_SATURATION = os.getenv("MAX_SATURATION", 100)
TRANSITION_MS = os.getenv("TRANSITION_MS", 1000)
TRANSITION_DIVISOR = os.getenv("TRANSITION_DIVISOR", 2500)

ON=False
FIXED=False

state = None
listener = None

def setup():
    global listener
    # listener = Listener( ('localhost', 6780), authkey=b'secret')
    devices = pyHS100.Discover().discover()
    for ip, obj in devices.items():
        if obj.__class__ == pyHS100.SmartBulb:
            lights.append(obj)

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
    global ON, FIXED
    ON = data.get('power', ON)
    FIXED = data.get('fixed', FIXED)
    prepped_data = {}
    prepped_data["hue"] = data.get("hue", random.choice(range(0,360)))
    prepped_data["saturation"] = data.get("saturation", random.choice(range(MIN_SATURATION,MAX_BRIGHTNESS)))
    prepped_data["brightness"] = data.get("brightness", random.choice(range(MIN_BRIGHTNESS,MAX_BRIGHTNESS)))
    prepped_data["transition_period"] = data.get("transition_period", TRANSITION_MS)
    prepped_data["ignore_default"] = "1"
    return prepped_data

def main(loop):
    global ON
    ON = True
    setup()
    # conn = listener.accept()
    while True:
        # if conn.poll():
        #     data = prepare_light_data(conn.recv())
        #     print(data)
        # else:
        data = prepare_light_data()

        if ON:
            transition_period = data.get('transition_period', TRANSITION_MS)
            for light in lights:
                change_light_state(light, data)
                sleep(transition_period/TRANSITION_DIVISOR)

    sys.exit(0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_forever(main(loop))
