"""
This module contains 5 functions used to scrape 
combine, draft, nfl, and college, stats from pro football reference.

As well as 2 functions used for cleaning the same data.

@author: markafunke
"""
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import numpy as np
import re
import time
import os


def scrape_draft_data(min_year,max_year):
    """
    Scrapes profootballreference NFL Draft data for the years entered
    into a dataframe
    
    Parameters
    ----------
    min_year : int from 2000-2020
    max_year : int from 2000-2020

    Returns
    -------
    draft_df : DataFrame

    """
    
    draft_df = pd.DataFrame()
    
    for year in range(min_year,max_year+1):
    
        #create url for each year and initiate http request
        url = f"https://www.pro-football-reference.com/play-index/draft-finder.cgi?request=1&year_min={year}&year_max={year}&type=&round_min=1&round_max=30&slot_min=1&slot_max=500&league_id=&team_id=&pos[]=WR&college_id=all&conference=any&show=all"
        response = requests.get(url)
       
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        
        #find all rows of table
        table = soup.find("table")
        rows = [row for row in table.find_all("tr")]
        
        #scrape every column and store in dictionary
        #row 32 is a repeat of column headers, skip
        draft_dict = {}
        for row in rows[2:32]+rows[33:]:
            columns = row.find_all('td')
            links = row.find_all('a')
            
            #pull links to nfl and college pages
            #all valid nfl links contain "/player"
            #all valid college links contain "sports-reference"
            #set all missing or invalid to None
            try:
                nfl_link = links[1].get('href')
                if re.search('/player',nfl_link) == None:
                    nfl_link = None  
            except:
                nfl_link = None
            try:
                college_link = links[4].get('href')
                if re.search('sports-reference',college_link) == None:
                    college_link = None
            except:
                college_link = np.NaN
            
                
            name = columns[3].text
            draft_dict[name] = [nfl_link, college_link] + [column.text for column in columns]
        
        #convert to dataframe
        draft_df_year = pd.DataFrame(draft_dict).T  #transpose
        draft_df_year.columns= (["nfl_link", "college_link", "year", "rnd", "pick", "player", "pos"
                                   , "age", "team", "first_yr", "last_yr"
                                   , "all_pro", "pro_bowl", "starter_years"
                                   , "AV_career", "games", "games_started"
                                   , "rush_att", "rush_yds", "rush_td", "rec"
                                   , "rec_yds", "rec_td", "college"
                                   , "college stats"])
        draft_df = pd.concat([draft_df, draft_df_year])
        
    return draft_df

def scrape_combine_data(min_year,max_year):
    """
    Scrapes profootballreference combine data for the years entered
    into a dataframe
    
    Parameters
    ----------
    min_year : int from 2000-2020
    max_year : int from 2000-2020

    Returns
    -------
    combine_df : DataFrame

    """
    
    combine_df = pd.DataFrame()
    
    for year in range(min_year,max_year+1):
    
        #create url for each year and initiate http request
        url = f"https://www.pro-football-reference.com/play-index/nfl-combine-results.cgi?request=1&year_min={year}&year_max={year}&height_min=65&height_max=82&weight_min=140&weight_max=400&pos%5B%5D=WR&show=all&order_by=year_id"
        response = requests.get(url)
       
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        
        #find all rows of table
        table = soup.find("table")
        rows = [row for row in table.find_all("tr")]
        
        #scrape every column and store in dictionary
        #row 51 is a repeat of column headers, skip
        combine_dict = {}
        for row in rows[1:51]+rows[52:]:
            columns = row.find_all('td')
            links = row.find_all('a')
            
            #pull links to nfl and college pages
            #all valid nfl links contain "/player"
            #all valid college links contain "sports-reference"
            #set all missing or invalid to None
            try:
                nfl_link = links[1].get('href')
                if re.search('/player',nfl_link) == None:
                    nfl_link = None  
            except:
                nfl_link = None
            try:
                college_link = links[3].get('href')
                if re.search('sports-reference',college_link) == None:
                    college_link = None
            except:
                college_link = np.NaN
            
                
            name = columns[1].text
            combine_dict[name] = [nfl_link, college_link] + [column.text for column in columns]
        
        #convert to dataframe
        combine_df_year = pd.DataFrame(combine_dict).T  #transpose
        combine_df_year.columns= (["nfl_link","college_link","year","player","pos","age","av","school","stats"
                                   ,"height","weight","time_40","vertical","bench_reps"
                                   ,"broad_jump","cone_3","shuttle","draft_pick"])
        combine_df = pd.concat([combine_df, combine_df_year])
        
    return combine_df


