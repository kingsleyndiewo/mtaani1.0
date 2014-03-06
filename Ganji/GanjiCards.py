# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiCards.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from ConfigParser import ConfigParser
# graphics
import kivy
# version check
kivy.require('1.7.1')
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
# system utilities
from GanjiSystem import GanjiSystem
# ---------------------------------------------
class GanjiCardBox():
    " The base class for all Ganji card boxes"
    def __init__(self, name, gameContext, fontSizes):
        # get the card values
        self.configger = ConfigParser()
        self.systemBox = GanjiSystem()
        self.configger.read(self.systemBox.cardsConf)
        self.name = name
        self.fontSizes = fontSizes
        # set initial values for variables
        self.cards = []
        self.currentCard = 0
        self.addWidgetToBoard = gameContext[0]
        self.removeWidgetFromBoard = gameContext[1]
        self.box = Button(text=name, font_size=self.fontSizes[1], size_hint=(.1, .1), color=[0,0,0,1], bold=True)
        self.box.bind(on_release=self.boxCallback)
    # general get methods
    def increment(self):
        self.currentCard += 1
        if self.currentCard == 20:
            self.currentCard = 0
    def dismissPopup(self, instance, touchArgs):
        self.removeWidgetFromBoard(self.popupDialog)
    def boxCallback(self, instance):
        content = Label(text=self.description, color=self.box.background_color, font_size=self.fontSizes[0])
        content.bind(on_touch_up=self.dismissPopup)
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=content, size_hint=(.25, .18))
        self.popupDialog.pos_hint = self.boxPosition
        self.addWidgetToBoard(self.popupDialog)
    def popNextCard(self):
        content = Label(text=self.cards[self.currentCard][0], color=self.box.background_color, font_size=self.fontSizes[0])
        content.bind(on_touch_up=self.dismissPopup)
        currIndex = self.currentCard
        self.increment()
        # make a popup and fill with info
        self.popupDialog = Popup(title=self.name, content=content, size_hint=(.3, .18))
        self.popupDialog.pos_hint = self.boxPosition
        self.addWidgetToBoard(self.popupDialog)
        return currIndex
            
class GanjiMathreeBox(GanjiCardBox):
    " The base class for all Ganji mathree boxes; extends GanjiCardBox "
    def __init__(self, gameContext, fontSizes):
        GanjiCardBox.__init__(self, 'Mathree Cards', gameContext, fontSizes) # ancestral constructor
        self.description = "Mathree cards are named for Kenyan public \ntransport minibuses which are known as matatus\n"
        self.description += "or mathrees in short. These cards take the \nplayer to the described destination tile."
        # position box
        self.box.pos_hint = {'x':.79, 'y':.78}
        # set popup position
        self.boxPosition = {'x':.65, 'y':.62}
        self.box.background_color = [1,0.4,0.9,1]
        # load the Ma-3 cards
        for m in range(1, 21):
            section = 'M%d' % m
            msg = self.configger.get(section, 'Message')
            dest = self.configger.getint(section, 'Destination')
            passpay = self.configger.getint(section, 'PassEM')
            self.cards.append([msg, dest, bool(passpay)])
    
class GanjiGanjiBox(GanjiCardBox):
    " The base class for all Ganji finance boxes; extends GanjiCardBox "
    def __init__(self, gameContext, fontSizes):
        GanjiCardBox.__init__(self, 'Ganji Cards', gameContext, fontSizes) # ancestral constructor
        self.description = "Ganji cards are named for Kenyan urban \nword 'ganji' which means cash. The card details\n"
        self.description += "a situation of either cash gain or loss\nfor the player. You win some, you lose some."
        # position box
        self.box.pos_hint = {'x':.1, 'y':.11}
        # set popup position
        self.boxPosition = {'x':.09, 'y':.2}
        self.box.background_color = [0.6,1,0.4,1]
        # load the Ganji cards
        for c in range(1, 21):
            section = 'G%d' % c
            msg = self.configger.get(section, 'Message')
            amount = self.configger.getint(section, 'Amount')
            signDir = self.configger.getint(section, 'Direction')
            players = self.configger.getint(section, 'Players')
            self.cards.append([msg, amount, signDir, bool(players)])