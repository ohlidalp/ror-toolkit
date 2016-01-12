import ogre.renderer.OGRE as ogre 
import logger

class MyLog(ogre.LogListener):
    def __init__(self):
        # Creates a C++ log that will try and write to console and file
        ogre.LogListener.__init__(self)
                 
    def messageLogged(self, message, level, debug, logName):
        # This should be called by Ogre instead of logging
        #print 'Python Logger Called -- Listener works !!!'
        #print ">>>", message
        pass

def initOgreLogging():
    # Create the global log manager instance
    logMgr = ogre.LogManager()

    # create a "log"
    currentLog = ogre.LogManager.getSingletonPtr().createLog("ogre.log" ,True, False, False) 

    #ogre.LogManager.getSingletonPtr().setDefaultLog(currentLog)

    myLog = MyLog()
    # register our listener
    currentLog.addListener ( myLog )    

    # And test it
    #ogre.LogManager.getSingletonPtr().logMessage('Should Not Appear',
    #                                             ogre.LML_CRITICAL, False) 
