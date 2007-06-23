import wx, os, os.path

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
        self.filename = "readme.txt"
        self.LoadHelp()

    def generateSsysinfo(self):
        import platform
        txt = ""
        txt += ", ".join(platform.uname()) + "\n"
        txt += ", ".join(platform.architecture()) + "\n"
        txt += ", ".join(platform.platform()) + "\n"
        txt += ", ".join(platform.version()) + "\n"
        txt += ", ".join(platform.python_build()) + "\n"
        txt += ", ".join(platform.python_version()) + "\n"

        
    def LoadHelp(self):
        if os.path.isfile(self.filename):
            self.TextCtrl.LoadFile(self.filename)

    def onSubmit(self, event=None):
        self.Close()

    def onExit(self, event=None):
        self.Close()

    def __do_layout(self): 
        sizer_main = wx.BoxSizer(wx.VERTICAL) 
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL) 
        sizer_2.Add(self.TextCtrl, -1, wx.EXPAND, 0) 
        sizer_main.Add(sizer_2, -1, wx.EXPAND, 0) 
        sizer_main.Add(self.btnExit, 0, wx.EXPAND, 0) 

        self.SetAutoLayout(True) 
        self.SetSizer(sizer_main) 
        sizer_main.Fit(self) 
        sizer_main.SetSizeHints(self) 
        self.Layout() 

def showBugReportFrame():
    myFrame = BugReportFrame(None, wx.ID_ANY, "BugReport") 
    myFrame.Show() 
