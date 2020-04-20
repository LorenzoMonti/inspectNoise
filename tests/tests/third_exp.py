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
from sklearn.ensemble import GradientBoostingRegressor
import util

def models(dataset_canarin_minutes):
    # ## Costruzione Modelli
    #
    # - Ora andiamo a costruire i modelli di leaerning sul dataset appena costruito.
    # - Per prima cosa dobbiamo andare a dividere l'insieme di dati in __Training Set__ e __Validation Set__.
    X_train, X_val, y_train, y_val = train_test_split(
        dataset_canarin_minutes.drop("db_phon", axis=1),    # X = tutto tranne db_phon
        dataset_canarin_minutes["db_phon"],                 # y = db_phon
        test_size=1/3, random_state=42                      # parametri divisione
    )

    # - Anche in questo ultimo caso si tratta di __Regressione Multivariata__.
    # - Partiamo con l'addestramento di un semplice modello lineare.
    print("Linear Regression")
    lrm = LinearRegression()
    lrm.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, lrm)
    pd.Series(lrm.coef_, index=X_train.columns)
    
    print("Polynomial Regression")
    poly = Pipeline([
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])
    poly.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, poly)

    print("Polynomial Regression with Ridge")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(degree=2, include_bias=False)),
        ("regr",  Ridge(alpha=0.5))
    ])
    model.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, model)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, model.predict(X_val))))
    
    # - Ora andiamo ad eseguire la __Grid Search__ per trovare i valori degli iperparametri che permettono di ottenere una maggiore accuratezza.
    # - Teniamo conto del fatto che avendo molti meno dati possiamo aumentare maggiormente il grado del polinomio.
    print("Polynomial Regression with GridSearch")
    model_poly = Pipeline([
        ("poly",   PolynomialFeatures(include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])

    grid_poly = {
        "poly__degree": range(1, 51),
    }

    gs = GridSearchCV(model_poly, param_grid=grid_poly)
    gs.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, gs)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, model.predict(X_val))))
   
    print("Polynomial Regression with Ridge and GridSearch")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(include_bias=False)),
        ("regr",  Ridge())
    ])

    grid = {
        "poly__degree": range(1, 51),
        "regr__alpha": [0.1, 1, 10]
    }

    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)
    print(pd.DataFrame(gs.cv_results_).sort_values("mean_test_score", ascending=False).head())
    util.print_error_stats(X_val, y_val, gs)
    
    # - Infine, avendo ottenuto ottimi risultati nei casi precedenti, utilizziamo le __Random Forest__.
    print("Random Forest")
    model_rf = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  RandomForestRegressor(random_state=42,n_jobs=25))
    ])

    grid_rf = {
        "model__n_estimators": range(1, 301)
    }

    gs_rf = GridSearchCV(model_rf, param_grid=grid_rf)
    gs_rf.fit(X_train, y_train)
    print(pd.DataFrame(gs_rf.cv_results_).sort_values("mean_test_score", ascending=False))
    util.print_error_stats(X_val, y_val, gs_rf)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, gs_rf.predict(X_val))))

    # - Anche in questo caso, il modello a produrre risultati migliori è quello che utilizza le __Random Forest__.
    # - Di seguito vengono riportati alcuni esempi di predizioni.
    #     - Da questi è possibile notare che l'errore eseguito è mediamente quello del modello testato sul validation set, ovvero quello riportato dalla metrica.
    predicted = gs_rf.predict(X_val)
    #y_val[122]
    #predicted[122]
    #y_val[10567]
    #predicted[10567]
    
