# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiNonMorgTile.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
# ---------------------------------------------
class GanjiNonMorgTile(GanjiTile):
    " The base class for all Ganji non-mortgageable tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext, prefixes = ['fees', 'Fees', 'business']):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        # set values
        self.owned = False
        self.owner = None
        self.prefixes = prefixes
        
    # general get methods
    def getCost(self):
        return self.cost
    def getFees(self):
        return (self.cost * self.fees)
    # handle purchase
    def playerArrives(self, player, boardObj, playerCount):
        # call parent method
        super(GanjiNonMorgTile, self).playerArrives(player, boardObj, playerCount)
        # if parent already set self.debtCollection then no further debt collection
        # check if owned
        if self.owned:
            # check if owner
            if self.owner.name == player.name:
                self.boardLog.text = self.boardLog.text + "\n%s: You own this property %s" % (self.name, player.name)
            else:
                # pay fees
                feesAmount = self.getFees()
                if player.cash >= feesAmount:
                    self.payFees(player)
                elif not self.debtCollection:
                    # has to raise amount
                    player.raiseAmount(feesAmount - player.cash)
                    # return callback
                    self.creditor = self.payFees
                    self.debtCollection = True
        else:
            # can be bought only if not already in debt to bank
            if not self.debtCollection:
                # set a dummy debt
                player.debt = self.dummyDebt
                # let player choose to buy or pay fees to bank
                self.popupBox("Buy %s at %d SFR or pay %s of\n%d SFR to bank? You have %d SFR in \ncash, %s" % (self.name,
                    self.getCost(), self.prefixes[0], self.getFees(), player.cash, player.name),
                    ["Buy", "Pay %s" % self.prefixes[1]])
                # setup post-dialog process
                self.returnExecution = self.processBuyFees
                self.reArgs = [player]
            
    def processBuyFees(self, argsList):
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
            feesAmount = self.getFees()
            if player.cash >= feesAmount:
                # pay fees
                self.payFees(player)
            else:
                # has to raise amount
                player.raiseAmount(feesAmount - player.cash)
                # return callback
                self.creditor = self.payFees
                self.debtCollection = True
        if player.debt == self.dummyDebt and self.debtCollection == False:
            # force a roll to change turn
            self.forcedRoll()
            
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
        self.boardLog.text = self.boardLog.text + "\n%s: %s just bought this %s company" % (self.name, player.name, self.prefixes[2])
        
    def payFees(self, player):
        """ The calling process is responsible for establishing that the funds are available to pay """
        feesAmount = self.getFees()
        player.cash -= feesAmount
        if self.owned:
            self.owner.cash += feesAmount
            self.boardLog.text = self.boardLog.text + "\n%s: %s just paid %2.f SFR to %s" % (self.name, player.name, feesAmount, self.owner.name)
        else: 
            player.ATMTile.cash += feesAmount
            self.boardLog.text = self.boardLog.text + "\n%s: %s just paid %2.f SFR to the bank" % (self.name, player.name, feesAmount)