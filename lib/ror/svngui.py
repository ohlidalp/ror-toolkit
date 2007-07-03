#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorcommon import *
from subprocess import Popen

from ror.logger import log
from ror.settingsManager import getSettingsManager

import svn

import wx, os, os.path

class svnUpdate(): 
    def __init__(self):
        self.pr = wx.ProgressDialog("Updating ...", "Updating ...", style = wx.PD_SMOOTH | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME)
        self.pr.Show()
        self.changes = 0
        svn.svnupdate(self.notify)
        self.showfinished()
        self.pr.Hide()
        del self.pr
        
    def showfinished(self):
        if self.changes == 2:
            dlg = wx.MessageDialog(self.pr, "No Update available!", "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.changes > 2:
            dlg = wx.MessageDialog(self.pr, "Update finished!\nPlease restart the Application!", "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
    def notify(self, event_dict):
        self.changes += 1
        msg = str(event_dict['action']) + ", " + event_dict['path']
        #self.pr.Update(self.changes % 100, msg)
        self.pr.Pulse(msg)
        