# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiEstate.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiMorgTile import GanjiMorgTile
# ---------------------------------------------
class GanjiEstate(GanjiMorgTile):
    " The base class for all Ganji estates; extends GanjiMorgTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiMorgTile.__init__(self, name, boardIndex, gameContext, ['Rent', 'rent', 'estate']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.estatesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.mortgage = self.configger.getfloat(name, 'Mortgage')
        self.emptyPay = self.configger.getfloat(name, 'Rent')
        tileColor = self.configger.get(name, 'Color')
        tileRGBA = self.parseColor(tileColor)
        self.widget.background_color = tileRGBA
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR\nMortgage: %s SFR\nMortgaged: %s" % (self.getCost(), self.prefixes[0],
            self.getEmptyPay(), self.getMortgageValue(), self.mortgaged)
    
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiEstate, self).playerArrives(player, boardObj, playerCount)
    
    def buyMe(self, player):
        # call parent method
        super(GanjiEstate, self).buyMe(player)
        # check hoods
        self.checkHoods()
        
    def checkHoods(self):
        # check hoods
        hoodCount = 0
        hoodEstates = []
        for p in self.owner.properties.values():
            try:
                if p.hood == self.hood:
                    hoodCount += 1
                    hoodEstates.append(p.name)
            except AttributeError:
                continue
        if hoodCount == len(self.hood):
            # we have a hood!
            for x in hoodEstates:
                self.owner.properties[x].hoodFull = True
                self.owner.properties[x].widget.text = self.owner.properties[x].name + "\n@ %s" % self.owner.name
            self.boardLog.text += "\n%s: %s now has all the estates in this hood!" % (self.name, self.owner.name)
    