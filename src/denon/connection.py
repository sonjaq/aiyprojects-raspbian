import time
from telnetlib import Telnet

class DenonConnection(object):
    """POSTS commands to Denon API server"""
    def __init__(self, api_host, port="8000"):
        self._api_host = api_host
        self._port = port
        self._connection = None 

    def process_command_string(self, text):
        command_queue = []
        if "on" in text:
            command_queue.append("ZMON")
        if "receiver off" in text:
            command_queue.append("ZMOFF")
            return command_queue

        if "xbox" in text:
            command_queue.append("SIGAME", None)
        elif "apple" in text:
            command_queue.append("SIMPLAY")
        elif "dvd" in text:
            command_queue.append("SIDVD")
        elif "cable" in text:
            command_queue.append("SISAT/CABLE")

        if "dolby" in text:
            command_queue.append("MSDOLBY_DIGITAL")
        elif "dts" in text:
            command_queue.append("MSDTS_SURROUND")
        elif "stereo" in text:
            command_queue.append("MSSTEREO")

        if "music" in text:
            command_queue.append("MSMUSIC")
        elif "movie" in text:
            command_queue.append("MSMOVIE")
        elif "direct" in text:
            command_queue.append("MSDIRECT")

        if "volume" in text:
            if "up" in text:
                command_queue.append("MVUP")
            elif "down" in text:
                command_queue.append("MVDOWN")

        if "quiet" in text:
            command_queue.append("MV20")
        elif "normal" in text:
            command_queue.append("MV42")
        elif "loud" in text:
            command_queue.append("MV60")

        if "unmute" in text:
            command_queue.append("MUOFF")
        elif "mute" in text:
            command_queue.append("MUON")

        print("queue:" + command_queue)
        return command_queue


    def handle_command_queue(self, queue):
        for item in queue:
            print("sending item {}".format(item))
            self.send(item)
            time.sleep(1)

    def send(self, command):
        if not self._connection or not self._connection.sock_avail():
            print('initiating receiver connection')
            self._connection = Telnet()
            self._connection.open(self._api_host, self._port)

        self._connection.write(command.encode('ascii') + b'\n')
