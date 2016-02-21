# import scipy
# import numpy as np
# import matplotlib.cm as cm
# import matplotlib.pyplot as plt
# import pylab as pl
# import sklearn
import csv
import json
import os
import NFLFileLogistics
# from sklearn import svm
# from sklearn.svm import SVC
# from scipy import io
# from sklearn import linear_model
# from pprint import pprint

game1Plays ='./data/Game1/game1plays'
teamPlays ='./data/Game1/TeamRosters' # changed this directory to have all 6 team's rosters
#game 2 and 3 plays
game2Plays ='./data/Game1/game2plays'
game3Plays = './data/Game1/game3plays'

positionIds = ["OT", "RB", "OL"] #SelfReference
rb_dict = {}
rb_list = []
ot_list = []
ol_list = []
rbIDMetricStorage = {}
runningBackRatios = {}
insideRBRatio = {}
outsideRBRatio = {}
speedRBRatio = {}


"""For team json file in TeamRoster, retrieves all ID's for provided position"""
def getPlayers():
    teamInformationDict = NFLFileLogistics.getJSONFiles(teamPlays)
    for fileName in teamInformationDict:
        roster = NFLFileLogistics.loadTeamJSONFile(fileName) 
        for player in roster["teamPlayers"]:
            if player["positionGroup"] == "RB":
                rb_list.append((player["nflId"], roster["team"]["abbr"]))
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
print rb_dict




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

print "Printing the metric storage\n"
print rbIDMetricStorage

                    

