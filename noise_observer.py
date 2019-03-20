import pyaudio
import pydub
import os
from config_manager import ConfigManager

class NoiseObserver(object):

    def __init__ (self, cnf_mng, seconds = None, calibrate = False, log = None,
                  collect = False, record = None, showindex = False,
                  setindex = None):
        config_manager = cnf_mng

    #def start(self):

    #def stop():

    #def is_running()
