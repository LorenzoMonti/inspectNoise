# inspectNoise
Real-time sound meter.

## REQUIREMENTS

The file requiremets.txt contains libraries that need to be installed.

```bash
        pip install -r requirements.txt
```

## Usage and FLAGS

To know available flags use:

```bash
        python3 inspect_noise --help
```

| Flag | Description |
| --- | --- |
| `-c/ --collect` | collect data as Min, Max and Avg |
| `-l/--log [file]` | log of recorded data as text file. [file] is an optional params, if not specified, program will save log on a file (name: log.log) in ~/.inspectNoise/ hidden folder |
| `-r/--record threshold` | record audio when dB are on average higher than the specified threshold. Timestamp used as name of audio file. |
| `-s/--seconds seconds` | specify recording time |
| `-sh/--showindex` | it is useful for know index of input audio devices available |
| `-se/--setindex index` | used to set index of input microphone (writing on configuration file) |
| `-f/--format [mp3, wav, ogg]` | define format of output record. It can be used only with --record |
| `-to/--thrashesoutput` | used for debug or utility, when specified permit to not show output on terminal |
| `-ca/--calibrate` | used to load machine learning model that try to predict db read by a calibrated phonometer. The calibration tries to predict the values read by the [UT351/352] (the calibration tries to predict the read values of the UT321 sound level meter) sound level meter |

## Note

Please pay attention when use --calibrate flag, because, as reported in requirements.txt file, in our Raspberry the version of scikit-learn is 0.21.3, and the model was printed using the same version of this library.

## Extension

After first use the tool creates a hidden folder with name ".inspectNoise" in ~ (user dir).
In this directory will be created (after using flag --record for the first time) a new
directory with name gathered_mp3. Within this folder will be saved recorded data in sub-folder
with date of recoded day.

In the project directory are included 2 more utils file.
  - First is plotter.py that can be ran separately to create graphs starting from a log file
    (created with flag --log). The output will be located in "plot_data" folder, located in
    ".inspect_noise" folder.

```bash
        python3 plotter.py file.log my_dpi [threshold]
```

  - Second is audio_merger.py that it can be used to merge audio in a specific folder.

```bash
        python3 audio_merger.py input_dir_path export_file format
```

## Created Dataset

Using this library for the environmental noise monitoring with a microphone and a SPL meter three different datasets were created.
The following datasets are located in subdirectory named "dataset" and stored in simple csv files.

1. __DB_dataset_first_model.csv__. This dataset contains microphone and SPL meter samples corresponding to the same second.
2. __DB_dataset_canarin_second_model.csv__.  This dataset contains microphone, SPL meter and environmental (like temperature, humidity, pression, PM ecc.) samples corresponding to the same second.
3. __DB_dataset_canarin_third_model.csv__. This dataset contains microphone, SPL meter and environmental (like temperature, humidity, pression, PM ecc.) samples corresponding to the same minute.

In the first and second datasets are used data from a month of sampling, while in the third are used two months' data.

## Citation

Monti, L.; Vincenzi, M.; Mirri, S.; Pau, G.; Salomoni, P. RaveGuard: A Noise Monitoring Platform Using Low-End Microphones and Machine Learning. Sensors 2020, 20, 5583. 
[DOI](https://doi.org/10.3390/s20195583)

## License

[MIT](https://choosealicense.com/licenses/mit/)
