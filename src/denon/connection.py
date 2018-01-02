import time
from telnetlib import Telnet

"""
Connects to a Denon AVR-X1400H receiver via telnet and sends commands that line
up with with the Denon AVR Spec

author: Sonja Leaf <avleaf@gmail.com>
"""
class DenonConnection(object):
    """POSTS commands to Denon API server"""
    def __init__(self, api_host, port, trigger_map):
        self._api_host = api_host
        self._port = port
        self._connection = None
        self.action_map = trigger_map

    def process_command_string(self, words, text):
        command = self.action_map.mapped_trigger(words, text)
        self.send(command)
        return command


    def connector(self):
        if self._connection is None or not self._connection.sock_avail():
            self._connection = Telnet()
            self._connection.open(self._api_host, self._port)
            time.sleep(4)
        return self._connection


    def send(self, command):
        if b"ZMON\r" in command:
            self.connector().write(b"ZMON\r")
            command = command.replace(b"ZMON\r", b"")
            time.sleep(7)
        self.connector().write(command)
