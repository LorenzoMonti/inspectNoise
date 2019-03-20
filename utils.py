import os
from ctypes import *
import stat

# Glabal variables used by all program.
PROG = 'inspectNoise'
USER_DIR = os.path.join(os.path.expanduser('~'), '.' + PROG)
USER_LOGFILE = os.path.join(USER_DIR, 'log.log')
USER_CONFIG = os.path.join(USER_DIR, 'config.cnf')
USER_RECORDFILE = os.path.join(USER_DIR, 'record.wav')

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
