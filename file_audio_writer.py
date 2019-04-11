import pydub
import sys
import os
import wave
from threading import Thread
from utils import create_audio_file
from config_manager import ConfigManager
from io import BytesIO

class FileAudioWriter(Thread):

    def __init__(self, queue, format, file, audio):
        """
            Constructor.
            :queue: global queue used to communicate with buffered writer.
            :format: export format.

            Format is specified by user.
        """
        Thread.__init__(self)
        self.queue = queue
        self.format = format
        self.file = file
        self.recorder = BytesIO()

        self.config = ConfigManager()
        self.audio = audio

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
        print("\n\t Printing on file")
        print("In memory Wav")
        # StringIO passed as first param to write into memory buffer.
        w = wave.open(self.recorder, 'wb')

        # Setting params of wav.
        w.setnchannels(self.config.CHANNELS)
        w.setsampwidth(self.audio.get_sample_size(self.config.FORMAT))
        w.setframerate(self.config.RATE)

        for frame in data:
            w.writeframes(b''.join(frame))

        w.close()
        print("Create audio segment")
        new_data = pydub.AudioSegment(self.recorder.getvalue())
        print("Import file")
        stored_data = pydub.AudioSegment.from_file(self.file, format=self.format)
        print("Merging")
        merged = stored_data + new_data
        print("Export")
        merged.export(self.file, format=self.format)

        self.recorder.seek(0)
