# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# Desc: Base Ganji Game CodeBase
# File name: GanjiGame.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from GanjiInteraction import GanjiInteraction
from ConfigParser import ConfigParser
from GanjiEstate import GanjiEstate
from GanjiFastFood import GanjiFastFood
from GanjiTransport import GanjiTransport
from GanjiUtility import GanjiUtility
from GanjiComms import GanjiComms
from GanjiEM import GanjiEM
from GanjiJail import GanjiJail
from GanjiPolice import GanjiPolice
from GanjiATM import GanjiATM
from GanjiTaxes import GanjiTaxes
from GanjiPlayer import GanjiPlayer
from GanjiCardTile import GanjiMathreeTile, GanjiGanjiTile
from GanjiCards import GanjiMathreeBox, GanjiGanjiBox
from GanjiGlobals import boardTiles, othersList
# graphics
import kivy
# version check
kivy.require('1.7.1')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import *
from kivy.uix.image import Image
from kivy.config import Config
# network
import socket
# ---------------------------------------------
# a class that defines the simple Ganji board game
class GanjiGame(App):
    " The base class for all Ganji games "
    def __init__(self, playerList):
        # ===============================================================
        # set kivy config variables
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        Config.write()
        # ===============================================================
        self.board = []
        self.companiesConf = 'config/companies.ini'
        self.estatesConf = 'config/estates.ini'
        self.utilitiesConf = 'config/utilities.ini'
        self.mainConf = 'config/general.ini'
        self.playersList = playerList
        self.gameSpeak = GanjiInteraction()
        self.playerCount = len(self.playersList)
        # parsers
        ganjiConfig = ConfigParser()
        # read in estate list
        ganjiConfig.read(self.estatesConf)
        self.estatesList = ganjiConfig.sections()
        # read in companies list
        ganjiConfig = ConfigParser()
        ganjiConfig.read(self.companiesConf)
        self.fastFoodList = ganjiConfig.sections()[:4]
        self.commsList = ganjiConfig.sections()[-2:]
        self.transportList = ganjiConfig.sections()[4:8]
        # read in utilities
        ganjiConfig = ConfigParser()
        ganjiConfig.read(self.utilitiesConf)
        self.utilitiesList = ganjiConfig.sections()
        # generate taxes list
        self.taxesList = ['PAYE', 'VAT']
        # read in settings
        ganjiConfig = ConfigParser()
        ganjiConfig.read(self.mainConf)
        self.screenW = ganjiConfig.getint('GAME', 'ScreenX')
        self.screenH = ganjiConfig.getint('GAME', 'ScreenY')
        self.ttsRoll = bool(ganjiConfig.getint('TTS-ROLLS', 'Speak'))
        self.scrollable = bool(ganjiConfig.getint('DISPLAY', 'Scrollable'))
        self.mortgageRate = ganjiConfig.getfloat('BANK', 'Mortgage')
        # make a list of the rest
        self.othersList = othersList
        # make layout
        self.fontSizes = [13, 15]
        self.boardGfx = GanjiBoard(self.screenW, self.screenH, self.scrollable)
        # =============================================================
        # run graphics constructor
        App.__init__(self)
        # =============================================================
        # create button for rolling dice
        self.dice = Button(text='ROLL DICE', font_size=self.fontSizes[1], size_hint=(.07, .07), color=[0,0,0,1],
            pos_hint={'x':.39, 'y':.28}, bold=True)
        self.manager = Button(text='MANAGE ASSETS', font_size=self.fontSizes[1], size_hint=(.09, .05), color=[0,0,0,1],
            pos_hint={'x':.5, 'y':.28}, bold=True)
        self.dice.bind(on_release=self.diceCallback)
        self.manager.bind(on_release=self.mgrCallback)
        self.rolls = Label(text='0    0', font_size=self.fontSizes[1], size_hint=(.07, .07), color=[1,1,1,1],
            pos_hint={'x':.39, 'y':.35}, bold=True)
        self.turnLabel = Label(text='None', font_size=self.fontSizes[0], size_hint=(.07, .07), color=[1,1,1,1],
            pos_hint={'x':.51, 'y':.35})
        self.msgBox = TextInput(text='System: No current messages', font_size=self.fontSizes[0], size_hint=(.21, .25),
                foreground_color=[.7,1,.7,1], pos_hint = {'x':.39, 'y':.65}, readonly = True, background_color=[0,0,0,1])
        self.hailBox = TextInput(text='Niko Hapa', font_size=self.fontSizes[0], size_hint=(.18, .25),
            foreground_color=[1,0,.3,1], pos_hint = {'x':.16, 'y':.65}, readonly = True, background_color=[0,0,0,1])
        # just a convenience list of things we send to other classes a lot
        toolBox = [self.boardGfx.add_widget, self.boardGfx.remove_widget, self.msgBox]
        # create card boxes
        self.GanjiBox = GanjiGanjiBox(toolBox, self.fontSizes)
        self.Ma3Box = GanjiMathreeBox(toolBox, self.fontSizes)
        # =============================================================
        # setup network
        # =============================================================
        self.socket = socket.socket()
        # get local machine name
        self.host = socket.gethostname()
        self.port = 20143
        self.socket.bind((self.host, self.port)) 
        # create tiles
        self.createBoard()
        # create players
        self.players = {}
        # add ATM tile to toolbox
        toolBox.append(self.board[24])
        # add Bankruptcy method to toolbox
        toolBox.append(self.bankruptcy)
        # add font sizes to toolbox
        toolBox.append(self.fontSizes)
        for n, x in enumerate(playerList):
            self.players[x] = GanjiPlayer(x, toolBox)
            self.board[0].occupants.append(x)
            self.players[x].index = n
            # add to board
            self.board[0].placePlayer(self.players[x], self.boardGfx, self.playerCount)
            self.boardGfx.add_widget(self.players[x].token)
        # assign current player
        self.currentPlayer = 0
        # set oweFlag to false
        self.oweFlag = False
        # set initial turn
        self.switchTurn()
    
    def switchTurn(self, incrementFlag=False):
        if incrementFlag:
            # next player
            self.currentPlayer += 1
            if self.currentPlayer >= self.playerCount:
                # if equal, same as zeroing
                self.currentPlayer = self.currentPlayer - self.playerCount
        pname = self.playersList[self.currentPlayer]
        self.turnLabel.text = "%s, your turn to roll" % pname
        playerObj = self.players[pname]
        textColor = playerObj.token.background_color[:-1]
        textColor.append(1)
        self.turnLabel.color = textColor
    
    def payDues(self, playerObj, bankrupt = False):
        if playerObj.debt == 0:
            # call callback
            self.board[playerObj.position].creditor(playerObj)
            # clean up
            playerObj.trueDebt = 0
            self.oweFlag = False
            self.board[playerObj.position].debtCollection = False
            self.board[playerObj.position].creditor = self.board[playerObj.position].runLast
            # switch turn
            if playerObj.doublesCount == 0:
                self.switchTurn(True)
            return True
        elif bankrupt:
            # give player exact cash
            playerObj.cash += playerObj.debt
            # call callback
            self.board[playerObj.position].creditor(playerObj)
            # clean up
            self.oweFlag = False
            self.board[playerObj.position].debtCollection = False
            self.board[playerObj.position].creditor = self.board[playerObj.position].runLast
            return True
        else:
            return False
                
    def mgrCallback(self, instance):
        name = self.playersList[self.currentPlayer]
        playerObj = self.players[name]
        # check for any debt
        if self.board[playerObj.position].debtCollection and not self.oweFlag:
            self.oweFlag = True
        playerObj.manageAssets()
        
    def processFakeRoll(self):
        # get player object
        name = self.playersList[self.currentPlayer]
        playerObj = self.players[name]
        if self.oweFlag:
            # check for dummy debt
            if playerObj.debt == self.board[playerObj.position].dummyDebt:
                playerObj.debt = 0
                self.oweFlag = False
                if playerObj.doublesCount == 0:
                    # change turn
                    self.switchTurn(True)
    
    def bankruptcy(self, player):
        # process a bankruptcy
        self.msgBox.text = self.msgBox.text + "\nGanji: %s declared bankruptcy!" %  self.playersList[self.currentPlayer]
        self.msgBox.text = self.msgBox.text + "\nGanji: Bank will liquidate assets and pay liabilities"
        # pay dues
        self.payDues(player, True)
        # reclaim properties
        for p in player.properties.values():
            # set as not owned and recover money
            player.ATMTile.cash += p.getCost()
            p.owned = False
            p.owner = None
            p.widget.text = p.name
            p.widget.color=[0,0,0,1]
            # remove mortgage
            try:
                if p.mortgaged:
                    p.mortgaged = False
                    mortgageFee = p.getMortgageValue() * (1 + self.mortgageRate)
                    player.ATMTile.cash -= mortgageFee
                    if player.ATMTile.cash < 0:
                        player.ATMTile.cash = 0
            except AttributeError:
                pass
            # remove tycoons and hoods
            if p.tycoonFull:
                p.tycoonFull = False
            if p.hoodFull:
                p.hoodFull = False
        # remove from board
        name = self.playersList[self.currentPlayer]
        self.boardGfx.remove_widget(player.token)
        self.playersList.pop(self.currentPlayer)
        self.playerCount -= 1
        del self.players[name]
        # switch turn
        self.switchTurn(True)
        
    def diceCallback(self, instance):
        # get player object
        name = self.playersList[self.currentPlayer]
        playerObj = self.players[name]
        if self.oweFlag:
            if not self.payDues(playerObj):
                # no one else plays
                self.msgBox.text = self.msgBox.text + "\nSystem: %s must pay debt before play continues" %  self.playersList[self.currentPlayer]
            # we can't give player extra turn
            return
        result = playerObj.rollDice()
        self.rolls.text = "%d    %d" % (result[0], result[1])
        self.rolls.canvas.ask_update()
        # clear notifications label if too long
        if len(self.msgBox.text) > 700:
            self.msgBox.text = ''
        if len(self.hailBox.text) > 700:
            self.hailBox.text = ''
        if self.ttsRoll:
            # speak the rolls
            self.gameSpeak.notifyText("%s, You rolled %d and %d" % (name, result[0], result[1]))
        # check jail
        if playerObj.inJail:
            # doubles first
            if result[2]:
                # just continue as usual; but cancel doubles
                result[2] = False
            else:
                if playerObj.jailTurn < 0:
                    # too many turns in jail
                    if playerObj.cash >= self.board[playerObj.position].bail:
                        self.board[playerObj.position].payBail(playerObj)
                        # continue as usual and move
                    else:
                        playerObj.raiseAmount(self.board[playerObj.position].bail - playerObj.cash)
                        # set callback
                        self.board[playerObj.position].creditor = self.board[playerObj.position].payBail
                        self.board[playerObj.position].debtCollection = True
                        # no move or turn change
                        return
                else:
                    # reduce jail turns
                    playerObj.jailTurn -= 1
                    self.switchTurn(True)
                    # stop to prevent move
                    return
        
        # ================PROCESSING MOVEMENT====================================================
        switchFlag = False
        if result[2] != True and result[3] != True:
            # no doubles and not jail
            move_fb = self.movePlayer(name, result[0] + result[1])
            # tentatively, we will switch turn
            switchFlag = True
        elif result[3] == True:
            # jail
            if 36 > self.players[name].position:
                steps = 36 - self.players[name].position
            else:
                steps = (48 + 36) - self.players[name].position
            move_fb = self.movePlayer(name, steps)
            # we should switch turn here
            switchFlag = True
        else:
            # just doubles
            move_fb = self.movePlayer(name, result[0] + result[1])
            # we don't switch turn here because of doubles
            switchFlag = False
        # =========================================================================================
        # test the feedback for mathree ride
        matCount = 0
        while move_fb != []:
            # we need to call again
            if move_fb[1] > self.players[name].position:
                steps = move_fb[1] - self.players[name].position
            else:
                steps = (48 + move_fb[1]) - self.players[name].position
                
            move_fb = self.movePlayer(name, steps, move_fb[2])
            # check oweFlag
            if playerObj.debt != 0:
                self.oweFlag = True
            matCount += 1
        # ========================================================================================
        # here we have already set oweFlag if it was necessary
        # if player is in debt suddenly, don't change turn
        if self.oweFlag == False and switchFlag:
            # we aren't in debt and our logic before any mathree ride agreed with a turn switch
            self.switchTurn(True)
                
    def movePlayer(self, name, steps, noSalary=False):
        playerObj = self.players[name]
        # leave current point
        self.board[playerObj.position].playerLeaves(playerObj)
        dest = playerObj.position + steps
        if dest == 48:
            dest = 0
        elif dest > 48:
            dest = dest - 48
            # passed Payday
            if not noSalary:
                playerObj.cash += playerObj.salary
                self.msgBox.text = self.msgBox.text + "\nPayday: %s collected salary for getting to the end of the month" % playerObj.name
            playerObj.age += 1
        # test for special tiles
        destTile = self.board[dest]
        # ================CARD TILES==========================================================================
        if isinstance(destTile, GanjiMathreeTile):
            # pick card
            result = self.board[dest].playerArrives(playerObj, self.Ma3Box, self.boardGfx, self.playerCount)
            # moves to a new spot
            return result
        elif isinstance(destTile, GanjiGanjiTile):
            # pick card
            result = self.board[dest].playerArrives(playerObj, self.GanjiBox, self.boardGfx, self.playerCount)
            return []
        # ================POLICE TILE=========================================================================
        elif isinstance(destTile, GanjiPolice):
            # this is police
            # call playerArrives on the police tile
            self.board[dest].playerArrives(playerObj, self.boardGfx, self.playerCount)
            # call playerLeaves on the tile
            self.board[dest].playerLeaves(playerObj)
            # call playerArrives on the jail tile
            self.board[12].playerArrives(playerObj, self.boardGfx, self.playerCount)
            return []
        # ================TAX TILES===========================================================================
        elif isinstance(destTile, GanjiTaxes):
            # call playerArrives on the destination tile and add tax to ATM
            taxAmount = self.board[dest].playerArrives(playerObj, self.boardGfx, self.playerCount)
            self.board[24].cash += taxAmount
            return []
        # ===================PROPERTIES=======================================================================
        else:
            # call playerArrives on the destination tile
            self.board[dest].playerArrives(playerObj, self.boardGfx, self.playerCount)
            if playerObj.debt != 0:
                self.oweFlag = True
            return []
        
    def createBoard(self):
        # initialize counts
        estateCount = 0
        fastFoodCount = 0
        commsCount = 0
        transportCount = 0
        utilityCount = 0
        taxesCount = 0
        # create the tile objects
        toolBox = [self.boardGfx.add_widget, self.boardGfx.remove_widget, self.msgBox, self.processFakeRoll, self.hailBox,
            self.fontSizes, self.mortgageRate]
        for x, y in enumerate(boardTiles):
            if y[0] == 'E':
                # load an estate
                e = GanjiEstate(self.estatesList[estateCount], x, toolBox)
                self.board.append(e)
                self.boardGfx.add_widget(e.widget)
                estateCount += 1
            elif y[0] == 'F':
                # load a fast food joint
                f = GanjiFastFood(self.fastFoodList[fastFoodCount], x, toolBox)
                self.board.append(f)
                f.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(f.widget)
                fastFoodCount += 1
            elif y[0] == 'C':
                # load a communications company
                c = GanjiComms(self.commsList[commsCount], x, toolBox)
                self.board.append(c)
                c.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(c.widget)
                commsCount += 1
            elif y[0] == 'T':
                # load a transport company
                t = GanjiTransport(self.transportList[transportCount], x, toolBox)
                self.board.append(t)
                t.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(t.widget)
                transportCount += 1
            elif y[0] == 'U':
                # load a utility
                u = GanjiUtility(self.utilitiesList[utilityCount], x, toolBox)
                self.board.append(u)
                u.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(u.widget)
                utilityCount += 1
            elif y[0] == 'EM':
                # set payday tile
                em = GanjiEM('Payday', x, toolBox)
                self.board.append(em)
                em.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(em.widget)
            elif y[0] == 'M':
                # set a Mat tile
                m = GanjiMathreeTile('MATHREE', x, toolBox)
                self.board.append(m)
                m.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(m.widget)
            elif y[0] == 'G':
                # set a Ganji tile
                g = GanjiGanjiTile('GANJI', x, toolBox)
                self.board.append(g)
                g.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(g.widget)
            elif y[0] == 'J':
                # set the jail tile
                j = GanjiJail('JAIL', x, toolBox)
                self.board.append(j)
                j.widget.background_color = [0,0,0,1]
                self.boardGfx.add_widget(j.widget)
            elif y[0] == 'P':
                # set the police tile
                p = GanjiPolice('POLICE\nSTATION', x, toolBox)
                self.board.append(p)
                p.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(p.widget)
            elif y[0] == 'A':
                a = GanjiATM('ATM', x, toolBox)
                self.board.append(a)
                a.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(a.widget)
            elif y[0] == 'TX':
                tx = GanjiTaxes(self.taxesList[taxesCount], x, toolBox)
                self.board.append(tx)
                tx.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(tx.widget)
                taxesCount += 1
            else:
                # nothing should be handled here
                pass
        # add the two boxes of cards
        self.boardGfx.add_widget(self.GanjiBox.box)
        self.boardGfx.add_widget(self.Ma3Box.box)
        # add roll dice button
        self.boardGfx.add_widget(self.dice)
        # add manage properties button
        self.boardGfx.add_widget(self.manager)
        # add label for dice results
        self.boardGfx.add_widget(self.rolls)
        # add label for turn
        self.boardGfx.add_widget(self.turnLabel)
        # add message box for system messages
        self.boardGfx.add_widget(self.msgBox)
        # add hail box for tile messages and chats
        self.boardGfx.add_widget(self.hailBox)
        # add image
        #self.boardGfx.add_widget(Image(source='images/Monopoly.png', pos=(0,0),size=self.boardGfx.size))
    
    def build(self):
        if self.scrollable:
            # create a scroll view
            self.easel = ScrollView(size_hint=(1, 1), scroll_timeout=200)
            self.easel.add_widget(self.boardGfx)
            return self.easel
        else:
            return self.boardGfx
    
# a layout class to arrange the Ganji board tiles
class GanjiBoard(FloatLayout):

    def __init__(self, x, y, scrollFlag, **kwargs):
        super(GanjiBoard, self).__init__(**kwargs)
        # 13 tiles wide, 13 tiles high
        if scrollFlag:
            self.size_hint=(1.5, 1.5)
        else:
            self.size = (x, y)
        # make a background
        #self.canvas.add(Color(1,1,1))
        #self.canvas.add(Rectangle(pos=(0,0), size=self.size))

        