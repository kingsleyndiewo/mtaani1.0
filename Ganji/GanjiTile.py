# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiTile.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiInteraction import GanjiInteraction
from ConfigParser import ConfigParser
from GanjiGlobals import boardTiles, hoods, tycoons
# graphics
import kivy
# version check
kivy.require('1.7.1')
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import *
# threading
from GanjiThreads import GanjiThread
# system utilities
from GanjiSystem import GanjiSystem
# ---------------------------------------------
# a class that defines the simple Ganji board tile
class GanjiTile(object):
    " The base class for all Ganji tiles "
    def __init__(self, name, boardIndex, gameContext):
        # set initial values for variables
        self.name = name
        self.index = boardIndex
        self.occupants = []
        self.systemBox = GanjiSystem()
        self.color = [1,1,1,1]
        self.popupValue = None
        self.ownerSpeak = GanjiInteraction()
        self.configger = ConfigParser()
        self.fontSizes = gameContext[5]
        self.widget = Button(text=name, font_size=self.fontSizes[0], size_hint=(.076, .076), color=[0,0,0,1],
            pos_hint=boardTiles[boardIndex][2], bold=False)
        self.widget.bind(on_release=self.tileCallback)
        self.infoLabel = "This is an estate"
        self.addWidgetToBoard = gameContext[0]
        self.removeWidgetFromBoard = gameContext[1]
        self.boardLog = gameContext[2]
        self.forcedRoll = gameContext[3]
        self.hailsLog = gameContext[4]
        self.mortgageRate = gameContext[6]
        # work out which hood this is in
        for c in hoods:
            if self.index in c:
                self.hood = c
        for d in tycoons:
            if self.index in d:
                self.tycoon = d
        self.hoodFull = False
        self.tycoonFull = False
        # spaces for development
        self.lots = []
        # set default button callback
        self.returnExecution = self.runLast
        self.reArgs = None
        # set callback after debt management
        self.creditor = self.runLast
        self.debtCollection = False
        self.dummyDebt = 1
    
    def createLots(self, boardObj):
        lotColor = self.widget.background_color[:-1]
        lotColor.reverse()
        lotColor.append(1)
        screenW = boardObj.width
        screenH = boardObj.height
        new_x = (self.widget.pos_hint['x'] * screenW)
        new_y = (self.widget.pos_hint['y'] * screenH)
        lot_width = self.widget.width / 5
        lot_height = self.widget.height / 5
        # create 5 lots
        for x in range(5):
            newLot = GanjiLot(x, self, lotColor, [lot_width, lot_height], [new_x, new_y])
            self.widget.add_widget(newLot.box)
            self.lots.append(newLot)
            
    def runLast(self, dummyArg):
        # dummy function for button callback default
        pass
    
    def playerArrives(self, player, boardObj, playerCount):
        # get over here
        player.position = self.index
        self.occupants.append(player.name)
        self.placePlayer(player, boardObj, playerCount)
        self.addWidgetToBoard(player.token)
        self.hailsLog.text = self.hailsLog.text + "\n[NikoHapa]: Welcome to %s, %s" % (self.name, player.name)
        # check for bank loan
        if player.loan > 0:
            # compute due date
            monthsElapsed = player.age - player.loanDate
            if monthsElapsed >= player.ATMTile.loanTerm:
                # payment must be made
                self.boardLog.text += "\nGanji Bank: %s, your outstanding loan is now due" % player.name
                if player.cash >= player.getLoanValue():
                    self.payLoan(player)
                else:
                    # set as debt
                    player.raiseAmount(player.getLoanValue())
                    # return callback
                    self.creditor = self.payLoan
                    self.debtCollection = True
                    
    def playerLeaves(self, player):
        # cleanup
        self.occupants.remove(player.name)
        self.removeWidgetFromBoard(player.token)
        self.hailsLog.text = self.hailsLog.text + "\n[NikoHapa]: %s has left %s" % (player.name, self.name)
    
    def payLoan(self, player):
        # simply process a loan payment
        player.repayLoanLite()
        
    def parseColor(self, colorCSV):
        # split the RGB CSV
        tileRGB = colorCSV.split(',')
        tileRGB = map(int, tileRGB)
        tileFloats = []
        for x in tileRGB:
            newVal = (float(x) / 255)
            newVal = round(newVal, 2)
            tileFloats.append(newVal)
        # add alpha value
        tileFloats.append(1)
        self.color = tileFloats
        return tileFloats
    
    def tileCallback(self, instance):
        content = Label(text=self.infoLabel, color=self.color)
        content.bind(on_touch_up=self.dismissPopup)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=content, size_hint=(.2, .2))
        self.popupDialog.pos_hint = {'x':.4, 'y':.4}
        self.addWidgetToBoard(self.popupDialog)
        
    def popupCallback(self, instance):
        # just return the value of the clicked button
        self.popupValue = instance.text
        # return execution to where it was
        self.returnExecution(self.reArgs)
        # cleanup after
        self.returnExecution = self.runLast
        self.reArgs = None
    
    def popupBox(self, boxText, options):
        # make a popup box with the buttons specified
        content = GridLayout(cols=1)
        note = Label(text=boxText, color=self.color, size_hint=(.22, .18), font_size=self.fontSizes[0])
        #note.bind(on_touch_up=self.dismissPopup)
        content.add_widget(note)
        for x in options:
            newBtn = Button(text=x, font_size=self.fontSizes[0], size_hint=(.2, .08), color=self.color)
            content.add_widget(newBtn)
            # bind press to the button callback
            newBtn.bind(on_press=self.popupCallback)
            # bind release to the dialog close
            newBtn.bind(on_release=self.dismissPopup)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=content, size_hint=(.2, .2))
        self.popupDialog.pos_hint = {'x':.4, 'y':.4}
        self.addWidgetToBoard(self.popupDialog)
    def dismissPopup(self, instance, touchArgs=None):
        self.removeWidgetFromBoard(self.popupDialog)
    def placePlayer(self, playerObj, boardObj, playerCount):
        widget_w = self.widget.size[0]
        widget_h =  self.widget.size[1]
        screenW = boardObj.width
        screenH = boardObj.height
        levels = widget_h / playerCount
        new_x = (self.widget.pos_hint['x'] * screenW) + (float(widget_w) / 3)
        new_y = (self.widget.pos_hint['y'] * screenH) + (levels * playerObj.index)
        new_x /= float(screenW)
        new_y /= float(screenH)
        # round to 2 dp
        new_x = round(new_x, 2)
        new_y = round(new_y, 2)
        playerObj.token.pos_hint = {'x':new_x, 'y':new_y}
        
# ---------------------------------------------
# a class that defines the simple Ganji tile lot
class GanjiLot(object):
    " The base class for all Ganji tile lots "
    def __init__(self, tileIndex, tileObj, lotColor, lotSize, lotPos):
        self.box = Button(text='.', pos=(lotPos[0] + (lotSize[0] * tileIndex), lotPos[1]), color=lotColor,
                background_color=tileObj.widget.background_color, size=(lotSize[0], lotSize[1]))
        self.box.bind(on_release=tileObj.lotCallback)
        self.level = 0
        self.built = False