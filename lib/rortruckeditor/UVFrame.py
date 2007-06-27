#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorsettings import *
from ror.rorcommon import *
from RoRUVOgreWindow import *

ID_CLOSEWINDOW = 100

class UVFrame(wx.Frame): 
    rordir = None
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds) 

        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
 
        #main splitter
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_PERMIT_UNSPLIT|wx.SP_3DSASH)
        self.splitterleft = wx.Panel(self.splitter, wx.ID_ANY)
        self.splitterright = wx.Panel(self.splitter, wx.ID_ANY)
        self.splitter.SetSashGravity(1)
        self.splitter.SetSashPosition(100)
        self.splitter.SetMinimumPaneSize(200)
      
        self.rordir = getSettings().getRoRDir()

        #ogre windows
        self.uvOgreWin = RoRUVOgreWindow(self.splitterleft, wx.ID_ANY)
        
        #some labels
        #self.helptext = wx.StaticText(self.splitterleft, wx.ID_ANY, "short help: right click  = rotate; ctrl + right click, AWSD, mouse wheel = move") 
        #self.rotatingLabel = wx.StaticText(self.viewsplitterup, wx.ID_ANY, "rotating") 
        #self.topLabel = wx.StaticText(self.viewsplitterdown, wx.ID_ANY, "top") 

        #create statusbar
        self.statusbar = self.CreateStatusBar(3, 0, wx.ID_ANY, "mainstatusbar")
        self.statusbar.SetStatusWidths([-1, 80, 80])
        self.statusbar.SetStatusText("-", 1)

        
        self.__set_properties() 
        self.__do_layout() 

    def setTree(self,tree):
        self.uvOgreWin.setTree(tree)
        self.trucktree = tree
        
    def OnClose(self, event = None):
        print "onClose"
        self.uvOgreWin.close()
        self.Destroy()

    def __set_properties(self): 
        self.SetTitle("UV Editor") 
        self.uvOgreWin.SetMinSize((640,480)) 

    def __do_layout(self): 
        sizer_main = wx.BoxSizer(wx.HORIZONTAL) 

        sizer_left = wx.BoxSizer(wx.VERTICAL) 
        sizer_left.Add(self.uvOgreWin, 2, wx.EXPAND, 0) 
        self.splitterleft.SetSizer(sizer_left)

        self.splitter.SplitVertically(self.splitterleft, self.splitterright)
        self.splitter.Unsplit()
        self.splitter.SetSashPosition(600)

        
        sizer_main.Add(self.splitter, 1, wx.EXPAND, 0)

        self.SetAutoLayout(True) 
        self.SetSizer(sizer_main) 
        sizer_main.Fit(self) 
        sizer_main.SetSizeHints(self) 
        self.Layout() 

