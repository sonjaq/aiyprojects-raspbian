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
Adapted from the demos within  the Google Assistant Library that shipped
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

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


global plug, denon, roku, trigger_map

def device_setup():
    global plug, denon, roku, trigger_map
    trigger_map = TriggerMap()
    denon = DenonConnection(device_details.denon_ip_address(), "23", trigger_map)
    roku = Roku.discover(timeout=5)[0]
    plug_ip = list(pyHS100.Discover().discover())[0]
    plug = pyHS100.SmartPlug(plug_ip)

def plug_power_off():
    global plug
    if plug.is_on:
        plug.power_off()

def plug_power_on():
    global plug
    if plug.is_off:
        plug.power_on()

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


def process_event(assistant, event):
    global denon, trigger_map, roku
    status_ui = aiy.voicehat.get_status_ui()

    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
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
            try:
                roku_off()
                plug_power_off()
                denon.send(actions.receiver_standby())
                return
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif text == "tv power toggle":
            assistant.stop_conversation()
            try:
                roku.power()
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif text == "xbox time":
            assistant.stop_conversation()
            try:
                plug_power_on()
                roku_on()
                roku_switch_to_named_input("Receiver")
                denon.send(actions.xbox_game())
                xbox.wake(device_details.xbox_ip_address(), device_details.xbox_live_device_id())
                logging.info("XBOX TIME COMPLETE")
            except:
                logging.info("Unexpected error:", sys.exc_info()[0])
                pass
        elif text == "music time":
            assistant.stop_conversation()
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
            sent_command = denon.process_command_string(words, text)
            logging.info(sent_command)

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')
    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')
    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    device_setup()
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:

        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()
