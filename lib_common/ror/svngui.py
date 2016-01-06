#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorcommon import *
from subprocess import Popen

from ror.logger import log
from ror.settingsManager import rorSettings

# these functions are deprecated

"""
import svn

import wx, os, os.path

class svnUpdate(): 
    def __init__(self, restartApp=True):
        self.pr = wx.ProgressDialog("Updating ...", "Updating ...", style = wx.PD_SMOOTH | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME)
        self.pr.Show()
        self.changes = 0
        self.restartApp = restartApp
        svn.svnupdate(self.notify)
        self.showfinished()
        self.pr.Hide()
        del self.pr
        
    def restart(self):
        path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "updaterestart.py"))
        log().info("restarting ...")
        p = Popen(path, shell = True)
        sys.exit(0)
        
    def showfinished(self):
        if self.changes == 2:
            dlg = wx.MessageDialog(self.pr, "No Update available!", "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.changes > 2:
            if self.restartApp:
                dlg = wx.MessageDialog(self.pr, "Update finished!\nThe Application now restarts itself!", "Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.restart()
            else:
                dlg = wx.MessageDialog(self.pr, "Update finished!", "Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

        
    def notify(self, event_dict):
        self.changes += 1
        msg = str(event_dict['action']) + ", " + os.path.basename(event_dict['path'])
        #self.pr.Update(self.changes % 100, msg)
        self.pr.Pulse(msg)
        
"""