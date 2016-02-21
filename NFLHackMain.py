import scipy
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pylab as pl
# import sklearn
import csv
import json
import os
import NFLFileLogistics
# from sklearn import svm
# from sklearn.svm import SVC
from scipy import stats
# from sklearn import linear_model
# from pprint import pprint

game1Plays ='./data/Game1/game1plays'
teamPlays ='./data/Game1/TeamRosters' # changed this directory to have all 6 team's rosters
#game 2 and 3 plays
game2Plays ='./data/Game1/game2plays'
game3Plays = './data/Game1/game3plays'

positionIds = ["OT", "RB", "OL"] #SelfReference

metrics = ["outside" , "inside", "speed", "passCatching", "shortYardage"]
rb_dict = {}
rb_list = []
rb_list_name = {}
ot_list = []
ol_list = []
rbIDMetricStorage = {}
runningBackRatios = {}
insideRBRatio = {}
outsideRBRatio = {}
speedRBRatio = {}
leagueAverages = {}


playermetricRatios = {}
playerMetricScores = {}

# plt.plot([1,2,3,4])
# plt.show()

"""For team json file in TeamRoster, retrieves all ID's for provided position"""
def getPlayers():
    teamInformationDict = NFLFileLogistics.getJSONFiles(teamPlays)
    for fileName in teamInformationDict:
        roster = NFLFileLogistics.loadTeamJSONFile(fileName) 
        for player in roster["teamPlayers"]:
            if player["positionGroup"] == "RB":
                rb_list.append((player["nflId"], roster["team"]["abbr"], player["displayName"]))
            if player["position"] == "OT":
                ot_list.append((player["nflId"], roster["team"]["abbr"]))
            if player["positionGroup"] == "OL":
                ol_list.append((player["nflId"], roster["team"]["abbr"]))

def make_rb_dict():
    playInfoDict = NFLFileLogistics.getJSONFiles(game1Plays)
    for play_file in playInfoDict:
        play = NFLFileLogistics.loadJSONFile1(play_file)
        for running_back in rb_list:
            for stat_getter in play["play"]["playStats"]:
                for key in stat_getter:
                    if key == "nflId":
                        if stat_getter[key] == running_back[0]:
                            if running_back[0] not in rb_dict:
                                rb_dict[running_back[0]] = []
                                rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))
                            else :
                                if ((play["gameId"], play["ngsPlayId"], running_back[1]) not in rb_dict[running_back[0]]) :
                                    rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))

    # print rb_dict
    #importing 2nd and 3rd game's running back plays                                
    playInfoDict = NFLFileLogistics.getJSONFiles(game2Plays)
    for play_file2 in playInfoDict:
        play = NFLFileLogistics.loadJSONFile2(play_file2)
        for running_back in rb_list:
            for stat_getter in play["play"]["playStats"]:
                for key in stat_getter:
                    if key == "nflId":
                        if stat_getter[key] == running_back[0]:
                            if running_back[0] not in rb_dict:
                                rb_dict[running_back[0]] = []
                                rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))
                            else :
                                if ((play["gameId"], play["ngsPlayId"], running_back[1]) not in rb_dict[running_back[0]]) :
                                    rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))  

        # print rb_dict

    playInfoDict = NFLFileLogistics.getJSONFiles(game3Plays)
    for play_file3 in playInfoDict:
        play = NFLFileLogistics.loadJSONFile3(play_file3)
        for running_back in rb_list:
            for stat_getter in play["play"]["playStats"]:
                for key in stat_getter:
                    if key == "nflId":
                        if stat_getter[key] == running_back[0]:
                            if running_back[0] not in rb_dict:
                                rb_dict[running_back[0]] = []
                                rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))
                            else :
                                if ((play["gameId"], play["ngsPlayId"], running_back[1]) not in rb_dict[running_back[0]]) :
                                    rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))  

        # print rb_dict

# print "   "
        
