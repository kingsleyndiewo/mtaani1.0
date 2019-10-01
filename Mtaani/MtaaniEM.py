# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniEM.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniTile import MtaaniTile
# ---------------------------------------------
class MtaaniEM(MtaaniTile):
    " The base class for Mtaani end month tiles; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.mainConf)
        self.goFactor = self.configger.getint('PAYDAY', 'GoFactor')
        self.infoLabel = "Receive salary when \nyou pass PAYDAY\nLanding at PAYDAY gets\n you twice the salary"
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniEM, self).playerArrives(player, boardObj, playerCount)
        # called when player lands on tile
        self.agePlayer(player)
        # pay salaries first
        player.cash += (player.salary * self.goFactor)
        self.boardLog.text += "\n%s: Here's your pay and a times %d bonus for punctuality." % (self.name, self.goFactor)
    def agePlayer(self, player):
        # just increment
        player.age += 1