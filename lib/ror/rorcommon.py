import wx

def ShowOnAbout(event = None):
    rev = ""
    try:
        import ror.svn
        rev = str(ror.svn.getRevision())
    except:
        pass

    dlg = wx.MessageDialog(None, "RoR Toolkit revision %s\nAuthors: Aperion, Thomas" % rev,
                          "About This", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()          