def calculateInsideRun(rb_play_dict):
    for rbID in rb_play_dict:
        total_inside_plays = 0
        total_inside_yards = 0
        for ngsGameandPlayID in rb_play_dict[rbID]:
            game_num = ngsGameandPlayID[0]
            if (game_num == 1 or game_num == 2 or game_num == 3): #Check Game
                ngsPlayID_string = str(ngsGameandPlayID[1])
                tempFile = None
                if game_num == 1:
                    tempFile = NFLFileLogistics.loadJSONFile1(ngsPlayID_string + ".json")
                elif game_num == 2:
                    tempFile = NFLFileLogistics.loadJSONFile2(ngsPlayID_string + ".json")
                else: 
                    tempFile = NFLFileLogistics.loadJSONFile3(ngsPlayID_string + ".json")
                if tempFile["play"]["playType"] == "play_type_rush":
                    offensive_tackles_loc = offensive_tackles_y(tempFile)
                    line_of_scrimmage = tempFile["play"]["absoluteYardlineNumber"]
                    play_stats = tempFile["play"]["playStats"]
                    for play_stat in play_stats:
                        if "nflId" in play_stat:
                            if play_stat["nflId"] == rbID:
                                for trackingData in tempFile["homeTrackingData"]:
                                    if play_stat["yards"] < 0:
                                        if "event" in trackingData:
                                            if trackingData["event"] == "playStopped":
                                                if trackingData["playerTrackingData"]["y"] >= offensive_tackles_loc[0] and trackingData["playerTrackingData"]["y"] <= offensive_tackles_loc[1]:
                                                    total_inside_plays += 1 
                                                    total_inside_yards += play_stat["yards"]
                                    else:
                                        y_loc = min_and_max(trackingData, rbID, line_of_scrimmage)
                                        if y_loc >= offensive_tackles_loc[0] and y_loc <= offensive_tackles_loc[1]:
                                            total_inside_plays += 1 
                                            total_inside_yards += play_stat["yards"]
                                for trackingData in tempFile["awayTrackingData"]:
                                    if play_stat["yards"] < 0:
                                        if "event" in trackingData:
                                            if trackingData["playerTrackingData"]["event"] == "playStopped":
                                                if trackingData["playerTrackingData"]["y"] >= offensive_tackles_loc[0] and trackingData["playerTrackingData"]["y"] <= offensive_tackles_loc[1]:
                                                    total_inside_plays += 1 
                                                    total_inside_yards += play_stat["yards"]
                                    else:
                                        y_loc = min_and_max(trackingData, rbID, line_of_scrimmage)
                                        if y_loc >= offensive_tackles_loc[0] and y_loc <= offensive_tackles_loc[1]:
                                            total_inside_plays += 1 
                                            total_inside_yards += play_stat["yards"]
        if total_inside_plays == 0:
            insideRBRatio[rbID] = 0
        else:
            insideRBRatio[rbID] = float(total_inside_yards) / float(total_inside_plays)

def calculateOutsideRun(rb_play_dict):
    for rbID in rb_play_dict:
        total_outside_plays = 0
        total_outside_yards = 0
        for ngsGameandPlayID in rb_play_dict[rbID]:
            game_num = ngsGameandPlayID[0]
            if (game_num == 1 or game_num == 2 or game_num == 3): #Check Game
                ngsPlayID_string = str(ngsGameandPlayID[1])
                tempFile = None
                if game_num == 1:
                    tempFile = NFLFileLogistics.loadJSONFile1(ngsPlayID_string + ".json")
                elif game_num == 2:
                    tempFile = NFLFileLogistics.loadJSONFile2(ngsPlayID_string + ".json")
                else: 
                    tempFile = NFLFileLogistics.loadJSONFile3(ngsPlayID_string + ".json")
                if tempFile["play"]["playType"] == "play_type_rush":
                    offensive_tackles_loc = offensive_tackles_y(tempFile)
                    line_of_scrimmage = tempFile["play"]["absoluteYardlineNumber"]
                    play_stats = tempFile["play"]["playStats"]
                    for play_stat in play_stats:
                        if "nflId" in play_stat:
                            if play_stat["nflId"] == rbID:
                                for trackingData in tempFile["homeTrackingData"]:
                                    if play_stat["yards"] < 0:
                                        if "event" in trackingData:
                                            if trackingData["event"] == "playStopped":
                                                if trackingData["playerTrackingData"]["y"] < offensive_tackles_loc[0] or trackingData["playerTrackingData"]["y"] > offensive_tackles_loc[1]:
                                                    total_outside_plays += 1 
                                                    total_outside_yards += play_stat["yards"]
                                    else:
                                        y_loc = min_and_max(trackingData, rbID, line_of_scrimmage)
                                        if y_loc < offensive_tackles_loc[0] or y_loc > offensive_tackles_loc[1]:
                                            total_outside_plays += 1 
                                            total_outside_yards += play_stat["yards"]
                                for trackingData in tempFile["awayTrackingData"]:
                                    if play_stat["yards"] < 0:
                                        if "event" in trackingData:
                                            if trackingData["playerTrackingData"]["event"] == "playStopped":
                                                if trackingData["playerTrackingData"]["y"] < offensive_tackles_loc[0] or trackingData["playerTrackingData"]["y"] > offensive_tackles_loc[1]:
                                                    total_outside_plays += 1 
                                                    total_outside_yards += play_stat["yards"]
                                    else:
                                        y_loc = min_and_max(trackingData, rbID, line_of_scrimmage)
                                        if y_loc < offensive_tackles_loc[0] or y_loc > offensive_tackles_loc[1]:
                                            total_outside_plays += 1 
                                            total_outside_yards += play_stat["yards"]
        if total_outside_plays == 0:
            outsideRBRatio[rbID] = 0
        else:
            outsideRBRatio[rbID] = float(total_outside_yards) / float(total_outside_plays)

