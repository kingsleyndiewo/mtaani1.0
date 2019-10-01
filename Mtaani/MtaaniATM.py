# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniATM.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniTile import MtaaniTile
# ---------------------------------------------
class MtaaniATM(MtaaniTile):
    " The base class for Mtaani ATM tiles; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.mainConf)
        self.maxDispense = self.configger.getint('ATM', 'Max')
        self.loanAmount = self.configger.getint('ATM', 'Loan')
        self.interestRate = self.configger.getfloat('ATM', 'Interest')
        self.loanTerm = self.configger.getint('ATM', 'Term')
        self.cash = self.configger.getint('ATM', 'Initial')
        self.infoLabel = "Withdraw up to the maximum\nwhen you land at ATM.\nThe cash comes from taxes, initial \npurchases and Mtaani cards."
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniATM, self).playerArrives(player, boardObj, playerCount)
        # pay out withdrawal
        if self.cash > self.maxDispense:
            player.cash += self.maxDispense
            self.cash -= self.maxDispense
            self.boardLog.text += "\n%s: %s withdrew %2.f SFR from the ATM" % (self.name, player.name, self.maxDispense)
        elif self.cash > 0:
            player.cash += self.cash
            self.boardLog.text += "\n%s: %s withdrew %2.f SFR from the ATM" % (self.name, player.name, self.cash)
            self.cash = 0
        else:
            self.boardLog.text += "\n%s: %s found the ATM depleted" % (self.name, player.name)
    def tileCallback(self, instance):
        self.infoLabel = "Withdraw up to the\nmaximum when you land\nat ATM. The cash comes from taxes, initial \npurchases and Mtaani cards.\n\nCash: %d" % self.cash
        # call parent method
        super(MtaaniATM, self).tileCallback(instance)