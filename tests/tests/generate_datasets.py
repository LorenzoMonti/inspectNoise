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

   # Save dataSet in a csv file.
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

    # - Per prima cosa vengono eliminate tutte quelle colonne che non sono utili all'analisi.
    #print(canarin_first_month.drop(['GPS_Lat', 'GPS_Lng', 'GPS_Alt', 'Node', "Timestamp"], axis='columns', inplace=True))
    #print(canarin_first_month.columns)

    # - Per comodità vengono rinominate tutte le colonne che hanno dei nomi eccessivamente lunghi.
    canarin_first_month["Datetime"] = pd.to_datetime(canarin_first_month["Datetime(UTC+2)"])
    canarin_first_month["Temperature"] = canarin_first_month["Temperature Ext"]
    canarin_first_month["Humidity"] = canarin_first_month["Humidity Ext"]
    # - Eliminiamo ora le colonne che sono state rinominate.
    canarin_first_month.drop(["Datetime(UTC+2)", "Temperature Ext", "Humidity Ext", "Node"], axis='columns', inplace=True)
    canarin_first_month.head()
    # - Settiamo il campo DateTime come indice del nostro DataFrame.
    canarin_first_month.set_index("Datetime", inplace=True)
    # - Espandiamo ora i dati del canarino al secondo, in modo di averli alla stessa frequenza di quelli del dataset contenente i decibel del microfono e del fonometro.
    canarin_upsampled = canarin_first_month.resample('1S')

    # - Infine, filliamo i dati precedentemente espansi con una tecnica di __interpolazione__.
    # - L'__interpolazione__ ci consente di individuare i punti "mancanti" a partire dall'insieme noto di punti che abbiamo, supponendo che tutti i punti si possano ricondurre ad una determinata funzione matematica.
    # - Nel nostro caso proviamo ad utilizzare una semplice __interpolazione lineare__.
    # - __Nota:__ Andando ad espandere una serie ed eseguendo interpolazione, anche i valori che erano NaN vengono fillati, per dare "continuità" alla funzione.
    canarin_upsampled_interpolated = canarin_upsampled.interpolate(method="linear")
    #print(type(canarin_upsampled_interpolated))

    # - Una volta espansi i dati del canarino al secondo sono da unire con quelli del dataset, precedentemente utilizzato, contenente i decibel.
    # - Per effettuare l'unione utilizziamo la funzione __merge__ (come effettuato per il dataset dei decibel) che ci consente di eseguire una operazione di __join__ considerando i due DataFrame come due tabelle di un DataBase realazionale.
    # - A differenza del caso precedente non è stato utilizzato l'__outer join__, ma i valori che non trovavano corrispondenza sono stati scartati non essendo utili all'analisi.
    # - I parametri __left_index__ e __right_index__ sono impostati a true in quanto consentono di eseguire il __join__ tra gli indici, ovvero i __Datetime__.
    dataset_canarin_seconds = dataset.merge(canarin_upsampled_interpolated, left_index=True, right_index=True)
    #print(dataset_canarin_seconds.shape)

    # - Prima di proseguire con il lavoro esportiamo su file .csv il dataset elaborato ed utilizzato per realizzare questo secondo metodo.
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

    # - Utilizziamo lo stesso algoritmo utilizzato precedentemente per mergiare i file del microfono e del fonometro.
    dataset_db_second_month = pd.DataFrame()
    for m, p in zip(meter_files, phonometer_files):
        # Step 1: lettura dati da file csv.
        microphone_second_month, phonometer_second_month = util.read_data(m, p, path_mic = "../microphone-second-month", path_phon = "../phonometer-second-month");
        # Step 2: eliminazione prima ed ultima riga microfono.
        util.drop_dumb_data(microphone_second_month)
        # Step 3: merge di Date e Time in un unico campo.
        util.create_datetime(microphone_second_month, phonometer_second_month)
        # Step 4: rimozione dei duplicati.
        util.remove_duplicate(microphone_second_month, phonometer_second_month)
        # Step 5: operazione di join tra i due DataFrame sulla colonna DateTime.
        merged_second_month = util.join(microphone_second_month, phonometer_second_month)
        # Step 6: rimozione e salvataggio dei valori NaN.
        util.remove_and_save_NaN(merged_second_month)
        # Step 7: append nel dataset che verrà utilizzato per l'analisi.
        dataset_db_second_month = dataset_db_second_month.append(merged_second_month)

    #print(dataset_db_second_month.head())
    #print(dataset_db_second_month.tail())

    # - Una volta uniti correttamente (medinate operazione di __join__) i due file basta concatenare i due dataset dei due mesi per ottenere un unico grande dataset con i Decibel del microfono e del fonometro.
    db_dataset_2_month = dataset.append(dataset_db_second_month)
    #print(db_dataset_2_month.head())
    #db_dataset_2_month.tail()

    # - Mediante la stessa procedura utilizzata nel caso precedente è possibile caricare i dati del canarino del secondo mese.
    canarin_second_month = pd.read_csv("../canarin-second-month.csv", skiprows=4)
    #print(canarin_second_month.head())
    #canarin_second_month.tail()
    canarin_second_month.drop(['GPS_Lat', 'GPS_Lng', 'GPS_Alt', 'Node', "Timestamp"], axis='columns', inplace=True)
    #print(canarin_second_month.columns)

    # - Per comodità vengono rinominate alcune colonne.
    canarin_second_month["Datetime"] = pd.to_datetime(canarin_second_month["Datetime(UTC+2)"])
    canarin_second_month["Temperature"] = canarin_second_month["Temperature Ext"]
    canarin_second_month["Humidity"] = canarin_second_month["Humidity Ext"]
    canarin_second_month.drop(["Datetime(UTC+2)", "Temperature Ext", "Humidity Ext"], axis='columns', inplace=True)
    canarin_second_month.head()

    # - Settiamo come indice il Datetime.
    canarin_second_month.set_index("Datetime", inplace=True)
    #print(canarin_second_month.head())

    # - Effettuaiamo ora l'unione dei dati del primo mese del canarino con quelli del secondo.
    canarin_2_month = canarin_first_month.append(canarin_second_month)
    #canarin_2_month.head()
    #canarin_2_month.tail()

    # - A differenza del caso precedente andiamo ad eliminare i dati con valori NaN.
    # - Mentre prima abbiamo eseguito __Upsampling__, ovvero abbiamo espanso i dati del DataSet per avere una frequenza al secondo utilizzando interpolazione, per la "continuità" della funzione che rappresentava i dati abbiamo assegnato un valore anche ai NaN. In questo caso per semplicità li eliminiamo.
    canarin_2_month.dropna(inplace=True)

    # - Infine, per avere il dataset completo su cui eseguire l'analisi andiamo a effettuare la join tra il dataset contenente i Decibel di due mesi e quello contenente i dati del canarino di due mesi.
    dataset_canarin_minutes = db_dataset_2_month.merge(canarin_2_month, left_index=True, right_index=True)
    print(dataset_canarin_minutes.head())
    print(dataset_canarin_minutes.tail())

    # - Prima di proseguire stampiamo su file .csv il dataset utilizzato per questa terza analisi.
    if not os.path.exists("DB_dataset_canarin_third_model.csv"):
        dataset_canarin_minutes.to_csv("DB_dataset_canarin_third_model.csv", sep=' ')

    return dataset, dataset_canarin_seconds, dataset_canarin_minutes
