import os
from ctypes import *
import stat
import pyaudio
import pydub
import datetime
from contextlib import contextmanager

# Glabal variables used by all program.
PROG = 'inspectNoise'
USER_DIR = os.path.join(os.path.expanduser('~'), '.' + PROG)
USER_LOGFILE = os.path.join(USER_DIR, 'log.log')
USER_CONFIG = os.path.join(USER_DIR, 'config.cnf')
#USER_RECORDFILE = os.path.join(USER_DIR, 'record.mp3')
PLOT_DIR = os.path.join(USER_DIR, 'plot_data')
AUDIO_DIR = os.path.join(USER_DIR, 'gathered_mp3')

d = os.path.dirname(__file__)
PROJECT_PATH = os.path.abspath(d)

def create_run_script(script_name, tmp_name):
    """
        :script_name: name of python script that will use cli.
        :tmp_name: name of file where print resulting dictionary (used by python script).
    """
    run_script = os.path.join(PROJECT_PATH, script_name)
    content = "from cli import get_args\n"
    content += "kargs = get_args()\n"
    content += "with open(\"" + tmp_name + "\", 'w') as f:\n"
    content += "\tf.write(str(kargs))"
    if not os.path.exists(run_script):
        create_executable(run_script, content)

def create_executable(path, content):
    """
        :path: Path where create executable.
        :content: Contenet of script.
    """
    with open(path, 'w') as f:
        f.write(content)
    s = os.stat(path)
    os.chmod(path, s.st_mode | stat.S_IEXEC)

def setup_user_dir():
    """
        Create user directory.
    """
    if not os.path.exists(USER_DIR):
        os.makedirs(USER_DIR)

def create_plot_dir():
    """
        Create plot directory.
    """
    if not os.path.exists(PLOT_DIR):
        os.makedirs(PLOT_DIR)

#def create_audio_file(name, format):
#    """
#        Method used to crate empty audio file.
#    """
#    if not os.path.exists(name):
        # Create a dumb audio segment.
#        dumb_data = pydub.AudioSegment.silent(duration=100)

#        dumb_data.export(name, format=format)

def create_audio_dir():
    """
        Method used to create audio dir.
    """
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    day_dir = os.path.join(AUDIO_DIR, str(datetime.date.today()))
    if not os.path.exists(day_dir):
        os.makedirs(day_dir)

    return day_dir

# Method used to detect and show audio device index.
# Thanks to: https://stackoverflow.com/questions/36894315/how-to-select-a-specific-input-device-with-pyaudio
def show_device_index_list():
    """
        Method used to show input device list.
    """
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

# Work-around on error messages by alsa-lib
# http://stackoverflow.com/questions/7088672/
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int,
                               c_char_p, c_int, c_char_p)

# Handler routine for errors on loading libraries.
def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    """
        Method used to load C lib.
    """
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield

def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.__next__()
        return g
    return start
