import sys, os, os.path

from wxogre.OgreManager import *
from ror.RoROgreWindow import *

from ror.logger import log
from ror.settingsManager import getSettingsManager

from ror.rorcommon import *
from RoRTerrainOgreWindow import *
from RoRObjectPreviewOgreWindow import *
from RoRTerrainSelectedObjectOgreWindow import *
from RoRTerrainSelectedObjectTopOgreWindow import *

# GUI Tools:
from GUIObjectTree import *
from MainFrame_Tools import *
    
import wx
import wx.grid
import wx.html
import wx.aui

import cStringIO

ID_OpenTerrain = wx.NewId()
ID_SaveTerrain = wx.NewId()
ID_SaveTerrainAs = wx.NewId()
ID_AddObject = wx.NewId()
ID_DeleteSelection = wx.NewId()
ID_CopySelection = wx.NewId()
ID_PasteSelection = wx.NewId()
ID_UndoAction = wx.NewId()
ID_RedoAction = wx.NewId()
ID_FindObject = wx.NewId()
ID_Quit = wx.NewId()

ID_ViewHelp = wx.NewId()

ID_CreateOgre = wx.NewId()

ID_CreatePerspective = wx.NewId()
ID_CopyPerspective = wx.NewId()

ID_Settings = wx.NewId()
ID_About = wx.NewId()
ID_FirstPerspective = ID_CreatePerspective+1000

DATADIR     = "data"
TRUCKDIR    = os.path.join(DATADIR, "trucks")
TERRAINDIR  = os.path.join(DATADIR, "terrains")
OBJECTDIR   = os.path.join(DATADIR, "objects")

