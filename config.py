import os
from utils import USER_CONFIG, PROG
import configparser
import pyaudio

class Config(object):
    """
        Class used to read configuration file.
    """
    FRAMES_PER_BUFFER = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    INPUT_DEVICE_INDEX = None # da modificare! E' necessario specificare l'Index del device di input appropriato.
                              # Nel nostro caso bisogna selezionare il microfono.
    RATE = 44100
    AUDIO_SEGMENT_LENGTH = 0.5

    def __init__ (self):

        config = configparser.ConfigParser()

        if not os.path.exists(USER_CONFIG):
            config[PROG] = {
                'frame_per_buffer': '2048',
                'format': '8',
                'channels': '2',
                'rate': '44100',
                'audio_segment_length': '0.5',
                'input_device_index': '0'
            }

            with open(USER_CONFIG, "w") as conf_file:
                config.write(conf_file)
        else:
            config_items = dict()

            config.read(USER_CONFIG)

            if not config.has_section(PROG):
                raise Exception("Default section not found in configuration file")

            for key, value in config.items(PROG):
                if key in ['frame_per_buffer', 'format', 'channels', 'input_device_index', 'rate']:
                    config_items[key] = int(value)
                elif key in ['audio_segment_length']:
                    config_items[key] = float(value)
                else:
                    raise Exception("Param {} in configuration file not recognized".format(key))

            for key, value in config_items.items():
                setattr(self, key.upper(), value)

            print(config_items)
