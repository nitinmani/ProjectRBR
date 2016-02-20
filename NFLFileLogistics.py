import json

"""Access JSON Directory and Store FileNames and Paths"""
game1Plays ='/Users/neildanait/Downloads/NFLHack/data/Game1/game1plays'
fileInformation = {}

def getGame1JSONFiles(Directory):
    for root, dirs, files in os.walk(Directory):
        for fileName in files:
            fullPath = os.path.join(root, fileName)
            fileInformation[fileName] = fullPath
getGame1JSONFiles(game1Plays);

"""Loads JSONFile To Work With. Example fileName = 180.json"""
def loadJSONFile(fileName):
    with open("data/Game1/game1plays/" + fileName) as data_file:    
        JSONContents = json.load(data_file)
        return JSONContents
