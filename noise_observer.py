import pyaudio
import pydub
import os
import logging
import wave
import signal
import time
from config_manager import ConfigManager
from io import BytesIO as StringIO
from utils import noalsaerr

class NoiseObserver(object):

    def __init__ (self, seconds = None, log = None,
                  collect = False, record = None,
                  bitrate = None, format = None):
        """
            :seconds: if flag was set it is the number of seconds when we need to monitor noise.
            :log: if flag is set, it represent name of log file.
            :collect: if this flag is set we need to collect and calculate min, max avg of data.
            :record: if this flag is set contains the name of audio file into record.
            :bitrate: if this flag is set contains the bitrate for printing file.
            :format: if is set contains export format.
        """
        self.config_manager = ConfigManager() # Get singletoon instance of configuration manager.

        # Save param passed as local variables.
        self.log = log
        self.seconds = seconds
        self.collect = collect
        self.record = record
        self.bitrate = bitrate
        self.format = format

        self.is_running = False
        self.output = StringIO()

        # Load C lib necessary for audio record.
        with noalsaerr():
            self.audio = pyaudio.PyAudio()

        # Initialize input PyAudio stream.
        self.stream = self.audio.open(
            format = self.config_manager.FORMAT,
            channels = self.config_manager.CHANNELS,
            input_device_index = self.config_manager.INPUT_DEVICE_INDEX,
            input = True,
            rate = self.config_manager.RATE,
            frames_per_buffer = self.config_manager.FRAMES_PER_BUFFER)

        if self.log:
            setup_log()

    def record(self):
        """
            Record PyAudio into memory buffer (StringIO).
        """
        while True:
            frames = [] # list of already read freames.
            self.stream.start_stream()
            for i in range(self.num_frames):
                # Reads FRAMES_PER_BUFFER chunks.
                data = self.stream.read(self.config_manager.FRAMES_PER_BUFFER)
                frames.append(data)
                
            # Positioning index on the start of the buffer.
            self.output.seek(0)

            # StringIO passed as first param to write into memory buffer.
            w = wave.open(self.output, 'wb')

            # Setting params of wav
            w.setnchannels(self.config_manager.CHANNELS)
            w.setsampwidth(self.audio.get_sample_size(self.config_manager.FORMAT))
            w.setframerate(self.config_manager.RATE)
            w.writeframes(b''.join(frames))
            w.close()
            yield

    def start_monitoring(self):
        """
            Method called to start monitoring.
        """
        self.is_running = True
        while self.alive:
            pass

    def stop_monitoring(self):
        """
            Method called to stop monitoring of sound.
        """
        self.is_running = False
        self.alive = False

    def is_running(self):
        """
            Return noise observer status.
        """
        return self.is_running

    def setup_log(self):
        """
            Method used to setup log on text file.
        """
        self.logger_file = logging.basicConfig(
            filename = self.log, # Name of the file passed by CLI.
            format = "%(asctime)s %(message)s", # Format date_time data.
            level = logging.INFO)
        self.logger_file = logging.getLogger(__name__) # Get logger personalized logger.
