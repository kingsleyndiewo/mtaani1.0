# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniJail.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniTile import MtaaniTile
# ---------------------------------------------
class MtaaniJail(MtaaniTile):
    " The base class for all Mtaani jails; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # set initial values for variables
        self.population = 0
        # get initial values for variables
        self.configger.read(self.systemBox.mainConf)
        self.bail = self.configger.getint('JAIL', 'Bail')
        self.turns = self.configger.getint('JAIL', 'Turns')
        self.widget.color = [1,1,1,1]
        self.infoLabel = "The prison facility. \nLand here to visit an inmate, \nor stay if you were booked by \npolice officers."
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniJail, self).playerArrives(player, boardObj, playerCount)
        if player.arrested == True:
            # admit the inmate
            self.admitInmate(player)
            self.boardLog.text += "\n%s: Think about your crimes %s" % (self.name, player.name)
        else:
            self.boardLog.text += "\n%s: Just visiting %s, this time." % (self.name, player.name)
    def admitInmate(self, player):
        # check-in a player
        player.inJail = True
        player.arrested = False
        player.jailTurn -= 1
        self.population += 1
    def playerLeaves(self, player):
        # check-out a player
        self.population -= 1
        player.inJail = False
        player.jailTurn = self.turns
        # call parent method
        super(MtaaniJail, self).playerLeaves(player)
    def payBail(self, player):
        """ The calling process is responsible for establishing that the funds are available to pay """
        player.cash -= self.bail
        player.ATMTile.cash += self.bail
        # has to be cleared
        player.inJail = False
        player.jailTurn = self.turns
        self.boardLog.text += "\n%s: %s just paid %2.f SFR bail to the police" % (self.name, player.name, self.bail)
            