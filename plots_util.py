#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains functions used to create descriptive plots including
- Scatterplot
- Residual Plot

@author: markfunke
"""

import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import scipy.stats as stats


def scatter_regression(x, y, df, title, xlabel, ylabel, savename = "temp"):
    
    # read in x and y values to be used in single variable
    # linear regression and scatterplot
    # Drop NaN values, if any
    plot_df = df[[y,x]].dropna()
    
    x1 = plot_df[[x]]
    y1 = plot_df[[y]]
    
    # fit linear regression of x on y
    rgr = LinearRegression()
    rgr.fit(x1,y1)
    pred = rgr.predict(x1)
    
    # calculate R squared
    R2 = round(rgr.score(x1, y1),3)
    
    # create scatterplot of results
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(15,5))
    plt.scatter(x1,y1)
    plt.plot(x1, pred, color='red',linewidth=1)
    plt.title(title, fontsize=18 , fontweight = 'bold')
    plt.suptitle(f"R\u00b2 = {R2}"
                 ,fontsize=18, y= .83, x = .16, style = 'italic') #R Squared
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(f"figures/{savename}.png", dpi=500, transparent = True
                 ,facecolor='white',edgecolor='w');


def diagnostic_plot(x, y):
    plt.figure(figsize=(20,5))
    
    rgr = LinearRegression()
    rgr.fit(x,y)
    pred = rgr.predict(x)
    
    plt.subplot(1, 2, 1)
    res = y - pred
    plt.scatter(pred, res)
    plt.title("Residual plot")
    plt.xlabel("prediction")
    plt.ylabel("residuals")
    
    plt.subplot(1, 2, 2)
    #Generates a probability plot of sample data against the quantiles of a 
    # specified theoretical distribution 
    stats.probplot(res, dist="norm", plot=plt)
    plt.title("Normal Q-Q plot")