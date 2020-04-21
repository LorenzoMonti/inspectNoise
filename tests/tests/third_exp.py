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
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, lrm.predict(X_val))))

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
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, poly.predict(X_val))))

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
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, model.predict(X_val))))

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
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, gs.predict(X_val))))

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
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, gs.predict(X_val))))

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
    print(pd.DataFrame(gs_rf.cv_results_).sort_values("mean_test_score", ascending=False))

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs_rf)
    print("   RMSE: ", np.sqrt(mean_squared_error(y_val, gs_rf.predict(X_val))))

    predicted = gs_rf.predict(X_val)
    #y_val[122]
    #predicted[122]
    #y_val[10567]
    #predicted[10567]
