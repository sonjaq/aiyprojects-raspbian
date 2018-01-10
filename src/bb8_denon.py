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

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
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

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


def power_off_pi(status_ui):
    status_ui.play_random_bb8_sound()
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi(status_ui):
    status_ui.play_random_bb8_sound()
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip(status_ui):
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    status_ui.play_random_bb8_sound()
    aiy.audio.say('%s' % ip_address.decode('utf-8'))


def process_event(assistant, event, denon, trigger_map, roku):
    status_ui = aiy.voicehat.get_status_ui()
    # status_ui.set_trigger_sound_wave('~/trigger_sound.wav')
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

        tv_info = ET.fromstring(roku._get("/query/device-info").decode())
        tv_power_status = tv_info.findtext("power-mode") == "PowerOn"
        if text == "shut it all down":
            assistant.stop_conversation()
            try:
                if tv_power_status: roku.power()
                denon.send(actions.receiver_standby())
                return
            except:
                pass

        elif text == "tv power toggle":
            assistant.stop_conversation()
            try:
                roku.power()
            except:
                pass
        elif text == "xbox time":
            assistant.stop_conversation()
            try:
                if not tv_power_status: roku.power()
                receiver_roku_input = list(itertools.filterfalse(lambda x: x.name != "Receiver", roku.apps)).pop()
                roku.launch(receiver_roku_input)
                denon.send(actions.xbox_game())
                xbox.wake(device_details.xbox_ip_address(), device_details.xbox_live_device_id())
                logging.info("XBOX TIME COMPLETE?")
            except:
                pass
        elif text == "music time":
            assistant.stop_conversation()
            try:
                denon.send(actions.apple_tv_stereo())
                if not tv_power_status: roku.power()
            except:
                pass
        elif text == "roku tv time":
            assistant.stop_conversation()
            try:
                denon.send(actions.roku_tv())
                roku.power()
                roku.home()
            except:
                pass
        elif trigger_map.receiver_triggered(words, text):
            assistant.stop_conversation()
            sent_command = denon.process_command_string(words, text)
            logging.info(sent_command)
        elif text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')


    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    trigger_map = TriggerMap()
    denon = DenonConnection(device_details.denon_ip_address(), "23", trigger_map)
    roku = Roku.discover(timeout=5)[0]
    with Assistant(credentials) as assistant:

        for event in assistant.start():
            process_event(assistant, event, denon, trigger_map, roku)


if __name__ == '__main__':
    main()
