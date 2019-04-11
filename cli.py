import argparse
from utils import USER_LOGFILE, USER_CONFIG

def parse_arguments():
    """
        Method used for parse arguments passed by terminal.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collect', action="store_true",
                        help="Collect data as min, max avg")
    parser.add_argument('-l', '--log', nargs="?",
                        type=argparse.FileType('w'),
                        const=USER_LOGFILE, # used to create file if user don't specify filename.
                        help="Write data on file as text")
    parser.add_argument('-r', '--record',
                        action="store_true",
                        #const=USER_RECORDFILE, # used to create file if user don't specify filename.
                        help="Write data on files as audio")
    parser.add_argument('-s', '--seconds',
                        type=int,
                        help="Time during record data")
    parser.add_argument('-ca', '--calibrate', action="store_true",
                        help="Calibrate input audio device")
    parser.add_argument('-sh', '--showindex', action="store_true",
                        help="Show input device index")
    parser.add_argument('-se', '--setindex', type=int,
                        help="Set input device index")
    parser.add_argument('-f', '--format', type=str,
                        nargs="?", const="mp3",
                        help="Set exportation format")
    #parser.add_argument('-b', '--bitrate', type=int,
    #                    const="256", nargs="?",
    #                    help="Set exportation bitrate")
    parser.add_argument('-to', '--trashesoutput', action="store_true",
                        help="Flag used for test, to redirect stdout on /dev/null")

    args = parser.parse_args()

    if args.calibrate and (args.log or args.record or args.seconds or args.collect or args.showindex or args.setindex or args.format or args.trashesoutput):
        raise parser.error("Calibrate flag can't be used with others flags")

    if args.showindex and (args.log or args.record or args.seconds or args.collect or args.calibrate or args.setindex or args.format or args.trashesoutput):
        raise parser.error("Show index flag can't be used with others flags")

    if args.setindex and (args.log or args.record or args.seconds or args.collect or args.calibrate or args.showindex or args.format or args.trashesoutput):
        raise parser.error("Set index flag can't be used with others flags")

    if args.seconds:
        if args.seconds < 0:
            raise parser.error("Second's number must be positive")

    if args.setindex:
        if args.setindex < 0:
            raise parser.error("Input device index must be positive")

    if args.seconds:
        if args.seconds > (3600 * 24): # Number of seconds in a day.
            raise parser.error("Number of seconds too large --> Note max is 86400s (seconds in a day)")

    if args.format:
        if args.format not in ['mp3', 'ogg', 'wav']: # possible formats.
            raise parser.error("Insert standard format {} !".format("mp3 - wav - ogg"))

    #if args.bitrate:
    #    if args.bitrate not in [128, 256, 320]: # possible bitrates.
    #        raise parser.error("Insert standard bitrate 128 - 256 - 320 !")

    if args.format and not args.record:
        raise parser.error("Format and Bitrate can be specified only with record.")

    return args

def get_args():
    """
        Returns dictionary created with key-value params passed to program.
    """
    kargs = dict(parse_arguments()._get_kwargs());
    return kargs;
