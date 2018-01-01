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
        if text.find("on") == 1:
            command_queue.append("ZMON")
        if text.find("receiver off") == 1:
            command_queue.append("ZMOFF")
            return command_queue

        if text.find("xbox") == 1:
            command_queue.append("SIGAME", None)
        elif text.find("apple") == 1:
            command_queue.append("SIMPLAY")
        elif text.find("dvd") == 1:
            command_queue.append("SIDVD")
        elif text.find("cable") == 1:
            command_queue.append("SISAT/CABLE")

        if text.find("dolby") == 1:
            command_queue.append("MSDOLBY_DIGITAL")
        elif text.find("dts") == 1:
            command_queue.append("MSDTS_SURROUND")
        elif text.find("stereo") == 1:
            command_queue.append("MSSTEREO")

        if text.find("music") == 1:
            command_queue.append("MSMUSIC")
        elif text.find("movie") == 1:
            command_queue.append("MSMOVIE")
        elif text.find("direct") == 1:
            command_queue.append("MSDIRECT")

        if text.find("volume") == 1:
            if text.find("up"):
                command_queue.append("MVUP")
            elif text.find("down") == 1:
                command_queue.append("MVDOWN")

        if text.find("quiet") == 1:
            command_queue.append("MV20")
        elif text.find("normal") == 1:
            command_queue.append("MV42")
        elif text.find("loud") == 1:
            command_queue.append("MV60")

        if text.find("unmute") == 1:
            command_queue.append("MUOFF")
        elif text.find('mute') == 1:
            command_queue.append("MUON")

        return command_queue


    def handle_command_queue(self, queue):
        for item in queue:
            self.send(item)
            time.sleep(1)

    def send(self, command):
        if not self._connection or not self._connection.sock_avail():
            print('initiating receiver connection')
            self._connection = Telnet()
            self._connection.open(self._api_host, self._port)

        self._connection.write(command.encode('ascii') + b'\n')
