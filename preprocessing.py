#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 09:22:59 2020

@author: markfunke
"""

import scrape_nfl
import pandas as pd

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
columns_to_merge = ["rec_yards","AV","nfl_link"]
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
draft_df_00_20['player_clean'] = draft_df_00_20.apply(clean_player_name, axis=1)


columns_to_merge = ["nfl_link","college_link","year","player"
                    ,"height","weight","time_40","vertical","bench_reps"
                    ,"broad_jump","cone_3","shuttle","draft_pick"]
combine_to_merge = combine_df_00_20[columns_to_merge]
draft_df_00_20 = draft_df_00_20.merge(combine_to_merge
                                     , how = "left"
                                     , left_on = ["player_clean","year"]
                                     , right_on = ["player","year"])

draft_df_00_20.to_csv("test_merge.csv")


Try to merge on Name/Year
There are a couple of name mismatches, also merge on nfl_link
Take max of 2 columns?


# Merge Team Data
Create team name to abreviation dictionary
Create year + 1 column
Merge on name/year + 1



# Pickle pre-cleaned DataFrame


