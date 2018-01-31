import os, sys
import device_details
from denon import actions, triggers
from denon.connection import DenonConnection
from roku import Roku
# import roku and light commands



class Scene():
    """docstring for Scene"""
    def __init__(self, connection=None, roku=None):
        self._connection = connection
        self._commands = []
        self._triggers = None
        self._hints = None
        self._roku = roku

    def send(self, commands):
        if commands is not None:
            for command in commands:
                # add logging here
                command()

    @property
    def connection(self):
        if not self._connection:
            self._connection = DenonConnection(
                device_details.denon_ip_address(), 23)
        return self._connection

    @property
    def roku(self):
        if not self._roku:
            self._roku = Roku.discover(timeout=5)[0]
        return self._roku

    @property
    def trigger_phrases(self):
        if not self._triggers:
            self._triggers = []
        return self._triggers

    @property
    def hints(self):
        if not self._hints:
            self._hints = []
        return self._hints


class XboxGameScene(Scene):
    """docstring for XboxGameScene"""
    def __init__(self):
        super().__init__(self)
        self._triggers = [
            "xbox time",
            "play games",
            "blow stuff up",
            "blow up",
            "shoot",
            "play video games",
            "video games",
            "games",
            "game",
            "video games",
            "race",
            "racing"
        ]
        self._commands = [self.xbox_game_mode]


    def xbox_game_mode(self):
        for action in actions.xbox_game():
            self._connection.send(action)



