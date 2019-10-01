# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniPlayer.py
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
from MtaaniSystem import MtaaniSystem
# ---------------------------------------------
class MtaaniPlayer:
    " The base class for all Mtaani players "
    # class variables
    playersGroup = {}
    def __init__(self, name, gameContext, boardPos = 0):
        # add to instance group
        MtaaniPlayer.playersGroup[name] = self
        # get initial values for variables
        self.configger = ConfigParser()
        self.systemBox = MtaaniSystem()
        self.configger.read(self.systemBox.mainConf)
        # set values
        self.cash = self.configger.getint('PLAYER', 'StartCash')
        self.salary = self.configger.getint('PAYDAY', 'Salary')
        scrollable = bool(self.configger.getint('DISPLAY', 'Scrollable'))
        scrollScale = self.configger.getint('DISPLAY', 'ScrollScale')
        self.broke = False
        self.position = boardPos
        self.debt = 0
        self.trueDebt = 0
        self.fontSizes = gameContext[5]
        self.myTurn = False
        # add a small font
        if scrollable:
            self.fontSizes.append(11 * scrollScale)
        else:
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
        self.tradePartner = None
        self.exportsBag = None
        self.importsBag = None
        self.proposedFlag = False
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
        infoBlock = "Cash: %2.f SFR\nAge: %d months\nFreedom: %s\nLoan: %d\nMore Info..." % (self.cash, self.age, jailTxt, self.loan)
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
        # variable maximum loan in Mtaani 2.0
        loanAmount = self.ATMTile.loanAmount
        if self.ATMTile.cash >= loanAmount and self.loan == 0:
            # can borrow
            self.loanDate = self.age
            self.cash += loanAmount
            self.ATMTile.cash -= loanAmount
            self.loan = loanAmount
            self.boardLog.text += "\nMtaani Bank: %s has borrowed %2.f SFR from the bank" % (self.name, loanAmount)
            if self.debt > 0:
                # check if cash in hand can cover debt now
                if loanAmount >= self.debt:
                    self.debt = 0
                else:
                    # reduce debt
                    self.debt -= loanAmount
            self.mpContent.text = self.infoBlock()
            self.propManSysMsgs.text = "Mtaani Bank: You have successfully borrowed %2.f SFR." % self.loan
            # change button
            instance.color = [1,0,0,1]
            instance.text = 'REPAY LOAN'
            instance.bind(on_release=self.repayLoan)
            # play sound
            self.systemBox.playSound('get_loan')
        elif self.loan > 0:
            # already have a loan
            self.propManSysMsgs.text = "Mtaani Bank: %s, you already have an outstanding loan\n of %2.f SFR" % (self.name, self.loan)
        else:
            # insufficient funds
            self.propManSysMsgs.text = "Mtaani Bank: %s, we currently have insufficient funds to lend" % self.name
    
    def getLoanValue(self):
        monthsElapsed = self.age - self.loanDate
        return self.loan * (1 + (self.ATMTile.interestRate * monthsElapsed))
    
    def repayLoanLite(self):
        if self.loan == 0:
            self.boardLog.text += "\nMtaani Bank: %s, you do not have an outstanding loan" % self.name
        else:
            loanValue = self.getLoanValue()
            if self.cash >= loanValue:
                self.cash -= loanValue
                self.ATMTile.cash += loanValue
                self.loanDate = -1
                self.loan = 0
                self.boardLog.text += "\nMtaani Bank: %s has repaid %2.f SFR to the bank" % (self.name, loanValue)
        
    def repayLoan(self, instance):
        # get total due
        loanValue = self.getLoanValue()
        if self.cash >= loanValue:
            self.cash -= loanValue
            self.ATMTile.cash += loanValue
            self.loanDate = -1
            self.loan = 0
            self.boardLog.text += "\nMtaani Bank: %s has repaid %2.f SFR to the bank" % (self.name, loanValue)
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
        
    def mortgageCallback(self, instance):
        if self.properties[instance.text].mortgaged:
            # mortgaged; unmortgage
            if self.unmortgageProperty(instance.text):
                instance.color=[0,0,0,1]
        else:
            # mortgage the property
            self.mortgageProperty(instance.text)
            instance.color=[1,0,0,1]
            # play sound
            self.systemBox.playSound('mortgage')
        self.mpContent.text = self.infoBlock()
            
    def dismissPopup(self, instance, touchArgs=None):
        self.removeWidgetFromBoard(self.popupDialog)
    
    def raiseAmount(self, amountDue):
        """ This function is called any time player can't pay cash on a debt """
        # create an info block
        self.debt = amountDue
        # get total payable, which includes your current cash
        self.trueDebt = amountDue + self.cash
        infoBlock = "You need to raise %2.f SFR.\nTry selling or mortgaging property.\nUse the 'MANAGE ASSETS' button" % (amountDue)
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
        # play sound
        self.systemBox.playSound('raise')
    
    def infoBlock(self):
        # info block
        if self.debt > 0:
            infoStr = "You need to raise %2.f SFR.\nTry selling or mortgaging property." % (self.debt)
        else:
            infoStr = "You currently have no outstanding debt."
        if self.loan > 0:
            infoStr = infoStr + "\nYou have an outstanding loan of %2.f SFR." % self.loan
        infoStr += "\nYour cash reserves are %2.f SFR" % self.cash
        return infoStr    
     
    def getPlayerProperties(self, instance):
        # place properties of player we're trading with in dialog
        self.tradePartner = MtaaniPlayer.playersGroup[instance.text]
        self.exchangePanel.clear_widgets()
        self.proposedTrade[1] = []
        textColor = self.tradePartner.token.background_color[:-1]
        textColor.append(1)
        label2 = Label(text="Please select properties you want from %s" % self.tradePartner.name, color=textColor,
            size_hint=(.05, .02), font_size=self.fontSizes[0])
        self.exchangePanel.add_widget(label2)
        # get properties
        for p in self.tradePartner.properties.values():
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
        cashItem = ToggleButton(text="CASH (up to %2.f SFR)" % self.tradePartner.cash, font_size=self.fontSizes[0], size_hint=(.05, .02),
            color=[0,0,0,1], background_color=textColor)
        self.cashText2 = TextInput(text='0', color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0], multiline=False,
            input_type='number')
        cashItem.bind(on_release=self.addToBuyBasket)
        self.exchangePanel.add_widget(cashItem)
        self.exchangePanel.add_widget(self.cashText2)
        # make propose and accept buttons
        self.tradeButton = Button(text='PROPOSE TRADE', font_size=self.fontSizes[0], size_hint=(.02, .02), color=[0,0,0,1],
            bold=True)
        self.tradeButton.bind(on_release=self.proposeTrade)
        propItem = Button(text='ACCEPT TRADE', font_size=self.fontSizes[0], size_hint=(.02, .02), color=[0,0,0,1],
            bold=True)
        propItem.bind(on_release=self.acceptTrade)
        self.exchangePanel.add_widget(self.tradeButton)
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
        for pl in MtaaniPlayer.playersGroup.values():
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
        cashItem = ToggleButton(text="CASH (up to %2.f SFR)" % self.cash, font_size=self.fontSizes[0], size_hint=(.05, .02),
            color=[0,0,0,1], background_color=playerColor)
        self.cashText = TextInput(text='0', color=textColor, size_hint=(.05, .02), font_size=self.fontSizes[0], multiline=False,
            input_type='number')
        cashItem.bind(on_release=self.addToSellBasket)
        traderPanel.add_widget(cashItem)
        traderPanel.add_widget(self.cashText)
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
        self.popupDialog = Popup(title=self.name, content=cpanel, size_hint=(.5, .8))
        self.popupDialog.pos_hint = {'x':.3, 'y':.21}
        self.addWidgetToBoard(self.popupDialog)
    
    def addToSellBasket(self, instance):
        # cash is processed separately
        if instance.text[:4] == 'CASH':
            itemStr = 'Cash'
        else:
            itemStr = instance.text
            
        if instance.state == 'down':
            # add
            self.proposedTrade[0].append(itemStr)
            self.tradeManSysMsgs.text = "Asset Trader: %s added to items you want to trade, %s" % (itemStr, self.name)
        else:
            # remove
            self.proposedTrade[0].remove(itemStr)
            self.tradeManSysMsgs.text = "Asset Trader: %s removed from items you want to trade, %s" % (itemStr, self.name)
            
    def addToBuyBasket(self, instance):
        # cash is processed separately
        if instance.text[:4] == 'CASH':
            itemStr = 'Cash'
        else:
            itemStr = instance.text
            
        if instance.state == 'down':
            # add
            self.proposedTrade[1].append(itemStr)
            self.tradeManSysMsgs.text = "Asset Trader: %s added to items you want from %s" % (itemStr, self.tradePartner.name)
        else:
            # remove
            self.proposedTrade[1].remove(itemStr)
            self.tradeManSysMsgs.text = "Asset Trader: %s removed from items you want from %s" % (itemStr, self.tradePartner.name)
        
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
        self.popupDialog = Popup(title=self.name, content=cpanel, size_hint=(.25, .8))
        self.popupDialog.pos_hint = {'x':.4, 'y':.21}
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
                # clear the doubles count
                self.doublesCount = 0
                jailFlag = True
        else:
            doubles = False
            # clear the doubles count
            self.doublesCount = 0
        self.boardLog.text += "\nSystem: %s rolled %d and %d" % (self.name, die1, die2)
        if jailFlag:
            self.boardLog.text += "\nSystem: %s rolled doubles thrice in a row and must go to jail" % self.name
        # play sound
        self.systemBox.playSound('dice_roll')
        return [die1, die2, doubles, jailFlag]
    
    def proposeTrade(self, instance):
        # propose a trade to an opponent
        myOffer = ''
        yourOffer = ''
        # sanitize cash text
        if 'Cash' in self.proposedTrade[0]:
            # cash is part of myOffer
            try:
                # check if player entered more than what cash is available
                if float(self.cashText.text) > self.cash:
                    self.cashText.text = str(self.cash)
            except ValueError:
                # change to zero, player entered non-numeric things
                self.cashText.text = '0'
        if 'Cash' in self.proposedTrade[1]:
            # cash is part of yourOffer
            try:
                # check if player entered more than what cash is available
                if float(self.cashText2.text) > self.tradePartner.cash:
                    self.cashText2.text = str(self.tradePartner.cash)
            except ValueError:
                # change to zero, player entered non-numeric things
                self.cashText2.text = '0'
        for x in self.proposedTrade[0]:
            if x == 'Cash':
                myOffer += (self.cashText.text + ' SFR,')
            else:
                myOffer += (x + ',')
        for y in self.proposedTrade[1]:
            if y == 'Cash':
                yourOffer += (self.cashText2.text + ' SFR,')
            else:
                yourOffer += (y + ',')
        if myOffer != '' and yourOffer != '':
            self.exportsBag = self.proposedTrade[0]
            self.importsBag = self.proposedTrade[1]
            # report
            self.proposedFlag = True
            self.tradeButton = "COUNTER TRADE"
            self.boardLog.text += "\nSystem: %s proposed to trade %s for %s from %s" % (self.name, myOffer, yourOffer,
                self.tradePartner.name)
        else:
            # not selected trade items either my or your
            self.tradeManSysMsgs.text = "Asset Trader: You must select items to exchange"
            self.tradeButton = "PROPOSE TRADE"
            self.proposedFlag = False
    
    def acceptTrade(self, instance):
        # force a proposal first
        self.proposeTrade(instance)
        # accept the currently prevailing deal
        expCash = 0
        impCash = 0
        if self.proposedFlag != True:
            self.tradeManSysMsgs.text = "Asset Trader: You must propose a trade first"
            return
        # =================================================================
        # deal with cash first
        # =================================================================
        if 'Cash' in self.exportsBag:
            # give cash to trade partner
            expCash = float(self.cashText.text)
            self.tradePartner.cash += expCash
            self.cash -= expCash
            # remove
            self.exportsBag.remove('Cash')
        if 'Cash' in self.importsBag:
            # take cash from trade partner
            impCash = float(self.cashText2.text)
            self.tradePartner.cash -= impCash
            self.cash += impCash
            # remove
            self.importsBag.remove('Cash')
        # =================================================================
        # change properties owners
        # =================================================================
        # first export
        myOffer = ''
        for e in self.exportsBag:
            self.properties[e].transferMe(self.tradePartner)
            # now they belong to trade partner
            self.tradePartner.properties[e].checkMonopoly()
            myOffer += (e + ',')
        if expCash > 0:
            myOffer += "%2.f SFR" % expCash
        # =================================================================
        # then import
        yourOffer = ''
        for i in self.importsBag:
            self.tradePartner.properties[i].transferMe(self)
            # now they belong to player
            self.properties[i].checkMonopoly()
            yourOffer += (i + ',')
        if impCash > 0:
            yourOffer += "%2.f SFR" % impCash
        # =================================================================
        # report
        self.boardLog.text += "\nSystem: %s traded %s for %s from %s" % (self.name, myOffer, yourOffer,
                self.tradePartner.name)
        # reset
        self.proposedFlag = False
        self.proposedTrade = [[], []]
        self.tradePartner = None
        self.exportsBag = None
        self.importsBag = None
        # close dialog
        self.dismissPopup(instance)
        
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
        self.propManSysMsgs.text = "%s has been mortgaged. Note that a fee of\n%2.f SFR will be charged on unmortgaging." % (propName, mortgageFee)
        
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