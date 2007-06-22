import wx

def ShowOnAbout(event = None):
    dlg = wx.MessageDialog(self, "RoR Toolkit version 0.0.3\n"
                          "Authors: Thomas Fischer",
                          "About Me", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()          
