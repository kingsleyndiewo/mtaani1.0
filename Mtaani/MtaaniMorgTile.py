# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniMorgTile.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniTile import MtaaniTile
# ---------------------------------------------
class MtaaniMorgTile(MtaaniTile):
    " The base class for all Mtaani mortgageable tiles; extends MtaaniTile "
    def __init__(self, name, boardIndex, gameContext, prefixes=['Pay', 'pay', 'lot', 'unit', 'monopoly']):
        MtaaniTile.__init__(self, name, boardIndex, gameContext, ) # ancestral constructor
        self.mortgaged = False
        self.owned = False
        self.owner = None
        self.prefixes = prefixes
        
    # general get methods
    def getCost(self):
        if self.monopolyFull:
            # part of an monopoly
            if self.lot.built:
                # there is at least a unit
                totalCost = self.cost + (self.unitCost * self.lot.unitCount) 
                return totalCost
            else:
                # cost when part of a monopoly
                return self.cost * 2
        else:
            # no monopoly
            return self.cost
        
    def getNetPay(self):
        try:
            if self.lot.unitCount == 0:
                # adjustments are done in getCost()
                return (self.getCost() * self.emptyPay)
            else:
                # the more the houses, the more expensive life is
                hikeFactor = float(self.lot.unitCount) / 5
                return (self.getCost() * hikeFactor)
        except AttributeError:
            # at startup, lot isn't yet created
            return (self.getCost() * self.emptyPay)
    
    def getMortgageValue(self):
        return (self.getCost() * self.mortgage)
    
    def tileCallback(self, instance):
        # update info label
        unitStr = self.prefixes[3].capitalize()
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR\nMortgage: %s SFR\nMortgaged: %s\n%s Cost: %s SFR" % (self.getCost(),
            self.prefixes[0], self.getNetPay(), self.getMortgageValue(), self.mortgaged, unitStr, self.unitCost)
        # call the ancestral callback
        super(MtaaniMorgTile, self).tileCallback(instance)
    
    # handle purchase
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(MtaaniMorgTile, self).playerArrives(player, boardObj, playerCount)
        # if parent already set self.debtCollection then no further debt collection
        # check if owned
        if self.owned:
            # check if owner
            if self.owner.name == player.name:
                self.boardLog.text += "\n%s: You own this property %s" % (self.name, player.name)
            elif self.mortgaged:
                # no rent
                self.boardLog.text += "\n%s: Free today only %s" % (self.name, player.name)
            else:
                # pay rent
                payAmount = self.getNetPay()
                if player.cash >= payAmount:
                    self.payPay(player)
                elif not self.debtCollection:
                    # has to raise amount
                    player.raiseAmount(payAmount - player.cash)
                    # return callback
                    self.creditor = self.payPay
                    self.debtCollection = True
        else:
            # can be bought only if not already in debt to bank
            if not self.debtCollection:
                # set a dummy debt
                player.debt = self.dummyDebt
                # let player choose to buy or pay pay to bank
                if player.cash >= self.getCost():
                    promptText = "%s, will you buy %s at %2.f SFR or\npay %s of %2.f SFR to bank? You have %2.f SFR\nin cash, enough to buy in cash." % (player.name,
                        self.name, self.getCost(), self.prefixes[1], self.getNetPay(), player.cash)
                else:
                    promptText = "%s, will you buy %s at %2.f SFR or\npay %s of %2.f SFR to bank? You have %2.f SFR\nin cash, you'll need to raise cash if buying." % (player.name,
                        self.name, self.getCost(), self.prefixes[1], self.getNetPay(), player.cash)
                self.popupBox(promptText, ["Buy", "Pay %s" % self.prefixes[0]])
                # setup post-dialog process
                self.returnExecution = self.processBuyPay
                self.reArgs = [player]
            
    def processBuyPay(self, argsList):
        player = argsList[0]
        if self.popupValue == "Buy":
            if player.cash >= self.getCost():
                # buy property
                self.buyMe(player)
            else:
                # has to raise amount
                player.raiseAmount(self.getCost() - player.cash)
                # return callback
                self.creditor = self.buyMe
                self.debtCollection = True
        else:
            payAmount = self.getNetPay()
            if player.cash >= payAmount:
                # pay pay
                self.payPay(player)
            else:
                # has to raise amount
                player.raiseAmount(payAmount - player.cash)
                # return callback
                self.creditor = self.payPay
                self.debtCollection = True
        
        if player.debt == self.dummyDebt and self.debtCollection == False:
            # force a roll to change turn
            self.forcedRoll()
            
    def payPay(self, player):
        """ The calling process is responsible for establishing that the funds are available to pay """
        payAmount = self.getNetPay()
        player.cash -= payAmount
        if self.owned:
            self.owner.cash += payAmount
            self.boardLog.text += "\n%s: %s just paid %2.f SFR to %s" % (self.name, player.name, payAmount, self.owner.name)
        else:
            player.ATMTile.cash += payAmount
            self.boardLog.text += "\n%s: %s just paid %2.f SFR to the bank" % (self.name, player.name, payAmount)
        self.systemBox.playSound('rent')
    
    def buyMe(self, player):
        """ The calling process is responsible for establishing that the funds are available to buy """
        # just check ownership in case
        if self.owned:
            return
        player.cash -= self.getCost()
        # send to bank
        player.ATMTile.cash += self.getCost()
        self.owner = player
        self.owned = True
        player.properties[self.name] = self
        self.widget.text = self.widget.text + "\n{%s}" % player.name
        self.boardLog.text += "\n%s: %s just bought this %s" % (self.name, player.name, self.prefixes[2])
        self.systemBox.playSound('buy')
        
    def transferMe(self, player):
        # shift from one player to another
        del self.owner.properties[self.name]
        self.owner = player
        player.properties[self.name] = self
        self.widget.text = self.name + "\n{%s}" % player.name
     
    def lotCallback(self, instance):
        if not self.owned:
            # no monopoly
            self.boardLog.text += "\n%s: This %s has unowned properties!" % (self.name, self.prefixes[4])
        else:
            # check monopoly
            self.checkMonopoly()
            # buy or sell a unit
            if self.monopolyFull and self.owner.myTurn:
                if self.mortgaged:
                    # cannot build or sell on mortgaged property
                    self.boardLog.text += "\n%s: You cannot build or sell %ss on mortgaged property" % (self.name,
                        self.prefixes[3])
                    return
                # process purchase / sale
                if self.lot.unitCount == 0:
                    # buy unit
                    if self.owner.cash >= self.unitCost:
                        self.popupBox("Build a %s for %2.f SFR?" % (self.prefixes[3], self.unitCost), ["Yes", "No"])
                        # setup post-dialog process
                        self.returnExecution = self.buildUnit
                        self.reArgs = [self.owner]
                    else:
                        self.boardLog.text += "\n%s: You do not have enough cash to build a %s %s!" % (self.name,
                            self.prefixes[3], self.owner.name)
                elif self.lot.unitCount == 5:
                    # sell unit
                    self.popupBox("Sell a %s for %2.f SFR?" % (self.prefixes[3], (self.unitCost / 2)), ["Yes", "No"])
                    # setup post-dialog process
                    self.returnExecution = self.sellUnit
                    self.reArgs = [self.owner]
                else:
                    # buy or sell
                    if self.owner.cash >= self.unitCost:
                        self.popupBox("Sell a %s for %2.f SFR or \nbuild another %s for %2.f SFR?" % (self.prefixes[3], (self.unitCost / 2),
                            self.prefixes[3], self.unitCost), ["Build", "Sell", "Cancel"])
                        # setup post-dialog process
                        self.returnExecution = self.tradeUnit
                        self.reArgs = [self.owner]
                    else:
                        # sell unit
                        self.popupBox("You don't have enough cash to build \na %s. Sell a %s for %2.f SFR?" % (self.prefixes[3],
                            self.prefixes[3], (self.unitCost / 2)), ["Yes", "No"])
                        # setup post-dialog process
                        self.returnExecution = self.sellUnit
                        self.reArgs = [self.owner]
            elif not self.monopolyFull:
                # no hood
                self.boardLog.text += "\n%s: Not all the %ss in this %s are yours!" % (self.name, self.prefixes[2],
                    self.prefixes[4])
            else:
                # not your turn
                self.boardLog.text += "\n%s: It is not your turn %s!" % (self.name, self.owner.name)
                
    def sellUnit(self, argsList):
        player = argsList[0]
        if self.popupValue == "No":
            pass
        elif self.lot.unitCount != 0:
            # set lot place empty
            self.lot.unitCount -= 1
            self.lot.box.text = "{%d}" % self.lot.unitCount
            if self.lot.unitCount == 0:
                self.lot.built = False
            # give money
            unitPrice = self.unitCost / 2
            player.ATMTile.cash -= unitPrice
            player.cash += unitPrice
            if player.debt > 0:
                # check if cash in hand can cover debt now
                if unitPrice >= player.debt:
                    player.debt = 0
                else:
                    # reduce debt
                    player.debt -= unitPrice
            self.boardLog.text += "\n%s: A %s has been sold for %2.f SFR" % (self.name, self.prefixes[3], unitPrice)
            self.systemBox.playSound('sell')
        
    def buildUnit(self, argsList):
        """ The calling process is responsible for establishing that the funds are available to buy """
        player = argsList[0]
        if self.popupValue == "No":
            pass
        elif self.lot.unitCount < 5:
            # set lot place built
            self.lot.unitCount += 1
            self.lot.box.text = "{%d}" % self.lot.unitCount
            self.lot.built = True
            # take money
            player.ATMTile.cash += self.unitCost
            player.cash -= self.unitCost
            self.boardLog.text += "\n%s: A %s has been built for %2.f SFR" % (self.name, self.prefixes[3], self.unitCost)
            self.systemBox.playSound('build')
            
    def tradeUnit(self, argsList):
        """ The calling process is responsible for establishing that the funds are available to buy """
        if self.popupValue == "Cancel":
            pass
        elif self.popupValue == "Build":
            # build unit
            self.buildUnit(argsList)
        else:
            # sell unit
            self.sellUnit(argsList)
            
    def bankruptcyCleanup(self, player):
        # the bounty to be given to beneficiary player (if any)
        bounty = 0
        # sell any units first
        if self.lot.unitCount != 0:
            unitPrice = self.unitCost / 2
            totalPrice = unitPrice * self.lot.unitCount
            player.ATMTile.cash += totalPrice
            # set lot places empty
            self.lot.unitCount == 0
            self.lot.built = False
            # add to bounty
            bounty += totalPrice
        # sell property itself    
        player.ATMTile.cash += self.getCost()
        bounty += self.getCost()
        # remove mortgage
        if self.mortgaged:
            self.mortgaged = False
            mortgageFee = self.getMortgageValue() * (1 + self.mortgageRate)
            player.ATMTile.cash -= mortgageFee
            bounty -= mortgageFee
            if player.ATMTile.cash < 0:
                player.ATMTile.cash = 0
        # restore variables
        self.owned = False
        self.owner = None
        self.widget.text = self.name
        self.widget.color=[0,0,0,1]
        # remove monopolies
        if self.monopolyFull:
            self.monopolyFull = False
        return bounty
    
            