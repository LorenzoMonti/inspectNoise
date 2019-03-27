import wave
import sys
from queue import Queue
from io import BytesIO as StringIO
from file_audio_writer import *
from config_manager import ConfigManager

class BufferedWriter(object):
    c = 0
    UPPER_BOUND = 20 * 2e6 # Max dimension of buffer before writing on audio file. (20Mb)

    def __init__(self, bitrate, format, file_name, audio):
        """
            Constructor for this class.
        """
        self.buffer = StringIO()
        self.queue = Queue()
        self.worker = FileAudioWriter(self.queue, bitrate, format, file_name)
        self.worker.daemon = True
        self.worker.start()

        # Added for testing wave memeory write.
        self.config_manager = ConfigManager()
        self.audio = audio

    def write(self, audio_segment):
        """
            Method call to write on file.
        """
        #self.buffer.write(audio_segment)

        # StringIO passed as first param to write into memory buffer.
        w = wave.open(self.buffer, 'wb')

        # Setting params of wav.
        w.setnchannels(self.config_manager.CHANNELS)
        w.setsampwidth(self.audio.get_sample_size(self.config_manager.FORMAT))
        w.setframerate(self.config_manager.RATE)
        w.writeframes(b''.join(audio_segment))
        w.close()

        # Debug print.
        #print("\nAudio length: " + str(sys.getsizeof(audio_segment)))
        #print("Buffer length: " + str(sys.getsizeof(self.buffer)))

        #if sys.getsizeof(self.buffer) >= self.UPPER_BOUND:
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
            # Waits until the queue is empty
            self.queue.join()
