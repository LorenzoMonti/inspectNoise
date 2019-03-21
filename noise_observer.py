import pyaudio
import pydub
import os
import logging
import wave
import signal
import time
from config_manager import ConfigManager
from io import BytesIO as StringIO
from utils import noalsaerr, coroutine

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
        print("OPEN")
        # Initialize input PyAudio stream.
        self.stream = self.audio.open(
            format = self.config_manager.FORMAT,
            channels = self.config_manager.CHANNELS,
            input_device_index = self.config_manager.INPUT_DEVICE_INDEX,
            input = True,
            rate = self.config_manager.RATE,
            frames_per_buffer = self.config_manager.FRAMES_PER_BUFFER)
        print("END STREAM CREATION")
        if self.log:
            setup_log()
        if self.collect:
            data_stats = dict()

    @coroutine
    def record(self):
        """
            Record PyAudio into memory buffer (StringIO).
        """
        while True:
            frames = [] # List of already read frames.
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
        segment = self.config_manager.AUDIO_SEGMENT_LENGTH

        # See: https://stackoverflow.com/questions/35970282/what-are-chunks-samples-and-frames-when-using-pyaudio
        # Calculate number of frames.
        # We have 2048 frame per buffer.
        # Our sampling rate is 44100 (elements for each seconds).
        # If we divide our sampling rate for the number of frame in buffer we have the number of
        # buffer necessary to contain our samplings.
        # We use 2 CHANNELS so we have for each sampling 2 value replied, indeed we multiply this number for 0,5 (SEGMENT).
        # If we double channels number we have to divide by 4 the segment (0,25), because the set of useful value is 4 times
        # smaller.
        self.num_frames = int(self.config_manager.RATE / self.config_manager.FRAMES_PER_BUFFER * segment)

        if self.seconds:
            # First param means that timer is decremented at real time.
            # Seconds params indicate number of seconds.
            # When the time expired will be generated a SIGALRM signal (Handler for this signal in inspect_noise).
            signal.setitimer(signal.ITIMER_REAL, self.seconds)

        if self.collect:
            print("Collectiong db values...")
        if self.record:
            print("Record values on audio file {}...".format(self.record))
        if self.log:
            print("Write values on a log file {}...".format(self.log))

        self.is_running = True

        # Generator of audio frame.
        record_gen = self.record()

        while self.alive:
            next(record_gen)

            recorded_data = self.output.getvalue() # Getting value writed in memory buffer by record.
            segment = pydub.AudioSegment(data) # Created audio segment by data recorded.

            dbSPL = segment.spl # Getting value of dbSPL by pydub.

            if self.collect:
                collect_data(dbSPL)
            if self.log:
                self.logger_file.info(dbSPL)
            if self.record:
                # Use thread to process audio data.
                pass

            # Always print data on stdout.
            sys.stdout.write('\r%10d  ' % dbSPL)
            sys.stdout.flush()

    def stop_monitoring(self):
        """
            Method called to stop monitoring of sound.
        """
        self.is_running = False
        self.alive = False
        self.stream.stop_stream()
        self.audio.terminate()

        if self.collect:
            print("Min: {}".format(self.data_stats['min']))
            print("Max: {}".format(self.data_stats['max']))
            print("Avg: {}".format(self.data_stats['avg']))

        print("Recording stopped...")

    def timeout(self):
        """
            Method called when time expired.
        """
        stop_monitoring()

        print("Time expired...")

    def is_running(self):
        """
            Return noise observer status.
        """
        return self.is_running

    def collect_data(self, dbSPL):
        if self.data_stats:
            self.data_stats['min'] = min(dbSPL, self.data_stats['min'])
            self.data_stats['max'] = max(dbSPL, self.data_stats['max'])
            self.data_stats['avg'] = dbSPL + self.data_stats['avg'] / 2
        else:
            self.data_stats['min'] = dbSPL
            self.data_stats['max'] = dbSPL
            self.data_stats['avg'] = dbSPL

    def setup_log(self):
        """
            Method used to setup log on text file.
        """
        self.logger_file = logging.basicConfig(
            filename = self.log, # Name of the file passed by CLI.
            format = "%(asctime)s %(message)s", # Format date_time data.
            level = logging.INFO)
        self.logger_file = logging.getLogger(__name__) # Get logger personalized logger.
