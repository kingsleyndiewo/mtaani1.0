# Package Description: Intellect Alliance Games Pack
# Title: Mtaani Board Game
# Desc: Base Mtaani Game CodeBase
# File name: MtaaniInteraction.py
# Developed by: Intellect Alliance Software Team
# Date: 02/07/2013
# Place: Nairobi, Kenya
# Copyright: (C)2013 Intellect Alliance Limited
# ---------------------------------------------
from MtaaniGlobals import voicesList
from threading import Thread
import os
from time import sleep
from random import randint
from kivy.utils import platform
# ---------------------------------------------
# a class that defines the Mtaani interactivity suite
class MtaaniInteraction:
    " The base class for all Mtaani interactions "
    def __init__(self, talker = 'espeak', volume = 20, voice = 'en'):
        # set initial values for variables
        self.talker = talker
        self.volume = volume
        # pick a random voice
        voiceSpectrum = len(voicesList)
        randVoice = randint(0, voiceSpectrum - 1)
        self.voice = voice + ('+%s' % voicesList[randVoice])
        self.platform = platform
    def notifyText(self, textToNotify, speakFlag = True):
        if speakFlag and False:
            if self.platform != "android":
                cmdStr = 'echo "%s" | %s -a %d -v %s > /dev/null 2>&1' % (textToNotify, self.talker, self.volume, self.voice)
                thread = Thread(target=self.sendCmd, args=(cmdStr,))
                thread.start()
            else:
                # android
                self.androidSpeak(textToNotify)
            sleep(2.5)
    def androidSpeak(self, msgString):
        from jnius import autoclass
        Locale = autoclass('java.util.Locale')
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        tts = TextToSpeech(PythonActivity.mActivity, None)
        tts.setLanguage(Locale.US)
        retries = 0
        while retries < 10 and \
              tts.speak(msgString.encode('utf-8'), TextToSpeech.QUEUE_FLUSH, None) == -1:
            # -1 indicates error. Let's wait and then try again
            sleep(0.1)
            retries += 1
    def sendCmd(self, cmdString):
        os.system(cmdString)
    def getInput(self, promptText, textInput = True, speakFlag = True):
        if speakFlag:
            cmdStr = 'echo "%s" | %s -a %d -v %s > /dev/null 2>&1' % (promptText, self.talker, self.volume, self.voice)
            thread = Thread(target=self.sendCmd, args=(cmdStr,))
            thread.start()
        if textInput:
            return raw_input(promptText)
        else:
            return input(promptText)
