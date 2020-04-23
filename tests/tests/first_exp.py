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
from sklearn.svm import SVR
from sklearn.model_selection import ShuffleSplit
import util

def models(dataset):
    # - Method 1:
    # - In the simplest case we try to perform a univariate regression, that is, starting from the microphone decibels, try to predict those of the sound level meter. Let's then divide the independent variable (x) from the dependent variable we want to predict (y).
    X = dataset[["db_mic"]]
    y = dataset["db_phon"]

    # - Split data in training and validation sets.
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=1/3, random_state=42)

    # - Linear regression
    print("Linear regression")

    lrm = LinearRegression()
    lrm.fit(X_train, y_train)

    # - Testing the score of the model on the set of valdation.
    # - __Note__: the default metric of the regression models is the coefficient $ R ^ 2 $ which describes how much the model approximates the variability of the data. The value of this metric varies between [0-1]; the greater it is, the better the model captures the variability of the data.    lrm.score(X_val, y_val)

    # - Print out the error metrics.
    util.print_error_stats(X_val, y_val, lrm)

    # - Plot data
    util.plot_model_on_data(X_train, y_train, lrm)

    # - Testing the prediction on some values.
    predicted = lrm.predict(X_val)
    #print(predicted[0])
    #print(y_val[0])
    #print(predicted[100])
    #print(y_val[100])


    # - Polynomial regression
    print("Polynomial regression")
    prm = Pipeline([
        # name     element
        ("poly",   PolynomialFeatures(degree=2, include_bias=False)),
        ("linreg", LinearRegression())
    ])

    prm.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, prm)

    # - Testing all combinations manually would be of little unuseless and expensive in terms of times, which is why we can use the __Grid Search__.
    # The __Grid Search__ allows us to set different values for each hyperparameter and then train a separate model for each possible combination
    # of these values by __k-fold cross validation__. Finally, once the score of each model has been calculated, the best model is automatically
    # trained on all data.
    print("Polynomial regression with GRID search")
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

    # - Encapsulating the result of the __Grid Search__ inside a DataFrame pandas so that we can check the results more simply and clearly.
    print(pd.DataFrame(gs.cv_results_).sort_values("rank_test_score").head(50))
    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs)

    # - We can expect that as the degree increases then the error continues to decrease, until it goes to __Overfitting__, to avoid this problem we can use __Regularization__
    # This technique allows to continue with the increase of the degree of the polynomial and the consequent complexity of the model, while avoiding the problem of __Overfitting__.
    # In this case the __Regularization__ is carried out by means of the __Ridge Regression__ or a regression that tries to limit the Theta values calculated by the algorithm through
    # a hypersphere centered on the origin.
    print("Polynomial regression with Ridge and GridSearch")
    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly",  PolynomialFeatures(include_bias=False)),
        ("regr",  Ridge())
    ])

    grid = {
        "poly__degree": range(1, 51),      # degree of the polynomial
        "regr__alpha":  [0.1, 1, 10]       # regularization
    }
    gs = GridSearchCV(model, param_grid=grid)
    gs.fit(X_train, y_train)

    print(pd.DataFrame(gs.cv_results_).sort_values("rank_test_score").head(50))
    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs)

    # - Testing some values using the validation set
    predicted = gs.predict(X_val)
    #print(predicted[0])
    #print(y_val[0])
    #print(predicted[100])
    #print(y_val[100])
    # - Plot data
    util.plot_model_on_data(X_train, y_train, gs)

    # - Random Forest
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
    # - Print out the error metrics
    util.print_error_stats(X_val, y_val, gs_lrf)

    # - Plot data
    util.plot_model_on_data(X_train, y_train, gs_lrf)

    # - SVR
    print("Support Vector Regression")

    grid_svr = {
        'kernel': ['linear'],
        'C': [1e0, 1e1, 1e2, 1e3],
        'gamma': np.logspace(-2, 2, 5)
    }

    #set up tuning algorithm
    gs_svr = GridSearchCV(SVR(), param_grid=grid_svr)
    #fit the classifier
    gs_svr.fit(X_train, y_train)
    util.print_error_stats(X_val, y_val, gs_svr)
    util.plot_model_on_data(X_train, y_train, gs_svr)
