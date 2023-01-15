# -*- coding: utf-8 -*-

"""
@Autor: Andrea Tufo

@Project: Football-betting detection System

"""
import sys


import csv
import math
from colorama import Back, Style
from scipy.stats import norm
from lib_aima.probability import *
import lib_aima.notebook

# Global variables
NO_GOAL=0.1
DATASET_PATH_MATCH = "archive/ginf.csv"
DATASET_PATH_EVENTS = "archive/events.csv"
DATASET_PATH_FILTERED = "archive/filtered_dataset.csv"
dataVal = []
sigma2OPI=0

meanOPI=0

teamH="US Pescara"
teamA="Siena"

sectorHighOPI=0
sectorLowOPI=0

teamH_matches=[]
teamA_matches=[]


prior_teamA=[0.67, 0.33]
prior_teamH=[0.31, 0.69]


probOver1Over1=0
probUnder1Under1=0
probOver1Under1=0
probUnder1Over1=0

probHighOPIOver=0
probHighOPIUnder=0
probLowOPIOver=0
probLowOPIUnder=0


evidences_teamH=[]
evidences_teamA=[]

teamH_matches_of_intrest=[]
teamA_matches_of_intrest=[]


###################################################### UTILITIES ###################################################


def is_over1goal(goal):
    if goal > 1:
      return  True
    return False
    
def get_sensor_model(team='Bologna'):
    global dataVal, probHighOPIOver, probHighOPIUnder, probLowOPIOver, probLowOPIUnder
    
    over1=0
    under1=0
    
    for el in dataVal:
        if el['home_team'] == team:
            if is_over1goal(int(el['home_team_goal'])):
                over1 += 1
                if is_high_OPI_sector(int(el['OPI_home'])):
                    probHighOPIOver += 1
                else: probLowOPIOver += 1
            else:
                under1 += 1
                if is_high_OPI_sector(int(el['OPI_home'])):
                    probHighOPIUnder += 1
                else: probLowOPIUnder += 1
        elif el['away_team'] == team:
            if is_over1goal(int(el['away_team_goal'])):
                over1 += 1
                if is_high_OPI_sector(int(el['OPI_away'])):
                    probHighOPIOver += 1
                else: probLowOPIOver += 1
            else:
                under1 += 1
                if is_high_OPI_sector(int(el['OPI_away'])):
                    probHighOPIUnder += 1
                else: probLowOPIUnder += 1
                
    probHighOPIOver = float(probHighOPIOver/over1)
    probLowOPIOver = float(probLowOPIOver/over1)
    
    
    probHighOPIUnder = float(probHighOPIUnder/under1)
    probLowOPIUnder = float(probLowOPIUnder/under1)

    
    
    

def transition_model_calculation(team='Bologna'):
    
    global dataVal, probOver1Over1, probUnder1Under1, probOver1Under1,probUnder1Over1
    
    prevSect=''
    
    overToOver=0
    overToUnder=0
    underToUnder=0
    underToOver=0
    
    for el in dataVal:
        if el['home_team'] == team:
            if prevSect.__len__() == 0:
                if is_over1goal(int(el['home_team_goal'])):
                    prevSect = 'o'
                else: prevSect = 'u'
            else:
                if prevSect == 'o' and is_over1goal(int(el['home_team_goal'])):
                    overToOver += 1
                elif prevSect == 'o' and not is_over1goal(int(el['home_team_goal'])):
                    overToUnder += 1
                    prevSect = 'u'
                elif prevSect == 'u' and is_over1goal(int(el['home_team_goal'])):
                    underToOver += 1
                    prevSect = 'o'
                elif prevSect == 'u' and not is_over1goal(int(el['home_team_goal'])):
                    underToUnder += 1
        elif el['away_team'] == team:
            if prevSect.__len__() == 0:
                if is_over1goal(int(el['away_team_goal'])):
                    prevSect = 'o'
                else: prevSect = 'u'
            else:
                if prevSect == 'o' and is_over1goal(int(el['away_team_goal'])):
                    overToOver += 1
                elif prevSect == 'o' and not is_over1goal(int(el['away_team_goal'])):
                    overToUnder += 1
                    prevSect = 'u'
                elif prevSect == 'u' and is_over1goal(int(el['away_team_goal'])):
                    underToOver += 1
                    prevSect = 'o'
                elif prevSect == 'u' and not is_over1goal(int(el['away_team_goal'])):
                    underToUnder += 1
                    

    
    sum_ = overToOver + overToUnder + underToUnder + underToOver
    
    probOver1Over1 = float(overToOver/sum_)
    probOver1Under1= float(overToUnder/sum_)
    probUnder1Under1 = float(underToUnder/sum_)
    probUnder1Over1 = float(underToOver/sum_)
    
    

