#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorcommon import *
from subprocess import Popen

from ror.logger import log
from ror.settingsManager import getSettingsManager

import wx, os, os.path

RENDERSYSTEMS = ['OpenGL', 'DirectX9']

DIRECTXLINE = "Plugin=RenderSystem_Direct3D9.dll"
OPENGLLINE = "Plugin=RenderSystem_GL.dll"
SPLASHIMAGE = "splash.bmp"


class ImagePanel(wx.Panel):
    """ class Panel1 creates a panel with an image on it, inherits wx.Panel """
    def __init__(self, parent, id, imageFile):
        wx.Panel.__init__(self, parent, id)
        try:
            jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            wx.StaticBitmap(self, wx.ID_ANY, jpg1, (0, 0), (jpg1.GetWidth(), jpg1.GetHeight()))
        except IOError:
            print "Image file %s not found" % imageFile
            raise SystemExit


class SettingsDialog(wx.Frame): 
    rordir = None
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds) 

        self.panel = wx.Panel(self, wx.ID_ANY)
        
        self.image = ImagePanel(self.panel, wx.ID_ANY, SPLASHIMAGE)
                             
        self.lblRoRDir = wx.StaticText(self.panel, wx.ID_ANY, "Please select Rigs of Rods Directory!", size = (20, 20), style = wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE)
        self.btnSelectRoRDir = wx.Button(self.panel, wx.ID_ANY, "Select RoR Directory")
        self.Bind(wx.EVT_BUTTON, self.OnSelectRoRDir, self.btnSelectRoRDir)

        self.btnStartRoR = wx.Button(self.panel, wx.ID_ANY, "Start RoR")
        self.Bind(wx.EVT_BUTTON, self.OnStartRoR, self.btnStartRoR)

        self.cbbRenderEngine = wx.ComboBox(self.panel, wx.ID_ANY, RENDERSYSTEMS[0], style=wx.CB_READONLY, choices=RENDERSYSTEMS)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectRenderer, self.cbbRenderEngine)
        
        self.btnStartTerrainEditor = wx.Button(self.panel, wx.ID_ANY, "Start Terrain Editor")
        self.Bind(wx.EVT_BUTTON, self.OnTerrainEditor, self.btnStartTerrainEditor)
        
        self.btnStartTruckEditor = wx.Button(self.panel, wx.ID_ANY, "Start Truck Editor")
        self.Bind(wx.EVT_BUTTON, self.OnTruckEditor, self.btnStartTruckEditor)

        self.btnBugReport = wx.Button(self.panel, wx.ID_ANY, "Report a Bug")
        self.Bind(wx.EVT_BUTTON, self.OnBugReport, self.btnBugReport)

        self.btnUpdate = wx.Button(self.panel, wx.ID_ANY, "Update")
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.btnUpdate)
        
        self.btnExit = wx.Button(self.panel, wx.ID_ANY, "Exit")
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.btnExit)
        
        self.rordir = getSettingsManager().getSetting("RigsOfRods", "BasePath")
        
        # this takes too long! threading it?!
        #if self.checkForUpdate():
        #    dlg = wx.MessageDialog(self, "Update Available!", "Info", wx.OK | wx.ICON_INFORMATION)
        #    dlg.ShowModal()
        #    dlg.Destroy()
            
        #print self.rordir
        if not self.rordir is None:
            if self.checkRoRDir(self.rordir):
                self.btnStartRoR.Enable(True)
                self.btnStartTruckEditor.Enable(True)
                self.btnStartTerrainEditor.Enable(True)
            else:
                self.rordir = ""
                self.btnStartRoR.Enable(False)
                self.btnStartTruckEditor.Enable(False)
                self.btnStartTerrainEditor.Enable(False)
        else:
            self.btnStartRoR.Enable(False)
            self.btnStartTruckEditor.Enable(False)
            self.btnStartTerrainEditor.Enable(False)
        self.displayRoRDir()
        self.__set_properties() 
        self.__do_layout() 
        
        self.renderSystem = RENDERSYSTEMS[0]

    def displayRoRDir(self):
        if self.rordir == "":
            self.lblRoRDir.SetLabel("Please select Rigs of Rods Directory!")
        else:
            self.lblRoRDir.SetLabel("Selected Rigs of Rods Directory: " + self.rordir)
        
    def OnSelectRenderer(self, id=None, func=None):
        self.renderSystem = self.cbbRenderEngine.GetCurrentSelection()
        self.updateRenderer()

    def updateRenderer(self):
        filename = os.path.join(os.getcwd(), "plugins.cfg")
        f=open(filename, 'r')
        content = f.readlines()
        f.close()
        log().info("selected rendersystem: %s" % RENDERSYSTEMS[self.renderSystem])
        for i in range(0, len(content)):
            if content[i].find(OPENGLLINE) >= 0:
                if self.renderSystem == 0:
                    content[i] = OPENGLLINE+"\n"
                else:
                    content[i] = "#"+OPENGLLINE+"\n"
            elif content[i].find(DIRECTXLINE) >= 0:
                if self.renderSystem == 1:
                    content[i] = DIRECTXLINE+"\n"
                else:
                    content[i] = "#"+DIRECTXLINE+"\n"

        f=open(filename, 'w')
        f.writelines(content)
        f.close()        
        
    def OnUpdate(self, event=None):
        import svngui
        gui = svngui.svnUpdate()
        del gui

    def checkForUpdate(self):
        import svn
        return svn.checkForUpdate()
        

    def OnStartRoR(self, event=None):
        try:
            path = os.path.join(self.rordir, "RoR.exe")
            log().info("starting RoR: %s" % path)
            p = Popen(path, shell = False, cwd = self.rordir)
            #sts = os.waitpid(p.pid, 0)
        except Exception, e:
            log().exception(str(e))

    def OnTruckEditor(self, event=None):
        try:
            import rortruckeditor.MainFrame
            self.Close()
            log().info("starting Truckeditor")
            app = rortruckeditor.MainFrame.startApp()
            del app
        except Exception, e:
            log().exception(str(e))
    
    def OnBugReport(self, event=None):
        try:
            log().info("starting bugreporter")
            import ror.bugreport
            ror.bugreport.showBugReportFrame()
        except Exception, e:
            log().exception(str(e))

    def OnTerrainEditor(self, event=None):
        try:
            import rorterraineditor.MainFrame
            log().info("starting Terraineditor")
            self.Close()
            app = rorterraineditor.MainFrame.startApp()
            del app
        except Exception, e:
            log().exception(str(e))

    def checkRoRDir(self, fn):
        # withoutspaces = (fn.find(" ") == -1)
        # if not withoutspaces:
            # dlg = wx.MessageDialog(self, "Your RoR installation directory contains spaces. Rename/move it to a directory with no spaces.\nFor example c:\\ror", "Error", wx.OK | wx.ICON_INFORMATION)
            # dlg.ShowModal()
            # dlg.Destroy()
            # return False
            
        exists = os.path.isfile(os.path.join(fn,"RoR.exe"))
        if not exists:
            dlg = wx.MessageDialog(self, "RoR.exe not found in the selected directory!\nPlease select a new directory!", "Error", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        return True
        
    def OnSelectRoRDir(self, event=None):
        dialog = wx.DirDialog(self, "Choose RoR Directory", "")
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            newpath = dialog.GetPath()
            if not self.checkRoRDir(newpath):
                return
               
            # no need to escape here!
            #newpath = newpath.replace(" ", "\ ")
            self.rordir = newpath
            self.lblRoRDir.SetLabel(newpath)
            getSettingsManager().setSetting("RigsOfRods", "BasePath", newpath)
            self.btnStartRoR.Enable(True)
            self.btnStartTruckEditor.Enable(True)
            self.btnStartTerrainEditor.Enable(True)
            
    def OnExit(self, event=None):
        self.Close()
        sys.exit(0)

    def __set_properties(self): 
        try:
            import ror.svn
            self.SetTitle("RoR Toolkit r%d" % ror.svn.getRevision())
        except:
            self.SetTitle("RoR Toolkit")

    def __do_layout(self): 
        
        sizer_panel = wx.BoxSizer(wx.VERTICAL)
        sizer_panel.Add(self.image, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.lblRoRDir, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.btnSelectRoRDir, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.cbbRenderEngine, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.btnStartRoR, 0, wx.EXPAND, 0) 
        sizer_panel.Add(self.btnStartTerrainEditor, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.btnStartTruckEditor, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.btnBugReport, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.btnUpdate, 0, wx.EXPAND, 0)
        sizer_panel.Add(self.btnExit, 0, wx.EXPAND, 0)
        self.panel.SetSizer(sizer_panel)

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(self.panel, 0, wx.EXPAND, 0)
        
        self.SetAutoLayout(True) 
        self.SetSizer(sizer_main) 
        sizer_main.Fit(self) 
        sizer_main.SetSizeHints(self) 
        self.Layout() 

def startApp():
    MainApp = wx.PySimpleApp(0) 
    wx.InitAllImageHandlers() #you may or may not need this 
    myFrame = SettingsDialog(None, -1, "") 

    MainApp.SetTopWindow(myFrame) 
    myFrame.Show()
    
    MainApp.MainLoop()
