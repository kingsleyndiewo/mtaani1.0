# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniGame.py
# Developed by: Intellect Alliance Software Team
# Date: 06/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniInteraction import MtaaniInteraction
from ConfigParser import ConfigParser
from MtaaniEstate import MtaaniEstate
from MtaaniFastFood import MtaaniFastFood
from MtaaniTransport import MtaaniTransport
from MtaaniUtility import MtaaniUtility
from MtaaniComms import MtaaniComms
from MtaaniEM import MtaaniEM
from MtaaniJail import MtaaniJail
from MtaaniPolice import MtaaniPolice
from MtaaniATM import MtaaniATM
from MtaaniTaxes import MtaaniTaxes
from MtaaniPlayer import MtaaniPlayer
from MtaaniCardTile import MtaaniMathreeTile, MtaaniGanjiTile
from MtaaniCards import MtaaniMathreeBox, MtaaniGanjiBox
from MtaaniGlobals import boardTiles, othersList
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
# system utilities
from MtaaniSystem import MtaaniSystem
# network
import socket
# ---------------------------------------------
# ---------------------------------------------
# a class that defines the simple Mtaani board game
class MtaaniGame(App):
    " The base class for all Mtaani games "
    def __init__(self):
        # ===============================================================
        # set kivy config variables
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        Config.write()
        # ===============================================================
        self.board = []
        # system box has network object and directory paths
        self.systemBox = MtaaniSystem()
        self.playersList = []
        self.gameSpeak = MtaaniInteraction()
        # =============================================================
        # setup network
        # =============================================================
        self.socket = socket.socket()
        # get local machine name
        self.host = socket.gethostname()
        self.port = 20143
        #self.socket.bind((self.host, self.port)) 
        # parsers
        ganjiConfig = ConfigParser()
        # read in estate list
        ganjiConfig.read(self.systemBox.estatesConf)
        self.estatesList = ganjiConfig.sections()
        # read in companies list
        ganjiConfig = ConfigParser()
        ganjiConfig.read(self.systemBox.companiesConf)
        self.fastFoodList = ganjiConfig.sections()[:4]
        self.commsList = ganjiConfig.sections()[-2:]
        self.transportList = ganjiConfig.sections()[4:8]
        # read in utilities
        ganjiConfig = ConfigParser()
        ganjiConfig.read(self.systemBox.utilitiesConf)
        self.utilitiesList = ganjiConfig.sections()
        # generate taxes list
        self.taxesList = ['PAYE', 'VAT']
        # read in settings
        ganjiConfig = ConfigParser()
        ganjiConfig.read(self.systemBox.mainConf)
        self.screenW = ganjiConfig.getint('GAME', 'ScreenX')
        self.screenH = ganjiConfig.getint('GAME', 'ScreenY')
        self.textMax = ganjiConfig.getint('GAME', 'TextMax')
        self.ttsRoll = bool(ganjiConfig.getint('TTS-ROLLS', 'Speak'))
        self.scrollable = bool(ganjiConfig.getint('DISPLAY', 'Scrollable'))
        self.scrollScale = ganjiConfig.getint('DISPLAY', 'ScrollScale')
        self.mortgageRate = ganjiConfig.getfloat('BANK', 'Mortgage')
        # make a list of the rest
        self.othersList = othersList
        # make layout
        if self.scrollable:
            self.fontSizes = [13 * self.scrollScale, 15 * self.scrollScale]
        else:
            self.fontSizes = [13, 15]
        self.boardGfx = MtaaniBoard(self.screenW, self.screenH, self.scrollable, self.scrollScale)
        # =============================================================
        # run graphics constructor
        App.__init__(self)
        # =============================================================
        # create the login area
        banner = Label(text='WELCOME TO MTAANI', font_size=(self.fontSizes[0] * 2), size_hint=(.5, .2), color=[1,1,1,1],
            pos_hint={'x':.25, 'y':.85}, bold=True)
        self.sysNotices = Label(text='Please enter the names of up to 6 players', font_size=self.fontSizes[1], size_hint=(.5, .2), color=[1,1,1,1],
            pos_hint={'x':.25, 'y':.8})
        self.playerNames = []
        for x in range(6):  
            txtBox = (TextInput(text='', font_size=self.fontSizes[0], size_hint=(.3, .05),
                foreground_color=[.2,.1,.2,1], pos_hint = {'x':.35, 'y':(.78 - (.04 * x))}, background_color=[1,1,1,1]))
            self.boardGfx.add_widget(txtBox)
            self.playerNames.append(txtBox)
        # add the button for submitting
        self.submitter = Button(text='SUBMIT NAMES', font_size=self.fontSizes[0], size_hint=(.25, .05), color=[0,0,0,1],
            pos_hint={'x':.38, 'y':.5}, bold=True)
        # add image
        ganji20image = Image(source=self.systemBox.splashImg, pos_hint={'x':.01, 'y':.01}, size_hint=(.5, .5))
        ganji20image2 = Image(source=self.systemBox.splashImg, pos_hint={'x':.5, 'y':.01}, size_hint=(.5, .5))
        self.submitter.bind(on_release=self.loginCallback)
        self.boardGfx.add_widget(self.submitter)
        self.boardGfx.add_widget(banner)
        self.boardGfx.add_widget(self.sysNotices)
        self.boardGfx.add_widget(ganji20image)
        self.boardGfx.add_widget(ganji20image2)
    
    def loginCallback(self, instance):
        for n in self.playerNames:
            if n.text != '':
                self.playersList.append(n.text)
        if self.playersList == [] or len(self.playersList) < 2:
            self.sysNotices.text = "You must enter at least 2 players to proceed"
            return
        else:
            self.boardGfx.clear_widgets()
            self.initNewGame(self.playersList)
            
    def initNewGame(self, playerList):
        # initialize log file
        self.systemBox.initLogFile()
        # set the player count
        self.playerCount = len(self.playersList)
        # create button for rolling dice
        self.dice = Button(text='ROLL DICE', font_size=self.fontSizes[1], size_hint=(.07, .07), color=[0,0,0,1],
            pos_hint={'x':.42, 'y':.2}, bold=True, background_color=[.8,.8,1,1])
        # create button for the asset manager
        self.manager = Button(text='MANAGE ASSETS', font_size=self.fontSizes[1], size_hint=(.09, .05), color=[0,0,0,1],
            pos_hint={'x':.5, 'y':.2}, bold=True, background_color=[.8,.8,1,1])
        # create button for the trade manager
        self.trader = Button(text='TRADE ASSETS', font_size=self.fontSizes[1], size_hint=(.09, .05), color=[0,0,0,1],
            pos_hint={'x':.32, 'y':.2}, bold=True, background_color=[.8,.8,1,1])
        # set the three callbacks
        self.dice.bind(on_release=self.diceCallback)
        self.manager.bind(on_release=self.mgrCallback)
        self.trader.bind(on_release=self.tdrCallback)
        # create label for showing dice roll results
        self.rolls = Label(text='0    0', font_size=self.fontSizes[1], size_hint=(.07, .07), color=[1,1,1,1],
            pos_hint={'x':.42, 'y':.25}, bold=True)
        # create label for showing who's turn it is
        self.turnLabel = Label(text='None', font_size=self.fontSizes[0], size_hint=(.07, .07), color=[1,1,1,1],
            pos_hint={'x':.51, 'y':.25})
        # create a text box for showing the system and game messages
        self.msgBox = TextInput(text='System: No current messages', font_size=self.fontSizes[0], size_hint=(.24, .3),
                foreground_color=[.7,1,.7,1], pos_hint = {'x':.39, 'y':.58}, readonly = True, background_color=[0,0,0,1])
        # create a text box for showing the location hails (NikoHapa) and chats (Bonga)
        self.hailBox = TextInput(text='Niko Hapa and Chat Box', font_size=self.fontSizes[0], size_hint=(.24, .3),
            foreground_color=[1,0,.3,1], pos_hint = {'x':.12, 'y':.58}, readonly = True, background_color=[0,0,0,1])
        # create the input box for chat messages and the button for sending
        self.chatBox = TextInput(text='', font_size=self.fontSizes[0], size_hint=(.45, .04),
            foreground_color=[.3,.2,.3,1], pos_hint = {'x':.39, 'y':.11}, background_color=[.7,.8,1,1])
        self.chatSend = Button(text='SEND', font_size=self.fontSizes[1], size_hint=(.08, .04), color=[0,0,0,1],
            pos_hint={'x':.3, 'y':.11}, background_color=[.8,.8,1,1], bold=True)
        self.chatSend.bind(on_release=self.chatCallback)
        # just a convenience list of things we send to other classes a lot
        toolBox = [self.boardGfx.add_widget, self.boardGfx.remove_widget, self.msgBox]
        # create card boxes
        self.MtaaniBox = MtaaniGanjiBox(toolBox, self.fontSizes)
        self.Ma3Box = MtaaniMathreeBox(toolBox, self.fontSizes)
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
            self.players[x] = MtaaniPlayer(x, toolBox)
            self.board[0].occupants.append(x)
            self.players[x].index = n
            # add to board
            self.board[0].placePlayer(self.players[x], self.boardGfx, self.playerCount)
            self.boardGfx.add_widget(self.players[x].token)
        # assign current player
        self.currentPlayer = 0
        # set oweFlag to false
        self.oweFlag = False
        # set victory flag to false
        self.victorious = False
        # set jail bird flag to false
        self.jailBird = False
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
        for x in self.players.values():
            x.myTurn = False
        playerObj.myTurn = True
    
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
        
    def tdrCallback(self, instance):
        name = self.playersList[self.currentPlayer]
        playerObj = self.players[name]
        # check for any debt
        if self.board[playerObj.position].debtCollection and not self.oweFlag:
            self.oweFlag = True
        playerObj.tradeAssets()
        
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
    def chatCallback(self, instance):
        # check for empty chat
        if self.chatBox.text == '':
            return
        # send the chat to the chat log
        newChat = "\n%s: %s" % (self.playersList[self.currentPlayer], self.chatBox.text)
        self.hailBox.text += newChat
        # clear chat box
        self.chatBox.text = ''
    
    def bankruptcy(self, player):
        # process a bankruptcy
        self.msgBox.text = self.msgBox.text + "\nMtaani: %s declared bankruptcy!" %  player.name
        self.msgBox.text = self.msgBox.text + "\nMtaani: Bank will liquidate assets and pay liabilities"
        # pay dues
        self.payDues(player, True)
        bountyAmount = 0
        # reclaim properties
        for p in player.properties.values():
            bountyAmount += p.bankruptcyCleanup(player)
        # pay bounty
        try:
            # bounty goes to owner of where player is bankrupted
            self.board[player.position].owner.cash += bountyAmount
            self.msgBox.text = self.msgBox.text + "\nMtaani: %s had %2.f SFR in net assets,\nwhich have been liquidated and transferred\nto %s" % (player.name,
                bountyAmount, self.board[player.position].owner.name)
        except:
            # give to bank
            player.ATMTile.cash += bountyAmount
            self.msgBox.text = self.msgBox.text + "\nMtaani: %s had %2.f SFR in net assets,\nwhich have been liquidated and transferred\nto the bank" % (player.name,
                bountyAmount)
        # remove from board
        name = self.playersList[self.currentPlayer]
        self.boardGfx.remove_widget(player.token)
        self.playersList.pop(self.currentPlayer)
        self.playerCount -= 1
        del self.players[name]
        # check victory
        if self.playerCount == 1:
            self.victorious = True
            name = self.playersList[0]
            playerObj = self.players[name]
            self.msgBox.text = self.msgBox.text + "\nSystem: %s has won the game!!!" % playerObj.name
        else:
            # switch turn
            self.switchTurn(True)
        
    def diceCallback(self, instance):
        # get player object
        try:
            name = self.playersList[self.currentPlayer]
            playerObj = self.players[name]
        except IndexError:
            # game over
            self.msgBox.text = self.msgBox.text + "\nSystem: %s has already won the game" %  self.playersList[0]
            return
        # ==============CHECK VICTORY============================================================
        if self.victorious:
            self.msgBox.text = self.msgBox.text + "\nSystem: %s has already won the game" %  self.playersList[self.currentPlayer]
            return
        # ==============CHECK DEBT===============================================================
        if self.oweFlag:
            if not self.payDues(playerObj):
                # no one else plays
                self.msgBox.text = self.msgBox.text + "\nSystem: %s must pay debt before play continues" %  self.playersList[self.currentPlayer]
            # we can't give player extra turn
            return
        # ==============CHECK JAILED=============================================================
        if self.jailBird:
            # see what was chosen
            if self.board[playerObj.position].popupValue == "Roll":
                # just let the execution go through here as usual
                pass
            else:
                # pay bail and continue
                self.board[playerObj.position].payBail(playerObj)
            self.jailBird = False
        elif playerObj.inJail and playerObj.cash >= self.board[playerObj.position].bail and \
            playerObj.jailTurn < self.board[playerObj.position].turns:
            # prompt for whether to pay bail or roll for doubles
            self.board[playerObj.position].popupBox("Roll for doubles or pay the %2.f SFR bail?" %
                self.board[playerObj.position].bail, ["Roll", "Pay Bail"])
            # set callback
            # setup post-dialog process
            self.returnExecution = self.diceCallback
            self.reArgs = [None]
            self.jailBird = True
            return
        # =======================================================================================
        result = playerObj.rollDice()
        self.rolls.text = "%d    %d" % (result[0], result[1])
        self.rolls.canvas.ask_update()
        # clear notifications label if too long
        if len(self.msgBox.text) > self.textMax:
            self.systemBox.logFO.write(self.msgBox.text)
            self.systemBox.logFO.flush()
            self.msgBox.text = ''
        if len(self.hailBox.text) > self.textMax:
            self.hailBox.text = ''
        if self.ttsRoll:
            # speak the rolls
            self.gameSpeak.notifyText("%s, You rolled %d and %d" % (name, result[0], result[1]))
        # =======================================================================================
        # process rolling for doubles in jail
        if playerObj.inJail:
            # doubles first
            if result[2]:
                # just continue as usual; but cancel doubles
                result[2] = False
                self.msgBox.text = self.msgBox.text + "\nSystem: %s rolled doubles and broke out of jail!" % playerObj.name 
            else:
                if playerObj.jailTurn == 0:
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
        # =======================================================================================
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
            # unless doubles landed us in jail
            if playerObj.inJail == False:
                switchFlag = False
            else:
                # we cancel doubles because player went to jail
                switchFlag = True
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
            # check jail
            if playerObj.inJail:
                # cancel doubles
                switchFlag = True
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
        if isinstance(destTile, MtaaniMathreeTile):
            # pick card
            result = self.board[dest].playerArrives(playerObj, self.Ma3Box, self.boardGfx, self.playerCount)
            # moves to a new spot
            return result
        elif isinstance(destTile, MtaaniGanjiTile):
            # pick card
            self.board[dest].playerArrives(playerObj, self.MtaaniBox, self.boardGfx, self.playerCount)
            # ganji card may put player in debt
            if playerObj.debt != 0:
                self.oweFlag = True
            return []
        # ================POLICE TILE=========================================================================
        elif isinstance(destTile, MtaaniPolice):
            # this is police
            # call playerArrives on the police tile
            self.board[dest].playerArrives(playerObj, self.boardGfx, self.playerCount)
            # call playerLeaves on the tile
            self.board[dest].playerLeaves(playerObj)
            # call playerArrives on the jail tile
            self.board[12].playerArrives(playerObj, self.boardGfx, self.playerCount)
            return []
        # ================TAX TILES===========================================================================
        elif isinstance(destTile, MtaaniTaxes):
            # call playerArrives on the destination tile and add tax to ATM
            self.board[dest].playerArrives(playerObj, self.boardGfx, self.playerCount)
            # tax may put player in debt
            if playerObj.debt != 0:
                self.oweFlag = True
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
            self.fontSizes, self.mortgageRate, self.scrollable, self.scrollScale]
        for x, y in enumerate(boardTiles):
            tileObj = None
            if y[0] == 'E':
                # load an estate
                e = MtaaniEstate(self.estatesList[estateCount], x, toolBox)
                self.board.append(e)
                self.boardGfx.add_widget(e.widget)
                estateCount += 1
                # make lots for development
                e.createLots(self.boardGfx)
            elif y[0] == 'F':
                # load a fast food joint
                f = MtaaniFastFood(self.fastFoodList[fastFoodCount], x, toolBox)
                self.board.append(f)
                f.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(f.widget)
                fastFoodCount += 1
                f.createLots(self.boardGfx)
            elif y[0] == 'C':
                # load a communications company
                c = MtaaniComms(self.commsList[commsCount], x, toolBox)
                self.board.append(c)
                c.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(c.widget)
                commsCount += 1
                c.createLots(self.boardGfx)
            elif y[0] == 'T':
                # load a transport company
                t = MtaaniTransport(self.transportList[transportCount], x, toolBox)
                self.board.append(t)
                t.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(t.widget)
                transportCount += 1
                t.createLots(self.boardGfx)
            elif y[0] == 'U':
                # load a utility
                u = MtaaniUtility(self.utilitiesList[utilityCount], x, toolBox)
                self.board.append(u)
                u.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(u.widget)
                utilityCount += 1
                u.createLots(self.boardGfx)
            elif y[0] == 'EM':
                # set payday tile
                em = MtaaniEM('Payday', x, toolBox)
                self.board.append(em)
                em.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(em.widget)
                tileObj = em
            elif y[0] == 'M':
                # set a Mat tile
                m = MtaaniMathreeTile('MATHREE', x, toolBox)
                self.board.append(m)
                m.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(m.widget)
                tileObj = m
            elif y[0] == 'G':
                # set a Ganji tile
                g = MtaaniGanjiTile('GANJI', x, toolBox)
                self.board.append(g)
                g.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(g.widget)
                tileObj = g
            elif y[0] == 'J':
                # set the jail tile
                j = MtaaniJail('JAIL', x, toolBox)
                self.board.append(j)
                j.widget.background_color = [0,0,0,1]
                self.boardGfx.add_widget(j.widget)
                tileObj = j
            elif y[0] == 'P':
                # set the police tile
                p = MtaaniPolice('POLICE STN', x, toolBox)
                self.board.append(p)
                p.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(p.widget)
                tileObj = p
            elif y[0] == 'A':
                a = MtaaniATM('ATM', x, toolBox)
                self.board.append(a)
                a.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(a.widget)
                tileObj = a
            elif y[0] == 'TX':
                tx = MtaaniTaxes(self.taxesList[taxesCount], x, toolBox)
                self.board.append(tx)
                tx.widget.background_color = [1,1,1,1]
                self.boardGfx.add_widget(tx.widget)
                taxesCount += 1
                tileObj = tx
            else:
                # nothing should be handled here
                pass
        # add the two boxes of cards
        self.boardGfx.add_widget(self.MtaaniBox.box)
        self.boardGfx.add_widget(self.Ma3Box.box)
        # add roll dice button
        self.boardGfx.add_widget(self.dice)
        # add manage assets button
        self.boardGfx.add_widget(self.manager)
        # add trade assets button
        self.boardGfx.add_widget(self.trader)
        # add label for dice results
        self.boardGfx.add_widget(self.rolls)
        # add label for turn
        self.boardGfx.add_widget(self.turnLabel)
        # add message box for system messages
        self.boardGfx.add_widget(self.msgBox)
        # add hail box for tile messages and chats
        self.boardGfx.add_widget(self.hailBox)
        # add the box for entering a chat message
        self.boardGfx.add_widget(self.chatBox)
        self.boardGfx.add_widget(self.chatSend)
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
    
# a layout class to arrange the Mtaani board tiles
class MtaaniBoard(FloatLayout):

    def __init__(self, x, y, scrollFlag, scrollScale, **kwargs):
        super(MtaaniBoard, self).__init__(**kwargs)
        # 13 tiles wide, 13 tiles high
        if scrollFlag:
            self.size_hint=(scrollScale, scrollScale)
        else:
            self.size = (x, y)
        # make a background
        #self.canvas.add(Color(1,1,1))
        #self.canvas.add(Rectangle(pos=(0,0), size=self.size))

        