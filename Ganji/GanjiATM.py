# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiATM.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
# ---------------------------------------------
class GanjiATM(GanjiTile):
    " The base class for Ganji ATM tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.mainConf)
        self.maxDispense = self.configger.getint('ATM', 'Max')
        self.loanAmount = self.configger.getint('ATM', 'Loan')
        self.interestRate = self.configger.getfloat('ATM', 'Interest')
        self.loanTerm = self.configger.getint('ATM', 'Term')
        self.cash = self.configger.getint('ATM', 'Initial')
        self.infoLabel = "Withdraw up to the maximum\nwhen you land at ATM.\nThe cash comes from taxes."
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiATM, self).playerArrives(player, boardObj, playerCount)
        # pay out withdrawal
        if self.cash > self.maxDispense:
            player.cash += self.maxDispense
            self.cash -= self.maxDispense
            self.boardLog.text += "\n%s: %s withdrew %d SFR from the ATM" % (self.name, player.name, self.maxDispense)
        elif self.cash > 0:
            player.cash += self.cash
            self.boardLog.text += "\n%s: %s withdrew %d SFR from the ATM" % (self.name, player.name, self.cash)
            self.cash = 0
        else:
            self.boardLog.text += "\n%s: %s found the ATM depleted" % (self.name, player.name, self.cash)
    def tileCallback(self, instance):
        self.infoLabel = "Withdraw up to the\nmaximum when you land\nat ATM. The cash comes from taxes.\n\nCash: %d" % self.cash
        # call parent method
        super(GanjiATM, self).tileCallback(instance)