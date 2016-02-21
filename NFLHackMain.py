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
teamPlays ='./data/Game1/TeamRosters'
positionIds = ["OT", "RB", "OL"] #SelfReference
rb_dict = {}
rb_list = []
ot_list = []
ol_list = []
runningBackRatios = {}

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
getPlayers()
def make_rb_dict():
    playInfoDict = NFLFileLogistics.getJSONFiles(game1Plays)
    for play_file in playInfoDict:
        play = NFLFileLogistics.loadJSONFile(play_file)
        for running_back in rb_list:
            for stat_getter in play["play"]["playStats"]:
                for key in stat_getter:
                    if key == "nflId":
                        if stat_getter[key] == running_back[0]:
                            if running_back[0] not in rb_dict:
                                rb_dict[running_back[0]] = []
                            rb_dict[running_back[0]].append((play["gameId"], play["ngsPlayId"], running_back[1]))
make_rb_dict()

def calculateShortYardage(runningPlayDict):
    for rbID in runningPlayDict:
        totalSuccesses = 0
        totalEligiblePlays = 0
        yardsGained = 0.0
        for ngsGameandPlayID in runningPlayDict[rbID]:
            if (ngsGameandPlayID[0] == 1): #Check Game
                ngsPlayID_string = str(ngsGameandPlayID[1])
                tempFile = NFLFileLogistics.loadJSONFile(ngsPlayID_string + ".json")
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
            successRatio = (totalSuccesses/(totalEligiblePlays))
            calculatedTuple = (averageYardsGained, successRatio)
        runningBackRatios[rbID] = calculatedTuple
calculateShortYardage(rb_dict)


