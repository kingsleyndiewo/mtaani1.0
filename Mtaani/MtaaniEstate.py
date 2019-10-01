# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniEstate.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniMorgTile import MtaaniMorgTile
# ---------------------------------------------
class MtaaniEstate(MtaaniMorgTile):
    " The base class for all Mtaani estates; extends MtaaniMorgTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniMorgTile.__init__(self, name, boardIndex, gameContext, ['Rent', 'rent', 'estate', 'house',
            'hood']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.estatesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.mortgage = self.configger.getfloat(name, 'Mortgage')
        self.emptyPay = self.configger.getfloat(name, 'Rent')
        # compute cost of house
        self.unitCost = self.cost * (self.mortgage + 0.2)
        tileColor = self.configger.get(name, 'Color')
        tileRGBA = self.parseColor(tileColor)
        self.widget.background_color = tileRGBA
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR\nMortgage: %s SFR\nMortgaged: %s" % (self.getCost(), self.prefixes[0],
            self.getNetPay(), self.getMortgageValue(), self.mortgaged)
    
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniEstate, self).playerArrives(player, boardObj, playerCount)
    
    def buyMe(self, player):
        # call parent method
        super(MtaaniEstate, self).buyMe(player)
        # check hoods
        self.checkMonopoly()
        
    def checkMonopoly(self):
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
        # check if we already found this
        if hoodCount > 0:
            if self.owner.properties[hoodEstates[0]].monopolyFull == True:
                return
        if hoodCount == len(self.hood):
            # we have a hood!
            for x in hoodEstates:
                self.owner.properties[x].monopolyFull = True
                self.owner.properties[x].widget.text = self.owner.properties[x].name + "\n@ %s" % self.owner.name
            self.boardLog.text += "\n%s: %s now has all the estates in this hood!" % (self.name, self.owner.name)
    