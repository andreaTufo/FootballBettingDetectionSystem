# -*- coding: utf-8 -*-

"""
@Autor: Andrea Tufo

@Project: Football-betting detection System

"""

import csv

# Global variables
DATASET_PATH = "FootballDataEurope/FootballDataEurope.csv"
dataVal = []
a = 0

# takes the values from the csv file and puts them into an array after a filtering by league and season
# (only italian league and season 2015/2016)
def filter_values():
    
    global dataVal
    global a
    
    with open(DATASET_PATH, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=";")
        
        for j,row in enumerate(reader):
           if row["league_name"] == "Italy Serie A" and row["season"] == "2015/2016":
               temp = {'id' : row["id"],
                       'home_team' : row["home_team"],
                       'away_team': row["away_team"],
                       'home_team_goal' : row["home_team_goal"],
                       'away_team_goal' : row["away_team_goal"], 
                       'homeVP' : float(100/float(row["B365H"])),   # home victory probability (with aggio)
                       'DP' : float(100/float(row["B365D"])),       # draw probability (with aggio)
                       'awayVP' : float(100/float(row["B365A"])),   # away victory probability (with aggio)
                       'totalP' : float(100/float(row["B365H"]))    # total probability with aggio
                                   + float(100/float(row["B365D"])) 
                                   + float(100/float(row["B365A"]))} 
               dataVal.append(temp)
            


# removes the aggio from each odds 
def remove_aggio_from_odds():
    
    global dataVal
    
    for el in dataVal:
         aggio = float(float(el['totalP']) - 100)
         eachAggio = float(aggio / 3)
         el['homeVP'] = float(el['homeVP'] - eachAggio)
         el['DP'] = float(el['DP'] - eachAggio)
         el['awayVP'] = float(el['awayVP'] - eachAggio)
         el['totalP'] = float(el['homeVP']) + float(el['DP']) + float(el['awayVP'])



filter_values()
remove_aggio_from_odds()





































