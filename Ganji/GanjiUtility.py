# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiUtility.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiNonMorgTile import GanjiNonMorgTile
# ---------------------------------------------
class GanjiUtility(GanjiNonMorgTile):
    " The base class for all Ganji utilities; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiNonMorgTile.__init__(self, name, boardIndex, gameContext, ['bill', 'Bill', 'utility']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.utilitiesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.fees = self.configger.getfloat(name, 'Bill')
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR" % (self.getCost(), self.prefixes[1], self.getFees())

    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiUtility, self).playerArrives(player, boardObj, playerCount)
        
    def lotCallback(self, instance):
        # buy or sell a house
        if self.tycoonFull:
            # process purchase
            pass
        elif not self.owned:
            # no hood
            self.boardLog.text += "\n%s: This tycoonery has unowned properties!" % self.name
        else:
            # no hood
            self.boardLog.text += "\n%s: Not all the utility companies in this tycoonery are yours %s!" % (self.name,
                self.owner.name)