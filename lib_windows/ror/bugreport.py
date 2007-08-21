import wx, os, os.path

from ror.logger import log
from ror.settingsManager import getSettingsManager

BUGREPORT_FILENAME = "hwinfo.txt"
ATTACHEDLOGFILES = ['editorlog.log', 'Ogre.log', 'ogre.cfg', 'editor.ini']

class BugReportFrame(wx.Frame): 
    def __init__(self, *args, **kwds): 
        kwds["style"] = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)

        self.panel = wx.Panel(self, wx.ID_ANY)
        desc = """Please describe the Bug below:
some tips:
* if you give us an email in the text (or a forum member name), we can answer you, otherwise not.
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
        txt += self.getLogs(ATTACHEDLOGFILES)
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
    
    def getLogs(self, files):
        txt = ""
        for f in files:
            try:
                txt += "==|==|== %s\n" % f
                if os.path.isfile(f):
                    txt += self.readFile(f)
                else:
                    txt += "file %s not found!" % f
            except Exception, e:
                txt += "ERROR: %s\n" % str(e)
                pass
        return txt
    
    def getHWInfos(self):
        
        try:
            import sysinfo
        except:
            dlg = wx.MessageDialog(self, "You must install pywin32 first.\nYou can find the setup in INSTALLDIR\\tools\\3rdparty\\pywin32-setup.exe (This means you must install it by hand!)\nPlease note that you must restart this program after the pywin installation.", "Error", wx.OK | wx.ICON_INFORMATION)
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
            txt += "Motherboard Vendor: %s\n" % hw.motherboard.vendor
        except:
            pass
        try:
            txt += "CPU: %s\n" % hw.cpu.product
        except:
            pass
        try:
            txt += "CPU Vendor: %s\n" % hw.cpu.vendor
        except:
            pass
        try:
            txt += "CPU Speed: %s\n" % hw.cpu.frequency
        except:
            pass
        try:
            txt += "Video memory: %.2f MB\n" % (float(hw.video_board.memory) / 1024 / 1024)
        except:
            pass
        try:
            txt += "HW Memory: %.2f MB\n" % (float(hw.memory.size) / 1024)
        except:
            pass
        try:
            txt += "GFX card: %s\n" % hw.video_board.product
        except:
            pass
        try:
            txt += "Resolution: %s@%d\n" % (hw.video_board.resolution, int(hw.video_board.width))
        except:
            pass
        try:
            txt += "Sound card: %s\n" % hw.sound_board.product
        except:
            pass
 
        return txt
        
    def LoadHWFile(self):
        if os.path.isfile(BUGREPORT_FILENAME):
            self.TextCtrl.LoadFile(BUGREPORT_FILENAME)

    def onSubmit(self, event=None):
        import base64
        import socket
        
        #combine files
        self.TextCtrl.SaveFile(BUGREPORT_FILENAME)
        hwinfos = self.readFile(BUGREPORT_FILENAME)

        self.TextCtrlOwn.SaveFile(BUGREPORT_FILENAME)
        owninfos = self.readFile(BUGREPORT_FILENAME)
        
        if owninfos.strip() == "":
            dlg = wx.MessageDialog(self, "You must provide an error description!", "Error", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        txt = owninfos + "\r\n" + hwinfos

        bugreport = base64.b64encode(txt)
        txt = "action=bugreport&bugreport=%s" % bugreport
        msg = """POST /index.php HTTP/1.0\r
Host: repository.rigsofrods.com\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: %d\r

%s""" % (len(txt), txt)
        
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('repository.rigsofrods.com', 80))
        #print "sending: %s" % msg
        s.send(msg)
        data = s.recv(9046)
        s.close()
        if data.find("successfully submitted") >= 0:
            dlg = wx.MessageDialog(self, "Bugreport successfully submitted! Thanks for reporting!", "successfull", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()   
        else:
            dlg = wx.MessageDialog(self, "Erro while submitting Bugreport! Please use the Forums to report the bug!", "error", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        #print 'Received', repr(data)
        self.Close()
        return
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.connect(('repository.rigsofrods.com', 443))
        #ssl_sock = socket.ssl(s)
        #print repr(ssl_sock.server())
        #print repr(ssl_sock.issuer())

        # Set a simple HTTP request -- use httplib in actual code.
        #ssl_sock.write(msg)

        # Read a chunk of data.  Will not necessarily
        # read all the data returned by the server.
        #print ssl_sock.read()

        # Note that you need to close the underlying socket, not the SSL object.
        #del ssl_sock
        #s.close()

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
