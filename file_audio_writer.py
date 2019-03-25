import pydub
from threading import Thread
from utils import create_audio_file

class FileAudioWriter(Thread):

    def __init__(self, queue, bitrate, format, file):
        """
            Constructor.
            :queue: global queue used to communicate with buffered writer.
            :bitrate: bitrate used to write audio on file.
            :format: export format.

            Bitrate and format are specified by user.
        """
        Thread.__init__(self)
        self.queue = queue
        self.bitrate = bitrate
        self.format = format
        self.file = file
        create_audio_file(self.file)

    def run(self):
        while True:
            # Block until data are available.
            data = self.queue.get()

            self.write_on_file(data)

    def write_on_file(self, data):
        # Create an empty audio segment.
        merged = pydub.AudioSegment.empty()

        # Convert byte data into audio segment
        new_data = pydub.AudioSegment(data)

        # Reads old data from file.
        stored_data = pydub.AudioSegment.from_file(self.file)

        # Merge audio data.
        merged = stored_data + new_data

        # Write merged audio segment on file.
        merged.export(self.file, format=str(self.format), bitrate=str(self.bitrate)+"k")