def speed(runningPlayDict):
    for rbID in runningPlayDict:
        speed_array = []
        for ngsGameandPlayID in runningPlayDict[rbID]:
            max_speed = 0
            game_num = ngsGameandPlayID[0]
            tempFile = None
            if (game_num == 1 or game_num == 2 or game_num == 3): #Check Game
                ngsPlayID_string = str(ngsGameandPlayID[1])  
                if game_num == 1:
                    tempFile = NFLFileLogistics.loadJSONFile1(ngsPlayID_string + ".json")
                elif game_num == 2:
                    tempFile = NFLFileLogistics.loadJSONFile2(ngsPlayID_string + ".json")
                else: 
                    tempFile = NFLFileLogistics.loadJSONFile3(ngsPlayID_string + ".json")
                incomplete = False
            if tempFile["play"]["playType"] == "play_type_rush":
                for playStat in tempFile["play"]["playStats"]:
                    if "nflId" in playStat:
                        if playStat["nflId"] == rbID:
                                
                                    
                # if tempFile["play"]["playStats"][0]["yards"] < 5: 
                #     print("RB " + str(rbID) + " did not run enough")
                #     continue
                            if (playStat["statId"] == 10 or playStat["statId"] == 11) and playStat["yards"] >= 5:
                                    
                                for tracking_data in tempFile["homeTrackingData"]:
                                   if tracking_data["nflId"] == rbID:
                                        for player_data in tracking_data["playerTrackingData"]:
                                            max_speed = max(max_speed, player_data["s"])
                                        speed_array.append(max_speed)
                                for tracking_data in tempFile["awayTrackingData"]:
                                    if tracking_data["nflId"] == rbID:
                                        for player_data in tracking_data["playerTrackingData"]:
                                            max_speed = max(max_speed, player_data["s"])
                                        speed_array.append(max_speed)
        avg_speed = 0
        if len(speed_array) != 0:
            for speed in speed_array:
               avg_speed += speed
            avg_speed = avg_speed*1.0 /(len(speed_array))*1.0
            if rbID not in speedRBRatio:
                speedRBRatio[rbID] = avg_speed
        else:
            speedRBRatio[rbID] = 0


#Have all the RB id's, go through all the play IDs, figure out which plays that the RB is part and that yardsToGo <=3
def offensive_tackles_y(play):
    max_y = 0
    min_y = 10000000000000000000

    for lineman in ol_list:
        for playerH in play["homeTrackingData"]:
            if lineman[0] == playerH["nflId"]:
                for player_data in playerH["playerTrackingData"]:
                    if "event" in player_data:
                        if player_data["event"] == "snap":
                            min_y = min(player_data["y"], min_y)
                            max_y = max(player_data["y"], max_y)
        for playerA in play["awayTrackingData"]:
            if lineman[0] == playerA["nflId"]:
                for player_data in playerA["playerTrackingData"]:
                    if "event" in player_data:
                        if player_data["event"] == "snap":
                            min_y = min(player_data["y"], min_y)
                            max_y = max(player_data["y"], max_y)
    return (min_y, max_y)


#Two Cases from Here:


