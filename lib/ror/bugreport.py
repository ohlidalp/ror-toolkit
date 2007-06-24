import wx, os, os.path

BUGREPORT_FILENAME = "hwinfo.txt"

class BugReportFrame(wx.Frame): 
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds) 
        self.TextCtrl = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_RICH2|wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY,size=wx.Size(500,400))
        self.btnSubmit = wx.Button(self, wx.ID_ANY, "Submit")
        self.btnCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.onSubmit, self.btnSubmit)
        self.Bind(wx.EVT_BUTTON, self.onExit, self.btnCancel)
        self.__do_layout()
        self.generateSysinfo()
        self.LoadHWFile()

    def generateSysinfo(self):
        import platform
        txt = ""
        txt += "Platform: " + ", ".join(platform.uname()) + "\n"
        txt += "Architecture: " + ", ".join(platform.architecture()) + "\n"
        txt += "Platform: " + platform.platform() + "\n"
        txt += "Version: " + platform.version() + "\n"
        txt += "Python build: " + ", ".join(platform.python_build()) + "\n"
        txt += "Python version:" + ", ".join(platform.python_version()) + "\n"
        txt += self.getHWInfos()
        self.writeFile(BUGREPORT_FILENAME, txt)
        
    def writeFile(self, filename, content):
        outfile = open(filename, 'w')
        outfile.write(content)
        outfile.close()
    
    def getHWInfos(self):
        import sysinfo
        txt = ""
        try:
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
            txt +=  "Video memory: %.2fMB\n" % (float(hw.video_board.memory) / 1024 / 1024)
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
        sizer_main = wx.BoxSizer(wx.VERTICAL) 
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL) 
        sizer_2.Add(self.TextCtrl, -1, wx.EXPAND, 0) 
        sizer_main.Add(sizer_2, -1, wx.EXPAND, 0) 
        sizer_main.Add(self.btnSubmit, 0, wx.EXPAND, 0) 

        self.SetAutoLayout(True) 
        self.SetSizer(sizer_main) 
        sizer_main.Fit(self) 
        sizer_main.SetSizeHints(self) 
        self.Layout() 

def showBugReportFrame():
    myFrame = BugReportFrame(None, wx.ID_ANY, "BugReport") 
    myFrame.Show() 
