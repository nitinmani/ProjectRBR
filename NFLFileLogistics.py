import json
import os

"""Access JSON Directory and Store FileNames and Paths"""
def getJSONFiles(Directory):
    fileInformation = {}
    for root, dirs, files in os.walk(Directory):
        for fileName in files:
            fullPath = os.path.join(root, fileName)
            fileInformation[fileName] = fullPath
    print fileInformation

"""Loads a Game1Play JSONFile To Work With. Example fileName = 180.json"""
def loadJSONFile(fileName):
    with open("data/Game1/game1plays/" + fileName) as data_file:    
        JSONContents = json.load(data_file)
        return JSONContents

"""Loads a TeamRoster JSONFile To Work With. Example fileName = team1.json"""
def loadTeamJSONFIle(fileName):
    with open("data/Game1/TeamRosters/" + fileName) as data_file:    
        JSONTeamContents = json.load(data_file)
        return JSONTeamContents  


