# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiMorgTile.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
# ---------------------------------------------
class GanjiMorgTile(GanjiTile):
    " The base class for all Ganji mortgageable tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext, prefixes=['Pay', 'pay', 'lot']):
        GanjiTile.__init__(self, name, boardIndex, gameContext, ) # ancestral constructor
        self.mortgaged = False
        self.owned = False
        self.owner = None
        self.prefixes = prefixes
    # general get methods
    def getCost(self):
        return self.cost
    def getEmptyPay(self):
        if self.hoodFull:
            # part of an estate monopoly
            return (self.cost * self.emptyPay * 2)
        elif self.tycoonFull:
            # part of a fast food tycoonery
            return (self.cost * self.emptyPay * 4)
        else:
            return (self.cost * self.emptyPay)
    def getMortgageValue(self):
        return (self.cost * self.mortgage)
    def tileCallback(self, instance):
        # update info label
        self.infoLabel = "Cost: %s SFR\n%s: %s SFR\nMortgage: %s SFR\nMortgaged: %s" % (self.getCost(), self.prefixes[0],
            self.getEmptyPay(), self.getMortgageValue(), self.mortgaged)
        # call the ancestral callback
        super(GanjiMorgTile, self).tileCallback(instance)
    
    # handle purchase
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiMorgTile, self).playerArrives(player, boardObj, playerCount)
        # if parent already set self.debtCollection then no further debt collection
        # check if owned
        if self.owned:
            # check if owner
            if self.owner.name == player.name:
                self.boardLog.text = self.boardLog.text + "\n%s: You own this property %s" % (self.name, player.name)
            elif self.mortgaged:
                # no rent
                self.boardLog.text = self.boardLog.text + "\n%s: Free today only %s" % (self.name, player.name)
            else:
                # pay rent
                payAmount = self.getEmptyPay()
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
                self.popupBox("Buy %s at %d SFR or pay %s of\n%d SFR to bank? You have %d SFR in \ncash, %s" % (self.name,
                    self.getCost(), self.prefixes[1], self.getEmptyPay(), player.cash, player.name),
                    ["Buy", "Pay %s" % self.prefixes[0]])
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
            payAmount = self.getEmptyPay()
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
        payAmount = self.getEmptyPay()
        player.cash -= payAmount
        if self.owned:
            self.owner.cash += payAmount
            self.boardLog.text = self.boardLog.text + "\n%s: %s just paid %2.f SFR to %s" % (self.name, player.name, payAmount, self.owner.name)
        else:
            player.ATMTile.cash += payAmount
            self.boardLog.text = self.boardLog.text + "\n%s: %s just paid %2.f SFR to the bank" % (self.name, player.name, payAmount)
    
    def buyMe(self, player):
        """ The calling process is responsible for establishing that the funds are available to buy """
        # just check ownership in case
        if self.owned:
            return
        player.cash -= self.getCost()
        self.owner = player
        self.owned = True
        player.properties[self.name] = self
        self.widget.text = self.widget.text + "\n{%s}" % player.name
        self.boardLog.text = self.boardLog.text + "\n%s: %s just bought this %s" % (self.name, player.name, self.prefixes[2])
        