#!/usr/bin/env python3

import os, sys
import pyHS100
import asyncio
import random
from time import sleep

lights = []
MAX_BRIGHTNESS = 60
MIN_BRIGHTNESS = 0
HUE_INTERVAL = 33 
SATURATION_INTERVAL = 10
MIN_SATURATION = 30
MAX_SATURATION = 100
TRANSITION_MS = 7000
state = None

def setup():
    devices = pyHS100.Discover().discover()
    for ip, obj in devices.items():
        if obj.__class__ == pyHS100.SmartBulb:
            lights.append(obj)
    
def change_light_color(light, hue=None, saturation=None, brightness=None, transition_period=None):
    global state
    if not state or state == None: state = light.get_light_state()
    if hue: state["hue"] = hue
    if saturation: state["saturation"] = saturation
    if brightness: state["brightness"] = brightness
    if transition_period: state["transition_period"] = transition_period
    light.set_light_state(state)

def check_light_status_file():
    tmpfile = os.getenv('XDG_RUNTIME_DIR') + os.sep + 'light_status.txt'
    try: 
        file = open(tmpfile, 'r+')
        return file.read()
    except FileNotFoundError:
        return ''

def main(loop):
    setup()
    interval = 0
    while True:
        #status = check_light_status_file()
       # if status != '':
       #     values = status.split(',')
       #     hue_interval = values[0]
       #     saturation_interval = values[1]
       #     brightness_interval = values[2]
       # 
        if interval % HUE_INTERVAL == 0: 
            hue = random.choice(range(0,360))
        else:
            hue = None
        if interval % SATURATION_INTERVAL == 0:
            saturation = random.choice(range(MIN_SATURATION,MAX_SATURATION))
        else:
            saturation = None

        brightness = random.choice(range(MIN_BRIGHTNESS,MAX_BRIGHTNESS))
        transition_period = TRANSITION_MS
        for light in lights:
            change_light_color(light, hue, saturation, brightness, transition_period)
            sleep(transition_period/2000)
        interval += 1
    sys.exit(0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_forever(main(loop))
