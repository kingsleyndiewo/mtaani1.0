# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniPolice.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniTile import MtaaniTile
# ---------------------------------------------
class MtaaniPolice(MtaaniTile):
    " The base class for all Mtaani police tiles; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        self.infoLabel = "Landing here will get \nyou arrested and carted \noff to Jail"
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniPolice, self).playerArrives(player, boardObj, playerCount)
        # arrest player
        player.arrested = True
        self.boardLog.text += "\n%s: You are under arrest %s" % (self.name, player.name)