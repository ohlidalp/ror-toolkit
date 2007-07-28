#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from ror.logger import log
from ror.settingsManager import getSettingsManager
import ror.modgui
import wx

def main():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = ror.modgui.ModGUI(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


if __name__=="__main__":
    main()
