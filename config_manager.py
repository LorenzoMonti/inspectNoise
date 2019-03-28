import os
from utils import USER_CONFIG, PROG
import configparser
import pyaudio

class ConfigManager(object):
    """
        Class used to create/read configuration file.
    """

    _config_manager = None # Singletoon instance of this class.
    _config = None # Instance of configuration reader.

    FRAMES_PER_BUFFER = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 2 # check number of channel whit get_device_info_by_index(index)
    INPUT_DEVICE_INDEX = 0 # Run inspect_noise with --showindex for discover index and name of input devices.
    RATE = 44100
    AUDIO_SEGMENT_LENGTH = 1 # Audio segment length recorded in seconds.

    def __new__ (self):
        # if is not define create new instance otherwise return only instance of thi class.
        if not isinstance(self._config_manager, self):
            self._config_manager = object.__new__(self)
        return self._config_manager

    def __init__ (self):

        self._config = configparser.ConfigParser()

        # If configuration file doesn't exist in user dir. create it.
        if not os.path.exists(USER_CONFIG):
            self._config[PROG] = {
                'frames_per_buffer': '2048',
                'format': '8',
                'channels': '2',
                'rate': '44100',
                'audio_segment_length': '1',
                'input_device_index': '0'
            }

            with open(USER_CONFIG, "w") as conf_file:
                self._config.write(conf_file)

        # If configuration file already exist in user dir. read it.
        else:
            config_items = dict()

            self._config.read(USER_CONFIG) # Read configuration file.

            if not self._config.has_section(PROG):
                raise Exception("Default section not found in configuration file.")

            # Extract key-values pair from file and update our configuration list.
            for key, value in self._config.items(PROG):
                if key in ['frames_per_buffer', 'format', 'channels', 'input_device_index', 'rate']:
                    config_items[key] = int(value)
                elif key in ['audio_segment_length']:
                    config_items[key] = float(value)
                else:
                    raise Exception("Param {} in configuration file not recognized".format(key))

            for key, value in config_items.items():
                # Set attribute read from configuration file to the class-attribute.
                setattr(self, key.upper(), value)


    def write_device_index(self, param, index):
        """
            Method used to override param on configuration file.
        """
        if not self._config is None:
            self._config[PROG][param] = str(index);
            with open(USER_CONFIG, 'w') as configfile:
                self._config.write(configfile)

    def get_config_value(self, param):
        """
            Method used to read param from configuration file.
            (Used for test).
        """
        if self._config:
            return self._config[PROG][param]
        return None
