import wave
import sys
from queue import Queue
from io import BytesIO as StringIO
from file_audio_writer import *
from config_manager import ConfigManager

class BufferedWriter(object):
    UPPER_BOUND = 20 * 1e6 # Max dimension of buffer before writing on audio file. (20Mb)
    SIZE = 50
    frames = []

    def __init__(self, bitrate, format, file_name, audio):
        """
            Constructor for this class.
        """
        self.buffer = StringIO()
        self.queue = Queue()
        self.worker = FileAudioWriter(self.queue, bitrate, format, file_name, audio)
        self.worker.daemon = True
        self.worker.start()

        # Added for testing wave memeory write.
        self.config_manager = ConfigManager()
        self.audio = audio

    def write(self, audio_frames):
        """
            Method call to write on file.
        """
        #self.buffer.write(audio_segment)

        # StringIO passed as first param to write into memory buffer.
        #w = wave.open(self.buffer, 'wb')

        # Setting params of wav.
        #w.setnchannels(self.config_manager.CHANNELS)
        #w.setsampwidth(self.audio.get_sample_size(self.config_manager.FORMAT))
        #w.setframerate(self.config_manager.RATE)
        #w.writeframes(b''.join(audio_segment))
        #w.close()

        self.frames.append(audio_frames)
        # Debug print.
        #print("\nAudio length: " + str(sys.getsizeof(audio_segment)))
        #print("Buffer length: " + str(sys.getsizeof(self.buffer)))
        #print("\n" + str(sys.getsizeof(self.buffer)))
        #print("\n" + str(self.UPPER_BOUND))

        #if sys.getsizeof(self.buffer) >= self.UPPER_BOUND:
        #    print("Buffer overflow.")

        #    self.queue.put(self.buffer.getvalue())

        #    self.buffer.close()

        #    self.buffer = StringIO() # Creating a new buffer.

            # Positioning index on the start of the buffer.
        #    self.buffer.seek(0)


        # PROVA BUFF List
        if len(self.frames) >= self.SIZE:
            print("\n\tMax list size reached...")
            self.queue.put(self.frames.copy())
            del self.frames[:]

        #PROVA SINGOLI
        #self.queue.put((self.buffer.getvalue(), self.PATH+str(self.c)+".mp3"))
        #self.c+=1
        #self.buffer = StringIO() # Creating a new buffer.


    def buffer_fflush(self):
        """
            Method called at the end of record to fflush the buffer and write on file
            last data.
        """
        #data = self.buffer.getvalue()
        #if sys.getsizeof(data) > 0:
        #    self.queue.put(data)

            # Waits until the queue is empty
        #    self.queue.join()
        print("\n\t fflush")
        if len(self.frames) > 0:
            self.queue.put(self.frames.copy())
            self.queue.join()
