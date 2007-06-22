#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx 
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *

class Struct: 
    "simple dummy class to regroup scene entities in a single parameter" 
    pass 

class wxOgreWindow(wx.PyWindow): 
    def __init__(self, parent, ID, size = wx.Size(200,200), **kwargs): 
        wx.PyWindow.__init__(self, parent, ID, size = size, **kwargs) 
        self.parent = parent 

 
        #Event bindings 
        self.Bind(wx.EVT_CLOSE,            self._OnCloseWindow) 
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._OnEraseBackground) 
        self.Bind(wx.EVT_SIZE,             self._OnSize) 

        #Ogre Initialisation 
        self.ogreRoot = getOgreManager().getRoot()

        # create a new RenderWindow
        self.renderWindow = getOgreManager().createRenderWindow(self, "wxPythonWxOgreRenderWindow", size[0], size[1], False, self.GetHandle())
        self.renderWindow.active = True 
        
        self.SceneInitialisation() 
        self.SetFocus()
        
    def _OnSize(self, event):         
        if getattr(self, 'ogreRoot', None): 
            self.renderWindow.windowMovedOrResized() 
        event.Skip() 

    def _OnEraseBackground(self, event): 
        # Do nothing, to avoid flashing on MSW. 
        pass 

    def _OnCloseWindow(self, event): 
        self.Destroy() 

    def AcceptsFocus(self): 
        return True 
    
    def SceneInitialisation(self): 
        pass

    def OnFrameStarted(self): 
        return 
    
    def OnFrameEnded(self): 
        return 
