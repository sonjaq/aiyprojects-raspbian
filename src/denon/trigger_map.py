import logging

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

    def receiver_recognition(self):
        return self.xbox_triggers() + self.receiver_name_triggers() + self.apple_tv_triggers() + self.blu_ray_triggers() + self.bluetooth_triggers() + self.nintendo_triggers() + self.audio_mode_triggers() + self.cable_triggers()

    def xbox_triggers(self):
        return ["games", "game", "xbox", "video games", "shoot", "blow up", "race", "racing", "netflix"]

    def apple_tv_triggers(self):
        return ["apple", "apple tv", "listen", "music", "tunes", "make out", "making out", "airplay"]

    def blu_ray_triggers(self):
        return ["blu-ray", "blue ray", "blu ray"]

    def nintendo_triggers(self):
        return ["nintendo switch", "switch", "nintendo"]

    def bluetooth_triggers(self):
        return ["bluetooth", "blue teeth", "blue to", "blooptooth"]

    def cable_triggers(self):
        return ["cable", "cable sat", "satellite"]

    def volume_triggers(self):
        return ["volume", "quiet", "load", "loud", "up", "down", "mute", "normal"]

    def audio_mode_triggers(self):
        return ["dolby", "digital", "surround", "dts", "dps", "mode", "music", "movie", "game", "games", "atmos", "at mo", "neural x", "normal x"]

    def receiver_power_triggers(self):
        return ["receiver on", "receiver off", "receiver app", "denon off", "denon app"]

    def receiver_name_triggers(self):
        return ["receiver", "denon", "radio", "sound box", "music lady", "dan"]


    def receiver_power_on_action(self):
        return b"ZMON\r"

    def receiver_standby_action(self):
        return b"ZMOFF\r"

    def xbox_action(self):
        return b"SIGAME\r"

    def apple_tv_action(self):
        return b"SIMPLAY\r"

    def bluetooth_action(self):
        return b"SIBT\r"

    def nintendo_action(self):
        return b"SIDVD\r"

    def blu_ray_action(self):
        return b"SIBD\r"

    def cable_action(self):
        return b"SISAT/CABLE\r"


    def volume_up_action(self):
        return b"MVUP\r" * 10

    def volume_down_action(self):
        return b"MVDOWN\r"

    def volume_quiet(self):
        return b"MV20\r"

    def volume_loud(self):
        return b"MV60\r"

    def volume_normal(self):
        return b"MV42\r"

    def volume_mute(self):
        return b"MUON\r"

    def volume_unmute(self):
        return b"MUOFF\r"


    def xbox_game_action(self):
        return b"SIGAME\rMSGAME\r"

    def xbox_movie_action(self):
        return b"SIGAME\rMSMOVIE\r"

    def xbox_movie_stereo_action(self):
        return b"SIGAME\rMSSTEREO\r"

    def apple_tv_music_action(self):
        return b"SIMPLAY\rMSMUSIC\r"

    def apple_tv_movie_action(self):
        return b"SIMPLAY\rMSMOVIE\r"

    def apple_tv_stereo_action(self):
        return b"SIMPLAY\rMSSTEREO\r"

    def bluetooth_music_action(self):
        return b"SIMPLAY\rMSMUSIC\r"

    def bluetooth_movie_action(self):
        return b"SIMPLAY\rMSMOVIE\r"

    def bluetooth_stereo_action(self):
        return b"SIMPLAY\rMSSTEREO\r"


    def mode_music_action(self):
        return b"MSMUSIC\r"

    def mode_movie_action(self):
        return b"MSMOVIE\r"

    def mode_stereo_action(self):
        return b"MSSTEREO\r"




    def xbox_triggered(self, words, text):
        for trigger in self.xbox_triggers():
            if trigger in words or trigger in text:
                return True

    def apple_tv_triggered(self, words, text):
        for trigger in self.apple_tv_triggers():
            if trigger in words or trigger in text:
                return True

    def nintendo_triggered(self, words, text):
        for trigger in self.nintendo_triggers():
            if trigger in words or trigger in text:
                return True

    def audio_mode_triggered(self, words, text):
        for trigger in self.audio_mode_triggers():
            if trigger in words or trigger in text:
                return True

    def receiver_power_triggered(self, words, text):
        for trigger in self.receiver_power_triggers():
            if trigger in words or trigger in text:
                return True

    def blu_ray_triggered(self, words, text):
        for trigger in self.blu_ray_triggers():
            if trigger in words or trigger in text:
                return True

    def bluetooth_triggered(self, words, text):
        for trigger in self.bluetooth_triggers():
            if trigger in words or trigger in text:
                return True

    def cable_triggered(self, words, text):
        for trigger in self.cable_triggers():
            if trigger in words or trigger in text:
                return True

    def receiver_triggered(self, words, text):
        matched = []
        for trigger in self.receiver_recognition():
            if trigger in words or trigger in text:
                matched.append(trigger)

        if len(matched) > 0:
            logging.info(matched)
            return True

    def volume_triggered(self, words, text):
        for trigger in self.volume_triggers():
            if trigger in words or trigger in text:
                return True


    def mapped_trigger(self, words, text):
        action = b""

        if self.receiver_power_triggered(words, text):
            if "on" in text:
                action = self.receiver_power_on_action()
            if "off" in text or "app" in text:
                return self.receiver_standby_action()

        if self.xbox_triggered(words, text):
            action = action + self.xbox_action()
        elif self.apple_tv_triggered(words, text):
            action =  action + self.apple_tv_action()
        elif self.nintendo_triggered(words, text):
            action = action + self.nintendo_action()
        elif self.blu_ray_triggered(words, text):
            action = action + self.blu_ray_action()
        elif self.bluetooth_triggered(words, text):
            action = action + self.bluetooth_action()
        elif self.cable_triggered(words, text):
            action = action + self.cable_action()

        if self.audio_mode_triggered(words, text):
            mode = b""
            if "game" in text:
                mode = b"MSGAME\r"
            elif "movie" in text:
                mode = self.mode_movie_action()
            elif "music" in text:
                mode = self.mode_music_action()

            if "dolby atmos" in text or "atmos" in text:
                mode = b"MSDOLBY ATMOS\r"
            elif "dolby" in text or "dolby surround" in text:
                mode = b"MSDOLBY DIGITAL\r"
            elif "dts" in text or "dps" in text or "digital theater" in text or "neural" in text or "surround sound" in text:
                mode = b"MSDTS SURROUND\r"
            elif "stereo" in text:
                mode = self.mode_stereo_action()
            elif "direct" in text:
                mode = b"MSDIRECT\b"
            action = action + mode

        if self.volume_triggered(words, text):
            if "up" in text:
                action = action + self.volume_up_action()
            elif "down" in text:
                action = action + self.volume_down_action()
            elif "quiet" in text:
                action = action + self.volume_quiet()
            elif "loud" in text:
                action = action + self.volume_loud()
            elif "normal" in text:
                action = action + self.volume_normal()
            elif "unmute" in text:
                action = action + self.volume_unmute()
            elif "mute" in text:
                action = action + self.volume_mute()

        return action

