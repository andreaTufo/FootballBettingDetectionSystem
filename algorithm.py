# -*- coding: utf-8 -*-

"""
@Autor: Andrea Tufo

@Project: Football-betting detection System

"""

import csv

#Global variables
DATASET_PATH = "FootballDataEurope/FootballDataEurope.csv"
dataVal = []


# takes the values from the csv file and puts them into an array after a filtering by league and season
# (only italian league and season 2015/2016)
def getValuesFiltered():
    
    global dataVal
    
    with open(DATASET_PATH, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=";")
        
        for j,row in enumerate(reader):
           if row["league_name"] == "Italy Serie A" and row["season"] == "2015/2016":
               temp = []
               temp.append(row["id"])
               temp.append(row["home_team"])
               temp.append(row["away_team"])
               temp.append(row["home_team_goal"])
               temp.append(row["away_team_goal"]) 
               temp.append(row["B365H"]) 
               temp.append(row["B365D"]) 
               temp.append(row["B365A"])
               dataVal.append(temp)
            



getValuesFiltered()
