# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiSystem.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
# network
import socket
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
        self.companiesConf = self.configDir + '/companies.ini'
        self.estatesConf = self.configDir + '/estates.ini'
        self.utilitiesConf = self.configDir + '/utilities.ini'
        self.cardsConf = self.configDir + '/cards.ini'
        self.mainConf = self.configDir + '/general.ini'
 