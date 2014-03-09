# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiCardTile.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiTile import GanjiTile
from GanjiPlayer import GanjiPlayer
# ---------------------------------------------
class GanjiMathreeTile(GanjiTile):
    " The base class for Ganji mathree card tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        self.infoLabel = "A Mathree card is \na chance card which takes you \nto the indicated destination"
    def playerArrives(self, player, cardBox, boardObj, playerCount):
        # call parent method
        super(GanjiMathreeTile, self).playerArrives(player, boardObj, playerCount)
        # get next card
        cardIndex = cardBox.popNextCard()
        # called when player lands on tile
        self.boardLog.text += "\n%s: %s" % (self.name, cardBox.cards[cardIndex][0])
        # move player to new spot
        return cardBox.cards[cardIndex]
        
class GanjiGanjiTile(GanjiTile):
    " The base class for Ganji finance card tiles; extends GanjiTile "
    def __init__(self, name, boardIndex, gameContext):
        GanjiTile.__init__(self, name, boardIndex, gameContext) # ancestral constructor
        self.infoLabel = "A Ganji card is \na chance card where you \neither gain or lose cash"
        self.cardCash = 0
    def playerArrives(self, player, cardBox, boardObj, playerCount):
        # call parent method
        super(GanjiGanjiTile, self).playerArrives(player, boardObj, playerCount)
        # get next card
        cardIndex = cardBox.popNextCard()
        # called when player lands on tile
        self.boardLog.text += "\n%s: %s" % (self.name, cardBox.cards[cardIndex][0])
        # check the card value
        cardValue = cardBox.cards[cardIndex][1]
        if cardBox.cards[cardIndex][2] == 1:
            # add to player cash
            if cardBox.cards[cardIndex][3] == False:
                player.cash += cardValue
                player.ATMTile.cash -= cardValue
            else:
                player.cash += (cardValue * (playerCount - 1))
                # charge other players
                for p in GanjiPlayer.playersGroup.values():
                    if p.name != player.name:
                        # charge
                        if p.cash >= cardValue:
                            p.cash -= cardValue
                            self.boardLog.text += "\n%s: %s just paid %s %2.f SFR" % (self.name,
                                p.name, player.name, cardValue)
                        else:
                            # set as bank loan
                            player.ATMTile.cash -= cardValue
                            p.loan += cardValue
                            if p.loanDate == -1:
                                p.loanDate = p.age
                            self.boardLog.text += "\n%s: %s just borrowed %2.f SFR to pay %s" % (self.name,
                                p.name, cardValue, player.name)
                            
        else:
            # subtract from player cash if enough
            if cardBox.cards[cardIndex][3] == False:
                amt_dent = cardValue
            else:
                amt_dent = (cardValue * (playerCount - 1))
            if player.cash >= amt_dent:
                # reduce the player's cash
                player.cash -= amt_dent
                if cardBox.cards[cardIndex][3]:
                    # loop and pay other players
                    for p in GanjiPlayer.playersGroup.values():
                        if p.name != player.name:
                            p.cash += cardValue
                            self.boardLog.text += "\n%s: %s just received %2.f SFR from %s" % (self.name,
                                p.name, cardValue, player.name)
                else:
                    # pay bank
                    player.ATMTile.cash += amt_dent
            else:
                # if paying other players pay from bank
                if cardBox.cards[cardIndex][3]:
                    # loop and pay
                    for p in GanjiPlayer.playersGroup.values():
                        if p.name != player.name:
                            p.cash += cardValue
                            self.boardLog.text += "\n%s: %s just received %2.f SFR from %s" % (self.name,
                                p.name, cardValue, player.name)
                # has to raise amount
                player.raiseAmount(amt_dent - player.cash)
                self.cardCash = amt_dent
                # return callback
                self.creditor = self.payCard
                self.debtCollection = True
                
    def payCard(self, player):
        player.cash -= self.cardCash
        # whichever recipient it was, the bank paid
        player.ATMTile.cash += self.cardCash
        self.cardCash = 0
                