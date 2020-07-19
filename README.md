# Predicting Rookie WR Yards With Linear Regression

This code scrapes NFL, college, draft, and combine data to fit a linear regression model on rookie wide receiver yards in the NFL. 

## Conclusions

Review the conclusions of this study, and final model used at the following blog post: *COMING SOON!*

## Outline of Files

In order to re-produce the results of this linear regression model, clone this repository and run the code in the following order:

**1. [preprocessing.py](https://github.com/markafunke/rookiewr-regression/blob/master/preprocessing.py/):** 

Scrapes and cleans the following data for wide receivers from [pro-football-reference](https://www.pro-football-reference.com/) and combines into a single pandas DataFrame:
    -Draft position
    -Combine stats
    -NFL rookie year stats
    -NCAA Senior (or final) year stats
    -NFL team-level season passing totals

Outputs pickles needed to run the following 2 files.

*Note: part or all of this code could be run on its own to scrape data for one's own analysis. The code is set up to scrape data from 2000-2020, but could be modified to scrape different years. Let me know of any interesting trends you can find!*

**2. [train_regression.py](https://github.com/markafunke/rookiewr-regression/blob/master/train_regression.py/):**

Fits linear regression model for NFL Rookie WR Yards using cross validation.
This code demonstrates an iterative process used to choose the best performing model based on R-squared and RMSE.

**3. [plots.py](https://github.com/markafunke/rookiewr-regression/blob/master/plots.py/):**

Used for Exploratory Data Analysis to inform decisions made in train_regression.py, as well as for visuals used in [presentation](https://github.com/markafunke/rookiewr-regression/blob/master/NFL_WR_Regression.pdf).

The python code above utilizes the following modules created for this project:

**[scrape_nfl.py](https://github.com/markafunke/rookiewr-regression/blob/master/scrape_nfl.py/)**: 

Contains five functions used to scrape 
data from [pro-football-reference](https://www.pro-football-reference.com/)  and [https://www.sports-reference.com/cfb/](https://www.pro-football-reference.com/), as well as two two functions used for cleaning the same data.

**[regression_util.py](https://github.com/markafunke/rookiewr-regression/blob/master/regression_util.py/)**: 

Contains 2 functions used to score linear regression models.

- sm_summary - Stats Model linear fit summary

- cross_val_score - Sklearn cross validation R2 score for both linear and Ridge.

**[plots_util.py](https://github.com/markafunke/rookiewr-regression/blob/master/plots_util.py/)**: 

Contains functions used to create descriptive scatter, residual, and Q-Q plots.