def calculateShortYardage(rb_play_dict):
    for rbID in rb_play_dict:
        totalSuccesses = 0
        totalEligiblePlays = 0
        yardsGained = 0.0
        for ngsGameandPlayID in rb_play_dict[rbID]:
            game_num = ngsGameandPlayID[0]
            if (game_num == 1 or game_num == 2 or game_num == 3): #Check Game
                ngsPlayID_string = str(ngsGameandPlayID[1])
                tempFile = None
                if game_num == 1:
                    tempFile = NFLFileLogistics.loadJSONFile1(ngsPlayID_string + ".json")
                elif game_num == 2:
                    tempFile = NFLFileLogistics.loadJSONFile2(ngsPlayID_string + ".json")
                else: 
                    tempFile = NFLFileLogistics.loadJSONFile3(ngsPlayID_string + ".json")
                if (tempFile["play"]["playType"] == "play_type_rush"):
                    if (tempFile["play"]["yardsToGo"] <= 3):

                        # For if its on the goal line, defined by being on the other team's side of the field and within 3 yards of their end zone
                        if ((ngsGameandPlayID[2] != tempFile["play"]["yardlineSide"]) and (tempFile["play"]["yardlineNumber"] <=3)):
                            totalEligiblePlays += 1
                            for playStat in tempFile["play"]["playStats"]:
                                if "nflId" in playStat:
                                    if playStat["nflId"] == rbID:
                                        yardsGained += playStat["yards"]
                                else:
                                    if playStat["statId"] == 3:
                                        totalSuccesses += 1
                                    
                        # For if its not on the goal line, but 3rd or 4th down, within 3 yards of next first down
                        else:
                            if (tempFile["play"]["down"] >= 3):
                                totalEligiblePlays += 1
                                for playStat in tempFile["play"]["playStats"]:
                                    if "nflId" in playStat:
                                        if playStat["nflId"] == rbID:
                                            yardsGained += playStat["yards"]
                                    else:
                                        if playStat["statId"] == 3:
                                            totalSuccesses += 1
        if ((totalEligiblePlays) == 0):
            calculatedTuple = (0, 0)
        else:                  
            averageYardsGained = yardsGained/(totalEligiblePlays)
            successRatio = ((totalSuccesses*1.0)/(totalEligiblePlays*1.0))
            calculatedTuple = (averageYardsGained, successRatio)
        if (rbID in rbIDMetricStorage):
            rbIDMetricStorage[rbID].append(("Short Yardage Metric", calculatedTuple))
        else:
            rbIDMetricStorage[rbID] = [("Short Yardage Metric", calculatedTuple)]

def min_and_max(trackingData, rbid, scrimmage):
    max_x = 0
    min_x = 1000
    min_y = 1000
    max_y = 0
    for track in trackingData["playerTrackingData"]:
            if scrimmage >= track["x"] and max_x < track["x"]:
                max_x = track["x"]
                max_y = track["y"]
            if scrimmage <= track["x"] and min_x > track["x"]:
                min_x = track["x"]
                max_y = track["y"]
    if max_x == min_x:
        return (max_y + min_y)  / 2
    slope = (max_y - min_y)/(max_x - min_x)
    return max_y - slope*(max_x - scrimmage)


# calculateShortYardage(rb_dict)
# print rbIDMetricStorage

