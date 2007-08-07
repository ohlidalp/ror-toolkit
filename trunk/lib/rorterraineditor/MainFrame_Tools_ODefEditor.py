import sys, os, os.path

from ror.logger import log
from ror.settingsManager import getSettingsManager

import wx
import wx.aui

import cStringIO

ID_ChangeMainMeshTrans = wx.NewId()
ID_ChangeMainMeshVisibility = wx.NewId()
ID_ChangeNormalBoxesVisibility = wx.NewId()
ID_ChangeVirtualBoxesVisibility = wx.NewId()

class OdefViewPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition,
                          wx.DefaultSize)
        self._frame = frame
        self.parent = parent
        
        vert = wx.BoxSizer(wx.VERTICAL)

        s1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ObjTransparencySlider = wx.SpinCtrl(self, ID_ChangeMainMeshTrans, "", wx.DefaultPosition, wx.Size(50,20), min=0, max=100, initial=60)
        s1.Add((1, 1), 1, wx.EXPAND)
        s1.Add(wx.StaticText(self, -1, "Object Transparency:"))
        s1.Add(self.ObjTransparencySlider)
        s1.Add((1, 1), 1, wx.EXPAND)
        vert.Add(s1, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

        self.chkMeshVisible = wx.CheckBox(self, ID_ChangeMainMeshVisibility, "Display Object", wx.DefaultPosition, wx.Size(50,20))
        vert.Add(self.chkMeshVisible, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

        self.chkBoxNormalVisible = wx.CheckBox(self, ID_ChangeNormalBoxesVisibility, "Display Collision Boxes", wx.DefaultPosition, wx.Size(50,20))
        vert.Add(self.chkBoxNormalVisible, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

        self.chkBoxVirtualVisible = wx.CheckBox(self, ID_ChangeVirtualBoxesVisibility, "Display Virtual Boxes", wx.DefaultPosition, wx.Size(50,20))
        self.chkBoxVirtualVisible.SetValue(True)
        vert.Add(self.chkBoxVirtualVisible, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)
        
        
        self.Bind(wx.EVT_SPINCTRL, self.OnMainMeshTransChange, id=ID_ChangeMainMeshTrans)
        self.Bind(wx.EVT_CHECKBOX, self.OnMainMeshVisibilityChange, id=ID_ChangeMainMeshVisibility)
        self.Bind(wx.EVT_CHECKBOX, self.OnNormalBoxesVisibilityChange, id=ID_ChangeNormalBoxesVisibility)
        self.Bind(wx.EVT_CHECKBOX, self.OnVirtualBoxesVisibilityChange, id=ID_ChangeVirtualBoxesVisibility)

        self.SetSizer(vert)
        self.GetSizer().SetSizeHints(self)
        self.resetControls()
    
    def resetControls(self):
        self.chkMeshVisible.SetValue(True)
        self.chkBoxNormalVisible.SetValue(True)
        self.ObjTransparencySlider.SetValue(60)
        
    
    def OnMainMeshTransChange(self, event):
        self.parent.odefEditorOgreWin.setMainMeshTrans(event.GetInt())
        
    def OnMainMeshVisibilityChange(self, event):
        self.parent.odefEditorOgreWin.setMainMeshVisible(event.IsChecked())

    def OnNormalBoxesVisibilityChange(self, event):
        self.parent.odefEditorOgreWin.setBoxesVisibility("normal", event.IsChecked())

    def OnVirtualBoxesVisibilityChange(self, event):
        self.parent.odefEditorOgreWin.setBoxesVisibility("virtual", event.IsChecked())
        
    def loadReadme(self):
        if os.path.isfile(HELPFILENAME):
            try:
                f = open(HELPFILENAME,'r')
                content = f.read()
                f.close()
                return content
            except Exception, err:
                log().error(str(err))
                return None
        else:
            log().error("TerrainEditor Readme not found: %s" % HELPFILENAME)
            return None
