import time
from telnetlib import Telnet
"""
Connects to a Denon AVR-X1400H receiver via telnet and sends commands that line
up with with the Denon AVR Spec
"""
class DenonConnection(object):
    """POSTS commands to Denon API server"""
    def __init__(self, api_host, port="23"):
        self._api_host = api_host
        self._port = port
        self._connection = None
        self._words = None
        self._queue = []

    def process_command_string(self, words):
        self._words = frozenset(words)
        print(words)
        power = self.power_commands()
        source = self.input_commands()
        audio = self.audio_commands()
        volume = self.volume_commands()
        self.queue_commands(power, source, audio, volume)


    def queue_commands(self, power, source, audio, volume):
        print(power, source, audio, volume)
        if power is not None:
            self._queue.append(power)
            if power == b"ZMOFF\r":
                return

        if source is not None:
            self._queue.append(source)
        if audio is not None:
            self._queue.append(audio)
        if volume is not None:
            self._queue.append(volume)


    def power_commands(self):
        found = None
        if "receiver" and "off" in self._words:
            found = b"ZMOFF"
        elif "receiver" and "on" in self._words:
            found = b"ZMON"
        if found:
            return found + b'\r'
        return None

    def input_commands(self):
        found = None
        if "xbox" in self._words or "games" in self._words:
            found = b"SIGAME"
        elif "apple" in self._words or "tv" in self._words or "listen" in self._words:
            found = b"SIMPLAY"
        elif "dvd" in self._words:
            found = b"SIDVD"
        elif "cable" in self._words:
            found = b"SISAT/CABLE"
        elif "bluetooth" in self._words:
            found = b"SIBT"
        if found:
            return found +  b'\r'
        return None

    def audio_commands(self):
        processing = None
        if "stereo" in self._words:
            processing = b"MSSTEREO"
        elif "atmos" in self._words or "atmos" in self._words or "mose" in self._words or "atmose" in self._words:
            processing = b"MSDOLBY ATMOS"
        elif "dolby" in self._words or "digital" in self._words:
            processing = b"MSDOLBY DIGITAL"
        elif "dps" in self._words or "dts" in self._words:
            processing = b"MSDTS SURROUND"

        mode = None
        if "music" in self._words or "listen" in self._words:
            mode = b"MSMUSIC"
        elif "game" in self._words:
            mode = b"MSGAME"
        elif "movie" in self._words:
            mode = b"MSMOVIE"
        elif "direct" in self._words:
            mode = b"MSDIRECT"

        if processing and mode:
            return processing + b'\r' + mode + b'\r'
        elif processing:
            return processing + b'\r'
        elif mode:
            return mode + b'\r'

        return None


    def volume_commands(self):
        if "volume" in self._words and "up" in self._words:
            return b"MVUP" + b'\r'
        elif "volume" in self._words and "down" in self._words:
            return b"MVDOWN" + b'\r'

        if "quiet" in self._words:
            return b"MV20" + b'\r'
        elif "normal" in self._words:
            return b"MV42" + b'\r'
        elif "loud" in self._words:
            return b"MV60" + b'\r'

        if "unmute" in self._words:
            return b"MUOFF" + b'\r'
        elif "mute" in self._words:
            return b"MUON" + b'\r'

        return None


    def handle_command_queue(self):
        for item in self._queue:
            self.send(item)
            print(item)
            sleep_time = 1
            time.sleep(sleep_time)
        self._queue = []

    def connector(self):
        if self._connection == None or not self._connection.sock_avail():
            self._connection = Telnet()
            self._connection.open(self._api_host, self._port)
            time.sleep(4)
        return self._connection


    def send(self, command):
        self.connector().write(command)
