#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorsettings import *
from ror.rorcommon import *
from subprocess import Popen
import wx

class SettingsDialog(wx.Frame): 
    rordir = None
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds) 

        self.panel = wx.Panel(self, wx.ID_ANY)
                             
        self.lblRoRDir = wx.StaticText(self.panel, wx.ID_ANY, "Please select Rigs of Rods Directory!")
        self.btnSelectRoRDir = wx.Button(self.panel, wx.ID_ANY, "Select RoR Directory")
        self.Bind(wx.EVT_BUTTON, self.OnSelectRoRDir, self.btnSelectRoRDir)

        self.btnStartRoR = wx.Button(self.panel, wx.ID_ANY, "Start RoR")
        self.Bind(wx.EVT_BUTTON, self.OnStartRoR, self.btnStartRoR)
        
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
        
        self.rordir = getSettings().getRoRDir()
        #print self.rordir
        if not self.rordir is None:
            if self.checkRoRDir(self.rordir):
                self.btnStartRoR.Enable(True)
                self.btnStartTruckEditor.Enable(True)
                self.btnStartTerrainEditor.Enable(True)
                self.lblRoRDir.SetLabel(self.rordir)
            else:
                self.rordir = ""
                self.btnStartRoR.Enable(False)
                self.btnStartTruckEditor.Enable(False)
                self.btnStartTerrainEditor.Enable(False)
                self.lblRoRDir.SetLabel("Please select Rigs of Rods Directory!")

        else:
            self.btnStartRoR.Enable(False)
            self.btnStartTruckEditor.Enable(False)
            self.btnStartTerrainEditor.Enable(False)
        self.__set_properties() 
        self.__do_layout() 

    def OnUpdate(self, event=None):
        import svn
        svn.run()

    def OnStartRoR(self, event=None):
        #escape spaces!
        path = newpath.replace(" ", "\ ")
        p = Popen(os.path.join(path, "RoR.exe"), shell=True, cwd=self.rordir)
        #sts = os.waitpid(p.pid, 0)

    def OnTruckEditor(self, event=None):
        import rortruckeditor.MainFrame
        try:
            app = rortruckeditor.MainFrame.startApp()
            del app
        except:
            pass
    
    def OnBugReport(self, event=None):
        import ror.bugreport
        #try:
        ror.bugreport.showBugReportFrame()
        #except:
        #    pass

    def OnTerrainEditor(self, event=None):
        import rorterraineditor.MainFrame
        try:
            app = rorterraineditor.MainFrame.startApp()
            del app
        except:
            pass

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
            getSettings().setRoRDir(newpath)
            self.btnStartRoR.Enable(True)
            self.btnStartTruckEditor.Enable(True)
            self.btnStartTerrainEditor.Enable(True)
            
    def OnExit(self, event=None):
        self.Close()        

    def __set_properties(self): 
        self.SetTitle("RoR Toolkit starter") 

    def __do_layout(self): 
        
        sizer_panel = wx.BoxSizer(wx.VERTICAL)
        sizer_panel.Add(self.lblRoRDir, 0, wx.EXPAND, 0) 
        sizer_panel.Add(self.btnSelectRoRDir, 0, wx.EXPAND, 0) 
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
