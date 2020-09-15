import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from thundersvm import SVR
from sklearn.svm import LinearSVR
import time
import util

def models(dataset_canarin_minutes):
    # - Method 3: Prediction of decibels calibrated starting from those of the microphone and from the environmental data of the canary - using a frequency per minute.

    # - Split the dataset
    X_train, X_val, y_train, y_val = train_test_split(
        dataset_canarin_minutes.drop("db_phon", axis=1),    # X = tutto tranne db_phon
        dataset_canarin_minutes["db_phon"],                 # y = db_phon
        test_size=1/3, random_state=42                      # parametri divisione
    )

    # - Linear regression. (__multivariate__ regression)
    print("Linear regression")
    lrm = LinearRegression()
    lrm.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, lrm)

    pd.Series(lrm.coef_, index=X_train.columns)

    # - Polynomial regression
    print("Polynomial regression")
    poly = Pipeline([
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])
    poly.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, poly)

    # - Polynomial regression with Ridge
    print("Polynomial regression with Ridge")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(degree=2, include_bias=False)),
        ("regr",  Ridge(alpha=0.5))
    ])
    model.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, model)

    # - Polynomial regression with GridSearch
    # - With less data it is possible to increase the polynomial degrees
    print("Polynomial regression with GridSearch")
    model_poly = Pipeline([
        ("poly",   PolynomialFeatures(include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])

    grid_poly = {
        "poly__degree": range(1, 15),
    }

    gs = GridSearchCV(model_poly, param_grid=grid_poly)
    gs.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs)

    # - Polynomial regression with Ridge and GridSearch
    print("Polynomial regression with Ridge and GridSearch")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(include_bias=False)),
        ("regr",  Ridge())
    ])

    grid = {
        "poly__degree": range(1, 15),
        "regr__alpha": [0.1, 1, 10]
    }

    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)

    print(pd.DataFrame(gs.cv_results_).sort_values("mean_test_score", ascending=False).head())

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs)

    # - Random Forest
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
    print(pd.DataFrame(gs_rf.best_estimator_.named_steps['model'].feature_importances_)) # features importances
    print(pd.DataFrame(gs_rf.cv_results_).sort_values("mean_test_score", ascending=False))

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs_rf)

    predicted = gs_rf.predict(X_val)
    #y_val[122]
    #predicted[122]
    #y_val[10567]
    #predicted[10567]

    # - SVR
    print("Support Vector Regression (linear)")
    grid_svr = {
        #'kernel': ['linear'],
        'C': [1e0, 1e1, 1e2, 1e3]
        #'gamma': np.logspace(-2, 2, 5)
    }

    #X_train = X_train.iloc[:100000]
    #y_train = y_train.iloc[:100000]
    #X_val = X_val.iloc[:100000]
    #y_val = y_val.iloc[:100000]
    # - set up tuning algorithm
    gs_svr = make_pipeline(StandardScaler(), GridSearchCV(LinearSVR(), param_grid=grid_svr, n_jobs=1))
    # - fit the classifier
    gs_svr.fit(X_train, y_train)
    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs_svr)

    print("Support Vector Regression (gaussian)")
    grid_svr = {
        'kernel': ['rbf'],
        'C': [1e0, 1e1, 1e2, 1e3],
        'gamma': np.logspace(-2, 2, 5)
    }

    # - set up tuning algorithm
    gs_svr = make_pipeline(StandardScaler(), GridSearchCV(SVR(), param_grid=grid_svr, n_jobs=1))
    # - fit the classifier
    gs_svr.fit(X_train, y_train)
    # -  Print out the error metrics
    util.print_error_stats(X_val, y_val, gs_svr)

