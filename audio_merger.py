import os
import re
import sys
import pyaudio
import time
import pydub

def merge(dir, format, export_file):
    """
        Method used to merge all files in a dir.
    """
    # Create an dumb audio_segment.
    merged = pydub.AudioSegment.silent(10)

    # list all file in a dir with format passed as param.
    files = [file for file in os.listdir(dir) if (file.lower().endswith('.' + format))]
    files.sort()

    for file in sorted(files):
        print(file)
        path = os.path.join(dir, file)
        data = pydub.AudioSegment.from_file(path, format=format)
        merged += data

    merged.export(export_file, format=format)

# Call main program.
if __name__ == "__main__":

    if len(sys.argv) != 4:
        raise Exception("Usage: python audio_merger.py input_dir_path export_file format")

    name, dir_path, export_file, format = sys.argv

    merge(dir_path, format, export_file)