def calculatePassCatching(runningPlayDict):

    for rbID in runningPlayDict:

        totalComplete = 0
        yardsGained = 0.0
        totalEligiblePlays = 0
        # print rbID

        # print runningPlayDict[rbID]

        for ngsGameandPlayID in runningPlayDict[rbID]:
            game_num = ngsGameandPlayID[0]
            if (game_num == 1 or game_num == 2 or game_num == 3): #Check Game
                ngsPlayID_string = str(ngsGameandPlayID[1])
                tempFile = None
                if game_num == 1:
                    tempFile = NFLFileLogistics.loadJSONFile1(ngsPlayID_string + ".json")
                elif game_num == 2:
                    tempFile = NFLFileLogistics.loadJSONFile2(ngsPlayID_string + ".json")
                else: 
                    tempFile = NFLFileLogistics.loadJSONFile3(ngsPlayID_string + ".json")
                incomplete = False
                if (tempFile["play"]["playType"] == "play_type_pass"):
                    #print "Pass Play"
                    # print "exists"
                    totalEligiblePlays += 1
                    for playStat in tempFile["play"]["playStats"]:
                        if "nflId" in playStat:
                            if playStat["nflId"] == rbID:
                                if playStat["statId"] == 21:
                                    totalComplete +=1;
                                    yardsGained += playStat["yards"]
                                elif playStat["statId"] == 22:
                                    totalComplete +=1;
                                    yardsGained += playStat["yards"]    
        
        if ((totalEligiblePlays) == 0):
            calculatedTuple = (0, 0)
        else :
            averageYardsGained = yardsGained/totalEligiblePlays
            catchSuccessRatio = (totalComplete*1.0)/(totalEligiblePlays*1.0)
            calculatedTuple = (averageYardsGained, catchSuccessRatio)

        if (rbID in rbIDMetricStorage):
            rbIDMetricStorage[rbID].append(("Pass Catching Metric", calculatedTuple))
        else:
            rbIDMetricStorage[rbID] = [("Pass Catching Metric", calculatedTuple)]

# print "Printing the metric storage\n"
# print rbIDMetricStorage

def setLeagueAverages():
    #leagueAverages

    # {2552483: [('Pass Catching Metric', (1.0, 1.0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 4.2), ('Outside Run Metric', 5.698275862068965), ('Speed Run Metric', 6.688)], 
    # 2552388: [('Pass Catching Metric', (0.0, 0.0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 2.5), ('Outside Run Metric', 2.671875), ('Speed Run Metric', 0)], 2495173: [('Pass Catching Metric', (0, 0)), ('Short Yardage Metric', (1.0, 1.0)), ('Inside Run Metric', 1.3333333333333333), ('Outside Run Metric', 1.5121951219512195), ('Speed Run Metric', 0)], 2539272: [('Pass Catching Metric', (6.0, 0.5)), ('Short Yardage Metric', (0.0, 0.3333333333333333)), ('Inside Run Metric', 1.4), ('Outside Run Metric', 6.007246376811594), ('Speed Run Metric', 7.45)], 2553129: [('Pass Catching Metric', (0, 0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 0), ('Outside Run Metric', 0), ('Speed Run Metric', 0)], 2552394: [('Pass Catching Metric', (-2.0, 1.0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 6.333333333333333), ('Outside Run Metric', 6.333333333333333), ('Speed Run Metric', 6.38)], 2553451: [('Pass Catching Metric', (5.0, 0.6666666666666666)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 5.545454545454546), ('Outside Run Metric', 3.7914438502673797), ('Speed Run Metric', 6.395)], 2532876: [('Pass Catching Metric', (2.5, 1.0)), ('Short Yardage Metric', (3.5, 0.5)), ('Inside Run Metric', 1.0), ('Outside Run Metric', 4.046153846153846), ('Speed Run Metric', 4.525)], 2530702: [('Pass Catching Metric', (7.166666666666667, 0.6666666666666666)), ('Short Yardage Metric', (16.666666666666668, 0.6666666666666666)), ('Inside Run Metric', 2.5555555555555554), ('Outside Run Metric', 6.3803921568627455), ('Speed Run Metric', 6.8675)], 2506416: [('Pass Catching Metric', (-0.2, 0.2)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 4.461538461538462), ('Outside Run Metric', 4.0504731861198735), ('Speed Run Metric', 5.7025)], 2550419: [('Pass Catching Metric', (10.0, 0.8)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 7.0), ('Outside Run Metric', 7.0), ('Speed Run Metric', 5.92)], 2541556: [('Pass Catching Metric', (11.333333333333334, 1.0)), ('Short Yardage Metric', (1.0, 1.0)), ('Inside Run Metric', 0.3333333333333333), ('Outside Run Metric', 14.301587301587302), ('Speed Run Metric', 10.78)], 2541173: [('Pass Catching Metric', (7.666666666666667, 0.3333333333333333)), ('Short Yardage Metric', (6.0, 1.0)), ('Inside Run Metric', 3.68), ('Outside Run Metric', 3.665768194070081), ('Speed Run Metric', 5.905714285714287)], 2550486: [('Pass Catching Metric', (7.0, 0.5)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 3.3636363636363638), ('Outside Run Metric', 3.2966507177033493), ('Speed Run Metric', 6.623333333333334)], 2536056: [('Pass Catching Metric', (0.0, 0.0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 8.0), ('Outside Run Metric', 8.536585365853659), ('Speed Run Metric', 5.585)], 2495326: [('Pass Catching Metric', (0.6666666666666666, 0.6666666666666666)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 0), ('Outside Run Metric', 0), ('Speed Run Metric', 0)], 2543514: [('Pass Catching Metric', (0, 0)), ('Short Yardage Metric', (-1.0, 0.0)), ('Inside Run Metric', 2.9375), ('Outside Run Metric', 3.3535031847133756), ('Speed Run Metric', 5.515000000000001)], 2552476: [('Pass Catching Metric', (1.0, 1.0)), ('Short Yardage Metric', (1.0, 1.0)), ('Inside Run Metric', 1.0), ('Outside Run Metric', 1.0), ('Speed Run Metric', 0)], 4445: [('Pass Catching Metric', (7.0, 1.0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 0), ('Outside Run Metric', 0), ('Speed Run Metric', 0)], 2531230: [('Pass Catching Metric', (0, 0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 0), ('Outside Run Metric', 0), ('Speed Run Metric', 0)]}

    passCatchingYPC = 0.0
    passCatchingCompletionRatio = 0.0
    shortYardageYPC = 0.0
    shortYardageSuccessRatio = 0.0
    insideRunYPC = 0.0
    outsideRunYPC = 0.0
    averageMaxSpeed = 0.0


    for metricArray in rbIDMetricStorage.values():
        passCatchingYPC += metricArray[0][1][0]
        passCatchingCompletionRatio += metricArray[0][1][1]
        shortYardageYPC += metricArray[1][1][0]
        shortYardageSuccessRatio += metricArray[1][1][1]
        insideRunYPC += metricArray[2][1]
        outsideRunYPC += metricArray[3][1]
        averageMaxSpeed += metricArray[4][1]

    

    numberPlayers =  len(rbIDMetricStorage)

    passCatchingYPC /= numberPlayers
    passCatchingCompletionRatio /= numberPlayers
    shortYardageYPC /= numberPlayers
    shortYardageSuccessRatio /= numberPlayers
    insideRunYPC /= numberPlayers
    outsideRunYPC /= numberPlayers
    averageMaxSpeed /= numberPlayers

    leagueAverages["passCatchingYPC"] =  passCatchingYPC
    leagueAverages["passCatchingCompletionRatio"] =passCatchingCompletionRatio
    leagueAverages["shortYardageYPC"] = shortYardageYPC
    leagueAverages["shortYardageSuccessRatio"] = shortYardageSuccessRatio
    leagueAverages["insideRunYPC"] = insideRunYPC
    leagueAverages["outsideRunYPC"] = outsideRunYPC
    leagueAverages["averageMaxSpeed"] =averageMaxSpeed

    #2552483: [('Pass Catching Metric', (1.0, 1.0)), ('Short Yardage Metric', (0, 0)), ('Inside Run Metric', 4.2), ('Outside Run Metric', 5.698275862068965), ('Speed Run Metric', 6.688)], 
