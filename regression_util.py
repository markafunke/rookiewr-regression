#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains 2 functions used to score linear regression models.
sm_summary - Stats Model linear fit summary
cross_val_score - Sklearn cross validation R2 score for both linear and Ridge.

@author: markfunke
"""
import numpy as np
from math import sqrt

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

import statsmodels.api as sm

def sm_summary(X, y):
    '''
    For a set of features and target X, y, fit statsmodels linear regression
    Return full model summary
    
    Parameters
    ----------
    X : DataFrame of Features
    Y: Series of Target Variable

    Returns
    -------
    StatsModels Linear Regression Fit Summary

    """
    '''
  
    # report summary from Stats Models OLS to evaluate p values
    # and coefficients in more detail
    X = sm.add_constant(X)
    model = sm.OLS(y, X)
    fit = model.fit()
    return fit.summary()
    
    
def cross_val_scores(X, y, rand = None, lamb = 1):
    """
    For a set of features X, and target y, fit both Linear Regression
    and Ridge model. Validate with cross validation and print validation
    R2, RMSE,and print Ridge coefficients.

    Parameters
    ----------
    X : DataFrame of features
    y : Series of target variable
    rand : Integer to set random state. The default is None.
    lamb : Float to set lamda of Ridge model. The default is 1.

    Returns
    -------
    Ridge Model coefficients.

    """
    
    # Prepare data for cross validation
    X, y = np.array(X), np.array(y)
    kf = KFold(n_splits=5, shuffle=True, random_state = rand)
    
    # Initiate lists to store results
    cv_lm_r2s = []
    cv_lm_RMSEs = []
    cv_lm_reg_r2s = []
    
    for train_ind, val_ind in kf.split(X,y):
        X_train, y_train = X[train_ind], y[train_ind]
        X_val, y_val = X[val_ind], y[val_ind]
        
        # Create Linear and Ridge Objects
        lm = LinearRegression()
        lm_reg = Ridge(alpha=lamb)
        
        # linear model
        lm.fit(X_train, y_train)
        cv_lm_r2s.append(lm.score(X_val, y_val))
        
        # Inverse transformation and calc RMSE
        cubed_y_val = y_val ** 3
        cubed_pred = lm.predict(X_val) ** 3
        RMSE_actual = sqrt(mean_squared_error(cubed_y_val, cubed_pred)) 
        cv_lm_RMSEs.append(RMSE_actual)
        
        # regularization feature scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # ridge regression
        lm_reg.fit(X_train_scaled, y_train)
        cv_lm_reg_r2s.append(lm_reg.score(X_val_scaled, y_val))
        
    linear_model_r2 = round(np.mean(cv_lm_r2s),3)
    linear_model_RMSE = round(np.mean(cv_lm_RMSEs),1)
    ridge_model_r2 = round(np.mean(cv_lm_reg_r2s),3)
        
    print(f"Linear Val R2: {linear_model_r2}")
    print(f"Linear Val RMSE: {linear_model_RMSE}")
    print(f"Ridge Val R2: {ridge_model_r2}")
    return lm_reg.coef_

if __name__ == '__main__':
    main()