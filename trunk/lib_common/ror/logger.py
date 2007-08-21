import os, os.path, sys, logging,logging.config

LOGCONFIGFILE = "logging.ini"

# "extended" singleton
_rorlogger = None
def log():
    global _rorlogger
    if _rorlogger is None:
        _rorlogger = RoRLogger()
    return _rorlogger.getLog()


class RoRLogger:
    logconfigfilename = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGCONFIGFILE)

    def __init__(self):
        logging.config.fileConfig(self.logconfigfilename)
        self.myLog = logging.getLogger("root")
        self.myLog.info("logging initialised")

    def getLog(self):
        return self.myLog