def calcRBOutsideYardage():

    for rbID in rbIDMetricStorage.keys():
        playermetricRatios[rbID] = []

        finalResult = rbIDMetricStorage[rbID][3][1] / leagueAverages["outsideRunYPC"]

        playermetricRatios[rbID].append(("outsideRatio", finalResult))

    calcRBInsideYardage()

def calcRBInsideYardage():

    for rbID in rbIDMetricStorage.keys():

        finalResult = rbIDMetricStorage[rbID][2][1] / leagueAverages["insideRunYPC"]

        playermetricRatios[rbID].append(("insideRatio", finalResult))

    calcRBopenFieldRunning()

def calcRBopenFieldRunning():

    for rbID in rbIDMetricStorage.keys():

        finalResult = rbIDMetricStorage[rbID][4][1] / leagueAverages["averageMaxSpeed"]

        playermetricRatios[rbID].append(("speedRatio", finalResult))

    calcRBpassCatching()

def calcRBpassCatching():

	for rbID in rbIDMetricStorage.keys():

		partYPC = rbIDMetricStorage[rbID][0][1][0] / leagueAverages["passCatchingYPC"]
		partCompletionRatio = rbIDMetricStorage[rbID][0][1][1] / leagueAverages["passCatchingCompletionRatio"]
		finalResult = partYPC + partCompletionRatio
		playermetricRatios[rbID].append(("passCatchingRatio", finalResult))

	calcRBshortYardage()


