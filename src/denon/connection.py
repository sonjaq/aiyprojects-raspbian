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
        self._queue = None

    def process_command_string(self, words):
        self._words = words
        self._queue = []
        self.power_commands()
        self.input_commands()
        self.audio_commands()


    def power_commands(self):
        if "receiver" and "off" in self._words:
            self._queue.append("ZMOFF")
        elif "receiver" and "on" in self._words:
            self._queue.append("ZMON")


    def input_commands(self):
        if "xbox" or "games" in self._words:
            self._queue.append("SIGAME")
        elif "apple" or "tv" or "listen" in self._words:
            self._queue.append("SIMPLAY")
        elif "dvd" in self._words:
            self._queue.append("SIDVD")
        elif "cable" in self._words:
            self._queue.append("SISAT/CABLE")
        elif "bluetooth" in self._words:
            self._queue.append("SIBT")

    def audio_commands(self):
        if "stereo" in self._words:
            self._queue.append("MSSTEREO")
        elif "atmos" or "atmos" or "mose" or "atmose" in self._words:
            self._queue.append("MSDOLBY ATMOS")
        elif "dolby" or "digital" in self._words:
            self._queue.append("MSDOLBY DIGITAL")
        elif "neural" or "dps" or "dts" in self._words:
            self._queue.append("MSDTS SURROUND")

        if "music" or "listen" in self._words:
            self._queue.append("MSMUSIC")
        elif "game" in self._words:
            self._queue.append("MSGAME")
        elif "movie" in self._words:
            self._queue.append("MSMOVIE")
        elif "direct" in self._words:
            self._queue.append("MSDIRECT")


    def volume_commands(self):
        if "volume" and "up" in self._words:
            self._queue.append("MVUP")
            return
        elif "volume" and "down" in self._words:
            self._queue.append("MVDOWN")
            return

        if "quiet" in self._words:
            self._queue.append("MV20")
            return
        elif "normal" in self._words:
            self._queue.append("MV42")
            return
        elif "loud" in self._words:
            self._queue.append("MV60")
            return

        if "unmute" in self._words:
            self._queue.append("MUOFF")
        elif "mute" in self._words:
            self._queue.append("MUON")


    def handle_command_queue(self):
        for item in self._queue:
            self.send(item)
            print(item)
            sleep_time = 1
            time.sleep(sleep_time)

    def connector(self):
        if self._connection == None or not self._connection.sock_avail():
            self._connection = Telnet()
            self._connection.open(self._api_host, self._port)
            time.sleep(4)
        return self._connection


    def send(self, command):
        self.connector.write(command.encode('ascii') + b'\r')
