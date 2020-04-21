import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import util

def gen():
    meter_path = "../microphone"
    meter_files = [f for f in listdir(meter_path) if isfile(join(meter_path, f))]
    meter_files.sort()
    meter_files = [f for f in meter_files if f[0:5] == "meter"]
    meter_files

    phonometer_path = "../phonometer"
    phonometer_files = [f for f in listdir(phonometer_path) if isfile(join(phonometer_path, f))]
    phonometer_files.sort()
    phonometer_files = [f for f in phonometer_files if f[0:10] == "phonometer"]
    phonometer_files

    len(meter_files) == len(phonometer_files)
    dataset = pd.DataFrame()
    for m, p in zip(meter_files, phonometer_files):
        # Step 1: read data from csv file.
        microphone, phonometer = util.read_data(m, p);
        # Step 2: drop first and last row in microphone csv.
        util.drop_dumb_data(microphone)
        # Step 3: merge Date and Time in the same field.
        util.create_datetime(microphone, phonometer)
        # Step 4: remove duplicates.
        util.remove_duplicate(microphone, phonometer)
        # Step 5: join between DataFrame on DateTime coloumn.
        merged = util.join(microphone, phonometer)
        # Step 6: remove and save NaN values.
        util.remove_and_save_NaN(merged)
        # Step 7: append in the dataset.
        dataset = dataset.append(merged)

   # Save the dataset in a csv file.
    if not os.path.exists("DB_dataset_first_model.csv"):
        dataset.to_csv("DB_dataset_first_model.csv", sep=' ')

    dataset.shape
    dataset.head()
    dataset.tail()

    ################################################################################################
    #                                       SECOND DATASET                                         #
    ################################################################################################

    canarin_first_month = pd.read_csv("../canarin-first-month.csv", skiprows=4)
    #print(canarin_first_month.shape)
    #print(canarin_first_month.head())
    #print(canarin_first_month.tail())

    #print(canarin_first_month.drop(['GPS_Lat', 'GPS_Lng', 'GPS_Alt', 'Node', "Timestamp"], axis='columns', inplace=True))
    #print(canarin_first_month.columns)

    # - Renaming of the coloumns that have too long names.
    canarin_first_month["Datetime"] = pd.to_datetime(canarin_first_month["Datetime(UTC+2)"])
    canarin_first_month["Temperature"] = canarin_first_month["Temperature Ext"]
    canarin_first_month["Humidity"] = canarin_first_month["Humidity Ext"]
    # - Drop the columns that have been renamed.
    canarin_first_month.drop(["Datetime(UTC+2)", "Temperature Ext", "Humidity Ext", "Node"], axis='columns', inplace=True)
    canarin_first_month.head()
    canarin_first_month.set_index("Datetime", inplace=True)
    # - Expand the data of the canarin station per second, in order to have them at the same frequency as those of the dataset containing the decibels of the microphone and the sound level meter.
    canarin_upsampled = canarin_first_month.resample('1S')

    # - We use interpolation to fill in previously expanded data.
    canarin_upsampled_interpolated = canarin_upsampled.interpolate(method="linear")
    #print(type(canarin_upsampled_interpolated))

    # - Once expanded, the data of the canary per second are to be combined with those of the dataset, previously used, containing the decibels.
    dataset_canarin_seconds = dataset.merge(canarin_upsampled_interpolated, left_index=True, right_index=True)
    #print(dataset_canarin_seconds.shape)

    # - Export in csv file the dataset.
    if not os.path.exists("DB_dataset_canarin_second_model.csv"):
        dataset_canarin_seconds.to_csv("DB_dataset_canarin_second_model.csv", sep=' ')

    ################################################################################################
    #                                       THIRD DATASET                                          #
    ################################################################################################

    meter_path = "../microphone-second-month"
    meter_files = [f for f in listdir(meter_path) if isfile(os.path.join(meter_path, f))]
    meter_files.sort()
    meter_files = [f for f in meter_files if f[0:5] == "meter"]
    #print(meter_files)

    phonometer_path = "../phonometer-second-month"
    phonometer_files = [f for f in listdir(phonometer_path) if isfile(os.path.join(phonometer_path, f))]
    phonometer_files.sort()
    phonometer_files = [f for f in phonometer_files if f[0:10] == "phonometer"]
    #print(phonometer_files)

    len(meter_files) == len(phonometer_files)

    # - Same step used in the previous method in order to merge microphone files and phonometer files.
    dataset_db_second_month = pd.DataFrame()
    for m, p in zip(meter_files, phonometer_files):
        # Step 1:  read data from csv file.
        microphone_second_month, phonometer_second_month = util.read_data(m, p, path_mic = "../microphone-second-month", path_phon = "../phonometer-second-month");
        # Step 2:  drop first and last row in microphone csv.
        util.drop_dumb_data(microphone_second_month)
        # Step 3:  merge Date and Time in the same field.
        util.create_datetime(microphone_second_month, phonometer_second_month)
        # Step 4: remove duplicates.
        util.remove_duplicate(microphone_second_month, phonometer_second_month)
        # Step 5: join between DataFrame on DateTime coloumn.
        merged_second_month = util.join(microphone_second_month, phonometer_second_month)
        # Step 6: remove and save NaN values.
        util.remove_and_save_NaN(merged_second_month)
        # Step 7: append in the dataset.
        dataset_db_second_month = dataset_db_second_month.append(merged_second_month)

    #print(dataset_db_second_month.head())
    #print(dataset_db_second_month.tail())

    db_dataset_2_month = dataset.append(dataset_db_second_month)
    #print(db_dataset_2_month.head())
    #db_dataset_2_month.tail()

    # - read second month canarin data for the third experiment
    canarin_second_month = pd.read_csv("../canarin-second-month.csv", skiprows=4)
    #print(canarin_second_month.head())
    #canarin_second_month.tail()
    canarin_second_month.drop(['GPS_Lat', 'GPS_Lng', 'GPS_Alt', 'Node', "Timestamp"], axis='columns', inplace=True)
    #print(canarin_second_month.columns)

    # - Renaming some coloumns.
    canarin_second_month["Datetime"] = pd.to_datetime(canarin_second_month["Datetime(UTC+2)"])
    canarin_second_month["Temperature"] = canarin_second_month["Temperature Ext"]
    canarin_second_month["Humidity"] = canarin_second_month["Humidity Ext"]
    canarin_second_month.drop(["Datetime(UTC+2)", "Temperature Ext", "Humidity Ext"], axis='columns', inplace=True)
    canarin_second_month.head()

    canarin_second_month.set_index("Datetime", inplace=True)
    #print(canarin_second_month.head())

    # - Append second month data in first month data.
    canarin_2_month = canarin_first_month.append(canarin_second_month)
    #canarin_2_month.head()
    #canarin_2_month.tail()

    # - Unlike the previous case, we are going to delete the data with NaN values.
    canarin_2_month.dropna(inplace=True)

    # - Finally, to have the complete dataset on which to perform the analysis we go to make the join between the dataset containing the two-month Decibels and the one containing the data of the two-month canary.
    dataset_canarin_minutes = db_dataset_2_month.merge(canarin_2_month, left_index=True, right_index=True)
    print(dataset_canarin_minutes.head())
    print(dataset_canarin_minutes.tail())

    if not os.path.exists("DB_dataset_canarin_third_model.csv"):
        dataset_canarin_minutes.to_csv("DB_dataset_canarin_third_model.csv", sep=' ')

    # return datasets
    return dataset, dataset_canarin_seconds, dataset_canarin_minutes
