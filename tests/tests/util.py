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

# Elaborazione dati e costruzione del dataset
# - Definizione funzioni utili alla creazione del Dataset. Il dataset che viene creato di seguito è quello di base, che contiene al suo interno il valore monitorato dal microfono e quello del fonometro. Sarà successivamente utile anche per ulteriori elaborazioni.
# - Questa funzione consente la lettura dei dati da file csv e il salvataggio all'interno di DataFrame pandas.
def read_data(file_mic, file_phon, path_mic = "../microphone", path_phon = "../phonometer"):
    microphone = pd.read_csv(path_mic + "/{}".format(file_mic), sep=" ", names=["Date", "Time", "db_mic"])
    phonometer = pd.read_csv(path_phon + "/{}".format(file_phon), sep=" ", names=["Date", "Time", "db_phon"])
    return microphone, phonometer


# - Remove first and last woe in the file.
def drop_dumb_data(microphone):
    microphone.drop(microphone.index[[0,-1]], inplace=True)


# - Unisco Date e Time in un unico campo Datetime, eliminando i millisecondi.
# - Oltretutto elimino anche le colonne Date e Time nel DataFrame iniziale.
def create_datetime(microphone, phonometer):
    phonometer['Datetime'] = pd.to_datetime(phonometer['Date'].apply(str) + ' ' + phonometer['Time'].apply(str).str.split(',').str[0])
    microphone['Datetime'] = pd.to_datetime(microphone['Date'].apply(str) + ' ' + microphone['Time'].apply(str).str.split(',').str[0])
    microphone.drop(['Date', 'Time'], axis='columns', inplace=True)
    phonometer.drop(['Date', 'Time'], axis='columns', inplace=True)

# - Elimino i duplicati (dati campionati nello stesso secondo).
#     - Ovvero vado ad eliminare quei dati che hanno esattamente lo stesso datetime, ovvero stessa data, stessa ora e stessi secondi.
def remove_duplicate(microphone, phonometer):
    phonometer.drop_duplicates('Datetime', inplace=True)
    microphone.drop_duplicates('Datetime', inplace=True)

# - Operazione di Join tra i Datetime dei due DataFrame.
#     - In questo caso ho deciso di utilizzare una operazione di __Outer Join__. Tale operazione consete di manatenere le chiavi di entrambi i DataFrame e nel caso in cui non trovino corrispondenze di completarle con valori null. In questo modo è possibile controllare quali sono i record che non hanno trovato corrispondenza.
def join(microphone, phonometer):
    merged = pd.merge(microphone, phonometer, on="Datetime", how="outer")
    merged.set_index("Datetime", inplace=True)
    return merged


# - Estrazione delle osservazioni che a seguito dell'operazione di Join possiedono valori __NaN__, ovvero quelli che non hanno trovato corrispondenze. Tali record vengono salvati in un file separato, in modo da poterne tenere traccia.
def remove_and_save_NaN(merged):
    df_nan = merged[merged.isna().any(axis=1)]
    if os.path.exists("NaN_Data.csv"):
        with open('NaN_Data.csv', 'a') as f:
            df_nan.to_csv(f, header=False)
    else:
        df_nan.to_csv("NaN_Data.csv", sep=' ')
    merged.dropna(inplace=True)

def relative_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true))



def print_error_stats(X, y, model):
    print("   Mean squared error: {:.5}".format(mean_squared_error(model.predict(X), y)))
    print("   Relative error: {:.5%}".format(relative_error(model.predict(X), y)))
    print("   R-squared coefficient: {:.5}".format(model.score(X, y)))

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
