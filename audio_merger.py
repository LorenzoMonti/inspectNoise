import os
import sys
import pyaudio
import pydub

PATH = "./*.mp3"

#PATH = "~/inspectNoise/.tmp/*.mp3"

#def __init__(self, filename, input_format, output_format, bitrate):
#    self.input_format = input_format
#    self.output_format = output_format
#    self.bitrate = bitrate
#    self.filename = filename
#    self.PATH += input_format

def main():

#    merged = pydub.AudioSegment.silence(100)

#    print(str(self.PATH))

#    for f in os.listdir(self.PATH):
#        data = AudioSegment(f)
#        merged += data

#    merged.export(self.filename, format=output_format)

    merged = pydub.AudioSegment.silent(100)
    for i in range(0, 30):
        data = pydub.AudioSegment.from_mp3(str(i) + ".mp3")
        merged += data

    merged.export("merged.mp3", format="mp3")

# Call main program.
if __name__ == "__main__":
    main()
