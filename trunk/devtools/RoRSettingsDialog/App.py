# -*- coding: iso-8859-1 -*-
import wx

provider = wx.SimpleHelpProvider()
wx.HelpProvider_Set(provider)

import MyDlg

class App(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.main = MyDlg.MyDlg(None,-1,'')
        self.main.ShowModal()
        return 0

def main():
    application = App(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
