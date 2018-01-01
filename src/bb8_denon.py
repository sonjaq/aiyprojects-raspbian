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

import aiy.audio
import aiy.assistant.auth_helpers
import aiy.voicehat

from denon.connection import DenonConnection
from google.assistant.library import Assistant
from google.assistant.library.event import EventType

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


def process_event(assistant, event, denon):
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
        if 'receiver' or 'denon' or 'listen' or 'watch' or 
            'xbox' or 'apple' or 'tv' or 
            'music' or 'movie' or 'mode' 
            in text:  
            assistant.stop_conversation()
            denon.handle_command_queue(denon.process_command_string(text))
        elif text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        # elif "xbox" or "apple" or "audio" or "video" or "music" or "stereo" or "dolby" or "dts" or "volume" or "tv":

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')


    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    denon = DenonConnection("192.168.1.137", "23")
    with Assistant(credentials) as assistant:

        for event in assistant.start():
            process_event(assistant, event, denon)


if __name__ == '__main__':
    main()
