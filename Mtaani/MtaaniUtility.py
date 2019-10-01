# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniUtility.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniNonMorgTile import MtaaniNonMorgTile
# ---------------------------------------------
class MtaaniUtility(MtaaniNonMorgTile):
    " The base class for all Mtaani utilities; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniNonMorgTile.__init__(self, name, boardIndex, gameContext, ['Bill', 'bill', 'utility', 'station',
            'tycoonery']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.utilitiesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.fees = self.configger.getfloat(name, 'Bill')
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR" % (self.getCost(), self.prefixes[1], self.getFees())
        self.unitCost = self.cost * self.configger.getfloat(name, 'Station')

    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniUtility, self).playerArrives(player, boardObj, playerCount)