def calcRBshortYardage():

    for rbID in rbIDMetricStorage.keys():

        partYPC = rbIDMetricStorage[rbID][1][1][0] / leagueAverages["shortYardageYPC"]
        partCompletionRatio = rbIDMetricStorage[rbID][1][1][1] / leagueAverages["shortYardageSuccessRatio"]
        finalResult = partYPC + partCompletionRatio

        playermetricRatios[rbID].append(("shortYardageRatio", finalResult))

def setScoresForEachMetric():

	index = 0

	while index < 5 :

		rbIDs = []
		tempArray = []

		for rbId, listofMetricRatios in playermetricRatios.items():
			rbIDs.append(rbId)
			tempArray.append(listofMetricRatios[index][1])

		a = np.array(tempArray)
		zscores = stats.zscore(a)

		# print("All running backs:")
		# print rbIDs
		for i in range(0, len(rbIDs)):
			if index == 0:
				playerMetricScores[rbIDs[i]] = []
			# print "What it look lik " 
			# print  playerMetricScores


			zscore = zscores[i]
			score = stats.norm.cdf(zscore) * 20
			playerMetricScores[rbIDs[i]].append((metrics[index], score))

		index+=1


	# print playerMetricScores

"""Basically where all the function calls are happening in the program"""
getPlayers()
make_rb_dict()
#print rb_dict
calculatePassCatching(rb_dict)
calculateShortYardage(rb_dict)
calculateInsideRun(rb_dict)
#print insideRBRatio
#print("Done with inner")
calculateOutsideRun(rb_dict)
#print outsideRBRatio
#print("Done with outer")
speed(rb_dict)
#print speedRBRatio
# print rb_dict

# print rbIDMetricStorage
for ID in insideRBRatio:
    if ID in rbIDMetricStorage:
        rbIDMetricStorage[ID].append(("Inside Run Metric", insideRBRatio[ID]))
    else:
        rbIDMetricStorage[ID] = []
        rbIDMetricStorage[ID].append(("Inside Run Metric", insideRBRatio[ID]))

for ID in outsideRBRatio:
    if ID in rbIDMetricStorage:
        rbIDMetricStorage[ID].append(("Outside Run Metric", outsideRBRatio[ID]))
    else:
        rbIDMetricStorage[ID] = []
        rbIDMetricStorage[ID].append(("Outside Run Metric", outsideRBRatio[ID]))

for ID in speedRBRatio:
    if ID in rbIDMetricStorage:
        rbIDMetricStorage[ID].append(("Speed Run Metric", speedRBRatio[ID]))
    else:
        rbIDMetricStorage[ID] = []
        rbIDMetricStorage[ID].append(("Speed Run Metric", speedRBRatio[ID]))


setLeagueAverages()
calcRBOutsideYardage()

setScoresForEachMetric()



""" Printing out the graph """


class Radar(object):

    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = np.arange(90, 90+360, 360.0/self.n)
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i) 
                         for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=12)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(range(1, 6), angle=angle, labels=label)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, 5)

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)


# titles = list("ABCDE")

# labels = [
#     list("abcde"), list("12345"), list("uvwxy"), 
#     ["one", "two", "three", "four", "five"],
#     list("jklmn")
# ]


print rb_list
fig = pl.figure(figsize=(5, 5))

titles = ["Outside Running", "Inside Running", "Downfield Running", "Short Yardage Running" , "Pass Catching"]
labels = [
    ['0','5','10','15','20'],
    ['0','5','10','15','20'],
    ['0','5','10','15','20'],
    ['0','5','10','15','20'],
    ['0','5','10','15','20']
]


radar = Radar(fig, titles, labels)
radar.plot([1, 3, 2, 5, 4],  "-", lw=2, color="b", alpha=0.4, label="first")
radar.plot([2.3, 2, 3, 3, 2],"-", lw=2, color="r", alpha=0.4, label="second")
radar.plot([3, 4, 3, 4, 2], "-", lw=2, color="g", alpha=0.4, label="third")
radar.ax.legend()
plt.show()


# print playermetricRatios















                    

