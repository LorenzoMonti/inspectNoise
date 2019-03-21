from cli import get_args
from utils import setup_user_dir, show_device_index_list
from config_manager import ConfigManager
import signal
from noise_observer import NoiseObserver

noise_observer = None

def main():
    """
        Entry point of application.
    """
    setup_user_dir();

    # Register signal handlers.
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGALRM, sigalrm_handler)

    conf_manager = ConfigManager()

    kargs = get_args()
    print(kargs)
    # if one of these three flags is used on program we run correct function;
    # otherwhise run instance of NoiseObserver.
    if kargs['showindex']:
        show_device_index_list()
    elif kargs['setindex'] != None: # If kargs['setindex'] is 0 condition is false withut != None.
        conf_manager.write_device_index('input_device_index', kargs['setindex'])
    elif kargs['calibrate']:
        # Call to start calibration function
        pass
    else:
        del kargs['showindex']
        del kargs['setindex']
        del kargs['calibrate']
        noise_observer = NoiseObserver(**kargs)
        noise_observer.start_monitoring()

# Signal handlers+

# This function is called when termination signal event occur.
def sigint_handler(signum, frame):
    """
        Termination Signal Handler.
    """
    if noise_observer:
        noise_observer.stop_monitoring()

# This function/Handler will be called when a SIGALARM event occur.
# This event is generated when timeout (seconds set by command line interface) expired.
def sigalrm_handler(signum, frame):
    """
        SEGALARM Handler.
    """
    noise_observer.timeout()

# Call main program.
if __name__ == "__main__":
    main()
