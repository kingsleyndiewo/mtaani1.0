# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiSystem.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
# paths
import os
# ---------------------------------------------
# a class that provides basic OS utility
class GanjiSystem(object):
    " The base class for all Ganji system utilities "
    def __init__(self):
        # ===============================================================
        # set config variables
        self.configDir = os.path.join(os.path.dirname(__file__),'../config')
        self.imgDir = os.path.join(os.path.dirname(__file__),'../images')
        self.logDir = os.path.join(os.path.dirname(__file__),'../logs')
        self.companiesConf = self.configDir + '/companies.ini'
        self.estatesConf = self.configDir + '/estates.ini'
        self.utilitiesConf = self.configDir + '/utilities.ini'
        self.cardsConf = self.configDir + '/cards.ini'
        self.mainConf = self.configDir + '/general.ini'
        
        self.splashImg = self.imgDir + '/Monopoly.png'
        self.logFile = self.logDir + '/Ganji.log'
    
    def initLogFile(self):
        # open the object for writing, existing file will be overwritten
        self.logFO = open(self.logFile, 'w')
        
    def appendToLogFile(self):
        # open the object for writing, existing file content will be preserved
        self.logFO = open(self.logFile, 'a')