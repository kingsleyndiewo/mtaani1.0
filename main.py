# Package Description: Intellect Alliance Games Pack
# Title: Ganji Board Game
# File: main.py
# Desc: Entry point for the Ganji game
# Author: Kingsley Ndiewo
# Company: Intellect Alliance Limited
# Copyright: (C)2013 Intellect Alliance Limited
from Ganji.GanjiGame import GanjiGame

def loadConfiguration():
    newGame = GanjiGame(['Kingsley', 'Matt', 'Jerry', 'Kimari'])
    newGame.run()
    
if __name__ == '__main__':
    loadConfiguration()