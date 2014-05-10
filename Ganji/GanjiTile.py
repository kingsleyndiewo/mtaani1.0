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
        self.scrollable = gameContext[7]
        self.scrollScale = gameContext[8]
        # work out which hood this is in
        for c in hoods:
            if self.index in c:
                self.hood = c
        for d in tycoons:
            if self.index in d:
                self.tycoon = d
        self.monopolyFull = False
        # spaces for development
        self.lot = None
        # set default button callback
        self.returnExecution = self.runLast
        self.reArgs = None
        # set callback after debt management
        self.creditor = self.runLast
        self.debtCollection = False
        self.dummyDebt = 1
        # lot dimensions
        self.lot_width = self.widget.size_hint[0] / 2
        self.lot_height = self.widget.size_hint[1] / 5
        self.lot_w = self.widget.width / 2
        self.lot_h = self.widget.height / 5
    
    def createLots(self, boardObj):
        lotColor = self.widget.background_color[:-1]
        lotColor.reverse()
        lotColor.append(1)
        # create the lot with 5 spaces
        newLot = GanjiLot(self, lotColor, [self.lot_width, self.lot_height], [self.lot_w, self.lot_h])
        #self.widget.add_widget(newLot.box)
        boardObj.add_widget(newLot.box)
        self.lot = newLot
    #    # set bindings
    #    self.widget.bind(on_size=self.moveLots, on_pos=self.moveLots)
    #         
    #def moveLots(self, instance):
    #     for c in self.lots:
    #         c.resizeLot()
            
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
# class that defines the simple Ganji tile lot
class GanjiLot(object):
    " The base class for all Ganji tile lots "
    def __init__(self, tileObj, lotColor, lotSizeHint, lotSize):
        # save values
        self.unitCount = 0
        self.tile = tileObj
        self.level = 0
        self.built = False
        self.sizeHint = lotSizeHint
        # create the lot
        self.box = Button(text='{0}', color=lotColor, size_hint=(None, None),
            background_color=tileObj.widget.background_color, size=(lotSize[0], lotSize[1]))
        self.box.bind(on_release=tileObj.lotCallback)
        self.resizeLot()
        
    def resizeLot(self):
        # resize
        if self.tile.scrollable:
            self.lot_w = (self.tile.widget.width / 2) * self.tile.scrollScale
            self.lot_h = (self.tile.widget.height / 5) * self.tile.scrollScale
        else:
            self.lot_w = self.tile.widget.width / 2
            self.lot_h = self.tile.widget.height / 5
        self.box.size=(self.lot_w, self.lot_h)
        # set other variables
        new_x = self.tile.widget.pos_hint['x']
        # above tile for tiles between 0 and 12
        if self.tile.index < 12 and self.tile.index > 0:
            new_y = self.tile.widget.pos_hint['y'] + self.tile.widget.size_hint[1]
        # below tile for tiles between 25 and 36
        elif self.tile.index < 36 and self.tile.index > 24:
            new_y = self.tile.widget.pos_hint['y'] - (self.tile.lot_height * 1.5)
        # base height remains same
        else:
            new_y = self.tile.widget.pos_hint['y']
        # make sure we don't have a string of decimal places
        new_y = round(new_y, 3)
        
        # ========================================================================================
        # custom layout for the 2 vertical columns of tiles
        if self.tile.index > 12 and self.tile.index < 24:
            # left side column starting at Githurai
            # line on left edge
            lot_x = new_x
            lot_y = new_y + (self.sizeHint[1] * 3.5)
        elif self.tile.index > 36:
            # right side column starting at Kitisuru
            # line beyond right edge
            lot_x = new_x
            lot_y = new_y + (self.sizeHint[1] * 3.5)
        else:
            # all horizontal row tiles
            lot_x = new_x + (self.sizeHint[0] * 0.75)
            lot_y = new_y
        # set the values
        self.box.pos_hint = {'x':lot_x, 'y':lot_y}