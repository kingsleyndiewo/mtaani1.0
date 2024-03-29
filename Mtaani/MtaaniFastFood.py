# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniFastFood.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniMorgTile import MtaaniMorgTile
# ---------------------------------------------
class MtaaniFastFood(MtaaniMorgTile):
    " The base class for all Mtaani fast food joints; extends MtaaniMorgTile "
    def __init__(self, name, boardIndex, gameContext):
        MtaaniMorgTile.__init__(self, name, boardIndex, gameContext, ['Bill', 'bill', 'fast food joint', 'shop',
            'tycoonery']) # ancestral constructor
        # get initial values for variables
        self.configger.read(self.systemBox.companiesConf)
        # set values
        self.cost = self.configger.getint(name, 'Cost')
        self.mortgage = self.configger.getfloat(name, 'Mortgage')
        self.emptyPay = self.configger.getfloat(name, 'Meal')
        # compute cost of shop
        self.unitCost = self.cost * self.configger.getfloat(name, 'Shop')
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR\nMortgage: %s SFR\nMortgaged: %s" % (self.getCost(), self.prefixes[0],
            self.getNetPay(), self.getMortgageValue(), self.mortgaged)
    
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniFastFood, self).playerArrives(player, boardObj, playerCount)
        
    def buyMe(self, player):
        # call parent method
        super(MtaaniFastFood, self).buyMe(player)
        # check tycoonery
        self.checkMonopoly()
        
    def checkMonopoly(self):
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
        # check if we already found this
        if tycoonCount > 0:
            if self.owner.properties[tycooneryJoints[0]].monopolyFull == True:
                return
        if tycoonCount == len(self.tycoon):
            # we have a tycoonery!
            for x in tycooneryJoints:
                self.owner.properties[x].monopolyFull = True
                self.owner.properties[x].widget.text = self.owner.properties[x].name + "\n@ %s" % self.owner.name
            self.boardLog.text += "\n%s: %s is now a fast food joints tycoon!" % (self.name, self.owner.name)