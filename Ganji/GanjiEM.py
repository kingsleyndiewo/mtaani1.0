# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiEM.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
# ---------------------------------------------
class GanjiEM(GanjiTile):
    " The base class for Ganji end month tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.mainConf)
        self.goFactor = self.configger.getint('PAYDAY', 'GoFactor')
        self.infoLabel = "Receive salary when \nyou pass PAYDAY\nLanding at PAYDAY gets\n you twice the salary"
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiEM, self).playerArrives(player, boardObj, playerCount)
        # called when player lands on tile
        self.agePlayer(player)
        # pay salaries first
        player.cash += (player.salary * self.goFactor)
        self.boardLog.text += "\n%s: Here's your pay and a times %d bonus for punctuality." % (self.name, self.goFactor)
    def agePlayer(self, player):
        # just increment
        player.age += 1