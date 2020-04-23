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

# Data processing and dataset construction
# - Definition of useful functions for the creation of the Dataset. The dataset that is created below is the basic one, which contains the value monitored by the microphone and that of the sound level meter. It will also be useful for further processing.
# - Function that allows the reading of data from csv files and the saving inside DataFrame pandas.
def read_data(file_mic, file_phon, path_mic = "../microphone", path_phon = "../phonometer"):
    microphone = pd.read_csv(path_mic + "/{}".format(file_mic), sep=" ", names=["Date", "Time", "db_mic"])
    phonometer = pd.read_csv(path_phon + "/{}".format(file_phon), sep=" ", names=["Date", "Time", "db_phon"])
    return microphone, phonometer


# - Remove first and last woe in the file.
def drop_dumb_data(microphone):
    microphone.drop(microphone.index[[0,-1]], inplace=True)


# - Merge Date and Time in the same field Datetime, removing milliseconds.
# - also, remove coloumns Date and Time in the first DataFrame.
def create_datetime(microphone, phonometer):
    phonometer['Datetime'] = pd.to_datetime(phonometer['Date'].apply(str) + ' ' + phonometer['Time'].apply(str).str.split(',').str[0])
    microphone['Datetime'] = pd.to_datetime(microphone['Date'].apply(str) + ' ' + microphone['Time'].apply(str).str.split(',').str[0])
    microphone.drop(['Date', 'Time'], axis='columns', inplace=True)
    phonometer.drop(['Date', 'Time'], axis='columns', inplace=True)

# - Removing of duplicates (data sampled in the same second).
#     - Remove those data that have exactly the same datetime, i.e. same date, same time and same seconds.
def remove_duplicate(microphone, phonometer):
    phonometer.drop_duplicates('Datetime', inplace=True)
    microphone.drop_duplicates('Datetime', inplace=True)

# - Join operation bewteen Datetime of two DataFrame.
def join(microphone, phonometer):
    merged = pd.merge(microphone, phonometer, on="Datetime", how="outer")
    merged.set_index("Datetime", inplace=True)
    return merged


# - Extraction of the observations that following the Join operation have __NaN__ values, i.e. those that have not found any matches. These records are saved in a separate file, so you can keep track of them.
def remove_and_save_NaN(merged):
    df_nan = merged[merged.isna().any(axis=1)]
    if os.path.exists("NaN_Data.csv"):
        with open('NaN_Data.csv', 'a') as f:
            df_nan.to_csv(f, header=False)
    else:
        df_nan.to_csv("NaN_Data.csv", sep=' ')
    merged.dropna(inplace=True)

# - Print relative error
def relative_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true))


# - Print MSE, relative error and R^2 errors
def print_error_stats(X, y, model):
    print("   Mean squared error: {:.5}".format(mean_squared_error(model.predict(X), y)))
    print("   Root Mean squared error: {:.5}".format(np.sqrt(mean_squared_error(model.predict(X), y))))
    print("   Relative error: {:.5%}".format(relative_error(model.predict(X), y)))
    print("   R-squared coefficient: {:.5}".format(model.score(X, y)))


# - Plot data
def plot_model_on_data(x, y, model=None):
    plt.scatter(x, y)
    if model is not None:
        xlim, ylim = plt.gca().get_xlim(), plt.gca().get_ylim()
        line_x = np.linspace(xlim[0], xlim[1], 100)
        line_y = model.predict(line_x[:, None])
        plt.plot(line_x, line_y, c="red", lw=3)
        plt.xlim(xlim); plt.ylim(ylim)
    plt.grid()
    plt.xlabel("db_microphone"); plt.ylabel("db_phonometer")
    #plt.show()
