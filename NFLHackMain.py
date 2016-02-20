import scipy
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pylab as pl
import sklearn
import csv
import json
import os
import NFLFileLogistics
from sklearn import svm
from sklearn.svm import SVC
from scipy import io
from sklearn import linear_model
from pprint import pprint


# """Generate a list of JSON Files that contain StatID's that correspond to fumbles"""
# statID = [52, 53, 54, 55, 57, 59, 61, 91, 96, 103, 106, 403, 404, 420] #All ID's that correspond to fumbles
# # getGame1JSONFiles(game1Plays);
game1Plays ='./data/Game1/game1plays'
teamPlays ='./data/Game1/TeamRosters'

NFLFileLogistics.getJSONFiles(game1Plays)