def is_high_OPI_sector(OPI):
    interval=meanOPI/math.sqrt(sigma2OPI)
    
    
    if OPI <= meanOPI - (2*interval):
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
        
        
        
def calculate_mean_and_sigma2_OPI(team='Bologna'):
    
    global dataVal
    global meanOPI
    global sigma2OPI
    
    summatory=0
    count=0

    for el in dataVal:
        if el['home_team'] == team:
            count += 1
            summatory += float(el['OPI_home'])
            
        elif el['away_team'] == team:
            count += 1
            summatory += float(el['OPI_away'])
        
    meanOPI = summatory/count
    
    summatory=0
    for el in dataVal:
        if el['home_team'] == team:
            summatory += math.pow((float(el['OPI_home']) - meanOPI), 2)
            
        elif el['away_team'] == team:
            summatory += math.pow((float(el['OPI_away']) - meanOPI), 2)
        
    
    sigma2OPI = summatory/count
        
    
    
def calculate_probabilities_OPI():
    
    global sectorHighOPI, sectorLowOPI, meanOPI, sigma2OPI
    
    interval=meanOPI/math.sqrt(sigma2OPI)


    sectorHighOPI = float(norm.cdf(meanOPI + (2*interval), meanOPI, math.sqrt(sigma2OPI)))    

    
    sectorLowOPI = float(norm.cdf(meanOPI - (2*interval), meanOPI, math.sqrt(sigma2OPI)))    

    
def get_teamH_teamA_matches(teamH, teamA):
    
    global dataVal
    global teamH_matches
    global teamA_matches
    
    for el in dataVal:
        if el['home_team'] == teamH or el['away_team'] == teamH:
            teamH_matches.append(el)
            
        if el['home_team'] == teamA or el['away_team'] == teamA:
            teamA_matches.append(el)
            
def get_match_id(teamH,teamA,matches):

    for i,el in enumerate(matches):
        if el['home_team'] == teamH and el['away_team'] == teamA:
            return i
    
    return -1
            
def get_team_H_evidence_array(teamH,teamA):
    global teamH_matches, evidences_teamH, teamH_matches_of_intrest
    
    match_id = get_match_id(teamH,teamA,teamH_matches)    
    
 
    start_index = match_id - 10
    end_index = match_id + 10
    
    for i,el in enumerate(teamH_matches):
        if i >= start_index and i < end_index:
            teamH_matches_of_intrest.append(el)
            if el['home_team'] == teamH:
                if is_high_OPI_sector(float(el['OPI_home'])):
                    evidences_teamH.append(True)
                else: evidences_teamH.append(False)
            else:
                if is_high_OPI_sector(float(el['OPI_away'])):
                    evidences_teamH.append(True)
                else: evidences_teamH.append(False)

def get_teamA_evidence_array(teamH,teamA):
    global teamA_matches, evidences_teamA, teamA_matches_of_intrest
    
    match_id = get_match_id(teamH,teamA,teamA_matches)    
    print(match_id)
    start_index = match_id - 10
    end_index = match_id + 10
    
    for i,el in enumerate(teamA_matches):
        if i >= start_index and i < end_index:
            teamA_matches_of_intrest.append(el)
            if el['home_team'] == teamA:
                if is_high_OPI_sector(float(el['OPI_home'])):
                    evidences_teamA.append(True)
                else: evidences_teamA.append(False)
            else:
                if is_high_OPI_sector(float(el['OPI_away'])):
                    evidences_teamA.append(True)
                else: evidences_teamA.append(False)
                
def unfair_match():
    global dataVal
    
    match_id = get_match_id(dataVal)
    
    dataVal[match_id]['home_team_goal'] = '2'
    dataVal[match_id]['away_team_goal'] = '2'
    dataVal[match_id]['location_home']=['16','6','4']
    dataVal[match_id]['location_away']=['18', '17', '8','6']
    dataVal[match_id]['shots']='9'


