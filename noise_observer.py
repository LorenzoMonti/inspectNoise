import pyaudio
import pydub
import os
from config_manager import ConfigManager

class NoiseObserver(object):

    def __init__ (self, seconds = None, calibrate = False, log = None, collect = False, record = None):
        config_manager = ConfigManager()

    #def start(self):

    #def stop():

    #def is_running()
