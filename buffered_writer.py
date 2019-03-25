import wave
import sys
from queue import Queue
from io import BytesIO as StringIO
from file_audio_writer import *

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

    def write(self, audio_segment):
        """
            Method call to writed of file.
        """
        self.buffer.write(audio_segment)

        if sys.getsizeof(self.buffer) >= self.UPPER_BOUND:
            queue.put(self.buffer.getValue())

            # Positioning index on the start of the buffer.
            self.buffer.seek(0)

    def buffer_fflush(self):
        """
            Method called at the end of record to fflush the buffer and write on file
            last data.
        """
        if self.buffer.getvalue():
            self.queue.put(self.buffer.getvalue())

            # Waits until the queue is empty
            self.queue.join()
