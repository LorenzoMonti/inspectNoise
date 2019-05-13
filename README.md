# inspectNoise
Real-time sound meter.

The file requiremets.txt contains libraries that need to be installed.

To know available flags use:

        python3 inspect_noise --help

Flags:
    -c/ --collect: collect data as Min, Max and Avg.
    -l/--log [file]: log of recorded data as text file. [file] is an optional params, if not specified, program will save log on a file (name: log.log) in ~/.inspectNoise/ hidden folder.
    -r/--record threshold: record audio when dB are on average higher than the specified threshold. Timestamp used as name of audio file.
    -s/--seconds seconds: specify recording time.
    -sh/--showindex: it is useful for know index of input audio devices available.
    -se/--setindex index: used to set index of input microphone (writing on configuration file).
    -f/--format [mp3, wav, ogg]: define format of output record. It can be used only with --record.
    -to/--thrashesoutput: used for debug or utility, when specified permit to not show output on terminal.
    -ca/--calibrate: To be implemented.

After first use the tool creates a hidden folder with name ".inspectNoise" in ~ (user dir).
In this directory will be created (after using flag --record for the first time) a new
directory with name gathered_mp3. Within this folder will be saved recorded data in sub-folder
with date of recoded day.

In the project directory are included 2 more utils file.
  - First is plotter.py that can be ran separately to create graphs starting from a log file
    (created with flag --log). The output will be located in "plot_data" folder, located in
    ".inspect_noise" folder.
  - Second is audio_merger.py that it can be used to merge audio in a specific folder.
