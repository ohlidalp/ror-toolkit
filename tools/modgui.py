#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from ror.logger import log
from ror.settingsManager import getSettingsManager
import ror.modgui
import wx

def main():
    log().info("modgui started")
    import wx
    app = wx.PySimpleApp(0) 
    wx.InitAllImageHandlers() #you may or may not need this    
    
    # check for valid RoR Directory!
    import ror.settingsManager
    rorpath = ror.settingsManager.getSettingsManager().getSetting("RigsOfRods", "BasePath")
    if not os.path.isfile(os.path.join(rorpath,"RoR.exe")):
        import ror.starter
        ror.starter.startApp()
        return

    if len(sys.argv) == 1:
        log().error("missing arguments")
        return
    mode = sys.argv[1]
    if mode in ["uninstall"]:
        frame_1 = ror.modgui.ModGUI(None, -1, "")
        app.SetTopWindow(frame_1)
        frame_1.Show()
        app.MainLoop()

    elif mode in ['installrepo']:
        if len(sys.argv) != 3:
            return
        targetfile = sys.argv[2]    
        import ror.modtool
        result = ror.modtool.ModTool().work(mode, targetfile, False, False)
        if result == False or result is None:
            msg = "Installation failed! :( Please have a look at the file editorlog.log"
        else:
            msg = "Installation successfull! Mods installed:\n %s" % ", ".join(result)
        dlg = wx.MessageDialog(None, msg, "Info", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    else:
        log().error("function %s not implemented in gui version!" % mode)
        return





if __name__=="__main__":
    main()