def scrape_nfl_data(df):
    
    """
    Scrapes profootballreference receiving stats from series of player links
    returns a dataframe containing player name and all receiving related stats
    
    Parameters
    ----------
    df : DataFrame containing series:
        "player"(string)
        "nfl_link"(link to pro football reference player page
                   e.g. "/players/B/BurrPl00.htm")

    Returns
    -------
    nfl_df : DataFrame

    """

    #limit list to just valid urls
    scrape_url_list = df[["player","nfl_link"]].dropna()
    
    #initialize dataframes to be used later
    player_df = pd.DataFrame()
    nfl_df = pd.DataFrame()
    player_lookup = 0
    
    #Use sellenium webdriver to allow for receiving and rushing table to load
    chromedriver = "/Applications/chromedriver" # path to the chromedriver executable
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    
    for link in scrape_url_list["nfl_link"]:
        
        #load receiving table with sellenium, wait for it to load fully
        driver.get(f"https://www.pro-football-reference.com{link}#all_receiving_and_rushing")
        time.sleep(1)


        #locate receiving table and parse all rows 
        soup = BeautifulSoup(driver.page_source)
        table = soup.find(lambda tag: 
                          tag.name=='table' 
                          and tag.has_attr('id') 
                          and tag['id']=="receiving_and_rushing")
        
        try:
            rows = [row for row in table.find_all("tr")]
            
            #scrape game and receiving stats for each year of player's career
            #first year begins in row 2, calculate final year of career
            stats_dict = {}
            
            #rookie year starts in row 2
            #adding functionality to pull more than 1 year by adjusting final_year
            final_year = 5
            
            for row in rows[2:final_year]:
                columns = row.find_all('td')
                year = row.find("th").text
                team = columns[1].text
                games = columns[4].text
                games_started = columns[5].text
                tgt = columns[6].text
                rec = columns[7].text
                rec_yards = columns[8].text
                rec_tds = columns[10].text
                stats_dict[year] = ([year,team,games,games_started,tgt,rec,rec_yards
                                      ,rec_tds])
        except:
            stats_dict = {}
        #convert dictionary to dataframe, assign player name for each year(row)
        #add player dataframe to final dataframe
        player = scrape_url_list.index[player_lookup]
        nfl_link = scrape_url_list.nfl_link[player_lookup]
        player_df = pd.DataFrame(stats_dict).T
        player_df["player"] = player
        player_df["nfl_link"] = nfl_link
        nfl_df = pd.concat([nfl_df, player_df]) 
        player_lookup += 1
        time.sleep(0.5)
    
    nfl_df.columns= (["year","team","games","games_started","tgt","rec"
                      ,"rookie_rec_yards","rec_tds","player","nfl_link"])
    return nfl_df


def scrape_college_data(df):
    
    """
    Scrapes profootballreference receiving stats from series of player links
    returns a dataframe containing player name and all receiving related stats
    
    Parameters
    ----------
    df : DataFrame containing series:
        "player"(string)
        "nfl_link"(link to pro football reference player page
                   e.g. "/players/B/BurrPl00.htm")

    Returns
    -------
    college_df : DataFrame

    """

    #limit list to just valid urls
    scrape_url_list = df[["player","college_link"]].dropna()
    
    player_df = pd.DataFrame()
    college_df = pd.DataFrame()
    player_lookup = 0
    
    for link in scrape_url_list["college_link"]:
        
        #creates url for each player
        response = requests.get(link)
        
        page = response.text
        soup = BeautifulSoup(page, "lxml")

        table = soup.find("table")
        
        try:

            #only want to scrape player's final season in college
            #checks to find "career" row, so we can locate the row before it
            rows = [row for row in table.find_all("tr")]
            career_row = 0
            for row in rows:
                header = row.find("th").text
                if header == "Career":
                    break
                else:
                    career_row += 1
            final_year = career_row - 1
            row = rows[final_year]

            columns = row.find_all('td')
            year = row.find("th").text
            team = columns[0].text
            conf = columns[1].text
            grade = columns[2].text
            rec = columns[5].text
            rec_yds = columns[6].text
            rec_td = columns[8].text
            scrim_yds = columns[14].text
            scrim_td = columns[16].text

            stats_dict = {}
            stats_dict[year] = ([year,team,conf,grade,rec,rec_yds,rec_td,scrim_yds,scrim_td])
        except:
            stats_dict = {}
            
        #convert dictionary to dataframe, assign player name for each year(row)
        #add player dataframe to final dataframe
        player = scrape_url_list.index[player_lookup]
        college_link = scrape_url_list.college_link[player_lookup]
        player_df = pd.DataFrame(stats_dict).T
        player_df["player"] = player
        player_df["college_link"] = college_link
        college_df = pd.concat([college_df, player_df]) 
        player_lookup += 1
        time.sleep(0.5)
    
    college_df.columns= (["col_year","col_team","conf","col_class","col_rec","col_rec_yds","col_rec_td","col_scrim_yds","col_scrim_td","player","college_link"])
    return college_df


