# -*- coding: utf-8 -*-

"""
@Autor: Andrea Tufo

@Project: Football-betting detection System

"""

import csv
import math
from scipy.stats import norm
from aima_python.probability import *
from aima_python.utils import print_table
from aima_python.notebook import psource, pseudocode, heatmap

# Global variables
NO_GOAL=0.1
DATASET_PATH_MATCH = "archive/ginf.csv"
DATASET_PATH_EVENTS = "archive/events.csv"
DATASET_PATH_FILTERED = "archive/filtered_dataset.csv"
dataVal = []
sigma2UGI=0

meanUGI=0

sectorHighUGI=0
sectorLowUGI=0

udinese_matches=[]
novara_matches=[]


prior_novara=[0.62, 0.38]
prior_udinese=[0.57, 0.43]

probSectHToSectH=0
probSectHToSectL=0 
probSectLToSectH=0
probSectLToSectL=0

probOver3HighUgi=0
probUnder3LowUgi=0
probOver3LowUgi=0
probUnder3HighUgi=0

evidences_udinese=[]
evidences_novara=[]

udinese_matches_of_intrest=[]
novara_matches_of_intrest=[]


###################################################### UTILITIES ###################################################

def get_sensor_model(team='Cagliari'):
    global dataVal, probOver3HighUgi,probOver3LowUgi,probUnder3HighUgi,probUnder3LowUgi
    
    sumHighUgi=0
    sumLowUgi=0
    
    for el in dataVal:
        if el['home_team'] == team:
            if is_high_UGI_sector(int(el['UGI_home'])):
                sumHighUgi += 1
                if int(el['home_team_goal']) > 1:
                    probOver3HighUgi += 1
                else: probUnder3HighUgi += 1
            else:
                sumLowUgi += 1
                if int(el['home_team_goal']) > 1:
                    probOver3LowUgi += 1
                else: probUnder3LowUgi += 1
        elif el['away_team'] == team:
            if is_high_UGI_sector(int(el['UGI_away'])):
                sumHighUgi += 1
                if int(el['away_team_goal']) > 1:
                    probOver3HighUgi += 1
                else: probUnder3HighUgi += 1
            else:
                sumLowUgi += 1
                if int(el['away_team_goal']) > 1:
                    probOver3LowUgi += 1
                else: probUnder3LowUgi += 1
                
    probOver3HighUgi = float(probOver3HighUgi/sumHighUgi)
    probUnder3HighUgi = float(probUnder3HighUgi/sumHighUgi)
    
    
    probOver3LowUgi = float(probOver3LowUgi/sumLowUgi)
    probUnder3LowUgi = float(probUnder3LowUgi/sumLowUgi)

    
    
    

def transition_model_calculation(team='Cesena'):
    
    global dataVal, probSectHToSectH, probSectHToSectL, probSectLToSectH, probSectLToSectL
    
    prevSect=''
    
    sectHTosectH=0
    sectHTosectL=0
    sectLTosectL=0
    sectLTosectH=0
    
    for el in dataVal:
        if el['home_team'] == team:
            if prevSect.__len__() == 0:
                if is_high_UGI_sector(el['UGI_home']):
                    prevSect = 'h'
                else: prevSect = 'l'
            else:
                if prevSect == 'h' and is_high_UGI_sector(float(el['UGI_home'])):
                    sectHTosectH += 1
                elif prevSect == 'h' and not is_high_UGI_sector(float(el['UGI_home'])):
                    sectHTosectL += 1
                    prevSect = 'l'
                elif prevSect == 'l' and is_high_UGI_sector(float(el['UGI_home'])):
                    sectLTosectH += 1
                    prevSect = 'h'
                elif prevSect == 'l' and not is_high_UGI_sector(float(el['UGI_home'])):
                    sectLTosectL += 1
        elif el['away_team'] == team:
            if prevSect.__len__() == 0:
                if is_high_UGI_sector(el['UGI_away']):
                    prevSect = 'h'
                else: prevSect = 'l'
            else:
                if prevSect == 'h' and is_high_UGI_sector(float(el['UGI_away'])):
                    sectHTosectH += 1
                elif prevSect == 'h' and not is_high_UGI_sector(float(el['UGI_away'])):
                    sectHTosectL += 1
                    prevSect = 'l'
                elif prevSect == 'l' and is_high_UGI_sector(float(el['UGI_away'])):
                    sectLTosectH += 1
                    prevSect = 'h'
                elif prevSect == 'l' and not is_high_UGI_sector(float(el['UGI_away'])):
                    sectLTosectL += 1
                    
    probSectHToSectH=0
    probSectHToSectL=0
    probSectLToSectL=0
    probSectLToSectH=0
    
    sum_ = sectHTosectH + sectHTosectL + sectLTosectH + sectLTosectL
    
    probSectHToSectH = float(sectHTosectH/sum_)
    probSectHToSectL = float(sectHTosectL/sum_)
    probSectLToSectH = float(sectLTosectH/sum_)
    probSectLToSectL = float(sectLTosectL/sum_)
    
    

def is_high_UGI_sector(UGI):
    interval=meanUGI/math.sqrt(sigma2UGI)
    
    
    if UGI <= meanUGI - (2*interval):
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
        
        
        
