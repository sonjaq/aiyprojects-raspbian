#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Adapted from the demos within the Google Assistant Library that shipped
with the Google AIY Audio kit.

Controls exactly one home theater configuration that I am aware of, which
consists of the following:

* TPLink HS100 smart plug (backlight, subwoofer)
* Denon 7.2 receiver AVR-X1400H
* TCL Roku TV (55P605)
* Xbox One

Requires a credentials file named `device_details.py` as a sibling to this.
Google assistant credentials are required, as well.

Crammed into a Star Wars BB8 toy, this runs on a Raspberry Pi 3, with the
aforementioned Google AIY kit.

author: Sonja Leaf <avleaf@gmail.com>
"""

import logging
import subprocess
import sys
import itertools

import aiy.audio
import aiy.assistant.auth_helpers
import aiy.voicehat

import device_details

from denon.connection import DenonConnection
from denon.trigger_map import TriggerMap
import denon.triggers as triggers
import denon.actions as actions
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from roku import Roku

import xbox.xbox as xbox
import xml.etree.ElementTree as ET

import pyHS100
import random
from multiprocessing.connection import Client

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

global plug, denon, roku, trigger_map, setup_lights, light_controller
setup_lights = []
light_controller = None

def device_setup():
    global plug, denon, roku, trigger_map, setup_lights, light_controller
    trigger_map = TriggerMap()
    denon = DenonConnection(device_details.denon_ip_address(), "23", trigger_map)
    roku = Roku.discover(timeout=5)[0]
    discovery = pyHS100.Discover().discover()
    # light_controller = Client(('localhost', 6780), authkey=b'secret')
    for ip, obj in discovery.items():
        if obj.__class__ == pyHS100.SmartPlug:
            plug = obj
        if obj.__class__ == pyHS100.SmartBulb:
            setup_lights.append(obj)


def lights_on():
    global setup_lights
    for light in setup_lights:
        light.turn_on()
        light.hsv = (282, 50, 80)

def lights_off():
    global setup_lights, light_controller
    if light_controller is not None or subprocess.call(["sudo","systemctl","is-active","lights"]) == 0:
        subprocess.call(["sudo","service","lights","stop"])
        light_controller = None
        logging.info("disco time killed")
    for light in setup_lights:
        light.turn_off()

def lights_erica():
    global setup_lights
    for light in setup_lights:
        state = light.get_light_state()
        state["hue"] = 348
        state["saturation"] = 80
        state["brightness"] = 255
        light.set_light_state(state)

def random_light_color():
    global setup_lights
    random_color = random.choice(range(1,360))
    random_saturation = random.choice(range(1,100))
    random_brightness = random.choice(range(20,90))
    for light in setup_lights:
        state = light.get_light_state()
        state["hue"] = random_color
        state["saturation"] = random_saturation
        state["brightness"] = random_brightness
        state["transition_period"] = 3000
        light.set_light_state(state)


def bold_light_color():
    global setup_lights
    for light in setup_lights:
        hsv = list(light.hsv)
        hsv[1] = 99
        light.hsv = tuple(hsv)

def bright_light_color():
    global setup_lights
    for light in setup_lights:
        hsv = list(light.hsv)
        hsv[2] = 99
        light.hsv = tuple(hsv)

def low_light_color():
    global setup_lights
    for light in setup_lights:
        hsv = list(light.hsv)
        hsv[2] = 5
        light.hsv = tuple(hsv)

def plug_power_off():
    global plug
    if plug.is_on:
        plug.turn_off()

def plug_power_on():
    global plug
    if plug.is_off:
        plug.turn_on()

def roku_off():
    global roku
    if roku_is_on():
        roku.power()

def roku_on():
    global roku
    if not roku_is_on():
        roku.power()

def roku_is_on():
    global roku
    tv_info = ET.fromstring(roku._get("/query/device-info").decode())
    return tv_info.findtext("power-mode") == "PowerOn"

def roku_switch_to_named_input(target):
    global roku
    receiver_roku_input = list(itertools.filterfalse(lambda x: x.name != target, roku.apps)).pop()
    roku.launch(receiver_roku_input)


light_process = None

import lights

def process_event(assistant, event):
    global denon, trigger_map, roku, light_process, light_controller
    status_ui = aiy.voicehat.get_status_ui()

    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        status_ui.success_sound()
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        text = event.args['text'].lower()
        logging.info("Text: " + text)
        words = text.split()
        if text == "shut it all down" or text == "shut it down":
            assistant.stop_conversation()
            status_ui.shutdown_sound()
            if light_controller or subprocess.call(["sudo","systemctl","is-active","lights"]) == 0:
                subprocess.call(["sudo","service","lights","stop"])
                light_controller = None
                logging.info("disco time killed")
            try:
                roku_off()
                plug_power_off()
                denon.send(actions.receiver_standby())
                lights_off()
                return
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif text == "leave the lights on":
            assistant.stop_conversation()
            status_ui.shutdown_sound()
            roku_off()
            plug_power_off()
            denon.send(actions.receiver_standby())
            return
        elif text == "erica time":
            assistant.stop_conversation()
            lights_erica()
        elif text == "disco lights" or text == "disco" or text == "discount tire" or text == "rotating lights" or text == "disco time":
            assistant.stop_conversation()
            logging.info("Disco triggered")
            status_ui.success_sound()
            if light_controller == None:
                logging.info("Starting disco time")
                subprocess.call(["sudo","service","lights","start"])
                light_controller = True
            else:
                if subprocess.call(["sudo","systemctl","is-active","lights"]) == 0:
                    subprocess.call(["sudo","service","lights","stop"])
                light_controller = None
                logging.info("disco time killed")
        elif text == "lights off" or text == "bedtime" or text == "night night":
            assistant.stop_conversation()
            status_ui.shutdown_sound()
            lights_off()
        elif text == "lights on" or text == "then there was light":
            assistant.stop_conversation()
            status_ui.success_sound()
            lights_on()
        elif text == "old lights" or text == "bold lights" or text == "loud lights":
            assistant.stop_conversation()
            bold_light_color()
        elif text == "low lights" or text == "low light" or text == "lowlights" or text == "darkness please":
            assistant.stop_conversation()
            low_light_color()
        elif text == "hi lights" or text == "bright lights" or text == "highlights":
            assistant.stop_conversation()
            bright_light_color()
        elif text == "random color" or text == "mix it up" or text == "erica is the best":
            assistant.stop_conversation()
            random_light_color()
        elif text == "tv power toggle":
            assistant.stop_conversation()
            status_ui.success_sound()
            try:
                roku.power()
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif text == "xbox time":
            assistant.stop_conversation()
            status_ui.success_sound()
            try:
                plug_power_on()
                lights_on()
                roku_on()
                roku_switch_to_named_input("Receiver")
                denon.send(actions.xbox_game())
                xbox.wake(device_details.xbox_ip_address(), device_details.xbox_live_device_id())
                logging.info("XBOX TIME COMPLETE")
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
            return
        elif text == "music time":
            assistant.stop_conversation()
            status_ui.success_sound()
            try:
                plug_power_on()
                denon.send(actions.apple_tv_stereo())
                roku_on()
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif text == "roku YouTube time":
            assistant.stop_conversation()
            try:
                plug_power_on()
                denon.send(actions.roku_tv())
                roku_power_on()
                roku_switch_to_named_input("YouTube")
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif trigger_map.receiver_triggered(words, text):
            assistant.stop_conversation()
            status_ui.success_sound()
            sent_command = denon.process_command_string(words, text)
            logging.info(sent_command)
        elif text == '':
            status_ui.error_sound()
            return
        return
    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')
    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')
    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

import signal

def sigterm_handler(signal, frame):
    # save the state here or do whatever you want
    logging.info("Shutting down")
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)


def main():
    device_setup()
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()
