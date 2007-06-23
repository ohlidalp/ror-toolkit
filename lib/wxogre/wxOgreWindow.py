#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx 
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *

class wxOgreWindow(wx.PyWindow): 
    def __init__(self, parent, ID, size = wx.Size(200,200), **kwargs): 
        """
        @param parent: The parent wx Window
        @param size: the minimal window size
        @param kwargs: any other wx arguments
        @return: none
        """
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
        """
        Is called when the ogre Window is getting resized
        @param event: the sizing event
        @return: none
        """
        if getattr(self, 'ogreRoot', None): 
            self.renderWindow.windowMovedOrResized() 
        event.Skip() 

    def _OnEraseBackground(self, event): 
        """
        overwrite standart background drawing routing with empty one
        @param event: the draw event
        @return: none
        """
        # Do nothing, to avoid flashing on MSW. 
        pass 

    def _OnCloseWindow(self, event): 
        """
        called when the ogre window gets closed
        @param event: the closing event
        @return: none
        """
        self.Destroy() 

    def AcceptsFocus(self): 
        """
        this window may accept keyboard focus
        """
        return True 
    
    def SceneInitialisation(self): 
        """
        default, base function, that has to be overwritten in the inherited class. It gets called after create the window, and should select a scenemanger.
        @return: none
        """
        pass

    def OnFrameStarted(self): 
        """
        default, base function, that has to be overwritten in the inherited class. gets called before rendering a frame.
        @return: none
        """
        return 
    
    def OnFrameEnded(self): 
        """
        default, base function, that has to be overwritten in the inherited class. gets called after rendering a frame.
        @return: none
        """
        return 
