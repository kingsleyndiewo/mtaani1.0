# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiTaxes.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
# ---------------------------------------------
class GanjiTaxes(GanjiTile):
    " The base class for all Ganji estates; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # get initial values for variables
        self.confile = 'config/general.ini'
        self.configger.read(self.confile)
        if boardIndex > 30:
            # VAT
            self.tax = self.configger.getfloat('VAT', 'Rate')
        else:
            # PAYE
            self.tax = self.configger.getfloat('PAYE', 'Rate')
        self.infoLabel = "Pay the designated tax\nat %s percent of your \ncash in hand." % str(self.tax)
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiTaxes, self).playerArrives(player, boardObj, playerCount)
        # charge tax
        taxAmount = player.cash * self.tax
        player.cash -= taxAmount
        self.boardLog.text = self.boardLog.text + "\n%s: Thank you for paying your taxes %s" % (self.name, player.name)
        return taxAmount