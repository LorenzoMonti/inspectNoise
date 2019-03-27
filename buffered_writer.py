import wave
import sys
from queue import Queue
from io import BytesIO as StringIO
from file_audio_writer import *
from config_manager import ConfigManager

class BufferedWriter(object):

    UPPER_BOUND = 20 * 2e6 # Max dimension of buffer before writing on audio file. (20Mb)

    def __init__(self, bitrate, format, file_name):
        """
            Constructor for this class.
        """
        self.buffer = StringIO()
        self.queue = Queue()
        self.worker = FileAudioWriter(self.queue, bitrate, format, file_name)
        self.worker.daemon = True
        self.worker.start()
        self.config_manager = ConfigManager()

    def write(self, audio_segment):
        """
            Method call to written of file.
        """
        self.buffer.write(audio_segment)

        # Debug print.
        print("\nAudio length: " + str(sys.getsizeof(audio_segment)))
        print("Buffer length: " + str(sys.getsizeof(self.buffer)))

        if sys.getsizeof(self.buffer) >= self.UPPER_BOUND:
            self.queue.put(self.buffer.getvalue())

            # Positioning index on the start of the buffer.
            self.buffer.seek(0)

    def buffer_fflush(self):
        """
            Method called at the end of record to fflush the buffer and write on file
            last data.
        """
        data = self.buffer.getvalue()
        if data:
            self.queue.put(data)
            print("Thread NOT joined")
            # Waits until the queue is empty
            self.queue.join()
            print("Thread joined")
