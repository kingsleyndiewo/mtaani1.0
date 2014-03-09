# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiPlayer.py
# Developed by: Intellect Alliance Software Team
# Date: 01/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from random import randint, seed
from ConfigParser import ConfigParser
# graphics
import kivy
# version check
kivy.require('1.7.1')
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
# system utilities
from GanjiSystem import GanjiSystem
# ---------------------------------------------
class GanjiPlayer:
    " The base class for all Ganji players "
    # class variables
    playersGroup = {}
    def __init__(self, name, gameContext, boardPos = 0):
        # add to instance group
        GanjiPlayer.playersGroup[name] = self
        # get initial values for variables
        self.configger = ConfigParser()
        self.systemBox = GanjiSystem()
        self.configger.read(self.systemBox.mainConf)
        # set values
        self.cash = self.configger.getint('PLAYER', 'StartCash')
        self.salary = self.configger.getint('PAYDAY', 'Salary')
        self.broke = False
        self.position = boardPos
        self.debt = 0
        self.trueDebt = 0
        self.fontSizes = gameContext[5]
        # add a small font
        self.fontSizes.append(11)
        # jail-related
        self.inJail = False
        self.jailTurn = self.configger.getint('JAIL', 'Turns')
        self.arrested = False
        # gameplay
        self.properties = {}
        self.offer = None
        self.doublesCount = 0
        self.index = 0
        self.cards = []
        self.age = 0
        self.loan = 0
        self.loanDate = -1
        self.name = name
        seed()
        # trade
        self.proposedTrade = [[], []]
        # make the button (token)
        r_col = float(randint(10,90)) / 60
        g_col = float(randint(10,90)) / 60
        b_col = float(randint(10,90)) / 60
        self.token = Button(text=name, font_size=self.fontSizes[2], size_hint=(.04, .02), color=[0,0,0,1],
            background_color=[r_col, g_col, b_col, 0.2])
        self.addWidgetToBoard = gameContext[0]
        self.removeWidgetFromBoard = gameContext[1]
        self.boardLog = gameContext[2]
        self.ATMTile = gameContext[3]
        self.processBankruptcy = gameContext[4]
        self.token.bind(on_release=self.tokenCallback)
        
    def tokenCallback(self, instance):
        # create an info block
        if self.inJail:
            jailTxt = "Incarcerated. %d turns left in jail" % self.jailTurn
        else:
            jailTxt = "Free"
        infoBlock = "Cash: %d SFR\nAge: %d months\nFreedom: %s\nLoan: %d\nMore Info..." % (self.cash, self.age, jailTxt, self.loan)
        textColor = self.token.background_color[:-1]
        textColor.append(1)
        content = Label(text=infoBlock, color=textColor)
        content.bind(on_touch_up=self.dismissPopup)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=content, size_hint=(.15, .2))
        self.popupDialog.pos_hint = {'x':.4, 'y':.4}
        self.addWidgetToBoard(self.popupDialog)
    
    def declareBankruptcy(self, instance):
        self.dismissPopup(None)
        # call board function
        self.processBankruptcy(self)
        
    def borrowLoan(self, instance):
        # variable maximum loan in Ganji 2.0
        loanAmount = self.ATMTile.loanAmount
        if self.ATMTile.cash >= loanAmount and self.loan == 0:
            # can borrow
            self.loanDate = self.age
            self.cash += loanAmount
            self.ATMTile.cash -= loanAmount
            self.loan = loanAmount
            self.boardLog.text += "\nGanji Bank: %s has borrowed %d SFR from the bank" % (self.name, loanAmount)
            if self.debt > 0:
                # check if cash in hand can cover debt now
                if loanAmount >= self.debt:
                    self.debt = 0
                else:
                    # reduce debt
                    self.debt -= loanAmount
            self.mpContent.text = self.infoBlock()
            self.propManSysMsgs.text = "Ganji Bank: You have successfully borrowed %d SFR." % self.loan
            # change button
            instance.color = [1,0,0,1]
            instance.text = 'REPAY LOAN'
            instance.bind(on_release=self.repayLoan)
        elif self.loan > 0:
            # already have a loan
            self.propManSysMsgs.text = "Ganji Bank: %s, you already have an outstanding loan\n of %d SFR" % (self.name, self.loan)
        else:
            # insufficient funds
            self.propManSysMsgs.text = "Ganji Bank: %s, we currently have insufficient funds to lend" % self.name
    
    def getLoanValue(self):
        monthsElapsed = self.age - self.loanDate
        return self.loan * (1 + (self.ATMTile.interestRate * monthsElapsed))
    
    def repayLoanLite(self):
        if self.loan == 0:
            self.boardLog.text += "\nGanji Bank: %s, you do not have an outstanding loan" % self.name
        else:
            loanValue = self.getLoanValue()
            if self.cash >= loanValue:
                self.cash -= loanValue
                self.ATMTile.cash += loanValue
                self.loanDate = -1
                self.loan = 0
                self.boardLog.text += "\nGanji Bank: %s has repaid %d SFR to the bank" % (self.name, loanValue)
        
    def repayLoan(self, instance):
        # get total due
        loanValue = self.getLoanValue()
        if self.cash >= loanValue:
            self.cash -= loanValue
            self.ATMTile.cash += loanValue
            self.loanDate = -1
            self.loan = 0
            self.boardLog.text += "\nGanji Bank: %s has repaid %d SFR to the bank" % (self.name, loanValue)
            self.propManSysMsgs.text = "You successfully repaid the loan."
            # change button
            instance.color = [0,0,0,1]
            instance.text = 'BORROW LOAN'
            instance.bind(on_release=self.borrowLoan)
            # check if we owe anything
            if self.trueDebt > 0:
                # trueDebt = amountDue + (cash at time of debt)
                # restore debt value
                self.debt = self.trueDebt - self.cash
                if self.debt < 0:
                    self.debt = 0
            # notify
            self.mpContent.text = self.infoBlock()
        else:
            # not enough ganji :-)
            self.propManSysMsgs.text = "You do not have enough cash to repay the loan."
    
    def tradeCallback(self, instance):
        pass
        
    def mortgageCallback(self, instance):
        if self.properties[instance.text].mortgaged:
            # mortgaged; unmortgage
            if self.unmortgageProperty(instance.text):
                instance.color=[0,0,0,1]
        else:
            # mortgage the property
            self.mortgageProperty(instance.text)
            instance.color=[1,0,0,1]
            
    def dismissPopup(self, instance, touchArgs=None):
        self.removeWidgetFromBoard(self.popupDialog)
    
    def raiseAmount(self, amountDue):
        """ This function doesn't exit until amount is raised or bankruptcy is declared """
        # create an info block
        self.debt = amountDue
        # get total payable, which includes your current cash
        self.trueDebt = amountDue + self.cash
        infoBlock = "You need to raise %d SFR.\nTry selling or mortgaging property.\nUse the 'MANAGE ASSETS' button" % (amountDue)
        textColor = self.token.background_color[:-1]
        textColor.append(1)
        content = Label(text=infoBlock, color=textColor, size_hint=(.05, .03))
        # setup a canvas
        cpanel = GridLayout(cols=1)
        cpanel.add_widget(content)
        exitBtn = Button(text='CLOSE', font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1], bold=True)
        exitBtn.bind(on_release=self.dismissPopup)
        cpanel.add_widget(exitBtn)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=cpanel, size_hint=(.25, .2))
        self.popupDialog.pos_hint = {'x':.4, 'y':.4}
        self.addWidgetToBoard(self.popupDialog)
    
    def infoBlock(self):
        # info block
        if self.debt > 0:
            infoStr = "You need to raise %d SFR.\nTry selling or mortgaging property." % (self.debt)
        else:
            infoStr = "You currently have no outstanding debt."
        if self.loan > 0:
            infoStr = infoStr + "\nYou have an outstanding loan of %d SFR." % self.loan
        infoStr += "\nYour cash reserves are %d SFR" % self.cash
        return infoStr    
     
    def getPlayerProperties(self, instance):
        # place properties of player we're trading with in dialog
        playerObj = GanjiPlayer.playersGroup[instance.text]
        self.exchangePanel.clear_widgets()
        self.proposedTrade[1] = []
        textColor = playerObj.token.background_color[:-1]
        textColor.append(1)
        label2 = Label(text="Please select properties you want in exchange", color=textColor, size_hint=(.05, .02),
            font_size=self.fontSizes[0])
        self.exchangePanel.add_widget(label2)
        # get properties
        for p in playerObj.properties.values():
            # create the buttons
            propColor = p.widget.background_color
            try:
                # for mortgageable property
                if p.mortgaged:
                    propItem = ToggleButton(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[1,0,0,1],
                        background_color=propColor)
                else:
                    propItem = ToggleButton(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1],
                        background_color=propColor)
            except AttributeError:
                # any other property
                propItem = ToggleButton(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1],
                    background_color=propColor)
            self.exchangePanel.add_widget(propItem)
            propItem.bind(on_release=self.addToBuyBasket)
        # create a button for cash
        cashItem = ToggleButton(text="CASH %d SFR" % playerObj.cash, font_size=self.fontSizes[0], size_hint=(.05, .02),
            color=[0,0,0,1], background_color=textColor)
        cashText = TextInput(text='0', color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0], multiline=False,
            input_type='number')
        self.exchangePanel.add_widget(cashItem)
        self.exchangePanel.add_widget(cashText)
        # make a propose button
        propItem = Button(text='PROPOSE TRADE', font_size=self.fontSizes[0], size_hint=(.02, .02), color=[0,0,0,1], bold=True)
        propItem.bind(on_release=self.proposeTrade)
        self.exchangePanel.add_widget(propItem)
        
    def tradeAssets(self):
        # shows a dialog that allows selling and so on
        # setup a canvas
        cpanel = GridLayout(cols=2)
        traderPanel = GridLayout(cols=1)
        self.exchangePanel = GridLayout(cols=1)
        textColor = self.token.background_color[:-1]
        textColor.append(1)
        # set system messages
        sysMsg = "No message from the trade manager"
        self.tradeManSysMsgs = Label(text=sysMsg, color=textColor, size_hint=(.05, .04), font_size=self.fontSizes[0])
        traderPanel.add_widget(self.tradeManSysMsgs)
        # list players
        label2 = Label(text="Please select a player to trade with", color=textColor, size_hint=(.05, .02),
            font_size=self.fontSizes[0])
        traderPanel.add_widget(label2)
        for pl in GanjiPlayer.playersGroup.values():
            if pl.name != self.name:
                # create a toggle button
                playerColor = pl.token.background_color[:-1]
                playerColor.append(1)
                tgBtn = ToggleButton(text=pl.name, group="players", font_size=self.fontSizes[0], size_hint=(.05, .02),
                    background_color=playerColor)
                traderPanel.add_widget(tgBtn)
                tgBtn.bind(on_release=self.getPlayerProperties)
        # properties
        label2 = Label(text="Please select assets you want to offer", color=textColor, size_hint=(.05, .02),
            font_size=self.fontSizes[0])
        traderPanel.add_widget(label2)
        # list all the properties
        for p in self.properties.values():
            # create a button
            propColor = p.widget.background_color
            try:
                # for mortgageable property
                if p.mortgaged:
                    propItem = ToggleButton(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[1,0,0,1],
                        background_color=propColor)
                else:
                    propItem = ToggleButton(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1],
                        background_color=propColor)
            except AttributeError:
                # any other property
                propItem = ToggleButton(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1],
                    background_color=propColor)
            traderPanel.add_widget(propItem)
            propItem.bind(on_release=self.addToSellBasket)
        # create a button for cash
        playerColor = self.token.background_color[:-1]
        playerColor.append(1)
        cashItem = ToggleButton(text="CASH %d SFR" % self.cash, font_size=self.fontSizes[0], size_hint=(.05, .02),
            color=[0,0,0,1], background_color=playerColor)
        cashText = TextInput(text='0', color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0], multiline=False,
            input_type='number')
        traderPanel.add_widget(cashItem)
        traderPanel.add_widget(cashText)
        label2 = Label(text="Please select properties you want in exchange", color=textColor, size_hint=(.05, .02),
            font_size=self.fontSizes[0])
        self.exchangePanel.add_widget(label2)
        # make an exit button
        propItem = Button(text='CLOSE', font_size=self.fontSizes[0], size_hint=(.02, .02), color=[0,0,0,1], bold=True)
        propItem.bind(on_release=self.dismissPopup)
        traderPanel.add_widget(propItem)
        # add both to cpanel
        cpanel.add_widget(traderPanel)
        cpanel.add_widget(self.exchangePanel)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=cpanel, size_hint=(.5, .5))
        self.popupDialog.pos_hint = {'x':.3, 'y':.38}
        self.addWidgetToBoard(self.popupDialog)
    
    def addToSellBasket(self, instance):
        if instance.state == 'down':
            # add
            self.proposedTrade[0].append(instance.text)
        else:
            # remove
            self.proposedTrade[0].remove(instance.text)
            
    def addToBuyBasket(self, instance):
        if instance.state == 'down':
            # add
            self.proposedTrade[1].append(instance.text)
        else:
            # remove
            self.proposedTrade[1].remove(instance.text)
        
    def manageAssets(self):
        # shows a dialog that allows mortgaging and so on
        # setup a canvas
        cpanel = GridLayout(cols=1)
        textColor = self.token.background_color[:-1]
        textColor.append(1)
        self.mpContent = Label(text=self.infoBlock(), color=textColor, size_hint=(.05, .04), font_size=self.fontSizes[0])
        cpanel.add_widget(self.mpContent)
        # set system messages
        sysMsg = "No message from the property manager"
        self.propManSysMsgs = Label(text=sysMsg, color=textColor, size_hint=(.05, .04), font_size=self.fontSizes[0])
        cpanel.add_widget(self.propManSysMsgs)
        # properties
        label2 = Label(text="Mortgageable Property (click to mortgage or unmortgage)", color=textColor, size_hint=(.05, .02),
            font_size=self.fontSizes[0])
        cpanel.add_widget(label2)
        # list all the properties
        unMAble = []
        mAbleCount = 0
        for p in self.properties.values():
            # create a button
            propColor = p.widget.background_color
            try:
                # for mortgageable property
                if p.mortgaged:
                    propItem = Button(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[1,0,0,1],
                        background_color=propColor)
                else:
                    propItem = Button(text=p.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1],
                        background_color=propColor)
                cpanel.add_widget(propItem)
                mAbleCount += 1
                propItem.bind(on_release=self.mortgageCallback)
            except AttributeError:
                # any other property
                unMAble.append(p)
        if mAbleCount == 0:
            # no property
            label4 = Label(text="No mortgageable property owned", color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0])
            cpanel.add_widget(label4)
        # add the others
        label3 = Label(text="Unmortgageable Property", color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0])
        cpanel.add_widget(label3)
        if unMAble != []:
            for c in unMAble:
                propItem = Button(text=c.name, font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1],
                    background_color=c.widget.background_color)
                cpanel.add_widget(propItem)
        else:
            label4 = Label(text="No unmortgageable property owned", color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0])
            cpanel.add_widget(label4)
        # make a bankruptcy button
        propItem = Button(text='DECLARE BANKRUPTCY', font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1], bold=True)
        propItem.bind(on_release=self.declareBankruptcy)
        cpanel.add_widget(propItem)
        # make a loan button
        if self.loan == 0:
            propItem = Button(text='BORROW LOAN', font_size=self.fontSizes[0], size_hint=(.05, .02), color=[0,0,0,1], bold=True)
            propItem.bind(on_release=self.borrowLoan)
        else:
            propItem = Button(text='REPAY LOAN', font_size=self.fontSizes[0], size_hint=(.05, .02), color=[1,0,0,1], bold=True)
            propItem.bind(on_release=self.repayLoan)
        cpanel.add_widget(propItem)
        # make an exit button
        propItem = Button(text='CLOSE', font_size=self.fontSizes[0], size_hint=(.02, .02), color=[0,0,0,1], bold=True)
        propItem.bind(on_release=self.dismissPopup)
        cpanel.add_widget(propItem)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=cpanel, size_hint=(.25, .5))
        self.popupDialog.pos_hint = {'x':.4, 'y':.38}
        self.addWidgetToBoard(self.popupDialog)
        
    def rollDice(self):
        die1 = randint(1,6)
        die2 = randint(1,6)
        jailFlag = False
        if die1 == die2:
            doubles = True
            self.doublesCount += 1
            # check for 3 doubles in a row
            if self.doublesCount == 3:
                jailFlag = True
        else:
            doubles = False
            self.doublesCount = 0
        self.boardLog.text += "\nSystem: %s rolled %d and %d" % (self.name, die1, die2)
        if jailFlag:
            self.boardLog.text += "\nSystem: %s rolled doubles thrice in a row and must go to jail" % self.name
        return [die1, die2, doubles, jailFlag]
    
    def proposeTrade(self, instance):
        # propose a trade to an opponent
        myOffer = ''
        yourOffer = ''
        for x in self.proposedTrade[0]:
            myOffer += (x + ',')
        for y in self.proposedTrade[1]:
            yourOffer += (y + ',')
        self.boardLog.text += "\nSystem: %s proposed to trade %s for %s" % (self.name, myOffer, yourOffer)
        
    def sellProperty(self, propName, price, player):
        # check if you have the property
        if self.properties.has_key(propName):
            if self.properties[propName].processSale(player, price):
                # add to new owner's dictionary
                player.properties[propName] = self.properties[propName]
                # remove from old owner's dictionary
                self.properties.pop(propName)
                self.cash += price
                
    def mortgageProperty(self, propName):
        # process mortgage and check for outstanding debt
        self.properties[propName].mortgaged = True
        # add mortgaged value to cash in hand
        self.cash += self.properties[propName].getMortgageValue()
        # notify
        self.boardLog.text += "\nSystem: %s has mortgaged %s for %2.f SFR" % (self.name,
            self.properties[propName].name, self.properties[propName].getMortgageValue())
        if self.debt > 0:
            # check if cash in hand can cover debt now
            if self.properties[propName].getMortgageValue() >= self.debt:
                self.debt = 0
            else:
                # reduce debt
                self.debt -= self.properties[propName].getMortgageValue()
            # notify
            self.mpContent.text = self.infoBlock()
        # change widget text color on property to show mortgage
        old_color = self.properties[propName].widget.background_color[:3]
        old_color.reverse()
        old_color.append(1)
        self.properties[propName].widget.color = old_color
        mortgageFee = self.properties[propName].getMortgageValue() * self.properties[propName].mortgageRate
        self.propManSysMsgs.text = "%s has been mortgaged. Note that a fee of\n%d SFR will be charged on unmortgaging." % (propName, mortgageFee)
        
    def buyProperty(self):
        # this is only called when player is on property tile and tile has offered
        if self.offer == None:
            return False
        else:
            return self.offer.processSale(self)
    def unmortgageProperty(self, propName):
        # find total due
        totalDue = self.properties[propName].getMortgageValue() * (1 + self.properties[propName].mortgageRate)
        # check if player has enough cash
        if self.cash >= totalDue:
            # revert stuff back
            self.properties[propName].mortgaged = False
            self.cash -= totalDue
            self.ATMTile.cash += totalDue
            # notify
            self.boardLog.text += "\nSystem: %s has unmortgaged %s for %2.f SFR" % (self.name,
                self.properties[propName].name, totalDue)
            # revert widget text to black
            self.properties[propName].widget.color = [0,0,0,1]
            self.propManSysMsgs.text = "%s has been unmortgaged." % propName
            # check if we owe anything
            if self.trueDebt > 0:
                # restore debt value
                self.debt = self.trueDebt - self.cash
                if self.debt < 0:
                    self.debt = 0
                self.mpContent.text = self.infoBlock()
            return True
        else:
            # not enough ganji :-)
            self.propManSysMsgs.text = "You do not have enough cash to unmortgage %s." % propName
            return False
            
    def buyUnit(self, propName):
        # check if you have the property
        if self.properties.has_key(propName):
            return self.properties[propName].buyUnit(self)
    def sellUnit(self, propName):
        # check if you have the property
        if self.properties.has_key(propName):
            return self.properties[propName].sellUnit(self)