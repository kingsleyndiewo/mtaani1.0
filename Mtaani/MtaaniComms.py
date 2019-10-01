# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniComms.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniNonMorgTile import MtaaniNonMorgTile
# ---------------------------------------------
class MtaaniComms(MtaaniNonMorgTile):
    " The base class for all Mtaani communications companies; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniNonMorgTile.__init__(self, name, boardIndex, gameContext, ['Charge', 'charge', 'communications', 'satellite',
            'tycoonery']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.companiesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.fees = self.configger.getfloat(name, 'Fee')
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR" % (self.getCost(), self.prefixes[1], self.getFees())
        self.unitCost = self.cost * self.configger.getfloat(name, 'Satellite')
    
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniComms, self).playerArrives(player, boardObj, playerCount)