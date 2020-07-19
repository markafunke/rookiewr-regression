#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create plots of nfl dataset created in proprocessing.py, as well as
regression models in train_regression.py

Used for Exploratory Data Analysis and for visuals in presentation

@author: markfunke
"""

import plots_util as plot
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Read in pickle from final cleaned dataset in preprocessing.py
# Limit to only columns considered for features
# For the purpose of this analysis, only considering players with positive
# receiving yards in their rookie year.
nfl_df_clean = pd.read_pickle("pickles/cleaned.pkl")
nfl_df = nfl_df_clean.loc[:,["rookie_rec_yards", "pick", "col_rec_yds",
                           "left_early", "power_5", "total_yards","conf"
                           ,"player_clean","rnd","SEC_Rd1", "time_40"]]

mask = nfl_df["rookie_rec_yards"] > 0
nfl_df = nfl_df[mask]

# Test correlation between all variables to look for strong features
sns.heatmap(nfl_df.corr(), cmap="seismic", annot=True, vmin=-1, vmax=1);

# Create pairplot to look for any visual patterns between features

# Evaluate distribution of target variable
# Can see target is right skewed
plt.hist(nfl_df["rookie_rec_yards"],bins=50)

# Evaluate distribution of target variable with transformation
# Target appears to be close to normal with transformation
plt.hist(nfl_df["rookie_rec_yards"] ** (1/3),bins=20)

# Residual and Q-Q plot to check distribution of residuals
# Note this plot will only run if this code runs after train_regression.py
plot.diagnostic_plot(X_final,y)

# Plot 40 Yard Dash Scatter
plot.scatter_regression("time_40","rookie_rec_yards",nfl_df
                   , title = "40 Time vs. Rookie Receiving Yards (2000 - 2020)"
                   , xlabel = "40 Yard Dash Time (seconds)"
                   , ylabel = "Receiving Yards - Rookie Year"
                   , savename = "40time")

# Plot College Receiving Yards Scatter
plot.scatter_regression("col_rec_yds","rookie_rec_yards",nfl_df
                   , title = "College Yards vs. Rookie Yards"
                   , xlabel = "College Receiving Yards - Last Season"
                   , ylabel = "Receiving Yards - Rookie Year"
                   , savename = "college yards")

# Plot Draft Pick Scatter
plot.scatter_regression("pick","rookie_rec_yards",nfl_df
                   , title = "Draft Pick vs. Receiving Yards"
                   , xlabel = "Draft Pick"
                   , ylabel = "Receiving Yards - Rookie Year"
                   , savename = "draft pick")

# Create jitter strip plot of left_early variable
# Can see higher concentration of low yardage totals of seniors over fr/so/jr
sns.stripplot("left_early", "rookie_rec_yards", data=nfl_df, jitter = .2, color=".1")
plt.xlabel("Left Early (1 = Yes)")
plt.ylabel("Rookie Receiving Yards")
plt.title("Does Leaving College Early Increase Yardage?")
sns.set_style("white")
sns.despine();

# Create bar charts showing SEC dominance in Round 1 vs randomness in Round 2-7
# Round 1 Chart
bar_plot = nfl_df.copy()
mask = bar_plot["rnd"] == 1
bar_plot = bar_plot[mask]

bar_chart = bar_plot.groupby(["conf"]).rookie_rec_yards.median().reset_index()

sns.barplot(x = 'conf',y='rookie_rec_yards',data=bar_chart, color = ".5",
            order = ["SEC", "ACC", "Big 12", "Other", "Big Ten", "Pac-12"])
plt.xlabel("Conference")
plt.ylabel("Rookie Receiving Yards")
plt.title("Median Yardage by 1st Round Picks")
sns.set_style("white")
sns.despine()
plt.tight_layout()
plt.savefig(f"figures/SEC1.png", dpi=500, transparent=True);

# Round 2-7 Chart
bar_plot2 = nfl_df.copy()
mask = bar_plot2["rnd"] != 1
bar_plot2 = bar_plot2[mask]

bar_chart2 = bar_plot2.groupby(["conf"]).rookie_rec_yards.median().reset_index()

sns.barplot(x = 'conf',y='rookie_rec_yards',data=bar_chart2, color = ".5",
            order = ["SEC", "ACC", "Big 12", "Other", "Big Ten", "Pac-12"])
plt.xlabel("Conference")
plt.ylabel("Rookie Receiving Yards")
plt.title("Median Yardage by 2nd-7th Round Picks")
sns.set_style("white")
sns.despine()
plt.tight_layout()
plt.ylim(0,800)
plt.savefig(f"figures/SEC2.png", dpi=500, transparent=True);




