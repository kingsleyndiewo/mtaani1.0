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
from random import randint, seed
from kivy.core.audio import SoundLoader
# ---------------------------------------------
# a class that provides basic OS utility
class GanjiSystem(object):
    " The base class for all Ganji system utilities "
    def __init__(self):
        # ===============================================================
        # check if we have a data root
        data_root = os.environ.get('GANJI_DATA_ROOT', os.path.join(os.path.dirname(__file__),'../'))
        # set config variables
        self.configDir = data_root + '/config'
        self.imgDir = data_root + '/images'
        self.logDir = data_root + '/logs'
        self.soundDir = data_root + '/sounds'
        self.companiesConf = self.configDir + '/companies.ini'
        self.estatesConf = self.configDir + '/estates.ini'
        self.utilitiesConf = self.configDir + '/utilities.ini'
        self.cardsConf = self.configDir + '/cards.ini'
        self.mainConf = self.configDir + '/general.ini'
        
        self.splashImg = self.imgDir + '/Monopoly.png'
        self.logFile = self.logDir + '/Ganji.log'
        seed()
    
    def initLogFile(self):
        # open the object for writing, existing file will be overwritten
        self.logFO = open(self.logFile, 'w')
        
    def appendToLogFile(self):
        # open the object for writing, existing file content will be preserved
        self.logFO = open(self.logFile, 'a')
        
    def playSound(self, soundName):
        sound = SoundLoader.load(self.soundDir + '/%s%d.wav' % (soundName, randint(1,3)))
        sound.play()