def print_OPI_sector(OPI):
    if is_high_OPI_sector(float(OPI)):
        return "HIGH"
    return "LOW"
    
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
                        'OPI_home' : row['OPI_home'], 
                        'OPI_away' : row['OPI_away'],                                    
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
           if row["league"] == "I1" and row["season"] == "2013":
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
                       'OPI_home' : 0,
                       'OPI_away' : 0,                              # Potential Goals Index 
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
                      'adv_stats', 'shots', 'shots_on_target', 'post_hit', 'penalties', 'location_home','location_away', 'OPI_home', 'OPI_away', 'homeVP', 'DP', 'awayVP', 'totalP']
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

         
        
         
         
         
def calculate_OPI():
    
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
                match['OPI_home'] = float(home_type_3*3 + home_type_2*2 + home_type_1)
                match['OPI_away'] = float(away_type_3*3 + away_type_2*2 + away_type_1)        
      




def HMM_cons(team_home='Lecce',team_away="Lazio"):
    calculate_OPI()
    calculate_mean_and_sigma2_OPI()
    transition_model_calculation()
    get_sensor_model()
    get_teamH_teamA_matches(team_home,team_away)
    get_team_H_evidence_array(team_home,team_away)
    get_teamA_evidence_array(team_home,team_away)


get_filtered_values()
HMM_cons(teamH,teamA)


transition_model = [[probOver1Over1 , probUnder1Over1], [probUnder1Over1 ,probOver1Under1]]
sensor_model = [[probHighOPIOver, probHighOPIUnder],[probLowOPIOver, probLowOPIUnder]]
hmm = HiddenMarkovModel(transition_model, sensor_model)

hmm.prior=prior_teamH
belief_teamH = forward_backward(hmm, ev=evidences_teamH)

hmm.prior = prior_teamA
belief_teamA = forward_backward(hmm, ev=evidences_teamA)

def print_color(level):
    level = float(level)

    if level <= 0.30:
        print(Back.RED + '_______'+ Style.RESET_ALL)
    elif level > 0.30 and level <= 0.50:
        print(Back.YELLOW + '_______'+ Style.RESET_ALL)
    elif level > 0.50 and level <= 0.70:
        print(Back.GREEN + '_______'+ Style.RESET_ALL)
    else:
        print(Back.WHITE + '_______' + Style.RESET_ALL)
        
        
def print_results(team, array_of_matches, belief,i):

    print(Style.RESET_ALL + "  " +array_of_matches[i]['home_team'],"        ",array_of_matches[i]['away_team'])
    print("  " +" ",array_of_matches[i]['home_team_goal'],"            ",array_of_matches[i]['away_team_goal'])
    if array_of_matches[i]['home_team'] == team: 

        if is_over1goal(int(array_of_matches[i]['home_team_goal'])):
            print("  " + team + " scored more than one goal. PROBABILITY: ", str("%.2f" % belief[i][0]), end=" ")
            print_color(belief[i][0])
        else : 
            print("  " +team, " scored less then 2 goals. PROBABILITY: ", str("%.2f" % belief[i][1]), end=" ")
            print_color(belief[i][1])
    else:
        if is_over1goal(int(array_of_matches[i]['away_team_goal'])):
            print("  " +team + " scored more than one goal. PROBABILITY: ", str("%.2f" % belief[i][0]),end=" ")
            print_color(belief[i][0])
        else : 
            print("  " +team, " scored less then 2 goals. PROBABILITY: ", str("%.2f" % belief[i][1]),end=" ")
            print_color(belief[i][1])



print(teamH)
for i in range(0,14):
    if teamH_matches_of_intrest[i]['away_team']==teamA:
        print("------------------------- FIXED MATCH -------------------")
        print_results(teamH, teamH_matches_of_intrest, belief_teamH, i)
        print("---------------------------------------------------------")
    else:
        print_results(teamH, teamH_matches_of_intrest, belief_teamH, i)
        
    print()
    print()

print()
print()
print("--------------------------------------------------------------")
print()
print()
print(teamA)
print()

for i in range(0,14):
    if teamA_matches_of_intrest[i]['home_team']==teamH:
        print("------------------------ FIXED MATCH -----------------------")
        print_results(teamA, teamA_matches_of_intrest, belief_teamA, i)
        print("------------------------------------------------------------")
    else:
        print_results(teamA, teamA_matches_of_intrest, belief_teamA, i)
        
    print()
    print()









