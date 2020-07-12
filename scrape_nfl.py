import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re


url = "https://www.pro-football-reference.com/years/2000/index.htm#all_passing"
response = requests.get(url)        
page = response.text
        soup = BeautifulSoup(page, "lxml")
soup        
        #find all rows of table
        table = soup.find("table")
        rows = [row for row in table.find_all("tr")]
rows[3]

table = soup.find(lambda tag: 
                  tag.name=='table' 
                  and tag.has_attr('id') 
                  and tag['id']=="passing")

table


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
    
    player_df = pd.DataFrame()
    nfl_df = pd.DataFrame()
    player_lookup = 0
    
    for link in scrape_url_list["nfl_link"]:
        
        #creates url for each player
        url = f"https://www.pro-football-reference.com{link}"
        response = requests.get(url)
        
        page = response.text
        soup = BeautifulSoup(page, "lxml")

#        table = soup.find("table")

        #some players have multiple tables, find receiving & rushing table 
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
            final_year = 3
            
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
                AV = columns[30].text
                stats_dict[year] = ([year,team,games,games_started,tgt,rec,rec_yards
                                      ,rec_tds,AV])
        except:
            stats_dict = {}
        #convert dictionary to dataframe, assign player name for each year(row)
        #add player dataframe to final dataframe
        player = scrape_url_list.index[player_lookup]
        player_df = pd.DataFrame(stats_dict).T
        player_df["player"] = player
        nfl_df = pd.concat([nfl_df, player_df]) 
        player_lookup += 1
    
    nfl_df.columns= (["player","year","team","games","games_started","tgt","rec"
                      ,"rec_yards","rec_tds","AV"])
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
        player_df = pd.DataFrame(stats_dict).T
        player_df["player"] = player
        college_df = pd.concat([college_df, player_df]) 
        player_lookup += 1
    
    college_df.columns= (["year","team","conf","grade","rec","rec_yds","rec_td","scrim_yds","scrim_td","player"])
    return college_df


def scrape_team_data():


###RUN HERE


