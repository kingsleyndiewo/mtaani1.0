# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiFastFood.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiMorgTile import GanjiMorgTile
# ---------------------------------------------
class GanjiFastFood(GanjiMorgTile):
    " The base class for all Ganji fast food joints; extends GanjiMorgTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiMorgTile.__init__(self, name, boardIndex, gameContext, ['Bill', 'bill', 'fast food joint']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.companiesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.mortgage = self.configger.getfloat(name, 'Mortgage')
        self.emptyPay = self.configger.getfloat(name, 'Meal')
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR\nMortgage: %s SFR\nMortgaged: %s" % (self.getCost(), self.prefixes[0],
            self.getEmptyPay(), self.getMortgageValue(), self.mortgaged)
    
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiFastFood, self).playerArrives(player, boardObj, playerCount)
        
    def buyMe(self, player):
        # call parent method
        super(GanjiFastFood, self).buyMe(player)
        # check tycoonery
        self.checkTycoon()
        
    def checkTycoon(self):
        # check tycoonery
        tycoonCount = 0
        tycooneryJoints = []
        for p in self.owner.properties.values():
            try:
                if p.tycoon == self.tycoon:
                    tycoonCount += 1
                    tycooneryJoints.append(p.name)
            except AttributeError:
                continue
        if tycoonCount == len(self.tycoon):
            # we have a tycoonery!
            for x in tycooneryJoints:
                self.owner.properties[x].tycoonFull = True
                self.owner.properties[x].widget.text = self.owner.properties[x].name + "\n@ %s" % self.owner.name
            self.boardLog.text += "\n%s: %s is now a fast food joints tycoon!" % (self.name, self.owner.name)