#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorsettings import *
from ror.rorcommon import *
from RoRTruckOgreWindow import *

ID_ABOUT    = 101
ID_OPENFILE = 102
ID_VIEWINVISIBLEBEAMS = 103
ID_VIEWROPEBEAMS = 104
ID_VIEWNORMALBEAMS = 105
ID_VIEWNORMALNODES = 106
ID_VIEWLOADNODES = 107
ID_VIEWFRICTIONNODES = 108
ID_VIEWCONTACTNODES = 109
ID_VIEWHOOKNODES = 110
ID_VIEWEXHAUSTNODES = 111
ID_VIEWEXHAUSTREFNODES = 112       
ID_SUBMESHMODETEXTURE = 113
ID_SUBMESHMODEGROUPS = 114
ID_SUBMESHMODEOPTIONS = 115
ID_VIEWSUBMESHS = 116
ID_VIEWALLBEAMS = 117
ID_VIEWALLNODES = 118
ID_FREEMODE = 119
ID_EXIT     = 199


class MainFrame(wx.Frame): 
    rordir = None
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        
        wx.Frame.__init__(self, *args, **kwds) 


        #main splitter
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_PERMIT_UNSPLIT|wx.SP_3DSASH)
        self.splitterleft = wx.Panel(self.splitter, wx.ID_ANY)
        self.splitterright = wx.Panel(self.splitter, wx.ID_ANY)
        self.splitter.SetSashGravity(1)
        self.splitter.SetSashPosition(100)
        self.splitter.SetMinimumPaneSize(200)
      
        self.rordir = getSettings().getRoRDir()

        #ogre windows
        self.truckOgreWin = RoRTruckOgreWindow(self.splitterleft, wx.ID_ANY)
        
        #some labels
        #self.helptext = wx.StaticText(self.splitterleft, wx.ID_ANY, "short help: right click  = rotate; ctrl + right click, AWSD, mouse wheel = move") 
        #self.rotatingLabel = wx.StaticText(self.viewsplitterup, wx.ID_ANY, "rotating") 
        #self.topLabel = wx.StaticText(self.viewsplitterdown, wx.ID_ANY, "top") 

        #Timer creation (for label updates)
        self.timer = wx.Timer() 
        self.timer.SetOwner(self) #Sets the timer to notify self: binding the timer event is not enough 
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(200)

        #Timer creation  (for rendering)
        self.ogreTimer = wx.Timer() 
        self.ogreTimer.SetOwner(self)
        self.Bind(wx.EVT_TIMER, self.onUpdateRender, self.ogreTimer)
        self.ogreTimer.Start(25)
        
        #create statusbar
        self.statusbar = self.CreateStatusBar(3, 0, wx.ID_ANY, "mainstatusbar")
        self.statusbar.SetStatusWidths([-1, 80, 80])
        self.statusbar.SetStatusText("-", 1)

        #menu creation
        menuBar = wx.MenuBar()
        file_menu = wx.Menu()
        self.fileopenmenu = file_menu.Append(ID_OPENFILE, "&Open", "Open Truck")
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXIT, "E&xit", "Terminate the program")
        menuBar.Append(file_menu, "&File");


        view_menu = wx.Menu()

        beams_menu = wx.Menu()
        self.viewnormalbeams = beams_menu.AppendCheckItem(ID_VIEWNORMALBEAMS, "normal beams", "")
        self.viewnormalbeams.Check(True)
        self.viewinvisiblebeams = beams_menu.AppendCheckItem(ID_VIEWINVISIBLEBEAMS, "invisible beams", "")
        self.viewinvisiblebeams.Check(True)
        self.viewropebeams = beams_menu.AppendCheckItem(ID_VIEWROPEBEAMS, "rope beams", "")
        self.viewropebeams.Check(True)

        self.viewallbeams = view_menu.AppendCheckItem(ID_VIEWALLBEAMS, "show all beams", "")
        self.viewallbeams.Check(True)

        view_menu.AppendSubMenu(beams_menu, "View Beams");

        view_menu.AppendSeparator()


        nodes_menu = wx.Menu()
        self.viewnormalnodes = nodes_menu.AppendCheckItem(ID_VIEWNORMALNODES, "normal nodes", "")
        self.viewnormalnodes.Check(True)

        self.viewloadnodes = nodes_menu.AppendCheckItem(ID_VIEWLOADNODES, "load nodes", "")
        self.viewloadnodes.Check(True)

        self.viewfrictionnodes = nodes_menu.AppendCheckItem(ID_VIEWFRICTIONNODES, "friction nodes", "")
        self.viewfrictionnodes.Check(True)

        self.viewcontactnodes = nodes_menu.AppendCheckItem(ID_VIEWCONTACTNODES, "contact nodes", "")
        self.viewcontactnodes.Check(True)

        self.viewhooknodes = nodes_menu.AppendCheckItem(ID_VIEWHOOKNODES, "hook nodes", "")
        self.viewhooknodes.Check(True)

        self.viewexhaustnodes = nodes_menu.AppendCheckItem(ID_VIEWEXHAUSTNODES, "exhaust nodes", "")
        self.viewexhaustnodes.Check(True)

        self.viewexhaustrefnodes = nodes_menu.AppendCheckItem(ID_VIEWEXHAUSTREFNODES, "exhaust reference nodes", "")
        self.viewexhaustrefnodes.Check(True)

        self.viewallnodes = view_menu.AppendCheckItem(ID_VIEWALLNODES, "show all nodes", "")
        self.viewallnodes.Check(True)

        view_menu.AppendSubMenu(nodes_menu, "View Nodes");

        view_menu.AppendSeparator()

        submesh_menu = wx.Menu()
        self.viewsubmeshtexture = submesh_menu.AppendRadioItem(ID_SUBMESHMODETEXTURE, "texture", "")
        self.viewsubmeshgroup = submesh_menu.AppendRadioItem(ID_SUBMESHMODEGROUPS, "groups", "")
        self.viewsubmeshoption = submesh_menu.AppendRadioItem(ID_SUBMESHMODEOPTIONS, "options", "")


        self.viewsubmeshs = view_menu.AppendCheckItem(ID_VIEWSUBMESHS, "show submeshs", "")
        self.viewsubmeshs.Check(True)

        view_menu.AppendSubMenu(submesh_menu, "&Submesh Display Mode");
        self.viewexhaustrefnodes.Check(True)
        
        menuBar.Append(view_menu, "&View");


        mode_menu = wx.Menu()
        mode_menu.AppendRadioItem(ID_FREEMODE, "Free", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Nodes / Beams", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Wheels", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Flares", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Cameras", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Props", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "SubMeshs", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Wings", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Turboprops", "")
        mode_menu.AppendRadioItem(ID_FREEMODE, "Screwprops", "")
        menuBar.Append(mode_menu, "&Modes");
        
        
        self.Bind(wx.EVT_MENU, self.OnViewAllBeams, id=ID_VIEWALLBEAMS)
        self.Bind(wx.EVT_MENU, self.OnViewAllNodes, id=ID_VIEWALLNODES)
        
        self.Bind(wx.EVT_MENU, self.OnViewSubmeshTexture, id=ID_SUBMESHMODETEXTURE)
        self.Bind(wx.EVT_MENU, self.OnViewSubmeshGroups, id=ID_SUBMESHMODEGROUPS)
        self.Bind(wx.EVT_MENU, self.OnViewSubmeshOptions, id=ID_SUBMESHMODEOPTIONS)
        self.Bind(wx.EVT_MENU, self.OnViewSubmeshs, id=ID_VIEWSUBMESHS)

        
        self.Bind(wx.EVT_MENU, self.OnViewInvisibleBeams, id=ID_VIEWINVISIBLEBEAMS)
        self.Bind(wx.EVT_MENU, self.OnViewRopeBeams, id=ID_VIEWROPEBEAMS)
        self.Bind(wx.EVT_MENU, self.OnViewNormalBeams, id=ID_VIEWNORMALBEAMS)

        self.Bind(wx.EVT_MENU, self.OnViewNormalNodes, id=ID_VIEWNORMALNODES)
        self.Bind(wx.EVT_MENU, self.OnViewLoadNodes, id=ID_VIEWLOADNODES)
        self.Bind(wx.EVT_MENU, self.OnViewFrictionNodes, id=ID_VIEWFRICTIONNODES)
        self.Bind(wx.EVT_MENU, self.OnViewContactNodes, id=ID_VIEWCONTACTNODES)
        self.Bind(wx.EVT_MENU, self.OnViewHookNodes, id=ID_VIEWHOOKNODES)
        self.Bind(wx.EVT_MENU, self.OnViewExhaustNodes, id=ID_VIEWEXHAUSTNODES)
        self.Bind(wx.EVT_MENU, self.OnViewExhaustRefNodes, id=ID_VIEWEXHAUSTREFNODES)

        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_OPENFILE)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)

        
        self.SetMenuBar(menuBar)
        self.__set_properties() 
        self.__do_layout() 

    def OnViewSubmeshTexture(self, event=None):
        self.truckOgreWin.setSubmeshMode(0)

    def OnViewSubmeshGroups(self, event=None):
        self.truckOgreWin.setSubmeshMode(1)

    def OnViewSubmeshOptions(self, event=None):
        self.truckOgreWin.setSubmeshMode(2)

    def OnViewSubmeshs(self, event=None):
        self.truckOgreWin.showSubmeshs(self.viewsubmeshs.IsChecked())

    
    
    
    
    def OnViewExhaustRefNodes(self, event=None):
        self.truckOgreWin.showExhaustRefNodes(self.viewexhaustrefnodes.IsChecked())

    def OnViewExhaustNodes(self, event=None):
        self.truckOgreWin.showExhaustNodes(self.viewexhaustnodes.IsChecked())

    def OnViewHookNodes(self, event=None):
        self.truckOgreWin.showHookNodes(self.viewhooknodes.IsChecked())

    def OnViewContactNodes(self, event=None):
        self.truckOgreWin.showContactNodes(self.viewcontactnodes.IsChecked())

    def OnViewFrictionNodes(self, event=None):
        self.truckOgreWin.showFrictionNodes(self.viewfrictionnodes.IsChecked())

    def OnViewLoadNodes(self, event=None):
        self.truckOgreWin.showLoadNodes(self.viewloadnodes.IsChecked())

    def OnViewNormalNodes(self, event=None):
        self.truckOgreWin.showNormalNodes(self.viewnormalnodes.IsChecked())

    def OnViewAllNodes(self, event=None):
        value = self.viewallnodes.IsChecked()

        self.viewexhaustrefnodes.Check(value)
        self.OnViewExhaustRefNodes()

        self.viewexhaustnodes.Check(value)
        self.OnViewExhaustNodes()

        self.viewhooknodes.Check(value)
        self.OnViewHookNodes()
        
        self.viewcontactnodes.Check(value)
        self.OnViewContactNodes()

        self.viewfrictionnodes.Check(value)
        self.OnViewFrictionNodes()
        
        self.viewloadnodes.Check(value)
        self.OnViewLoadNodes()
        
        self.viewnormalnodes.Check(value)
        self.OnViewNormalNodes()
        
    def OnViewAllBeams(self, event=None):
        value = self.viewallbeams.IsChecked()
        
        self.viewnormalbeams.Check(value)
        self.OnViewNormalBeams()

        self.viewinvisiblebeams.Check(value)
        self.OnViewInvisibleBeams()
        
        self.viewropebeams.Check(value)
        self.OnViewRopeBeams()

    def OnViewNormalBeams(self, event=None):
        self.truckOgreWin.showNormalBeams(self.viewnormalbeams.IsChecked())

    def OnViewRopeBeams(self, event=None):
        self.truckOgreWin.showRopeBeams(self.viewropebeams.IsChecked())
        
    def OnViewInvisibleBeams(self, event=None):
        self.truckOgreWin.showInvisibleBeams(self.viewinvisiblebeams.IsChecked())
        
    def OnFileOpen(self, event=None):
        default = ""
        if self.rordir:
            default = self.rordir + "\\data\\trucks"
        print default
        dialog = wx.FileDialog(self, "Open Terrain", default, "", "Trucks or Loads (*.truck, *.load)|*.truck;*.load", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            self.fileopenmenu.Enable(False)
            filename = dialog.GetPath()
            print filename
            self.truckOgreWin.LoadTruck(filename)
            
    def onUpdateRender(self, event=None): 
        getOgreManager().RenderAll()
        pass

    def OnTimer(self, event):
        txt = "%0.2f FPS" % (self.truckOgreWin.renderWindow.getStatistics().lastFPS)
        self.statusbar.SetStatusText(txt, 2)
        
    def OnExit(self, event):
        self.Close(True)
        sys.exit(0)
        
    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "RoREditor version 0.0.3\n"
                              "Authors: Thomas Fischer",
                              "About Me", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()          

    def __set_properties(self): 
        self.SetTitle("RoR Truck Editor version 0.0.1") 
        self.truckOgreWin.SetMinSize((640,480)) 

    def __do_layout(self): 
        sizer_main = wx.BoxSizer(wx.HORIZONTAL) 

        sizer_left = wx.BoxSizer(wx.VERTICAL) 
        sizer_left.Add(self.truckOgreWin, 2, wx.EXPAND, 0) 
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

    
def startApp():
    MainApp = wx.PySimpleApp(0) 
    wx.InitAllImageHandlers() #you may or may not need this 
    myFrame = MainFrame(None, -1, "") 

    MainApp.SetTopWindow(myFrame) 
    myFrame.Show() 

    MainApp.MainLoop() 