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
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
import util


def models(dataset_canarin_seconds):
    # # Metodo 2: Predizione dei decibel calibrati a partire da quelli del microfono e dai dati ambientali del canarino - utilizzando una frequenza al secondo.
    # - Come nel caso precedente utilizziamo i dati con una frequenza di campionamento al secondo (come quella del microfono e del fonometro). Per via della quantità dei dati utilizziamo, anche in questo caso, quelli relativi ad un mese di campionamenti.

    # Costruzione Modelli
    # - Per prima cosa, come nel caso precedente, dobbiamo dividere tra __training set__ e __validation set__, con un rapporto rispettivamnete di 2/3 - 1/3.
    X_train, X_val, y_train, y_val = train_test_split(
        dataset_canarin_seconds.drop("db_phon", axis=1),    # X = tutto tranne db_phon
        dataset_canarin_seconds["db_phon"],                 # y = db_phon
        test_size=1/3, random_state=42                      # parametri divisione
    )

    # - Per prima cosa testiamo un semplice modello lineare. A differenza del caso precedente si tratta di regressione __multivariata__ avendo più variabili indipendenti (X).
    print("Linear Regression")
    lrm = LinearRegression()
    lrm.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, lrm)
    # - Come nel caso precedente calcolo il valore dell'__RMSE__.
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, lrm.predict(X_val))))
    # - Possiamo vedere il valore dei coefficienti attribuiti dal modello alle singole features per capire quali sono più importanti.
    pd.Series(lrm.coef_, index=X_train.columns)

    # - Proviamo ad applicare la standardizzazione ai dati prima di darli in pasto al modello.
    print("Linear Regression standardizzata")
    model = Pipeline([
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])
    model.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, model)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, lrm.predict(X_val))))
    pd.Series(model.named_steps["linreg"].coef_, index=X_train.columns)

    # - Proviamo ad eseguire una regressione polinomiale.
    print("Polynomial Regression")
    model = Pipeline([
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])
    model.fit(X_train, y_train)

    util.print_error_stats(X_val, y_val, model)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, model.predict(X_val))))


    # - Rispetto ai casi precedenti abbiamo notato un miglioramento dell'errore.
    # - Proviamo ad eseguire lo stesso procedimento inserendo la __regolarizzazione__. Come nel caso precedente ci consente di continuare con l'aumento della complessità del modello (aumentando il grado del polinomio) evitando l'overfitting del modello sui dati del __Training Set__.
    # - Proviamo ad esempio a testare la funzione di regolarizzazione __Ridge__, utilizzata anche nel caso precedente.
    print("Polynomial regression with Ridge")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(degree=2, include_bias=False)),
        ("regr",  Ridge(alpha=0.5))
    ])
    model.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, model)


    # - Proviamo ad utilizzare anche la regolarizzazione __Elastic Net__, ovvero una regolarizzazione "ibrida" tra la Ridge e la Lasso che aggiunge un iperparametro per controllare il peso di una o dell'altra.
    print("Polynomial regression with ElasticNet")
    model = Pipeline([
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", ElasticNet(alpha=0.5, l1_ratio=0.2))
    ])
    model.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, model)

    # - Ora che abbiamo testato alcuni dei modelli principali e capito quali di questi portino ad avere un calo dell'errore, andiamo ad effettuarne il tuning degli iperparametri mediante __Grid Search__.
    print("Polynomial ressione with GRID search")
    model = Pipeline([
        ("poly",   PolynomialFeatures(include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])

    grid = {
        "poly__degree": range(1, 11),
    }

    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)
    print(pd.DataFrame(gs.cv_results_).sort_values("mean_test_score", ascending=False))
    util.print_error_stats(X_val, y_val, gs)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, gs.predict(X_val))))
    
    print("Polynomial regression with Ridge and GridSearch")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(include_bias=False)),
        ("regr",  Ridge())
    ])
    grid = {
        "poly__degree": range(1, 41),
        "regr__alpha": [0.1, 1, 10]
    }
    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, gs)
    
    # - Proviamo ad utilizzare le __Random Forest__.
    # - Sono un tipo di algoritmo basato su __ensemble learning__ in cui vengono combinati diversi algoritmi per ottenere un modello di predizione migliore. Combina una serie di alberi decisionali, creando una foresta.
    # - Questo algoritmo estrapola N record casuali dal DataSet per creare un albero decisionale, basato su questi N record. Questo procedimento viene ripetuto N volte.
    # - L'iperparametro __n_estimators__ di cui effettuiamo il __tuning__ nella __Grid Search__ è il numero di alberi che formano la foresta.
    print("Random Forest")
    model_rf = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  RandomForestRegressor(random_state=42))
    ])

    grid_rf = {
        "model__n_estimators": range(1, 101)
    }

    gs_rf = GridSearchCV(model_rf, param_grid=grid_rf)
    gs_rf.fit(X_train, y_train)
    print(pd.DataFrame(gs_rf.cv_results_).sort_values("mean_test_score", ascending=False))
    util.print_error_stats(X_val, y_val, gs_rf)
    print("   RMSE: ",np.sqrt(mean_squared_error(y_val, gs_rf.predict(X_val))))


    # - Testiamo anche un modello basato sul __Gradient Boosting__.
    # - È un modello che si basa su algoritmi che addestrano alberi decisionali. Ogni osservazione viene pesata in maniera equivalente alla creazione del primo albero. Successivamente si va ad incrementare il peso associato alle osservazioni di difficile predizione, e viceversa a diminuire quello delle osservazione di facile predizione. Viene costruito quindi un secondo albero su questi nuovi dati pesati. Una volta fatta questa operazione viene calcolato l'errore di predizione compiuto dall'unione di questi due alberi, per costruirne un terzo. Questo procedimento viene eseguito iterativamente per decrementare ogni volta l'errore residuo.
    #
    # - L'iperparametro __n_estimators__ di cui effettuiamo il __tuning__ nella __Grid Search__ rappresenta il numero di iterazioni (__boosting stages__) da eseguire.
    # - Il modello è poco soggetto ad __Overfitting__.

    print("Gradient Boosting")
    model_gb = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  GradientBoostingRegressor(random_state=42))
    ])

    grid_gb = {
        "model__n_estimators": range(1, 101)
    }

    gs_gb = GridSearchCV(model_gb, param_grid=grid_gb)
    gs_gb.fit(X_train, y_train)
    print(pd.DataFrame(gs_gb.cv_results_).sort_values("mean_test_score", ascending=False))
    util.print_error_stats(X_val, y_val, gs_gb)


    # - In questo secondo modello i risultati migliori sono stati ottenuti mediante l'utilizzo delle __Random Forest__. In tal caso siamo arrivati a ridurre l'__RMSE__ a circa 3 dB.
    # - Dagli esperimenti sopra riportati è chiaro che man mano che saliamo con il numero degli __n_estimators__, ovvero degli alberi decisionali, l'errore continuerà a diminuire (stesso discorso con il grado del polinomio).
    #     - Per ragioni di complessità computazionale e tempi di addestramento troppo elevati mi fermo ai valori sopra riportati.
    # - Come abbiamo visto all'inizio di tale modello applicando la __Regressione Lineare__ la feature con maggior peso sono naturalmente i Decibel non calibrati (essendo la misura da calibrare), ma l'utilizzo di altre features aiuta comunque i modelli a raggiungere una maggiore precisione nella predizione.
   
