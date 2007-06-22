import os, os.path


_set = None
def getSettings():
    global _set
    if _set is None:
        _set = RoRSettings()
    return _set

class RoRSettings:
    rordir = None
    configfilename = os.path.join(os.path.dirname(os.path.abspath(__file__)),"editor.cfg")
    def __init__(self):
        self.LoadRoRDir()
    
    def getRoRDir(self):
        return self.rordir
    
    def setRoRDir(self, dir):
        self.rordir = dir
        self.SaveRoRDir()
    
    def LoadRoRDir(self):
        try:
            f = open(self.configfilename,'r')
            self.rordir = f.read()
            f.close()
        except:
            print "error while loading rordir: %s" % self.configfilename

    def SaveRoRDir(self):
        try:
            f = open(self.configfilename,'w')
            f.write(self.rordir)
            f.close()
        except:
            print "error while saving rordir: %s" % os.path.abspath("editor.cfg")
