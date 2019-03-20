from cli import get_args
from utils import setup_user_dir, show_device_index_list
from config_manager import ConfigManager
import signal
from noise_observer import NoiseObserver

def main():
    """
        Entry point of application.
    """
    setup_user_dir();

    conf_manager = ConfigManager()

    kargs = get_args()

    print(kargs) #DEBUG

    # if one of these three flags is used on program we run correct function;
    # otherwhise run instance of NoiseObserver.
    if kargs['showindex']:
        show_device_index_list()
    elif kargs['setindex']:
        conf_manager.write_device_index('input_device_index', kargs['setindex'])
    elif kargs['calibrate']:
        # Call to start calibration function
        pass
    else:
        noise_observer = NoiseObserver(conf_manager, **kargs)

    #noise_observer.start()

# Signal handlers
# This function is called when termination signal event occur.
def sigint_handler(signum, frame):
    """
        Termination Signal Handler.
    """
    #noise_observer.graceful() # CALL METHOD TO STOP NOISE OBSERVER

# This function/Handler will be called when a SIGALARM event occur.
# This event is generated when timeout (seconds set by command line interface) expired.
def sigalrm_handler(signum, frame):
    """
        SEGALAERM Handler.
    """
    #noise_observer.timeout() CALL METHOD TO STOP NOISE OBSERVER


# Register signal handlers.
signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGALRM, sigalrm_handler)

# Call main program.
if __name__ == "__main__":
    main()
