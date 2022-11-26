# -*- coding: utf-8 -*-

"""
@Autor: Andrea Tufo

@Project: Football-betting detection System

"""

import csv
import math
from scipy.stats import norm

# Global variables
K=100
NO_GOAL=0.1
DATASET_PATH_MATCH = "archive/ginf.csv"
DATASET_PATH_EVENTS = "archive/events.csv"
DATASET_PATH_FILTERED = "archive/filtered_dataset.csv"
dataVal = []
sigma2UGI={'UGI_home' :0,
           'UGI_away':0}

meanUGI={'UGI_home' :0,
         'UGI_away':0}

sectorHighUGI=0
sectorLowUGI=0

udinese_matches=[]
novara_matches=[]

transition_model = []

novara_first_match_goal_probabilites={'0':0.30, '1':0.32, '2':0.18, '3':0.13, '>3': 0.07}
udinese_first_match_goal_probabilites={'0':0.25, '1':0.29, '2':0.22, '3':0.14, '>3': 0.1}

##################################################### UTILITIES #################################################

def is_high_UGI_sector(UGI, meanUGI, sigma2UGI):
    interval=meanUGI/math.sqrt(sigma2UGI)
    
    
    if UGI < meanUGI - (2*interval):
        return False
    
    return True
    
    

def get_shot_type(position):
    if position == '3' or position == '10' or position == '12' or position == '13' or position == '14':
        return 3
    
    if position == '7' or position == '8' or position == '9' or position == '11' or position == '15':
        return 2
    
    if position != "'" and position != "," and position != "[" and position != "]" and position != " " and position != "": 
        return 1



def get_num_of_shots(location):
    
    type_3=0
    type_2=0
    type_1=0
    
    for pos in location:
        shot_type = get_shot_type(pos)
        
        if shot_type == 3:
            type_3 += 1
        elif shot_type == 2:
            type_2 += 1
        elif shot_type == 1:
            type_1 += 1
    

    return (type_3, type_2, type_1)
        
        
        
def calculate_mean_and_sigma2_UGI():
    
    global dataVal
    global meanUGI
    global sigma2UGI
    
    summatory=0
    count=0
    
    UGI=['UGI_home','UGI_away']
    
    for ugi in UGI:
        summatory=0
        count=0
        for el in dataVal:
            count += 1
            summatory += float(el[ugi])
            
        meanUGI[ugi] = summatory/count
        
        summatory=0
        for el in dataVal:
            summatory += math.pow((float(el[ugi]) - meanUGI), 2)
        
        sigma2UGI[ugi] = summatory/count
        
    
    
#probability for a value x to be in a interval [a,b]
def sector_probabilitoes_UGI(a,b):
    
    return norm.cdf(b, meanUGI, math.sqrt(sigma2UGI)) - norm.cdf(a, meanUGI, math.sqrt(sigma2UGI))
    
    
    
def calculate_probabilities_UGI(meanUGI, sigma2UGI):
    
    global sectorHighUGI, sectorLowUGI
    
    interval=meanUGI/math.sqrt(sigma2UGI)


    sectorHighUGI = float(norm.cdf(meanUGI + (2*interval), meanUGI, math.sqrt(sigma2UGI)))    

    
    sectorLowUGI = float(norm.cdf(meanUGI - (2*interval), meanUGI, math.sqrt(sigma2UGI)))    

    
def get_Udinese_and_Novara_matches():
    
    global dataVal
    global udinese_matches
    global novara_matches
    
    for el in dataVal:
        if el['home_team'] == 'Udinese' or el['away_team'] == 'Udinese':
            udinese_matches.append(el)
            
        elif el['home_team'] == 'Novara' or el['away_team'] == 'Novara':
            novara_matches.append(el)
            
def get_match_id():
    global udinese_matches
    
    for i,el in enumerate(udinese_matches):
        if el['home_team'] == 'Udinese' and el['away_team'] == 'Novara':
            return i
    
    return -1
            
def get_5_matches_befor_and_after():
    match_id = get_match_id()    
    
    
    if match_id != -1:
        print()
        
    
################################################# FILTERING FUNCTIONS ##############################################

