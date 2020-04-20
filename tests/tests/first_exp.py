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

def models(dataset):

    # - Nel caso più semplice proviamo ad eseguire una regressione univariata, ovvero partendo dai decibel del microfono provare a predire quelli del fonometro. Andiamo quindi a dividere la variabile indipendente (x) da quella dipendente che vogliamo andare a predire (y).
    X = dataset[["db_mic"]]
    y = dataset["db_phon"]

    # - Ora andiamo a dividere i dati in __Training Set__ e __Validation Set__ utilizzando la funzione di libreria.
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=1/3, random_state=42)

    # - Di seguito verranno realizzati metodi differenti di analisi, ognuno dei quali elaborerà e tratterà i dati in maniera differente. Ad ognuno di essi verranno applicati i principali algoritmi di regressione di machine learning.
    # # Metodo 1: Predizione semplice dei decibel calibrati a partire da quelli del microfono
    # - Nella definizione di questi modelli, andremo ad utilizzare come variabile dipendete (X) i decibel letti dal microfono, mentre andremo a predire i valori dei decibel calibrati letti dal fonometro (Y).
    # - Per prima cosa definiamo una funzione che ci consenta di calcolare le metriche principali per i vari modelli di regressione.

    # - Addestriamo il modello sull'insieme di training.
    print("Linear Regression")

    lrm = LinearRegression()
    lrm.fit(X_train, y_train)

    # - Testiamo lo score del modello sull'insieme di valdation.
    #     - __Nota__: la metrica di default dei modelli di regressione è il coefficiente $R^2$ che descrive quanto il modello approssimi la variabilità dei dati. Il valore di questa metrica varia tra [0-1]; tanto è maggiore, tanto il modello cattura al meglio la variabilità dei dati.
    lrm.score(X_val, y_val)

    # - Utilizziamo la funzione sopra definita per calcolare il valore delle metriche di default.
    util.print_error_stats(X_val, y_val, lrm)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, lrm.predict(X_val))))

    # - Dalle metriche appena calcolate possiamo notare che il modello realizzato approssima abbastanza bene la variabilità dei dati. Oltretutto l'errore quadratico medio posto sotto radice, ovvero l'__RMSE__ è di circa 5 dB. Tale valore rappresenta l'errore medio commesso nell'eseguire le predizioni.
    #  Visualizzazione del Modello
    # - Definiamo una funzione che, dato un modello basato su una variabile indipendente, mostri la funzione descritta dal modello sovrapposta ai dati.
    util.plot_model_on_data(X_train, y_train, lrm)

    # - Provo a testare la predizione su alcuni valori.
    predicted = lrm.predict(X_val)
    #print(predicted[0])
    #print(y_val[0])
    #print(predicted[100])
    #print(y_val[100])

    # - Possiamo notare che, come calcolato con l'__RMSE__, abbiamo un errore di pochi decibel.
    # ## Test altri modelli
    #
    # - Possiamo testare altri modelli anche più complessi.
    # - Proviamo ad esempio la regressione polinomiale.


    print("Polynomial regression")
    prm = Pipeline([
        # nome     elemento
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("linreg", LinearRegression())
    ])

    prm.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, prm)
    # - Utilizzando un polinomio di grado due possiamo notare che l'__MSE__ diminuisce.
    # - Proviamo quindi a calcolare l'__RMSE__.
    print("   RMSE: ",np.sqrt(mean_squared_error(y_val, prm.predict(X_val))))


    # - Tale errore è di poco inferiore rispetto al caso precedente.
    # - Naturalmente ognuna di queste operazioni si porta dietro i propri __iperparametri__. Testare tutte le combinazioni manualmente sarebbe poco utile e dispendioso, proprio per questo possiamo avvalerci della __Grid Search__. La __Grid Search__ ci consente di fissare diversi valori per ciascun iperparametro per poi addestrare un modello separato per ogni possibile combiazione di tali valori mediante __k-fold cross validation__. Infine, una volta calcolato lo score di ogni modello, in automatico viene addestrato il modello migliore su tutti i dati.
    print("Polynomial Regression with GRID search")
    prm_gs = Pipeline([
        # nome     elemento
        ("scale", StandardScaler()),
        ("poly",   PolynomialFeatures()),
        ("linreg", LinearRegression())
    ])

    grid = {
        "scale": [None, StandardScaler()],
        "poly__degree": range(1, 51),
        "poly__include_bias": [False, True]
    }

    gs = GridSearchCV(prm_gs, param_grid=grid)
    gs.fit(X_train, y_train)

    # - Incapsuliamo il risultato della __Grid Search__ all'interno di un DataFrame pandas in modo da poter controllare in maniera più semplice e chiara i risultati.
    print(pd.DataFrame(gs.cv_results_).sort_values("rank_test_score").head(50))
    # - Testiamo il miglior modello ottenuto sul __Validation Set__.
    util.print_error_stats(X_val, y_val, gs)
    print("   RMSE: ",np.sqrt(mean_squared_error(y_val, gs.predict(X_val))))


    # - Ci possiamo aspettare che all'aumento del grado allora l'errore continui a diminuire, fino ad andare in __Overfitting__, ovvero il modello rappresenta in maniera troppo stringente i dati del __Training set__, cercando di passare per tutti i suoi punti e causando, in particolare nei punti estremi, forti oscillazioni. Questo provoca un errore molto alto sul __Validation set__.
    # - Per evitare tale problema possiamo utilizzare la __Regolarizzazione__, ovvero ridurre le oscillazioni (controllando l'aumento spropositato dei coefficienti calcolati dall'algoritmo). Tale tecnica consente di continuare con l'aumento del grado del polinomio e della conseguente complessità del modello, evitando al contempo il problema dell' __Overfitting__.
    # - In tal caso la __Regolarizzazione__ viene effettuata mediante la __Ridge Regression__ ovvero una regressione che cerca di limitare i valori dei Theta calcolati dall'algoritmo tramite un'ipersfera centrata sull'origine.
    print("Polynomial Regressione with Ridge and GridSearch")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(include_bias=False)),
        ("regr",  Ridge())
    ])

    grid = {
        "poly__degree": range(1, 51),      # grado polinomio
        "regr__alpha":  [0.1, 1, 10]       # regolarizzazione
    }
    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)

    print(pd.DataFrame(gs.cv_results_).sort_values("rank_test_score").head(50))
    util.print_error_stats(X_val, y_val, gs)
    print("   RMSE: ",np.sqrt(mean_squared_error(y_val, gs.predict(X_val))))

    # - Possiamo infine notare che continuando ad aumentare il grado l'errore cala di poco.
    # - Non conviene andare avanti con questo aumento in quanto sarebbero necessarie risorse computazionali superiori per ottenere un aumento non molto significativo.

    # - Possiamo testare gli stessi valori calcolati con le predizioni precedenti.

    predicted = gs.predict(X_val)
    #print(predicted[0])
    #print(y_val[0])
    #print(predicted[100])
    #print(y_val[100])
    # - Sovrapponiamo infine l'ultimo modello ottenuto ai dati.
    util.plot_model_on_data(X_train, y_train, gs)

    # - Avendo ottenuto ottimi risultati nei modelli più complessi con le __Random Forest__, allora le proviamo ad appplicare anche nel caso della __regressione univariata__.
    print("Random Forest")
    rf = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  RandomForestRegressor(random_state=42))
    ])

    grid_lrf = {
        "model__n_estimators": range(1, 141)
    }

    gs_lrf = GridSearchCV(rf, param_grid=grid_lrf)
    gs_lrf.fit(X_train, y_train)
    print(pd.DataFrame(gs_lrf.cv_results_).sort_values("rank_test_score").head(140))
    util.print_error_stats(X_val, y_val, gs_lrf)
    print("   RMSE: ",np.sqrt(mean_squared_error(y_val, gs_lrf.predict(X_val))))
    # - Rappresentiamo anche in questo caso il modello sovrapposto ai dati di training.
    util.plot_model_on_data(X_train, y_train, gs_lrf)
