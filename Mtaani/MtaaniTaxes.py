# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniTaxes.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniTile import MtaaniTile
# ---------------------------------------------
class MtaaniTaxes(MtaaniTile):
    " The base class for all Mtaani estates; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.mainConf)
        if boardIndex > 30:
            # VAT
            self.tax = self.configger.getfloat('VAT', 'Rate')
        else:
            # PAYE
            self.tax = self.configger.getfloat('PAYE', 'Rate')
        self.infoLabel = "Pay the designated tax\nat %s percent of your \ncash in hand." % str(self.tax)
        self.taxDue = 0
        
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniTaxes, self).playerArrives(player, boardObj, playerCount)
        # charge tax
        self.taxDue = player.cash * self.tax
        # check if the player can pay
        if player.cash >= self.taxDue:
            self.payTax(player)
        else:
            # has to raise amount
            player.raiseAmount(self.taxDue - player.cash)
            # return callback
            self.creditor = self.payTax
            self.debtCollection = True
    
    def payTax(self, player):
        """ The calling process is responsible for establishing that the funds are available to pay """
        # charges tax on player's cash
        player.cash -= self.taxDue
        player.ATMTile.cash += self.taxDue
        self.boardLog.text += "\n%s: %s paid %2.f SFR in taxes" % (self.name, player.name, self.taxDue)
        self.taxDue = 0