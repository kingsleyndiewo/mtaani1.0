# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniThreads.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
import threading
# ---------------------------------------------
class MtaaniThread(threading.Thread):
    " The base class for all Mtaani threads; extends Thread "
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        # ancestral constructor
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)