import argparse
from utils import USER_LOGFILE, USER_CONFIG, USER_RECORDFILE

def parse_arguments():
    """
        Method used for parse arguments passed by terminal.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collect', action="store_true",
                        help="Collect data as min, max avg")
    parser.add_argument('-l', '--log', nargs="?",
                        type=argparse.FileType('a'),
                        const=USER_LOGFILE, # used to create file if user don't specify filename.
                        help="Write data on file as text")
    parser.add_argument('-r', '--record', nargs="?",
                        type=argparse.FileType('a'),
                        const=USER_RECORDFILE, # used to create file if user don't specify filename.
                        help="Write data on file as audio")
    parser.add_argument('-s', '--seconds',
                        type=int,
                        help="Time during record data")
    parser.add_argument('-a', '--calibrate', action="store_true",
                        help="Calibrate input audio device")

    args = parser.parse_args()

    if args.calibrate and (args.log or args.record or args.seconds or args.collect):
        raise parser.error("Calibrate flag can't be used with others flags")

    if args.seconds:
        if args.seconds < 0:
            raise parser.error("Second's number must be positive")

    return args

def get_args():
    """
        Returns dictionary created with key-value params passed to program.
    """
    kargs = dict(parse_arguments()._get_kwargs());
    return kargs;
