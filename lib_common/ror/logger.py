import os, os.path, sys, logging, logging.config
from ogre.renderer.OGRE import *
from TrueSingleton import Singleton
from settingsManager import rorSettings

LOGCONFIGFILE = "logging.ini"

import logging
logger = None


def log():
    return rorLog().getLog()

#Lepes: it works, but the log is difficult to read :s
#      On the other hand we don't have any log until
#None	Ogre is initialised...to bad. 
#class Ogrelog(Singleton):
#	def init(self):
#		self.log = ogre.LogManager.getSingleton()
#	def error(self, msg):
#		self.log.logMessage( "PYTHON ERROR:" + msg)
#	def warning(self, msg):
#        self.log.logMessage( "PYTHON WARNING:" + msg)
#    def debug(self, msg):
#        self.log.logMessage( "PYTHON DEBUG:" + msg)

class rorLog(Singleton):

    def init(self):
#        self.logconfigfilename = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGCONFIGFILE)
#        lm = ogre.LogManager()
#        l = lm.getSingleton()
#        lm.logMessage("python")
        self.logconfigfilename = rorSettings().concatToToolkitHomeFolder(['logs', LOGCONFIGFILE], True)

        logidentifier = 'RoRToolkit'
        # set up logging to file
        logfilename = self.logconfigfilename = rorSettings().concatToToolkitHomeFolder(['logs', 'editor.log'], True)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=logfilename,
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        
        self.myLog = logging.getLogger(logidentifier)
    def getLog(self):
        return self.myLog
