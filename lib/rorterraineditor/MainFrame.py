#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *

from ror.logger import log
from ror.settingsManager import getSettingsManager

from ror.rorcommon import *
from RoRTerrainOgreWindow import *
from RoRTerrainSelectedObjectOgreWindow import *
from RoRTerrainSelectedObjectTopOgreWindow import *

ID_ABOUT    = 101
ID_OPENFILE = 102
ID_SAVEFILE = 103
ID_VIEWOBJ  = 104
ID_OGRESET  = 105
ID_SHOWHELP = 106
ID_ADDTRUCK = 107
ID_ADDMESH  = 108
ID_CHECKUPDATE = 109
ID_SAVEFILEAS = 110
ID_TERRAINCOLLISION = 111
ID_EXIT     = 199

DATADIR     = "data"
TRUCKDIR    = os.path.join(DATADIR, "trucks")
TERRAINDIR  = os.path.join(DATADIR, "terrains")
OBJECTDIR   = os.path.join(DATADIR, "objects")

       
class MainFrame(wx.Frame): 
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

        #viewsplitter
        self.viewsplitter = wx.SplitterWindow(self.splitterright, wx.ID_ANY)
        self.viewsplitterup = wx.Panel(self.viewsplitter, wx.ID_ANY)
        self.viewsplitterdown = wx.Panel(self.viewsplitter, wx.ID_ANY)
        self.splitter.SetSashGravity(0.5)
        self.splitter.SetSashPosition(100)
        self.splitter.SetMinimumPaneSize(200)
        
        self.rordir = getSettingsManager().getSetting("RigsOfRods", "BasePath")

        #ogre windows
        self.terrainOgreWin = RoRTerrainOgreWindow(self.splitterleft, wx.ID_ANY, rordir=self.rordir)
        self.sharedOgreWin = RoRTerrainSelectedObjectOgreWindow(self.viewsplitterup, wx.ID_ANY, self.terrainOgreWin)            
        self.sharedOgreWin2 = RoRTerrainSelectedObjectTopOgreWindow(self.viewsplitterdown, wx.ID_ANY, self.terrainOgreWin)            
        
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
        self.statusbar = self.CreateStatusBar(4, 0, wx.ID_ANY, "mainstatusbar")
        self.statusbar.SetStatusWidths([-1, 300, 300, 80])
        #self.statusbar.SetStatusText("", 1)

        #create toolbar
        #self.toolbar  = wx.ToolBar(self, wx.ID_ANY, style = wx.TB_HORZ_TEXT)
        #self.SetToolBar(self.toolbar )
        #bitmap = wx.Bitmap("media/gui/OpenFile.gif", wx.BITMAP_TYPE_GIF)
        #self.toolbar.DoAddTool(0, "Open Terrain", bitmap, bitmap, wx.ITEM_NORMAL, "Open Terrain", "Opens a new terrain for edit")
        
        #create general settings
        #self.GeneralSettingsPanel = wx.Panel(self, wx.ID_ANY)
        self.terrainName = wx.StaticText(self, wx.ID_ANY, "Terrain Name:") 
        self.terrainNamectrl = wx.TextCtrl(self, wx.ID_ANY)
        self.Bind(wx.EVT_TEXT, self.OnChangeTerrainNameChange, self.terrainNamectrl)

        self.waterLevelText = wx.StaticText(self, wx.ID_ANY, "Water Level: 0") 
        self.waterlevelctrl = wx.Slider(self, wx.ID_ANY)
        self.waterlevelctrl.max =  300
        self.Bind(wx.EVT_SCROLL, self.OnChangeWaterLevel, self.waterlevelctrl)

        #self.CurrEntName = wx.StaticText(self, wx.ID_ANY, "\n\n\n") 
        #self.PosText = wx.StaticText(self, wx.ID_ANY, "Position: x,y,z") 
        #self.terrPosX = wx.TextCtrl(self, wx.ID_ANY)
        #self.terrPosY = wx.TextCtrl(self, wx.ID_ANY)
        #self.terrPosZ = wx.TextCtrl(self, wx.ID_ANY)
        #self.RotText = wx.StaticText(self, wx.ID_ANY, "Rotation: x,y,z") 
        #self.terrRotX = wx.TextCtrl(self, wx.ID_ANY)
        #self.terrRotY = wx.TextCtrl(self, wx.ID_ANY)
        #self.terrRotZ = wx.TextCtrl(self, wx.ID_ANY)
        #self.Bind(wx.EVT_TEXT, self.OnChangeObjPosRot, self.terrPosX)
        #self.Bind(wx.EVT_TEXT, self.OnChangeObjPosRot, self.terrPosY)
        #self.Bind(wx.EVT_TEXT, self.OnChangeObjPosRot, self.terrPosZ)
        #self.Bind(wx.EVT_TEXT, self.OnChangeObjPosRot, self.terrRotX)
        #self.Bind(wx.EVT_TEXT, self.OnChangeObjPosRot, self.terrRotY)
        #self.Bind(wx.EVT_TEXT, self.OnChangeObjPosRot, self.terrRotZ)

        self.btnResetRotation = wx.Button(self, wx.ID_ANY, "Reset Rotation")
        self.Bind(wx.EVT_BUTTON, self.OnBtnResetRotation, self.btnResetRotation)
        self.btnStickToGround = wx.ToggleButton(self, wx.ID_ANY, "Stick to Ground")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnBtnStickToGroundChange, self.btnStickToGround)
        
        
        #menu creation
        menuBar = wx.MenuBar()
        file_menu = wx.Menu()
        self.fileopenmenu = file_menu.Append(ID_OPENFILE, "&Open", "Open Terrain")
        self.filesavemenu = file_menu.Append(ID_SAVEFILE, "&Save", "Save Terrain")
        self.filesaveasmenu = file_menu.Append(ID_SAVEFILEAS, "&Save as", "Save Terrain as")
      
        self.filesavemenu.Enable(False)
        self.filesaveasmenu.Enable(False)
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXIT, "E&xit", "Terminate the program")
        menuBar.Append(file_menu, "&File");
        
        view_menu = wx.Menu()
        self.mnuterraincollision = view_menu.AppendCheckItem(ID_TERRAINCOLLISION, "Camera collides with Terrain", "")
        self.mnuterraincollision.Check(True)
        view_menu.AppendSeparator()
        self.viewObjectDetails = view_menu.AppendCheckItem(ID_VIEWOBJ, "&View Objects", "Display object details")
        self.viewObjectDetails.Check(False)
        view_menu.AppendSeparator()
        view_menu.Append(ID_OGRESET, "&Ogre Settings", "Change Ogre Display Settings")
        menuBar.Append(view_menu, "&View");
        
        add_menu = wx.Menu()
        add_menu.Append(ID_ADDTRUCK, "&Truck/Load", "add a Truck or a Load to the terrain")
        self.Bind(wx.EVT_MENU, self.OnAddTruck, id=ID_ADDTRUCK)
        add_menu.Append(ID_ADDMESH, "&Object", "add a static Object to the terrain")
        self.Bind(wx.EVT_MENU, self.OnAddMesh, id=ID_ADDMESH)
        menuBar.Append(add_menu, "&Add");

        help_menu = wx.Menu()
        help_menu.Append(ID_SHOWHELP, "Show &Help", "view the documentation")
        help_menu.AppendSeparator()
        help_menu.Append(ID_ABOUT, "&About", "More information about this program")
        menuBar.Append(help_menu, "&Help");
        
        #bindings
        self.SetMenuBar(menuBar)
        self.__set_properties() 
        self.__do_layout() 
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_OPENFILE)
        self.Bind(wx.EVT_MENU, self.OnFileSave, id=ID_SAVEFILE)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=ID_SAVEFILEAS)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onViewObjectDetails, id=ID_VIEWOBJ)
        self.Bind(wx.EVT_MENU, self.OnChangeOgreSettings, id=ID_OGRESET)
        self.Bind(wx.EVT_MENU, self.OnCameraTerrainCollision, id=ID_TERRAINCOLLISION)

    def OnAbout(self, event=None):
        ShowOnAbout()
        
    def OnCheckUpdate(self, event=None):
        pass
        
    def OnCameraTerrainCollision(self, event=None):
        self.terrainOgreWin.CameraLandCollision(self.mnuterraincollision.IsChecked())
        
    def OnHelp(self, event=None):
        import HelpFrame
        HelpFrame.showHelpFrame()
        
    def OnAddTruck(self, event=None):
        default = ""
        if self.rordir:
            default = os.path.join(self.rordir, TRUCKDIR)
        print default
        dialog = wx.FileDialog(self, "Add Truck", default, "", "Truck and Load Files (*.truck,*.load)|*.truck;*.load", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            if not self.terrainOgreWin.addTruckToTerrain(dialog.GetPath()):
                dlg = wx.MessageDialog(self, "You must select a position on the ground first!", "error", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()          

    def OnAddMesh(self, event=None):
        default = ""
        if self.rordir:
            default = os.path.join(self.rordir, OBJECTDIR)
        print default
        dialog = wx.FileDialog(self, "Add Object", default, "", "RoR Object Definitions (*.odef)|*.odef", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            print dialog.GetPath()
            if not self.terrainOgreWin.addMeshToTerrain(dialog.GetPath()):
                dlg = wx.MessageDialog(self, "You must select a position on the ground first!", "error", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()          
                

    def OnBtnResetRotation(self, event=None):
        self.terrainOgreWin.ObjectResetRotation()

    def OnBtnStickToGroundChange(self, event=None):
        self.terrainOgreWin.stickCurrentObjectToGround = self.btnStickToGround.GetValue()
        
    def updateObjPosRot(self, event=None):
        if self.terrainOgreWin.mSelected is None:
            self.statusbar.SetStatusText("", 1)
            return
        n = self.terrainOgreWin.mSelected.getParentNode()        
        comment = self.terrainOgreWin.getCommentsForObject(n.getName()).lstrip('/')
        if comment.strip() != "":
            txt = "%s / %s" % (n.getName(), comment)
        else:
            txt = "%s" % n.getName()
        self.statusbar.SetStatusText(txt, 1)

        posx, posy, posz, rotx, roty, rotz = self.terrainOgreWin.getSelectionPositionRotation()
        txt = "%0.2f, %0.2f, %0.2f / %0.2f, %0.2f, %0.2f" % (posx, posy, posz, rotx, roty, rotz)
        self.statusbar.SetStatusText(txt, 2)

        #pos = n.getPosition()
        #self.terrPosX.SetValue(str(round(pos.x,2)))
        #self.terrPosY.SetValue(str(round(pos.y,2)))
        #self.terrPosZ.SetValue(str(round(pos.z,2)))
        #rot = n.getOrientation()
        #self.terrRotX.SetValue(str(round(ogre.Radian(rot.getPitch(False)+90).valueDegrees(),2)))
        #self.terrRotY.SetValue(str(round(ogre.Radian(rot.getYaw(False)).valueDegrees(),2)))
        #self.terrRotZ.SetValue(str(round(ogre.Radian(rot.getRoll(False)).valueDegrees(),2)))
        
    #def OnChangeObjPosRot(self, event=None):
    #    pass
        
    def OnChangeTerrainNameChange(self, event=None):
        self.terrainOgreWin.TerrainName = self.terrainNamectrl.GetValue()
        
    def OnChangeWaterLevel(self, event=None):
        self.terrainOgreWin.WaterHeight = self.waterlevelctrl.GetValue()
        self.waterLevelText.Label = "Water Level: %0.1f" % (self.terrainOgreWin.WaterHeight)
        self.terrainOgreWin.updateWaterPlane()
    
    def OnChangeOgreSettings(self, event):
        getOgreManager().getRoot().showConfigDialog()
        dlg = wx.MessageDialog(self, "You must restart the program for the settings to get active", "Ogre Settings", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()          
        
    def OnFileSave(self, event):
        if self.terrainOgreWin.SaveTerrnFile():
            dlg = wx.MessageDialog(self, "saved","info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()           
        else:
            dlg = wx.MessageDialog(self, "error while saving, see console!\n","error", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def OnFileSaveAs(self, event):
        default = ""
        if self.rordir:
            default = os.path.join(self.rordir, TERRAINDIR)
        dialog = wx.FileDialog(self, "Save Terrain as", default, "", "Terrain Files (*.terrn)|*.terrn", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            if self.terrainOgreWin.SaveTerrnFile(dialog.GetPath()):
                dlg = wx.MessageDialog(self, "saved","info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()           
            else:
                dlg = wx.MessageDialog(self, "error while saving as another file, see console!\n","error", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()


    def OnFileOpen(self, event=None):
        default = ""
        if self.rordir:
            default = os.path.join(self.rordir, TERRAINDIR)
        #print default
        dialog = wx.FileDialog(self, "Open Terrain", default, "", "Terrain Files (*.terrn)|*.terrn", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            self.fileopenmenu.Enable(False)
            self.filesavemenu.Enable(True)
            self.filesaveasmenu.Enable(True)
            filename = dialog.GetPath()
            print filename

            #del self.terrainOgreWin
            #del self.sharedOgreWin
            #del self.sharedOgreWin2
            # getOgreManager().restart()
            #self.terrainOgreWin = RoRTerrainOgreWindow(self.splitterleft, wx.ID_ANY)            
            #self.sharedOgreWin = RoRTerrainSelectedObjectOgreWindow(self.viewsplitterup, wx.ID_ANY, self.terrainOgreWin)            
            #self.sharedOgreWin2 = RoRTerrainSelectedObjectTopOgreWindow(self.viewsplitterdown, wx.ID_ANY, self.terrainOgreWin)            
         
            self.terrainOgreWin.LoadTerrain(filename)
            
            #update some controls if finished loading
            self.waterlevelctrl.SetValue(self.terrainOgreWin.WaterHeight)
            self.waterLevelText.Label = "Water Level: %0.1f" % (self.terrainOgreWin.WaterHeight)
            self.terrainNamectrl.SetValue(self.terrainOgreWin.TerrainName)

    
    def onViewObjectDetails(self, event=None): 
        # split/unsplit
        if self.viewObjectDetails.IsChecked():
            self.viewObjectDetails.Check(True)
            self.splitter.SetSashPosition(600, True)
            self.splitter.SplitVertically(self.splitterleft, self.splitterright)
        else:
            self.viewObjectDetails.Check(False)
            self.splitter.Unsplit()
        
    def onUpdateRender(self, event=None): 
        getOgreManager().RenderAll()
        pass

    def OnTimer(self, event):
        #fill labels with some information, all windows have the same FPS!
        txt = "%0.2f FPS" % (self.terrainOgreWin.renderWindow.getStatistics().lastFPS)
        self.statusbar.SetStatusText(txt, 3)
        self.updateObjPosRot()
        
    def OnExit(self, event):
        self.Close(True)
        del self
        sys.exit(0)
        
    def __set_properties(self): 
        try:
            import ror.svn
            self.SetTitle("RoR Terrain Editor revision %d" % ror.svn.getRevision())
        except:
            self.SetTitle("RoR Terrain Editor")
            
        self.terrainOgreWin.SetMinSize((640,480)) 

    def __do_layout(self): 
        sizer_main = wx.BoxSizer(wx.HORIZONTAL) 

        sizer_left = wx.BoxSizer(wx.VERTICAL) 
        sizer_left.Add(self.terrainOgreWin, 2, wx.EXPAND, 0) 
        self.splitterleft.SetSizer(sizer_left)

        
        #construct view boxes
        sizerviewup = wx.BoxSizer(wx.VERTICAL) 
        #sizerviewup.Add(self.rotatingLabel, 0, wx.EXPAND, 0) 
        sizerviewup.Add(self.sharedOgreWin, 1, wx.EXPAND, 0) 
        self.viewsplitterup.SetSizer(sizerviewup)

        sizerviewdown = wx.BoxSizer(wx.VERTICAL) 
        #sizerviewdown.Add(self.topLabel, 0, wx.EXPAND, 0) 
        sizerviewdown.Add(self.sharedOgreWin2, 1, wx.EXPAND, 0) 
        self.viewsplitterdown.SetSizer(sizerviewdown)
        self.viewsplitter.SplitHorizontally(self.viewsplitterup, self.viewsplitterdown)

               
        sizer_right = wx.BoxSizer(wx.VERTICAL) 
        sizer_right.Add(self.viewsplitter, 1, wx.EXPAND, 0) 
        self.splitterright.SetSizer(sizer_right)


        self.splitter.SplitVertically(self.splitterleft, self.splitterright)
        self.splitter.Unsplit()
        self.splitter.SetSashPosition(600)

        
        sizer_main.Add(self.splitter, 1, wx.EXPAND, 0)


        sizer_settings = wx.BoxSizer(wx.VERTICAL) 
        sizer_settings.Add(self.waterLevelText, 0, wx.EXPAND, 0) 
        sizer_settings.Add(self.waterlevelctrl, 0, wx.EXPAND, 0) 
        sizer_settings.Add(self.terrainName, 0, wx.EXPAND, 0) 
        sizer_settings.Add(self.terrainNamectrl, 0, wx.EXPAND, 0) 
        
        #sizer_settings.Add(self.CurrEntName, 0, wx.EXPAND, 0) 
        #sizer_settings.Add(self.PosText, 0, wx.EXPAND, 0) 
        #sizer_terrPos = wx.BoxSizer(wx.HORIZONTAL) 
        #sizer_terrPos.Add(self.terrPosX, 0, wx.EXPAND, 0) 
        #sizer_terrPos.Add(self.terrPosY, 0, wx.EXPAND, 0) 
        #sizer_terrPos.Add(self.terrPosZ, 0, wx.EXPAND, 0) 
        #sizer_settings.Add(sizer_terrPos, 0, wx.EXPAND, 0) 
        
        #sizer_settings.Add(self.RotText, 0, wx.EXPAND, 0) 
        #sizer_terrRot = wx.BoxSizer(wx.HORIZONTAL) 
        #sizer_terrRot.Add(self.terrRotX, 0, wx.EXPAND, 0) 
        #sizer_terrRot.Add(self.terrRotY, 0, wx.EXPAND, 0) 
        #sizer_terrRot.Add(self.terrRotZ, 0, wx.EXPAND, 0) 
        #sizer_settings.Add(sizer_terrRot, 0, wx.EXPAND, 0) 
        
        sizer_settings.Add(self.btnResetRotation, 0, wx.EXPAND, 0) 
        sizer_settings.Add(self.btnStickToGround, 0, wx.EXPAND, 0) 
        
        
        sizer_main.Add(sizer_settings, 0, wx.EXPAND, 0)
        
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