def scrape_team_data(min_year,max_year):

    team_df = pd.DataFrame()
    
    #need to use sellenium webdriver to allow for passing table to load
    chromedriver = "/Applications/chromedriver" # path to the chromedriver executable
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    
    for year in range(min_year,max_year+1):
        
        #load passing table with sellenium, wait for it to load fully
        driver.get(f"https://www.pro-football-reference.com/years/{year}/index.htm#all_passing")
        time.sleep(3)
        
        #locate passing table and parse all rows
        soup = BeautifulSoup(driver.page_source)
        table = soup.find(lambda tag: 
                          tag.name=='table' 
                          and tag.has_attr('id') 
                          and tag['id']=="passing")

        rows = [row for row in table.find_all("tr")]
         
        #there were 31 team prior to 2002, 32 starting in 2003
        final_row = ''
        if year < 2002:
            final_row = 32
        else:
            final_row = 33
        
        #collect total receiving yards in dictionary
        stats_dict = {}
        for row in rows[1:final_row]:
            columns = row.find_all('td')
            team = columns[0].text
            total_yards = columns[5].text
            stats_dict[team] = ([year,team,total_yards])
                
        team_df_year = pd.DataFrame(stats_dict).T  #transpose
        team_df_year.columns= (["year","team","total_yards"])
        team_df = pd.concat([team_df, team_df_year])
        
    return team_df

def clean_player_name(df):
    
    #remove whitespaces
    player_name = df["player"].strip()
    
    #fix 8 outlier cases found through EDA
    player_issues = {'Ted Ginn Jr.' : 'Ted Ginn',
                     'Odell Beckham Jr.' : 'Odell Beckham, Jr.',
                     'Gary Jennings Jr' : 'Gary Jennings',
                     'Michael Pittman Jr.' : 'Michael Pittman',
                     'Lynn Bowden Jr.' : 'Lynn Bowden',
                     'JJ Nelson' : 'J.J. Nelson',
                     'JJ Arcega-Whiteside' : 'J.J. Arcega-Whiteside'}
                     
    if player_name in player_issues.keys():
            player_name = player_issues[player_name]
    
    return player_name

def add_team_abbrev(df):
    
    #mapping of team to 3 letter abbreviation
    team_abbreviations =    {'Arizona Cardinals' : 'ARI',
                            'Atlanta Falcons' : 'ATL',
                            'Baltimore Ravens' : 'BAL',
                            'Buffalo Bills' : 'BUF',
                            'Carolina Panthers' : 'CAR',
                            'Chicago Bears' : 'CHI',
                            'Cincinnati Bengals' : 'CIN',
                            'Cleveland Browns' : 'CLE',
                            'Dallas Cowboys' : 'DAL',
                            'Denver Broncos' : 'DEN',
                            'Detroit Lions' : 'DET',
                            'Green Bay Packers' : 'GNB',
                            'Houston Texans' : 'HOU',
                            'Indianapolis Colts' : 'IND',
                            'Jacksonville Jaguars' : 'JAX',
                            'Kansas City Chiefs' : 'KAN',
                            'Los Angeles Chargers' : 'LAC',
                            'Los Angeles Rams' : 'LAR',
                            'Miami Dolphins' : 'MIA',
                            'Minnesota Vikings' : 'MIN',
                            'New Orleans Saints' : 'NOR',
                            'New England Patriots' : 'NWE',
                            'New York Giants' : 'NYG',
                            'New York Jets' : 'NYJ',
                            'Oakland Raiders' : 'OAK',
                            'Philadelphia Eagles' : 'PHI',
                            'Pittsburgh Steelers' : 'PIT',
                            'San Diego Chargers' : 'SDG',
                            'Seattle Seahawks' : 'SEA',
                            'San Francisco 49ers' : 'SFO',
                            'St. Louis Rams' : 'STL',
                            'Tampa Bay Buccaneers' : 'TAM',
                            'Tennessee Titans' : 'TEN',
                            'Washington Redskins' : 'WAS'}
                     
    team = df["team"]
    team_abbrev = team_abbreviations[team]
    
    # Oakland changed to Las Vegas Raiders in 2020
    # St Louis Rams changed to Los Angeles Rams in 2016
    # San Diego Chargers changed to Los Angeles Chargers in 2017
    
    if team_abbrev == "OAK" and df["year_merge"] == "2020":
        team_abbrev = "LVR"
    if team_abbrev == "STL" and df["year_merge"] == "2016":
        team_abbrev = "LAR"
    if team_abbrev == "SDG" and df["year_merge"] == "2017":
        team_abbrev = "LAC"

    return team_abbrev

if __name__ == '__main__':
    main()
    
