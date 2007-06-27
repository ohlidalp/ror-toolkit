#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys
import wx
import ogre.renderer.OGRE as ogre 

# singleton implementation of OgreManager
_ogremanager = None
def getOgreManager():
    global _ogremanager
    if _ogremanager is None:
        _ogremanager = OgreManager()
    return _ogremanager


class OgreManager():
    renderWindows = {}

    def restart(self):
    	self.ogreRoot.shutdown()
        self.init()
        
    def __init__(self): 
        self.init()
        
    def init(self):
        #Root creation 
        self.ogreRoot = ogre.Root(self.getConfigPath('plugins.cfg'), self.getConfigPath('ogre.cfg'), "ogre.log")        
        self.ogreRoot.showConfigDialog()                     
        self.ogreRoot.initialise(False)

    def getRoot(self):
        return self.ogreRoot
        
    def getConfigPath(self, filename):
        """Return the absolute path to a valid config file.""" 
        import sys
        import os
        import os.path
        
        paths = [os.path.join(os.getcwd(), filename),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)]

        for path in paths:
            if os.path.exists(path):
                print path
                return path

        sys.stderr.write("\n"
            "** Warning: Unable to locate a suitable " + filename + " file.\n"
            "** Warning: Please check your ogre installation and copy a\n"
            "** Warning: working plugins.cfg file to the current directory.\n\n")
        #raise ogre.Exception(0, "can't locate the '%s' file" % filename, "")
        
    def createRenderWindow(self, wxOgrewin, name, width, height, fullscreen, handle):
        renderParameters = ogre.NameValuePairList() 
        renderParameters['externalWindowHandle'] = str(handle) 
        # use len to make the names unique!
        renderWindow = self.ogreRoot.createRenderWindow(name + str(len(self.renderWindows)), width, height, fullscreen, renderParameters) 
        #renderWindow.active = True 
        self.renderWindows[wxOgrewin] = renderWindow
        return renderWindow

    def removeRenderWindow(self, wxOgrewin):
        print "removing render target"
        self.ogreRoot.detachRenderTarget(self.renderWindows[wxOgrewin])
        del self.renderWindows[wxOgrewin]

    def RenderAll(self):
        for ogrewin in self.renderWindows.keys():
            try:
                ogrewin.OnFrameStarted()
            except:
                continue
    
        try:
            self.ogreRoot.renderOneFrame()
        except ogre.OgreException, e:
            print '## EXCEPTION ##'
            print str(e)
            pass
        
        for ogrewin in self.renderWindows.keys():
            try:
                ogrewin.OnFrameEnded()
            except:
                continue
        
    def createSceneManager(self, type):
        return self.ogreRoot.createSceneManager(type, "SceneManager" + str(len(self.renderWindows)))

    def destroySceneManager(self, sm):
        return self.ogreRoot.destroySceneManager(sm)
        