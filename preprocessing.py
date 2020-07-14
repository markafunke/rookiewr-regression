#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 09:22:59 2020

@author: markfunke
"""

import scrape_nfl
import pandas as pd
import seaborn as sns
import matplotlib.plotly as plt

# Scrape draft, combine, team stats, nfl stats, and college stats
# for all drafted wide receivers from the years 2000 - 2020
# Need team stats from 1999-2019 as I will be testing the previous year's
# team's total receiving stats as a feature
draft_df_00_20 = scrape_nfl.scrape_draft_data(2000,2020)
combine_df_00_20 = scrape_nfl.scrape_combine_data(2000,2020)
team_df_99_19 = scrape_nfl.scrape_team_data(1999,2019)
college_df_00_20 = scrape_nfl.scrape_college_data(draft_df_00_20)
nfl_df_00_20 = scrape_nfl.scrape_nfl_data(draft_df_00_20)

# Pickle scraped files as a checkpoint to avoid re-running scrapers
draft_df_00_20.to_pickle("pickles/draft.pkl")
combine_df_00_20.to_pickle("pickles/combine.pkl")
team_df_99_19.to_pickle("pickles/team.pkl")
college_df_00_20.to_pickle("pickles/college.pkl")
nfl_df_00_20.to_pickle("pickles/nfl.pkl")

# Read in pickled files to continue analysis
draft_df_00_20 = pd.read_pickle('pickles/draft.pkl')
combine_df_00_20 = pd.read_pickle('pickles/combine.pkl')
team_df_99_19 = pd.read_pickle('pickles/team.pkl')
college_df_00_20 = pd.read_pickle('pickles/college.pkl')
nfl_df_00_20 = pd.read_pickle('pickles/nfl.pkl')

# Merge 5 scraped files into one dataframe
# The following process is laid out as follows:
#   1) Treat draft_df_00_20 as the "base" dataframe where all others are merged
#   2) Make any adjustments to other 4 dataframes as needed to prepare for merge
#   3) Merge college, nfl, team, and combine data onto the "base" dataframe

# Merge NFL Data, nfl_link is unique to both datasets
columns_to_merge = ["rookie_rec_yards","nfl_link"]
nfl_to_merge = nfl_df_00_20[columns_to_merge]
draft_df_00_20 = draft_df_00_20.merge(nfl_to_merge
                                     , how = "left"
                                     , left_on = "nfl_link"
                                     , right_on = "nfl_link")

# Merge College Data, college_link is unique to both datasets
columns_to_merge = ["conf","col_class","col_rec","col_rec_yds","col_rec_td","col_scrim_yds","col_scrim_td","college_link"]
college_to_merge = college_df_00_20[columns_to_merge]
draft_df_00_20 = draft_df_00_20.merge(college_to_merge
                                     , how = "left"
                                     , left_on = "college_link"
                                     , right_on = "college_link")

# Merge Combine Data
#Clean "player" column in draft data before merging on "player"
draft_df_00_20['player_clean'] = draft_df_00_20.apply(scrape_nfl.clean_player_name, axis=1)


columns_to_merge = ["nfl_link","college_link","year","player"
                    ,"height","weight","time_40","vertical","bench_reps"
                    ,"broad_jump","cone_3","shuttle","draft_pick"]
combine_to_merge = combine_df_00_20[columns_to_merge]
draft_df_00_20 = draft_df_00_20.merge(combine_to_merge
                                     , how = "left"
                                     , left_on = ["player_clean","year"]
                                     , right_on = ["player","year"])


# Merge Team Data
# Since Team data is for prior year's receiving,
# We need to merge on the following year
team_df_99_19["year_merge"] = (team_df_99_19["year"] + 1).astype(str)

# This function adjusts the "team" series to a 3 letter abbreviation
# in order to merge with the draft data that uses 3 letters abbreviations
team_df_99_19['team_abbrev'] = team_df_99_19.apply(scrape_nfl.add_team_abbrev, axis=1)

columns_to_merge = ["total_yards","year_merge","team_abbrev"]
team_to_merge = team_df_99_19[columns_to_merge]
draft_df_00_20 = draft_df_00_20.merge(team_to_merge
                                     , how = "left"
                                     , left_on = ["team","year"]
                                     , right_on = ["team_abbrev","year_merge"])

# Pickle pre-cleaned DataFrame
draft_df_00_20.to_pickle("pickles/draft_pre_clean.pkl")
draft_df_00_20 = pd.read_pickle("pickles/draft_pre_clean.pkl")

# Clean Dataset for Analysis
# Limit to only columns that are candidates to be features
colums_to_keep = (["player_clean","rookie_rec_yards","rnd","pick","conf","col_class"
                  ,"col_scrim_yds", "col_rec_yds", "height", "weight", "time_40", "total_yards"])

df_cleaned = draft_df_00_20[colums_to_keep]

# Limit to only rows where y (rookie_rec_yards) isn't NaN since we can't
# perform any regression analysis without a y variable
# A missing rookie_rec_yards variable may mean that the player did not make the
# NFL, but for the purpose of this analysis, we will limit to only those players
# that caught at least 1 pass in the NFL
df_cleaned = df_cleaned[df_cleaned['rookie_rec_yards'].notna()]


# Convert all whitespace to NaN
df_cleaned = df_cleaned.applymap(lambda x: np.nan if isinstance(x, str) and (not x or x.isspace()) else x)

# Convert object datatypes that should be numerical to floats
numerical = (["rookie_rec_yards","rnd","pick","col_scrim_yds","col_rec_yds"
             ,"weight", "time_40", "total_yards"])

for column in numerical:
    df_cleaned[column] = pd.to_numeric(df_cleaned[column], errors='coerce') 
   
# Convert height to inches
def get_inches(el):
    r = re.compile(r"""(\d+)- *(\d+)""")
    m = r.match(el)
    if m == None:
        return float('NaN')
    else:
        return int(m.group(1))*12 + float(m.group(2))
    
df_cleaned["height"] = df_cleaned["height"].map(get_inches, na_action='ignore')

# Convert missing and conferences out of the "Power 5" to "Other"
# Add dummy column separating power 5 and non-power 5 players
# The power 5 conferences tend to have the most talented players,
# so the theory is that a player from there may do better in the NFL
power_5_conf = ["SEC", "Big Ten", "ACC", "Big 12", "Pac-10", "Pac-12"]
df_cleaned["conf"] = df_cleaned["conf"].map(lambda x: x if x in power_5_conf else "Other")
df_cleaned["power_5"] = df_cleaned["conf"].map(lambda x: 1 if x in power_5_conf else 0)

# Convert college_class to left_early 1/0 fummy column
# The theory is that someone leaving college early is likely doing so because
# they are good enough to have success in the NFL
underclassmen = ["JR", "SO", "FR"]
df_cleaned["left_early"] = df_cleaned["col_class"].map(lambda x: 1 if x in underclassmen else 0)
df_cleaned.drop("col_class", axis = 1, inplace = True)

# Pickle cleaned file after dropping NaN
df_cleaned_dropna = df_cleaned.dropna(axis=0)
df_cleaned_dropna.to_pickle("pickles/cleaned_nona.pkl")

# Create alternative  "raw" version that we can use to test imputing means
# or medians during regression analysis
df_cleaned.to_pickle("pickles/cleaned_impute.pkl")



