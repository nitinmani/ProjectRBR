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


# """Generate a list of JSON Files that contain StatID's that correspond to fumbles"""
# statID = [52, 53, 54, 55, 57, 59, 61, 91, 96, 103, 106, 403, 404, 420] #All ID's that correspond to fumbles
game1Plays ='./data/Game1/game1plays'
teamPlays ='./data/Game1/TeamRosters'
positionIds = ["OT", "RB", "OL"] #SelfReference
rb_list = []
ot_list = []
ol_list = []


running_back_play_dict = {}
"""For team json file in TeamRoster, retrieves all ID's for provided position"""
def getPlayers():
    teamInformationDict = NFLFileLogistics.getJSONFiles(teamPlays)
    for fileName in teamInformationDict:
        roster = NFLFileLogistics.loadTeamJSONFile(fileName) 
        for player in roster["teamPlayers"]:
            if player["positionGroup"] == "RB":
                rb_list.append(player["nflId"])
            if player["position"] == "OT":
                ot_list.append(player["nflId"])
            if player["positionGroup"] == "OL":
                ol_list.append(player["nflId"])
getPlayers()

def make_running_back_list():
	playInfoDict = NFLFileLogistics.getJSONFiles(game1Plays)
	for playFile in playInfoDict:
		play = NFLFileLogistics.loadJSONFile(playFile)
		for running_back in rb_list:
			for stat_getter in play["play"]["playStats"]:
				print stat_getter["u' statID"]

make_running_back_list()
				


#def calculateShortYardage(RB_ID):
#    RBPlayerIDs = getPlayers("RB")
#    #May have to make a call to Nitin's method for runningPlays
#    for playID in runningPlays:
        



#Have all the RB id's, go through all the play IDs, figure out which plays that the RB is part and that yardsToGo <=3

#Two Cases from Here:

#1.) If team <=3 yards on opponent's goal line (check yardline field). For example, if a RB is on AMS, then anything less than BAR <= 3, WE WANT
# For this case, calculate the number of successes and failures (check if statID is 3). if not, then its a failure. if is, its a success.

#2.) If team <=3 yards and it is 3rd or 4th down (using down field), calculate whether success or failure 

#Return like a success to failure ratio

#stacks up in a different row