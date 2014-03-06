# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiPolice.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
# ---------------------------------------------
class GanjiPolice(GanjiTile):
    " The base class for all Ganji police tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        self.infoLabel = "Landing here will get \nyou arrested and carted \noff to Jail"
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiPolice, self).playerArrives(player, boardObj, playerCount)
        # arrest player
        player.arrested = True
        self.boardLog.text = self.boardLog.text + "\n%s: You are under arrest %s" % (self.name, player.name)