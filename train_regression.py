#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fits linear regression model for NFL Rookie WR Yards using cross validation.
This code demonstrates an iterative process used to choose the best fitting
model.

Depends on:
    scrape_nfl.py
    prepoccessing.py

@author: markfunke
"""
import pandas as pd
import regression_util as rg
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from math import sqrt
from sklearn.metrics import mean_squared_error

# Read in pickle from final cleaned dataset
# Limit to only columns considered for features
# For the purpose of this analysis, only considering players with positive
# receiving yards in their rookie year.
nfl_df_clean = pd.read_pickle("pickles/cleaned.pkl")
nfl_df = nfl_df_clean.loc[:,["rookie_rec_yards", "pick", "col_rec_yds"
                           , "left_early", "power_5", "total_yards","conf"
                           , "player_clean","rnd","SEC_Rd1"]]
nfl_df = nfl_df.dropna(axis=0)
mask = nfl_df["rookie_rec_yards"] > 0
nfl_df = nfl_df[mask]

# Note the following strong correlations from the heatmap and pair plots
# created in plots.py
#   1) "pick": draft pick of player
#   2) "col_rec_yards": amount of rec yards in player's final year in college
#   3) "left_early": engineered in preprocessing.py, 
#       1: player left school as a JR, SO, or FR
#       0: player left school after SR year
#   Other variables worth testing could be:
#   1) Polynomial form of pick - as there is a dropoff from early to late rounds
#   2) "conf": Dummy variables based on conference of college. There appears
#       to be some minor patterns by conference, particularly the SEC has
#       a few of the top yardage totals.
#   3) Interaction of Round and Conference variables. Based on plot of median
#       yardage by round and conference, it appears 1st round SEC picks do
#       extraordinarily well. Created "SEC_Rd1" dummy.

# NOTE: The rest of the code is an iterative process, testing both the
# overall fit of the variables on the training set with sm_summary()
# and using cross validation to evaluate how the model generalizes with
# cross_val_scores(), as well as how a Ridge regression compares

# Separate our potential features from our target
X = nfl_df.loc[:,["pick", "col_rec_yds", "left_early", "conf", "SEC_Rd1"]]

# Our y value is right-skewed, in order to make residuals follow a normal
# distribution, transformed target variable to be roughly normal
# See plots.py for plots of target variable distribution
y = (nfl_df['rookie_rec_yards']) ** (1/3)

# Step 0: Separate out 20% of data for final test set
# Set random state for replicability, this is not necessary
X, X_test, y, y_test = \
    train_test_split(X, y, test_size=0.2, random_state = 22)

# Step 1: Create baseline model for comparison of all future models
# "pick" is the most correlated with the target variable, so starting there
# Baseline validation R2 : .248
rg.cross_val_scores(X.loc[:,["pick"]],y, rand=22, lamb=10)
rg.sm_summary(X.loc[:,["pick"]],y)

# Model 1 - Add College Receiving Yards
# Validation R2 : .257
rg.cross_val_scores(X.loc[:,["pick","col_rec_yds"]],y, rand=22, lamb=200)
rg.sm_summary(X.loc[:,["pick","col_rec_yds"]],y)

# Model 2 - Add left_early
# Validation R2 : .286
rg.cross_val_scores(X.loc[:,["pick","col_rec_yds","left_early"]],y, rand=22, lamb=200)
rg.sm_summary(X.loc[:,["pick","col_rec_yds","left_early"]],y)

# Model 3 - Test polynomial feature of pick
# as there appears to be a dropoff after early rounds
# This does increase R2 a bit, but not much is gained vs added complexity
# Validation R2 = .293
X['pick_2'] = X['pick'] ** (2)
rg.cross_val_scores(X.loc[:,["pick","col_rec_yds","left_early","pick_2"]],y, rand=22, lamb=200)
rg.sm_summary(X.loc[:,["pick","col_rec_yds","left_early","pick_2"]],y)

# Model 4 - Test adding conference dummy variables
# All conference dummies have very high p-values
# Ridge appears to agree by greatly reducing all conference features as we
# increase lamda, besides SEC (including that in model 5)
X_dummy = X.drop("pick_2",axis=1)
X_dummy = X
X_dummy = pd.get_dummies(X_dummy)
X_dummy.drop(["conf_Other"],inplace=True,axis=1)
rg.cross_val_scores(X_dummy,y, rand=22, lamb=500)
rg.sm_summary(X_dummy,y)

# Model 5 - Test adding Multiplicative SEC & Rd1 Value based on plots.py scatters
# This adds to our R2 minimally, but lowers RMSE and Ridge appears to value it
# just as much as college yards
# Validation R2 = .294
rg.cross_val_scores(X.loc[:,["pick","col_rec_yds","left_early","SEC_Rd1"]],y, rand=22, lamb=100)
rg.sm_summary(X.loc[:,["pick","col_rec_yds","left_early","SEC_Rd1"]],y)

# Final Test on Chosen Model
# Score = .279, generalizes pretty well!
# RMSE = 270, however, not a very good predictor
X_final = X[["pick","col_rec_yds","left_early","SEC_Rd1"]]
X_final_test = X_test[["pick","col_rec_yds","left_early","SEC_Rd1"]]

lm = LinearRegression()
lm.fit(X_final, y)
lm.score(X_final_test, y_test)

pred = lm.predict(X_final_test) ** 3
actual = y_test ** 3
RMSE_actual = sqrt(mean_squared_error(actual, pred)) 
RMSE_actual

#Export final file for use in plotting
total = nfl_df[["pick", "col_rec_yds","left_early","SEC_Rd1"]]
other = nfl_df[["rookie_rec_yards","player_clean","conf"]]

total["pred"] = lm.predict(total) ** 3
total["actual"] = other["rookie_rec_yards"]
total["player"] = other["player_clean"]
total["conf"] = other["conf"]

total.to_csv("final_model.csv")

if __name__ == '__main__':
    main()
