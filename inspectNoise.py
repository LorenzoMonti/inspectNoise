from cli import get_args
from utils import setup_user_dir
import config

def main():
    """
        Entry point of application.
    """
    setup_user_dir();
    config.Config()
    kargs = get_args()

if __name__ == "__main__":
    main()
