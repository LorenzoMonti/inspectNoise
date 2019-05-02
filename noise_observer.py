import pyaudio
import pydub
import os
import logging
import wave
import signal
import time
import sys
import numpy as np
from config_manager import ConfigManager
from io import BytesIO as StringIO
from utils import noalsaerr, coroutine, create_audio_dir
from buffered_writer import *

class NoiseObserver(object):

    SEC = 10 # Dimension in seconds of window.

    def __init__ (self, seconds = None, log = None,
                  collect = False, record = None,
                  format = None, trashesoutput = False):
        """
            :seconds: if flag was set it is the number of seconds when we need to monitor noise.
            :log: if flag is set, it represent name of log file.
            :collect: if this flag is set we need to collect and calculate min, max avg of data.
            :record: if this flag is set contains the name of audio file into record.
            :format: if is set contains export format.
        """
        self.config_manager = ConfigManager() # Get singletoon instance of configuration manager.

        # Save param passed as local variables.
        self.log = log
        self.seconds = seconds
        self.collect = collect
        self.record_thr = record
        self.trashes = trashesoutput

        #if not bitrate:
        #    self.bitrate = 256 # Default value.
        #else:
        #    self.bitrate = bitrate
        if not format:
            self.format = "mp3" # Default value.
        else:
            self.format = format

        self.is_running = False
        self.alive = True
        self.end_message = ""
        self.output = StringIO()
        self.data_stats = None
        self.audio_writer = None
        self.recorded_frames = []

        if self.trashes:
            # For testing redirect output to null.
            self.trash = open('/dev/null', 'w')
            sys.stdout = self.trash

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
            self.setup_log()
        if self.collect:
            self.data_stats = dict()
        if self.record_thr:
            self.setup_record()

    @coroutine
    def record_generator(self):
        """
            Record PyAudio into memory buffer (StringIO).
        """
        while True:
            frames = [] # List of already read frames.
            self.stream.start_stream()
            for i in range(self.num_frames):
                # Reads FRAMES_PER_BUFFER chunks.
                # Second param allow to avoid input overflow exceptions.
                data = self.stream.read(self.config_manager.FRAMES_PER_BUFFER, exception_on_overflow = False)
                frames.append(data)

            # Positioning index on the start of the buffer.
            self.output.seek(0)

            # StringIO passed as first param to write into memory buffer.
            w = wave.open(self.output, 'wb')

            # Setting params of wav and write frames on memory.
            w.setnchannels(self.config_manager.CHANNELS)
            w.setsampwidth(self.audio.get_sample_size(self.config_manager.FORMAT))
            w.setframerate(self.config_manager.RATE)
            w.writeframes(b''.join(frames))
            w.close()

            # Collect frames into list used to record audio.
            self.recorded_frames = frames #list(frames)
            yield

    def start_monitoring(self):
        """
            Method called to start monitoring.
        """
        # Audio segment length recorded in seconds.
        segment = self.config_manager.AUDIO_SEGMENT_LENGTH

        # Calculate number of frames.
        # We have 2048 frame per buffer.
        # Our sampling rate is 44100 (elements for each seconds).
        # If we divide our sampling rate for the number of frame in buffer we have the number of
        # buffer necessary to contain our samplings.
        #
        # See: https://stackoverflow.com/questions/35970282/what-are-chunks-samples-and-frames-when-using-pyaudio
        self.num_frames = int(self.config_manager.RATE / self.config_manager.FRAMES_PER_BUFFER * segment)

        if self.seconds:
            # First param means that timer is decremented at real time.
            # Seconds params indicate number of seconds.
            # When the time expired will be generated a SIGALRM signal (Handler for this signal in inspect_noise).
            signal.setitimer(signal.ITIMER_REAL, self.seconds)

        if self.collect:
            print("Collectiong db values...")
        if self.record_thr:
            print("Record values on audio files in ~/.inspectNoise/gathered_mp3/ with treshold fixed to {}...".format(self.record_thr))
        if self.log:
            print("Write values on a log file {}...".format(self.log.name))

        self.is_running = True

        # Generator of audio frames.
        record = self.record_generator()

        while self.alive:
            record.send(True)

            recorded_data = self.output.getvalue() # Getting value writed in memory buffer by record.
            segment = pydub.AudioSegment(recorded_data) # Created audio segment by data recorded.

            dbSPL = self.convert_to_spl(segment.rms) # Convert rms in dbSPL.

            if self.collect:
                self.collect_data(dbSPL)
            if self.log:
                self.file_logger.info(dbSPL)
            if self.record_thr:
                self.record_action(dbSPL)
                #del self.recorded_frames[:]

            # Always print data on stdout.
            sys.stdout.write('\r%10d  dbSPL' % dbSPL)
            sys.stdout.flush()

        self.is_running = False
        self.close_stream()

    def close_stream(self):
        """
            Method called after monitoring ending.
        """
        self.stream.stop_stream()
        self.audio.terminate()

        # If record flag was specified we need to clean buffer.
        if self.record_thr:
            # Write last data on file.
            self.audio_writer.buffer_fflush()

        sys.stdout.write("\n")

        if self.collect:
            print("Min: {:.2f}".format(self.data_stats['min']))
            print("Max: {:.2f}".format(self.data_stats['max']))
            print("Avg: {:.2f}".format(self.data_stats['avg']))

        sys.stdout.write("\n{}\n".format(self.end_message))

        # If trashes flag was setted by user, close
        # file (/dev/null).
        if self.trashes:
            self.trash.close()

    def stop_monitoring(self):
        """
            Method called to stop monitoring of sound.
            When this method is called allow to terminate current record.
        """
        self.alive = False
        self.end_message += "Recoring stooped..."

    def timeout(self):
        """
            Method called when time expired.
        """
        self.end_message = "Time expired...\n"
        self.stop_monitoring()

    def is_monitoring(self):
        """
            Return noise observer status.
        """
        return self.is_running

    def collect_data(self, dbSPL):
        """
            Method used to collect data as min, max and avg.
        """
        if self.data_stats:
            self.data_stats['min'] = min(dbSPL, self.data_stats['min'])
            self.data_stats['max'] = max(dbSPL, self.data_stats['max'])
            self.data_stats['avg'] = (dbSPL + self.data_stats['avg']) / 2
        else:
            self.data_stats['min'] = dbSPL
            self.data_stats['max'] = dbSPL
            self.data_stats['avg'] = dbSPL

    def record_action(self, dbSPL):
        """
            Decide if start record checking values of record window.
        """
        self.window[0, self.value_index] = dbSPL
        self.value_index =  int((self.value_index + 1) % self.window_size)
        #print("\n" + str(self.value_index))

        # Calculate average noise level.
        # See: https://www.cirrusresearch.co.uk/blog/2013/01/noise-data-averaging-how-do-i-average-noise-measurements/
        average_mean = self.window / 10
        average_mean = 10 ** average_mean
        mean = np.sum(average_mean) / 10
        mean = 10 * np.log10(mean)
        #print("Media: " + str(mean))

        # If average noise level is upper then threshold register.
        if mean >= self.record_thr:
            #print("Accumulo dati sopra la media")
            self.audio_writer.write(self.recorded_frames.copy())
        else:
            #print("Non accumulo")
            self.audio_writer.clear_buffer()

    def setup_log(self):
        """
            Method used to setup log on text file.
        """
        self.file_logger = logging.basicConfig(
            filename = self.log.name, # Name of the file passed by CLI.
            format = "%(asctime)s %(message)s", # Format date_time data.
            level = logging.INFO)
        self.file_logger = logging.getLogger(__name__) # Get personalized logger.

    def setup_record(self):
        """
            Method used to create file for setup record file.
        """
        # Create audio file used as base to record.
        self.record_dir = create_audio_dir()
        self.audio_writer = BufferedWriter(self.format, self.audio, self.record_dir)
        self.window_size = int(self.SEC // self.config_manager.AUDIO_SEGMENT_LENGTH)

        # Init value of window setted ro 30db (min value recorded).
        self.window = np.full((1, self.window_size), 30.0) #[30 for _ in range(self.window_size)]
        self.value_index = 0

    def convert_to_spl(self, rms):
        """
            Sound Pressure Level - defined as 20 * log10(p/p0),
            where p is the RMS of the sound wave in Pascals and p0 is
            20 micro Pascals.
            Since we would need to know calibration information about the
            microphone used to record the sound in order to transform
            the PCM values of this audiosegment into Pascals, we can't really
            give an accurate SPL measurement.
            However, we can give a reasonable guess that can certainly be used
            to compare two sounds taken from the same microphone set up.
            Be wary about using this to compare sounds taken under different recording
            conditions however, except as a simple approximation.
            Returns a scalar float representing the dB SPL of this audiosegment.

            See: https://github.com/MaxStrange/AudioSegment/blob/master/audiosegment.py
        """

        PASCAL_TO_PCM_FUDGE = 1000
        P_REF_PASCAL = 2E-5
        P_REF_PCM = P_REF_PASCAL * PASCAL_TO_PCM_FUDGE

        ratio = rms / P_REF_PCM
        return 20.0 * np.log10(ratio + 1E-9)  # 1E-9 for numerical stability.
