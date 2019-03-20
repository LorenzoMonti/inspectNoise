import os
from utils import USER_CONFIG, PROG
import configparser
import pyaudio

class ConfigManager(object):
    """
        Class used to create/read configuration file.
    """

    _config = None # Instance of configuration reader.

    FRAMES_PER_BUFFER = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    INPUT_DEVICE_INDEX = None # Run showInputDeviceIndex utils to discover index and name of input devices.
    RATE = 44100
    AUDIO_SEGMENT_LENGTH = 0.5

    def __init__ (self):

        self._config = configparser.ConfigParser()

        # If configuration file doesn't exist in user dir. create it.
        if not os.path.exists(USER_CONFIG):
            self._config[PROG] = {
                'frame_per_buffer': '2048',
                'format': '8',
                'channels': '2',
                'rate': '44100',
                'audio_segment_length': '0.5',
                'input_device_index': '2'
            }

            with open(USER_CONFIG, "w") as conf_file:
                _config.write(conf_file)

        # If configuration file already exist in user dir. read it.
        else:
            config_items = dict()

            self._config.read(USER_CONFIG) # Read configuration file.

            if not self._config.has_section(PROG):
                raise Exception("Default section not found in configuration file")

            # Extract key-values pair from file and update our configuration list.
            for key, value in self._config.items(PROG):
                if key in ['frame_per_buffer', 'format', 'channels', 'input_device_index', 'rate']:
                    config_items[key] = int(value)
                elif key in ['audio_segment_length']:
                    config_items[key] = float(value)
                else:
                    raise Exception("Param {} in configuration file not recognized".format(key))

            for key, value in config_items.items():
                # Set attribute read by configuration file in the class-attribute.
                setattr(self, key.upper(), value)


    def write_device_index(self, index):
        print(index)
        print(self._config)
        if not self._config is None:
            self._config[PROG]['input_device_index'] = str(index);
            with open(USER_CONFIG, 'w') as configfile:
                self._config.write(configfile)