# takes the values directly from the csv file in which the data have already been filtered.
# if the file is empty (is the first run of the code) the function calls some utilities in order 
# to initialite this file
def get_filtered_values():
    
    global dataVal
    
    with open(DATASET_PATH_FILTERED, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=",")
            
        print('loading filtered data...' )
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
                        'location_home': row['location_home'],
                        'location_away': row['location_away'],
                        'UGI_home' : row['UGI_home'], 
                        'UGI_away' : row['UGI_away'],                                    
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
                       'location_home': [],
                       'location_away': [],
                       'UGI_home' : 0,
                       'UGI_away' : 0,                                          # Potential Goals Index 
                       'homeVP' : float(100/float(row["odd_h"])),   # home victory probability (with aggio)
                       'DP' : float(100/float(row["odd_d"])),       # draw probability (with aggio)
                       'awayVP' : float(100/float(row["odd_a"])),   # away victory probability (with aggio)
                       'totalP' : float(100/float(row["odd_h"]))    # total probability with aggio
                                   + float(100/float(row["odd_d"])) 
                                   + float(100/float(row["odd_a"]))} 
               dataVal.append(temp)
               
               
               
               """
               
                location --> 
               
                    1	Attacking half
                    2	Defensive half
                    3	Centre of the box
                    4	Left wing
                    5	Right wing
                    6	Difficult angle and long range
                    7	Difficult angle on the left
                    8	Difficult angle on the right
                    9	Left side of the box
                    10	Left side of the six yard box
                    11	Right side of the box
                    12	Right side of the six yard box
                    13	Very close range
                    14	Penalty spot
                    15	Outside the box
                    16	Long range
                    17	More than 35 yards
                    18	More than 40 yards
                    19	Not recorded
                    
                """
                
                
                
# seek the events of a match, using the events.csv file (attemps, post, shots on target, penalties)
def get_attempts(row):
    
    
    with open(DATASET_PATH_EVENTS, newline=(''), encoding=('utf-8'), errors=('ignore')) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=",")
        
        shots = 0
        locations_home = []
        locations_away = []
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
                if el['location'] != 'NA' and el['event_type'] == '1' and el['is_goal'] == '0':
                    if el['event_team'] == row['home_team']:
                        locations_home.append(el['location'])
                    elif el['event_team'] == row['away_team']:
                        locations_away.append(el['location'])
            
        row['shots'] = shots
        row['shots_on_target'] = shots_on_target
        row['post_hit'] = post_hit
        row['location_home'] = locations_home
        row['location_away'] = locations_away
            
                    
            
            
    
# for each match calls get_attempts
def get_all_attempts():
    
    global dataVal
    
    for i,row in enumerate(dataVal):
     print('\rloading and filtering  - - -  ' + str("%.2f" % float(i*100/380)) + "%" , end='') 
     if row['adv_stats'] == 'TRUE':
         get_attempts(row)
         
        
# write the filtered dataset on a file
def write_filtered_dataset():
    
    with open(DATASET_PATH_FILTERED, 'w', encoding='UTF8', newline='') as f:
        fieldnames = ['id_odsp', 'home_team', 'away_team', 'home_team_goal', 'away_team_goal', 
                      'adv_stats', 'shots', 'shots_on_target', 'post_hit', 'penalties', 'location_home','location_away', 'UGI_home', 'UGI_away', 'homeVP', 'DP', 'awayVP', 'totalP']
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

         
        
         
         
         
def calculate_UGI():
    
    global dataVal

    """
        weights
        
        3 --> 
        
            3	Centre of the box
            10	Left side of the six yard box
            12	Right side of the six yard box
            13	Very close range
            14	Penalty spot
        
       2 --> 
           
           9	Left side of the box
           11	Right side of the box
           7	Difficult angle on the left
           8	Difficult angle on the right
           15	Outside the box (means just outside the box, not too far from the goal)
           
       1 -->
          
           1    Attacking half
           2    Defensive half
           4    Left wing
           5    Right wing
           6    Difficult angle and long range
          16	Long range
          17	More than 35 yards
          18	More than 40 yards
          19	Not recorded
        
                        
    """

    
    for match in dataVal:
        (home_type_3, home_type_2, home_type_1) = get_num_of_shots(match['location_home'])
        (away_type_3, away_type_2, away_type_1) = get_num_of_shots(match['location_away'])
        
        
        if match['adv_stats'] == 'TRUE': 
                match['UGI_home'] = float(home_type_3*3 + home_type_2*2 + home_type_1)
                match['UGI_away'] = float(away_type_3*3 + away_type_2*2 + away_type_1*1)        
      

            


get_filtered_values()
calculate_UGI()
get_Udinese_and_Novara_matches()
get_5_matches_befor_and_after()


































