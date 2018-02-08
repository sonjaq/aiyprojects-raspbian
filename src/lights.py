#!/usr/bin/env python3
# helpful information on color formulas located at 
# https://www.ethangardner.com/articles/2009/03/15/a-math-based-approach-to-color-theory-using-hue-saturation-and-brightness-hsb/
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
    "MAX_BRIGHTNESS": int(os.getenv("MAX_BRIGHTNESS", 50)),
    "MIN_BRIGHTNESS": int(os.getenv("MIN_BRIGHTNESS", 40)),
    "HUE_INTERVAL": int(os.getenv("HUE_INTERVAL", 30)),
    "SATURATION_INTERVAL": int(os.getenv("SATURATION_INTERVAL", 10)),
    "MIN_SATURATION": int(os.getenv("MIN_SATURATION", 70)),
    "MAX_SATURATION": int(os.getenv("MAX_SATURATION", 100)),
    "TRANSITION_MS": int(os.getenv("TRANSITION_MS", 2500)),
    "TRANSITION_DIVISOR": int(os.getenv("TRANSITION_DIVISOR", 1000)),
    "RAINBOW_INTERVAL": int(os.getenv("RAINBOW_INTERVAL", 1))
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
    rainbow = list(range(0, 360, config["RAINBOW_INTERVAL"]))
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
        range(config["MIN_SATURATION"], config["MAX_SATURATION"], 5))
    # intensity = intensity + list(
    #   range(config["MAX_SATURATION"], config["MIN_SATURATION"], -2))

    states = []
    last_hue = None
    for hue in rainbow:
                saturation = 85 # random.choice(intensity)
        # for saturation in intensity:
            # for brightness in luminescence:
                if hue is not last_hue:
                    last_hue = hue
                    transition_period = int(config["TRANSITION_MS"])  
                else:
                    transition_period = config["TRANSITION_MS"]
            # for brightness in luminescence:
                data = {
                    'hue': hue,
                    'brightness': 35,  # brightness,
                    'saturation': saturation,
                    'transition_period': transition_period
                    # 'ignore_default': 1
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
    prepped_data["brightness"] = data.get("brightness", random.choice(range(config["MIN_BRIGHTNESS"], config["MAX_BRIGHTNESS"])))
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
    logging.info("Setup complete")
    global ON
    global config

    for setting, value in config.items():
        if args:
            if setting is not "lights" and args.get("{setting}"):
                config["{setting}"] = args.get("{setting}", value)

    tetradic_hues_modifiers = [0, 90, 180, 270] 
    complimentary_hues = [0, 180, 0, 180]
    split_comp_hues = [0, 150, 210, 0]
    triadic_hues = [0, 120, 240, 0]
    analagous_hues = [0, 30, 60, 90]
    
    hues_collection = [ complimentary_hues, split_comp_hues, triadic_hues, analagous_hues ]

    ON = True
    # conn = listener.accept()
    # start_time = time.time()
    frame_counter = 0
    while True:
        # if frame_counter % 5 == 0:
        #   logging.info(
        #       "FPS:" + str(frame_counter / float(time.time() - start_time)))
        # if conn.poll():
        #     data = prepare_light_data(conn.recv())
        #     print(data)
        # else:
        # data = prepare_light_data()

        
        if ON:
            states = get_animated_states()
            random.shuffle(states)
            frame_delay = float(os.getenv("FRAMETIME", 3.0))
            logging.info("Frame Delay: " + str(frame_delay))

            for state in states:
                transition_period = state.get('transition_period')
                current_state_index = states.index(state)
                hue_modifiers = analagous_hues
                for light in setup_lights:
                    light_state = states[current_state_index]

                    li = setup_lights.index(light)
                    #logging.info(li)
                    light_state["hue"] = abs(int(light_state["hue"]) + hue_modifiers[li] - 360)
                    light_state["transition_period"] = transition_period
                    change_light_state(light, light_state)
                sleep(frame_delay)
        frame_counter += 1


if __name__ == '__main__':
    try:
        setup()
        main(lights)
    except KeyboardInterrupt:
        sys.exit(0)
