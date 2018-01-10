import logging

import denon.triggers as triggers
import denon.actions as actions

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

"""
This is a map of triggers and utility functions for Denon Commands

action lengths must be shorter than max of 135 bytes (hard to do, methinks)
"""
class TriggerMap(object):
    """docstring for TriggerMap"""
    def __init__(self):
        super(TriggerMap, self).__init__()

    def trigger_triggered(self, triggers, words, text):
        for trigger in triggers():
            if trigger in words or trigger in text:
                return True

    def input_trigger_triggered(self, triggers, words, text):
        for action, trigger in triggers.items():
            if self.trigger_triggered(trigger, words, text):
                return self.action_triggered(action)

    def action_triggered(self, action):
        action_map = {
            'xbox': actions.xbox,
            'apple_tv': actions.apple_tv,
            'nintendo': actions.nintendo,
            'blu_ray': actions.blu_ray,
            'bluetooth': actions.bluetooth,
            'cable': actions.cable
        }
        return action_map.get(action)

    def receiver_triggered(self, words, text):
        matched = []
        for trigger in triggers.receiver_recognition():
            if trigger in words or trigger in text:
                matched.append(trigger)

        if len(matched) > 0:
            logging.info(matched)
            return True

    def mapped_trigger(self, words, text):
        action = b""

        words = frozenset(words)
        if self.trigger_triggered(triggers.receiver_power, words, text):
            if "on" in text:
                action = actions.receiver_power_on()
            if "off" in text or "app" in text:
                return actions.receiver_standby()

        input_triggers = {
            'xbox': triggers.xbox,
            'apple_tv': triggers.apple_tv,
            'nintendo': triggers.nintendo,
            'blu_ray': triggers.blu_ray,
            'bluetooth': triggers.bluetooth,
            'cable': triggers.cable
        }

        input_triggered = None
        input_triggered = self.input_trigger_triggered(input_triggers, words, text)
        if input_triggered is not None:
            action = action + input_triggered()

        if self.trigger_triggered(triggers.audio_mode, words, text):
            mode = b""
            if "game" in text:
                mode = b"MSGAME\r"
            elif "movie" in text:
                mode = actions.mode_movie()
            elif "music" in text:
                mode = actions.mode_music()

            if "dolby atmos" in text or "atmos" in text:
                mode = b"MSDOLBY ATMOS\r"
            elif "dolby" in text or "dolby surround" in text:
                mode = b"MSDOLBY DIGITAL\r"
            elif "dts" in text or "dps" in text or "digital theater" in text or "neural" in text or "surround sound" in text:
                mode = b"MSDTS SURROUND\r"
            elif "stereo" in text:
                mode = actions.mode_stereo()
            elif "direct" in text:
                mode = b"MSDIRECT\r"
            action = action + mode

        if self.trigger_triggered(triggers.volume, words, text):
            if "up" in text:
                action = action + actions.volume_up()
            elif "down" in text:
                action = action + actions.volume_down()
            elif "quiet" in text or 'quietness' in text:
                action = action + actions.volume_quiet()
            elif "loud" in text or 'loudness' in text:
                action = action + actions.volume_loud()
            elif "normal" in text:
                action = action + actions.volume_normal()
            elif "unmute" in text:
                action = action + actions.volume_unmute()
            elif "mute" in text or 'zero' in text:
                action = action + actions.volume_mute()

        return action

