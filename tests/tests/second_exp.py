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
    # - Method 2: Prediction of decibels calibrated starting from those of the microphone and from the environmental data of the canary - using a frequency per second.
    # - As in the previous case, we use the data with a sampling frequency per second (such as that of the microphone and the sound level meter).
    # Due to the quantity of data we use, also in this case, those relating to a month of sampling.

    # - Split the dataset
    X_train, X_val, y_train, y_val = train_test_split(
        dataset_canarin_seconds.drop("db_phon", axis=1),    # X = tutto tranne db_phon
        dataset_canarin_seconds["db_phon"],                 # y = db_phon
        test_size=1/3, random_state=42                      # parametri divisione
    )

    # - Linear regression. (multivariate regression)
    print("Linear regression")
    lrm = LinearRegression()
    lrm.fit(X_train, y_train)
    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, lrm)

    # - The value of the coefficients attributed by the model to the individual features to understand which ones are most important.
    print(pd.Series(lrm.coef_, index=X_train.columns))

    # - Applying the standardization of data on linear regression
    print("Linear regression standardized")
    model = Pipeline([
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])
    model.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, model)
    print(pd.Series(model.named_steps["linreg"].coef_, index=X_train.columns))

    # - Polynomial regression
    print("Polynomial regression")
    model = Pipeline([
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", LinearRegression())
    ])
    model.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, model)


    # - Regularization with __Ridge__
    print("Polynomial regression with Ridge")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(degree=2, include_bias=False)),
        ("regr",  Ridge(alpha=0.5))
    ])
    model.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, model)

    # - Regularization with __Elastic Net__, (hybrid between Ridge and Lasso)
    print("Polynomial regression with ElasticNet")
    model = Pipeline([
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("scale",  StandardScaler()),
        ("linreg", ElasticNet(alpha=0.5, l1_ratio=0.2))
    ])
    model.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, model)

    # - We have tested some of the main models and understood which of these lead to a drop in the error,
    # let's perform the tuning of the hyperparameters using __Grid Search__.
    print("Polynomial regression with GRID search")
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
        "poly__degree": range(1, 41),
        "regr__alpha": [0.1, 1, 10]
    }
    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs)


    # - Random Forest
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


    # - Gradient Boosting
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

    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs_gb)
