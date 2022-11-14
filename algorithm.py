# -*- coding: utf-8 -*-

"""
@Autor: Andrea Tufo

@Project: Football-betting detection System

"""

import csv

# Global variables
DATASET_PATH_MATCH = "archive/ginf.csv"
DATASET_PATH_EVENTS = "archive/events.csv"
DATASET_PATH_FILTERED = "archive/filtered_dataset.csv"
dataVal = []



def get_filtered_values():
    
    global dataVal
    
    with open(DATASET_PATH_FILTERED, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=",")
            
        for row in reader:
             temp = {'id_odsp' : row["id_odsp"],
                        'home_team' : row["home_team"],
                        'away_team': row["away_team"],
                        'home_team_goal' : row["home_team_goal"],
                        'away_team_goal' : row["away_team_goal"], 
                        'adv_stats': row['adv_stats'],
                        'shots' : row['shots'],
                        'shots_on_target' : row['shots_on_target'],
                        'post_hit': row['post_hit'],
                        'penalties': row['penalties'],
                        'location': row['location'],
                        'EG' : row['EG'],                                
                        'homeVP' : row['homeVP'],
                        'DP' : row['DP'],
                        'awayVP' : row['awayVP'],
                        'totalP' :   row['totalP']
                        }
             dataVal.append(temp)
             
        if dataVal.__len__() == 0:
            print("not found... Start filtering...")
            filter_values()
            remove_aggio_from_odds()
            get_all_attempts()
            write_filtered_dataset()
    
     
            


# takes the values from the csv file and puts them into an array after a filtering by league and season
# (only italian league and season 2012/2013)
def filter_values():
    
    global dataVal
    
    
    with open(DATASET_PATH_MATCH, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=",")
        
        for row in reader:
           if row["league"] == "I1" and row["season"] == "2012":
               temp = {'id_odsp' : row["id_odsp"],
                       'home_team' : row["ht"],
                       'away_team': row["at"],
                       'home_team_goal' : row["fthg"],
                       'away_team_goal' : row["ftag"], 
                       'adv_stats': row['adv_stats'],
                       'shots' : 0,
                       'shots_on_target' : 0,
                       'post_hit': 0,
                       'penalties': 0,
                       'location': [],
                       'EG' : 0,                                    # Expected goals
                       'homeVP' : float(100/float(row["odd_h"])),   # home victory probability (with aggio)
                       'DP' : float(100/float(row["odd_d"])),       # draw probability (with aggio)
                       'awayVP' : float(100/float(row["odd_a"])),   # away victory probability (with aggio)
                       'totalP' : float(100/float(row["odd_h"]))    # total probability with aggio
                                   + float(100/float(row["odd_d"])) 
                                   + float(100/float(row["odd_a"]))} 
               dataVal.append(temp)
               

def get_attempts(row):
    
    global dataVal
    
    with open(DATASET_PATH_EVENTS, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=",")
        
        shots = 0
        locations = []
        shots_on_target = 0
        post_hit = 0
        for el in reader:
            if el['id_odsp'] == row['id_odsp']: 
                if el['event_type'] == '1':
                    shots += 1
                if el['shot_outcome'] == '1' or el['shot_outcome'] == '3':
                    shots_on_target += 1
                if el['shot_outcome'] == '4':
                    shots_on_target += 1
                    post_hit += 1
                if el['location'] != 'NA':
                    locations.append(el['location'])
            
        row['shots'] = shots
        row['shots_on_target'] = shots_on_target
        row['post_hit'] = post_hit
        row['location'] = locations
            
                    
            
            
    
    
def get_all_attempts():
    
    global dataVal
    
    for i,row in enumerate(dataVal):
     print('\rloading and filtering  - - -  ' + str("%.2f" % float(i*100/380)) + "% " + str(i) , end='') 
     if row['adv_stats'] == 'TRUE':
         get_attempts(row)
        


def write_filtered_dataset():
    
    with open(DATASET_PATH_FILTERED, 'w', encoding='UTF8', newline='') as f:
        fieldnames = ['id_odsp', 'home_team', 'away_team', 'home_team_goal', 'away_team_goal', 
                      'adv_stats', 'shots', 'shots_on_target', 'post_hit', 'penalties', 'location', 'EG', 'homeVP', 'DP', 'awayVP', 'totalP']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataVal)
    


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



get_filtered_values()





































