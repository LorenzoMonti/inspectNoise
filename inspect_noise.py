from cli import get_args
from utils import setup_user_dir
import signal
from noise_observer import NoiseObserver

def main():
    """
        Entry point of application.
    """
    setup_user_dir();

    kargs = get_args()

    noise_observer = NoiseObserver()

    #noise_observer.start()

# Signal handlers
# This function is called when termination signal event occur.
def sigint_handler(signum, frame):
    """
        Termination Signal Handler.
    """
    #noise_observer.graceful()

# This function/Handler will be called when a SIGALARM event occur.
# This event is generated when timeout (seconds set by command line interface) expired.
def sigalrm_handler(signum, frame):
    """
        SEGALAERM Handler.
    """
    #noise_observer.timeout()


# Register signal handlers.
signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGALRM, sigalrm_handler)

# Call main program.
if __name__ == "__main__":
    main()
