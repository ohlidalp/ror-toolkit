#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz

import sys, os, os.path, base64

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from logger import log
from settingsManager import *
import modtool

import wx, wx.html

class ModGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        

        self.mainPanel = wx.Panel(self, wx.ID_ANY)

        self.listbox = wx.ListBox(self.mainPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [], wx.LB_MULTIPLE)
        self.chkDryRun = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Dry run (only print out what would be done)")
        self.btnNext = wx.Button(self.mainPanel, wx.ID_ANY, "Uninstall selected")
        self.btnCancel = wx.Button(self.mainPanel, wx.ID_ANY, "Exit")

        self.Bind(wx.EVT_BUTTON, self.onUninstall , self.btnNext)
        self.Bind(wx.EVT_BUTTON, self.onCancel , self.btnCancel)

        self.updateData()
        
        if len(self.data) == 0:
            dlg = wx.MessageDialog(self, "No Mods found to uninstall!\n Uninstaller will now exit.", "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.Close()
            return


        self.__set_properties()
        self.__do_layout()

    def updateData(self):
        self.data = modtool.ModTool().getRoRMods(True)
        self.listbox.Set(self.data)
        
        
    def onCancel(self, event=None):
        self.Close()
    
    def onUninstall(self, event=None):
        if len(self.listbox.GetSelections()) == 0:
            dlg = wx.MessageDialog(self, "Please select a Mod to uninstall!", "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        counter = 0
        dryrun = self.chkDryRun.GetValue()
        log().info("starting uninstallation using the GUI")
        for number in self.listbox.GetSelections():
            targetname = self.data[number]
            log().info("trying to uninstall mod %s ..." % targetname)
            modtool.ModTool().work("uninstall", targetname, True, dryrun)
            counter += 1
        if not dryrun:
            dlg = wx.MessageDialog(self, "%d Mods uninstalled!" % counter, "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        log().info("finished uninstallation using the GUI.")
        self.updateData()
        
    def __set_properties(self):
        self.SetTitle("Mod Uninstaller")
        self.SetSize((400, 400))
   
    def __do_layout(self):       
        sizer_panel = wx.BoxSizer(wx.VERTICAL)
        sizer_panel.Add(self.listbox, 1, wx.EXPAND, 0)

        sizer_panel.Add(self.chkDryRun, 0, wx.EXPAND, 0)
        
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        sizer_buttons.Add(self.btnNext, 1, wx.EXPAND, 0)
        sizer_buttons.Add(self.btnCancel, 1, wx.EXPAND, 0)
        
        sizer_panel.Add(sizer_buttons, 0, wx.EXPAND, 0)
        
        self.mainPanel.SetSizer(sizer_panel)

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(self.mainPanel, 1, wx.EXPAND, 0)
        
        self.SetAutoLayout(True) 
        self.SetSizer(sizer_main) 
        sizer_main.Fit(self) 
        sizer_main.SetSizeHints(self) 