def calculate_mean_and_sigma2_UGI(team='Cesena'):
    
    global dataVal
    global meanUGI
    global sigma2UGI
    
    summatory=0
    count=0

    for el in dataVal:
        if el['home_team'] == team:
            count += 1
            summatory += float(el['UGI_home'])
            
        elif el['away_team'] == team:
            count += 1
            summatory += float(el['UGI_away'])
        
    meanUGI = summatory/count
    
    summatory=0
    for el in dataVal:
        if el['home_team'] == team:
            summatory += math.pow((float(el['UGI_home']) - meanUGI), 2)
            
        elif el['away_team'] == team:
            summatory += math.pow((float(el['UGI_away']) - meanUGI), 2)
        
    
    sigma2UGI = summatory/count
        
    
    
def calculate_probabilities_UGI():
    
    global sectorHighUGI, sectorLowUGI, meanUGI, sigma2UGI
    
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
            
def get_match_id(matches=udinese_matches):

    for i,el in enumerate(matches):
        if el['home_team'] == 'Novara' and el['away_team'] == 'Udinese':
            return i
    
    return -1
            
def get_udinese_evidence_array():
    global udinese_matches, evidences_udinese, udinese_matches_of_intrest
    
    match_id = get_match_id()    
    
  
    start_index = match_id - 10;
    end_index = match_id + 10;
    
    for i,el in enumerate(udinese_matches):
        if i >= start_index and i < end_index:
            udinese_matches_of_intrest.append(el)
            if el['home_team'] == 'Udinese':
                if int(el['home_team_goal']) > 1:
                    evidences_udinese.append(True)
                else: evidences_udinese.append(False)
            else:
                if int(el['away_team_goal']) > 1:
                    evidences_udinese.append(True)
                else: evidences_udinese.append(False)

def get_novara_evidence_array():
    global novara_matches, evidences_novara, novara_matches_of_intrest
    
    match_id = get_match_id()    
    
    start_index = match_id - 10;
    end_index = match_id + 10;
    
    for i,el in enumerate(novara_matches):
        if i >= start_index and i < end_index:
            novara_matches_of_intrest.append(el)
            if el['home_team'] == 'Novara':
                if int(el['home_team_goal']) > 1:
                    evidences_novara.append(True)
                else: evidences_novara.append(False)
            else:
                if int(el['away_team_goal']) > 1:
                    evidences_novara.append(True)
                else: evidences_novara.append(False)
                
def unfair_match():
    global dataVal
    
    match_id = get_match_id(dataVal)
    
    print(dataVal[match_id]['home_team'])
    print(dataVal[match_id]['away_team'])
    dataVal[match_id]['home_team_goal'] = '2'
    dataVal[match_id]['away_team_goal'] = '1'
    dataVal[match_id]['location_home']=['16','6','4','4']
    dataVal[match_id]['location_away']=['18']
    dataVal[match_id]['shots']='9'



    
################################################# FILTERING FUNCTIONS ################################################

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
                match['UGI_away'] = float(away_type_3*3 + away_type_2*2 + away_type_1)        
      




get_filtered_values()
calculate_UGI()
calculate_mean_and_sigma2_UGI()
transition_model_calculation()
get_sensor_model()
get_Udinese_and_Novara_matches()
get_udinese_evidence_array()
get_novara_evidence_array()



transition_model = [[probSectHToSectH, probSectLToSectH], [probSectLToSectL,probSectHToSectL]]
sensor_model = [[probOver3HighUgi, probOver3LowUgi],[probUnder3HighUgi, probUnder3LowUgi]]
hmm = HiddenMarkovModel(transition_model, sensor_model)

hmm.prior=prior_udinese
belief_udinese = forward_backward(hmm, ev=evidences_udinese)

hmm.prior = prior_novara
belief_novara = forward_backward(hmm, ev=evidences_novara)

print()
print()
print("################# FAIR MATCH ##################")
print("TARGET MATCH: Novara - Udinese")
print()
print(udinese_matches_of_intrest[10]['home_team'], " ------ ", udinese_matches_of_intrest[10]['away_team'])
print("   " + udinese_matches_of_intrest[10]['home_team_goal'], end="               ")
print(udinese_matches_of_intrest[10]['away_team_goal'])
print()
print("Udinese probability to core less than or exactly one goal: "+  str("%.2f" % float(belief_udinese[10][1])))
print("Novara probability to score less than or exactly one goal: "+  str("%.2f" % float(belief_novara[10][1])))



unfair_match()


calculate_UGI()
calculate_mean_and_sigma2_UGI()
transition_model_calculation()
get_sensor_model()
get_Udinese_and_Novara_matches()
get_udinese_evidence_array()
get_novara_evidence_array()


transition_model = [[probSectHToSectH, probSectLToSectH], [probSectLToSectL,probSectHToSectL]]
sensor_model = [[probOver3HighUgi, probOver3LowUgi],[probUnder3HighUgi, probUnder3LowUgi]]
hmm = HiddenMarkovModel(transition_model, sensor_model)

hmm.prior=prior_udinese
belief_udinese = forward_backward(hmm, ev=evidences_udinese)

hmm.prior = prior_novara
belief_novara = forward_backward(hmm, ev=evidences_novara)


print()
print()
print("################# UNFAIR MATCH ##################")
print("Supposing to rig the match and fake it with this result:")
print(udinese_matches_of_intrest[10]['home_team'], " ------ ", udinese_matches_of_intrest[10]['away_team'])
print("   2", end="               ")
print(1)

print()
print("Udinese probability to score more than one goal: "+  str("%.2f" % float(belief_udinese[10][0])))
print("Novara probability to score more then one goal: "+  str("%.2f" % float(belief_novara[10][0])))












