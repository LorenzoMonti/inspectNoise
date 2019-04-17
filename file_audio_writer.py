import pydub
import sys
import os
import wave
import time
from threading import Thread
from utils import AUDIO_DIR
from config_manager import ConfigManager
from io import BytesIO

class FileAudioWriter(Thread):

    def __init__(self, queue, format, audio, record_dir):
        """
            Constructor.
            :queue: global queue used to communicate with buffered writer.
            :format: export format.

            Format is specified by user.
        """
        Thread.__init__(self)
        self.queue = queue
        self.format = format
        self.recorder = BytesIO()

        self.config = ConfigManager()
        self.audio = audio
        self.record_dir = record_dir

    def run(self):
        while True:
            # Block until data are available.
            data = self.queue.get()

            self.write_on_file(data)

            # Thread set task done only if queue is empty.
            if self.queue.empty():
                self.queue.task_done()

    def write_on_file(self, data):
        # Convert byte data into audio segment
        #new_data = pydub.AudioSegment(data)

        # Reads old data from file.
        #stored_data = pydub.AudioSegment.from_file(self.file, format=self.format)

        # Merge audio data.
        #merged = stored_data + new_data

        # Write merged audio segment on file.
        #merged.export(self.file, format=self.format)
        #new_data.export(fname, format=self.format)
        print("\n\tPrinting on file")
        # StringIO passed as first param to write into memory buffer.
        w = wave.open(self.recorder, 'wb')

        # Setting params of wav.
        w.setnchannels(self.config.CHANNELS)
        w.setsampwidth(self.audio.get_sample_size(self.config.FORMAT))
        w.setframerate(self.config.RATE)

        for frame in data:
            w.writeframes(b''.join(frame))

        w.close()

        new_data = pydub.AudioSegment(self.recorder.getvalue())

        file_name = str(int(time.time())) #time.strftime("%Y%m%d-%H%M%S")

        file_path = os.path.join(self.record_dir, file_name + "." +self.format)
        #stored_data = pydub.AudioSegment.from_file(self.file, format=self.format)

        #merged = stored_data + new_data

        #merged.export(self.file, format=self.format)

        new_data.export(file_path, format=self.format)

        self.recorder.seek(0)