class MainFrame(wx.Frame):
    
    def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
                                            wx.SUNKEN_BORDER |
                                            wx.CLIP_CHILDREN):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        
        # tell FrameManager to manage this frame        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self._perspectives = []
        self.n = 0
        self.x = 0
        
        self.SetIcon(wx.Icon('ror.ico',wx.BITMAP_TYPE_ICO))

        # create menu
        mb = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(ID_OpenTerrain, "Open Terrain")
        file_menu.Append(wx.ID_EXIT, "Exit")

        view_menu = wx.Menu()
        view_menu.Append(ID_CreateOgre, "Create OgreWindow")
        
        self.managerInit()
        options_menu = wx.Menu()
        options_menu.Append(ID_Settings, "GUI Settings Pane")

        self._perspectives_menu = wx.Menu()
        self._perspectives_menu.Append(ID_CreatePerspective, "Create Perspective")
        self._perspectives_menu.Append(ID_CopyPerspective, "Copy Perspective Data To Clipboard")
        self._perspectives_menu.AppendSeparator()
        self._perspectives_menu.Append(ID_FirstPerspective+0, "Default Startup")
        self._perspectives_menu.Append(ID_FirstPerspective+1, "All Panes")

        help_menu = wx.Menu()
        help_menu.Append(ID_About, "About...")
        help_menu.Append(ID_ViewHelp, "View Help")
        
        mb.Append(file_menu, "File")
        mb.Append(view_menu, "View")
        mb.Append(self._perspectives_menu, "Perspectives")
        mb.Append(options_menu, "Options")
        mb.Append(help_menu, "Help")
        
        self.SetMenuBar(mb)

        self.statusbar = self.CreateStatusBar(5, 0, wx.ID_ANY, "mainstatusbar")
        self.statusbar.SetStatusWidths([-1, 200, 130, 250, 80])

        # min size for the frame itself isn't completely done.
        # see the end up FrameManager::Update() for the test
        # code. For now, just hard code a frame minimum size
        self.SetMinSize(wx.Size(600, 400))
        try:
            import ror.svn
            self.SetTitle("Rigs of Rods Terrain Editor revision %d" % ror.svn.getRevision())
        except:
            self.SetTitle("Rigs of Rods Terrain Editor")       
        
        # create some toolbars
        tb1 = wx.ToolBar(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
        tb1.SetToolBitmapSize(wx.Size(16,16))
        tb1.AddLabelTool(ID_OpenTerrain, "Open Terrain", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        tb1.AddLabelTool(ID_SaveTerrain, "Save Terrain", wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE))
        tb1.EnableTool(ID_SaveTerrain, False)
        tb1.AddLabelTool(ID_SaveTerrainAs, "Save Terrain as", wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE_AS))
        tb1.EnableTool(ID_SaveTerrainAs, False)
        tb1.AddSeparator()
        tb1.AddLabelTool(ID_AddObject, "Add Something", wx.ArtProvider_GetBitmap(wx.ART_NEW))
        tb1.EnableTool(ID_AddObject, False)
        tb1.AddLabelTool(ID_DeleteSelection, "Delete Selection", wx.ArtProvider_GetBitmap(wx.ART_DELETE))
        tb1.EnableTool(ID_DeleteSelection, False)
        tb1.AddSeparator()        
        tb1.AddLabelTool(ID_CopySelection, "Copy Selection", wx.ArtProvider_GetBitmap(wx.ART_COPY))
        tb1.EnableTool(ID_CopySelection, False)
        tb1.AddLabelTool(ID_PasteSelection, "Paste Selection", wx.ArtProvider_GetBitmap(wx.ART_PASTE))
        tb1.EnableTool(ID_PasteSelection, False)
        tb1.AddSeparator()        
        tb1.AddLabelTool(ID_UndoAction, "Undo last Action", wx.ArtProvider_GetBitmap(wx.ART_UNDO))
        tb1.EnableTool(ID_UndoAction, False)
        tb1.AddLabelTool(ID_RedoAction, "Redo last Undo", wx.ArtProvider_GetBitmap(wx.ART_REDO))
        tb1.EnableTool(ID_RedoAction, False)
        tb1.AddSeparator()        
        tb1.AddLabelTool(ID_FindObject, "Find Object", wx.ArtProvider_GetBitmap(wx.ART_FIND))
        tb1.EnableTool(ID_FindObject, False)
        tb1.AddSeparator()        
        tb1.AddLabelTool(ID_Quit, "Quit", wx.ArtProvider_GetBitmap(wx.ART_QUIT))
        tb1.Realize()
        self.tb1 = tb1
        
        
        self.rordir = getSettingsManager().getSetting("RigsOfRods", "BasePath")
        
        
        # add a bunch of panes
        self.objectPreviewWindow = ObjectPreviewOgreWindow(self, wx.ID_ANY, rordir=self.rordir)
        
        self._mgr.AddPane(self.objectPreviewWindow, wx.aui.AuiPaneInfo().
                          Name("ogretest1").
                          Caption("Object Preview").
                          Left().
                          MinSize(wx.Size(200,200)).
                          CloseButton(True).
                          MaximizeButton(False))

        self._mgr.AddPane(HelpPanel(self, self), wx.aui.AuiPaneInfo().
                          Name("help").
                          Caption("Help").
                          Dockable(False).
                          Float().
                          Fixed().
                          Hide().
                          CloseButton(True).
                          MaximizeButton(True))

        self._mgr.AddPane(SettingsPanel(self, self), wx.aui.AuiPaneInfo().
                          Name("settings").
                          Caption("Dock Manager Settings").
                          Dockable(False).
                          Float().
                          Fixed().
                          Hide().
                          CloseButton(True).
                          MaximizeButton(True))

        self._mgr.AddPane(RoRObjectTreeCtrl(self, self), wx.aui.AuiPaneInfo().
                          Caption("Object Tree").
                          MinSize(wx.Size(200,100)).
                          Left().
                          CloseButton(True).
                          MaximizeButton(True))
                          
        #  create the center pane
        #Timer creation  (for rendering)
        self.ogreTimer = wx.Timer() 
        self.ogreTimer.SetOwner(self)
        self.Bind(wx.EVT_TIMER, self.onUpdateRender, self.ogreTimer)
        self.ogreTimer.Start(25)
        
        # create timer for gui update
        self.guitimer = wx.Timer() 
        self.guitimer.SetOwner(self) #Sets the timer to notify self: binding the timer event is not enough 
        self.Bind(wx.EVT_TIMER, self.OnGUITimer, self.guitimer)
        self.guitimer.Start(200)

        
        
        self.terrainOgreWin = RoRTerrainOgreWindow(self, wx.ID_ANY, rordir=self.rordir)
        self._mgr.AddPane(self.terrainOgreWin, wx.aui.AuiPaneInfo().Name("ogre_content").
                          CenterPane())
                                
        # add the toolbars to the manager
                        
        self._mgr.AddPane(tb1, wx.aui.AuiPaneInfo().
                          Name("tb1").
                          Caption("General Toolbar").
                          ToolbarPane().Top().
                          LeftDockable(False).
                          RightDockable(False)
                          )

        # make some default perspectives
        perspective_all = self._mgr.SavePerspective()
        
        # all - perspective
        all_panes = self._mgr.GetAllPanes()       
        #for ii in xrange(len(all_panes)):
        #    if not all_panes[ii].IsToolbar():
        #        all_panes[ii].Hide()                
        self._mgr.GetPane("ogre_content").Show()
        perspective_default = self._mgr.SavePerspective()

        self._perspectives.append(perspective_default)
        self._perspectives.append(perspective_all)


        # "commit" all changes made to FrameManager   
        self._mgr.Update()

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Bind(wx.EVT_MENU, self.OnOpenTerrain, id=ID_OpenTerrain)
        self.Bind(wx.EVT_MENU, self.OnSaveTerrain, id=ID_SaveTerrain)
        self.Bind(wx.EVT_MENU, self.OnSaveTerrainAs, id=ID_SaveTerrainAs)
        self.Bind(wx.EVT_MENU, self.OnViewHelp, id=ID_ViewHelp)
        
        self.Bind(wx.EVT_MENU, self.OnCreateOgre, id=ID_CreateOgre)
        
        self.Bind(wx.EVT_MENU, self.OnCreatePerspective, id=ID_CreatePerspective)
        self.Bind(wx.EVT_MENU, self.OnCopyPerspective, id=ID_CopyPerspective)

        self.Bind(wx.EVT_MENU, self.OnSettings, id=ID_Settings)
        
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_Quit)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_About)
    
        self.Bind(wx.EVT_MENU_RANGE, self.OnRestorePerspective, id=ID_FirstPerspective,
                  id2=ID_FirstPerspective+1000)
    
    def OnViewHelp(self, event=None):
        # show the settings pane, and float it
        floating_pane = self._mgr.GetPane("help").Float().Show()

        if floating_pane.floating_pos == wx.DefaultPosition:
            floating_pane.FloatingPosition(self.GetStartPosition())

        self._mgr.Update()

    
    def addStuff(self, filename):
        try:
            onlyfilename, extension = os.path.splitext(os.path.basename(filename))
            if extension.lower() in ['.truck', '.load']:
                if not self.terrainOgreWin.addTruckToTerrain(truckFilename=filename):
                    dlg = wx.MessageDialog(self, "You must select a position on the ground first!", "error", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
            elif extension.lower() in ['.odef']:
                if not self.terrainOgreWin.addObjectToTerrain(odefFilename=filename):
                    dlg = wx.MessageDialog(self, "You must select a position on the ground first!", "error", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
        except:
            pass
    
    def previewObject(self, filename):
        try:
            self.objectPreviewWindow.loadFile(filename)
        except:
            pass
    
    def updateObjPosRot(self, event=None):
        self.statusbar.SetStatusText(self.terrainOgreWin.currentStatusMsg, 1)
        if self.terrainOgreWin.terrain is None:
            return
        if self.terrainOgreWin.selectedEntry is None:
            self.statusbar.SetStatusText("Nothing selected", 2)
            return
        entry = self.terrainOgreWin.selectedEntry
        #comment = self.terrainOgreWin.getCommentsForObject(n.getName()).lstrip('/')
        #if comment.strip() != "":
        #    txt = "%s / %s" % (n.getName(), comment)
        #else:
        txt = "%s %s" % (entry.data.name, " ".join(entry.data.additionaloptions))
        self.statusbar.SetStatusText(txt, 2)
        
        posx, posy, posz, rotx, roty, rotz = self.terrainOgreWin.getSelectionPositionRotation()
        txt = "%0.2f, %0.2f, %0.2f / %0.2f, %0.2f, %0.2f" % (posx, posy, posz, rotx, roty, rotz)
        self.statusbar.SetStatusText(txt, 3)

    def OnGUITimer(self, event):
        #fill labels with some information, all windows have the same FPS!
        txt = "%0.2f FPS" % (self.terrainOgreWin.renderWindow.getStatistics().lastFPS)
        self.statusbar.SetStatusText(txt, 4)
        self.updateObjPosRot()
        
    def onUpdateRender(self, event=None): 
        getOgreManager().RenderAll()
        pass

    def OnOpenTerrain(self, event=None):
        default = ""
        if self.rordir:
            default = os.path.join(self.rordir, TERRAINDIR)
        dialog = wx.FileDialog(self, "Open Terrain", default, "", "Terrain Files (*.terrn)|*.terrn", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            filename = dialog.GetPath()
            self.terrainOgreWin.LoadTerrain(filename)
            self.tb1.EnableTool(ID_AddObject, True)
            self.tb1.EnableTool(ID_DeleteSelection, True)
            self.tb1.EnableTool(ID_CopySelection, True)
            self.tb1.EnableTool(ID_PasteSelection, True)
            self.tb1.EnableTool(ID_UndoAction, True)
            self.tb1.EnableTool(ID_RedoAction, True)
            self.tb1.EnableTool(ID_FindObject, True)
            self.tb1.EnableTool(ID_SaveTerrain, True)
            self.tb1.EnableTool(ID_SaveTerrainAs, True)


    def OnSaveTerrain(self, event=None):
        if not self.terrainOgreWin.SaveTerrain():
            dlg = wx.MessageDialog(self, "error while saving, see console!\n","error", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def OnSaveTerrainAs(self, event=None):
        default = ""
        if self.rordir:
            default = os.path.join(self.rordir, TERRAINDIR)
        dialog = wx.FileDialog(self, "Save Terrain as", default, "", "Terrain Files (*.terrn)|*.terrn", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            if not self.terrainOgreWin.SaveTerrain(dialog.GetPath()):
                dlg = wx.MessageDialog(self, "error while saving as another file, see console!\n","error", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

    def OnClose(self, event):
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()

    def OnExit(self, event):
        self.Close()

    def OnAbout(self, event):
        ShowOnAbout()

    def GetDockArt(self):
        return self._mgr.GetArtProvider()

    def DoUpdate(self):
        self._mgr.Update()

    def OnEraseBackground(self, event):
        event.Skip()

    def OnSize(self, event):
        event.Skip()

    def OnSettings(self, event):
        # show the settings pane, and float it
        floating_pane = self._mgr.GetPane("settings").Float().Show()

        if floating_pane.floating_pos == wx.DefaultPosition:
            floating_pane.FloatingPosition(self.GetStartPosition())

        self._mgr.Update()

    def managerInit(self):
        flags = self._mgr.GetFlags()
        # based on default settings!
        flags |= wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE
        flags &= ~wx.aui.AUI_MGR_TRANSPARENT_DRAG
        self._mgr.SetFlags(flags)

    def OnCreatePerspective(self, event):
        dlg = wx.TextEntryDialog(self, "Enter a name for the new perspective:", "AUI Test")
        
        dlg.SetValue(("Perspective %d")%(len(self._perspectives)+1))
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        if len(self._perspectives) == 0:
            self._perspectives_menu.AppendSeparator()
        
        self._perspectives_menu.Append(ID_FirstPerspective + len(self._perspectives), dlg.GetValue())
        self._perspectives.append(self._mgr.SavePerspective())


    def OnCopyPerspective(self, event):
        s = self._mgr.SavePerspective()
        
        if wx.TheClipboard.Open():
        
            wx.TheClipboard.SetData(wx.TextDataObject(s))
            wx.TheClipboard.Close()
        
    def OnRestorePerspective(self, event):
        self._mgr.LoadPerspective(self._perspectives[event.GetId() - ID_FirstPerspective])


    def GetStartPosition(self):
        self.x = self.x + 20
        x = self.x
        pt = self.ClientToScreen(wx.Point(0, 0))
        
        return wx.Point(pt.x + x, pt.y + x)

    def OnCreateOgre(self, event):
        self._mgr.AddPane(self.CreateOgreCtrl(), wx.aui.AuiPaneInfo().
                          Caption("Ogre Window").
                          Float().FloatingPosition(self.GetStartPosition()).
                          CloseButton(True).MaximizeButton(False))
        self._mgr.Update()
    
    def CreateOgreCtrl(self):
        return RoRTerrainOgreWindow(self, wx.ID_ANY, scenemanager=self.terrainOgreWin.sceneManager)

def startApp():
    MainApp = wx.PySimpleApp(0) 
    wx.InitAllImageHandlers() #you may or may not need this 
    myFrame = MainFrame(None, -1, "") 

    MainApp.SetTopWindow(myFrame) 
    
    myFrame.SetSize((800, 600))
    myFrame.SetFocus()            
    myFrame.Show() 

    MainApp.MainLoop() 