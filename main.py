# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# File: main.py
# Desc: Entry point for the Mtaani game
# Author: Kingsley Ndiewo
# Company: Intellect Alliance Limited
# Copyright: (C)2013 Intellect Alliance Limited
from Mtaani.MtaaniGame import MtaaniGame

def loadConfiguration():
    newGame = MtaaniGame()
    newGame.run()
    
if __name__ == '__main__':
    loadConfiguration()