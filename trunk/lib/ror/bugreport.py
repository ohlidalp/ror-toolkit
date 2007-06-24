import wx, os, os.path
import rorsettings

BUGREPORT_FILENAME = "hwinfo.txt"

class BugReportFrame(wx.Frame): 
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)

        self.panel = wx.Panel(self, wx.ID_ANY)
        desc = """Please describe the Bug below:
some tips:
* if you give us an email in the text, we can answer you, otherwise not.
* it is good to take screenshots of errors, glitches and so on.
  you can insert imageshack.us or equivalent URLs below."""
        self.lblText1 = wx.StaticText(self.panel, wx.ID_ANY, desc)
        self.TextCtrlOwn = wx.TextCtrl(self.panel, wx.ID_ANY, style=wx.TE_RICH2|wx.TE_AUTO_URL|wx.TE_MULTILINE,size=wx.Size(400,200))
        desc2 = """The gathered system information, that will be send along the description:
* you may want to correct it and/or remove details you dont want to share with us."""
        self.lblText2 = wx.StaticText(self.panel, wx.ID_ANY, desc2)
        self.TextCtrl = wx.TextCtrl(self.panel, wx.ID_ANY, style=wx.TE_RICH2|wx.TE_AUTO_URL|wx.TE_MULTILINE,size=wx.Size(400,200))
        self.btnSubmit = wx.Button(self.panel, wx.ID_ANY, "Submit")
        self.btnCancel = wx.Button(self.panel, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.onSubmit, self.btnSubmit)
        self.Bind(wx.EVT_BUTTON, self.onExit, self.btnCancel)
        self.__do_layout()
        self.generateSysinfo()
        self.LoadHWFile()

    def generateSysinfo(self):
        import platform
        txt = "==========================\n"
        txt += "Platform/Software Information:\n"
        txt += "==========================\n"
        txt += "Platform: %s, %s\n"  % (platform.platform(), platform.version())
        txt += "Architecture: " + ", ".join(platform.architecture()) + "\n"
        txt += "Python version:" + "".join(platform.python_version()) + "\n"
        txt += "Python build: " + ", ".join(platform.python_build()) + "\n"
        hwinfo = self.getHWInfos()
        if hwinfo == "":
            return
        txt += hwinfo
        txt += self.getLogs()
        
        txt += "\n==========================\n"
        txt += "==========================\n"

        self.writeFile(BUGREPORT_FILENAME, txt)
        
    def writeFile(self, filename, content):
        outfile = open(filename, 'w')
        outfile.write(content)
        outfile.close()
    
    def readFile(self, filename):
        outfile = open(filename, 'r')
        t = outfile.read()
        outfile.close()
        return t
    # not working
    # def installPyWin(self):
        # dlg = wx.MessageDialog(self, "Python Windows extensions are required for this to work. I will try install them now in the Registry.\n", "Error", wx.OK | wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()
        # import  pywin32_postinstall
        # pywin32_postinstall.install()
    
    def getLogs(self):
        txt = ""
        try:
            txt += "==========================\n"
            txt += "RoR Ogre.log following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile(os.path.join(ogrelogfn,"Ogre.log"))
        except:
            txt += "RoR Ogre.log ERROR\n"
            pass
        try:
            txt += "==========================\n"
            txt += "RoR ogre.cfg following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile(os.path.join(ogrelogfn,"ogre.cfg"))
        except:
            txt += "RoR ogre.cfg ERROR\n"
            pass

        try:
            txt += "==========================\n"
            txt += "RoR plugins.cfg following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile(os.path.join(ogrelogfn,"plugins.cfg"))
        except:
            txt += "RoR plugins.cfg ERROR\n"
            pass
            
        try:
            txt += "==========================\n"
            txt += "RoR.cfg following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile(os.path.join(ogrelogfn,"RoR.cfg"))
        except:
            txt += "RoR.cfg ERROR\n"
            pass

        try:
            txt += "==========================\n"
            txt += "RoR resources.cfg following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile(os.path.join(ogrelogfn,"resources.cfg"))
        except:
            txt += "RoR resources.cfg ERROR\n"
            pass

        try:
            txt += "==========================\n"
            txt += "RoRToolkit Ogre.log following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile("Ogre.log")
        except:
            txt += "RoRToolkit Ogre.log ERROR\n"
            pass
            
        try:
            txt += "==========================\n"
            txt += "RoRToolkit ogre.cfg following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile("ogre.cfg")
        except:
            txt += "RoRToolkit ogre.cfg ERROR\n"
            pass

        try:
            txt += "==========================\n"
            txt += "RoRToolkit plugins.cfg following\n"
            txt += "==========================\n"
            ogrelogfn = rorsettings.getSettings().getRoRDir()
            txt += self.readFile("plugins.cfg")
        except:
            txt += "RoRToolkit plugins.cfg ERROR\n"
            pass
        return txt
    
    def getHWInfos(self):
        
        try:
            import sysinfo
        except:
            dlg = wx.MessageDialog(self, "You must install pywin32 first.\nYou can find the setup in INSTALLDIR/tools/pywin32-setup.exe\nPLease note that you must restart this program after the pywin installation.", "Error", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()    
            self.Close()
            return ""
            
        txt = "==========================\n"
        txt += "Hardware Information:\n"
        txt += "==========================\n"
        try:
            dlg = wx.MessageDialog(self, "This program will now try to figure out some Hardware Information. That can take a minute or so.", "Notice", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()    
        
            hw = sysinfo.hardware()
        except:
            pass

        try:
            txt += "Motherboard: %s\n" % hw.motherboard.product
        except:
            pass
        try:
            txt +=  "Motherboard Vendor: %s\n" % hw.motherboard.vendor
        except:
            pass
        try:
            txt +=  "CPU: %s\n" % hw.cpu.product
        except:
            pass
        try:
            txt +=  "Motherboard Vendor: %s\n" % hw.cpu.vendor
        except:
            pass
        try:
            txt +=  "CPU Speed: %s\n" % hw.cpu.frequency
        except:
            pass
        try:
            txt +=  "Video memory: %.2f MB\n" % (float(hw.video_board.memory) / 1024 / 1024)
        except:
            pass
        try:
            txt +=  "HW Memory: %.2f MB\n" % (float(hw.memory.size) / 1024)
        except:
            pass
        try:
            txt +=  "GFX card: %s\n" % hw.video_board.product
        except:
            pass
        try:
            txt +=  "Resolution: %s@%d\n" % (hw.video_board.resolution, int(hw.video_board.width))
        except:
            pass
        try:
            txt +=  "Sound card: %s\n" % hw.sound_board.product
        except:
            pass
 
        return txt
        
    def LoadHWFile(self):
        if os.path.isfile(BUGREPORT_FILENAME):
            self.TextCtrl.LoadFile(BUGREPORT_FILENAME)

    def onSubmit(self, event=None):
        self.Close()

    def onExit(self, event=None):
        self.Close()

    def __do_layout(self): 
        sizer_panel = wx.BoxSizer(wx.VERTICAL) 
        sizer_panel.Add(self.lblText1, 0, wx.EXPAND, 0) 
        sizer_panel.Add(self.TextCtrlOwn, -1, wx.EXPAND, 0) 
        sizer_panel.Add(self.lblText2, 0, wx.EXPAND, 0) 
        sizer_panel.Add(self.TextCtrl, -1, wx.EXPAND, 0) 
        sizer_panel.Add(self.btnSubmit, 0, wx.EXPAND, 0) 
        sizer_panel.Add(self.btnCancel, 0, wx.EXPAND, 0) 
        self.panel.SetSizer(sizer_panel)

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(self.panel, 0, wx.EXPAND, 0) 
  
        self.SetAutoLayout(True) 
        self.SetSizer(sizer_main) 
        sizer_main.Fit(self) 
        sizer_main.SetSizeHints(self) 
        self.Layout() 

def showBugReportFrame():
    myFrame = BugReportFrame(None, wx.ID_ANY, "BugReport") 
    myFrame.Show() 
