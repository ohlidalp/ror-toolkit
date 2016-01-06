import sys, os, os.path

from ror.logger import log
from ror.settingsManager import rorSettings
from ShapedControls import ShapedWindow
import wx
import wx.aui

import cStringIO

ID_ChangeMainMeshTrans = wx.NewId()
ID_ChangeMainMeshVisibility = wx.NewId()
ID_ChangeNormalBoxesVisibility = wx.NewId()
ID_ChangeVirtualBoxesVisibility = wx.NewId()

class OdefViewPanel(ShapedWindow):
	def __init__(self, parent, title, **kwargs):
		ShapedWindow.__init__(self, parent, title, ** kwargs)
	   
		self.parent = parent
		self.rordir = rorSettings().rorFolder
		self.title = title
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 3))
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		self.mainLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))

		r += 2
		self.transpa = wx.StaticText(self, -1, "Transparency", size=wx.Size(265, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		self.transpa.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		grid.Add(self.transpa, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))

		r += 1 
		self.ObjTransparencySlider = wx.SpinCtrl(self, ID_ChangeMainMeshTrans, "", wx.DefaultPosition, wx.Size(265, 20), min=0, max=100, initial=60)
		grid.Add(self.ObjTransparencySlider,
				pos=wx.GBPosition(r, c),
				span=wx.GBSpan(1, 4))
		
		r += 1
		c = 1

		self.chkMeshVisible = wx.CheckBox(self, ID_ChangeMainMeshVisibility, "Display Object", wx.DefaultPosition, wx.Size(265, 20))
		grid.Add(self.chkMeshVisible,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 4))
		
		r += 1
		self.chkBoxNormalVisible = wx.CheckBox(self, ID_ChangeNormalBoxesVisibility, "Display Collision Boxes", wx.DefaultPosition, wx.Size(265, 20))
		grid.Add(self.chkBoxNormalVisible,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 4))
		
		r += 1
		self.chkBoxVirtualVisible = wx.CheckBox(self, ID_ChangeVirtualBoxesVisibility, "Display Virtual Boxes", wx.DefaultPosition, wx.Size(265, 20))
		self.chkBoxVirtualVisible.SetValue(True)
		grid.Add(self.chkBoxVirtualVisible,
				pos=wx.GBPosition(r, c),
		 		span=wx.GBSpan(1, 4))

		self.Bind(wx.EVT_SPINCTRL, self.OnMainMeshTransChange, id=ID_ChangeMainMeshTrans)
		self.Bind(wx.EVT_CHECKBOX, self.OnMainMeshVisibilityChange, id=ID_ChangeMainMeshVisibility)
		self.Bind(wx.EVT_CHECKBOX, self.OnNormalBoxesVisibilityChange, id=ID_ChangeNormalBoxesVisibility)
		self.Bind(wx.EVT_CHECKBOX, self.OnVirtualBoxesVisibilityChange, id=ID_ChangeVirtualBoxesVisibility)

		self.SetSizerAndFit(grid)
		self.resetControls()
		self.updateSkin()
	
	def resetControls(self):
		self.chkMeshVisible.SetValue(True)
		self.chkBoxNormalVisible.SetValue(True)
		self.ObjTransparencySlider.SetValue(60)
		
	
	def OnMainMeshTransChange(self, event):
		self.parent.odefEditorOgreWin.setMainMeshTrans(event.GetInt())
		
	def OnMainMeshVisibilityChange(self, event):
		self.parent.odefEditorOgreWin.setMainMeshVisible(event.IsChecked())

	def OnNormalBoxesVisibilityChange(self, event):
		self.parent.odefEditorOgreWin.setBoxesVisibility("collision", event.IsChecked())

	def OnVirtualBoxesVisibilityChange(self, event):
		self.parent.odefEditorOgreWin.setBoxesVisibility("virtual", event.IsChecked())
		
	def loadReadme(self):
		if os.path.isfile(HELPFILENAME):
			try:
				f = open(HELPFILENAME, 'r')
				content = f.read()
				f.close()
				return content
			except Exception, err:
				log().error(str(err))
				return None
		else:
			log().error("TerrainEditor Readme not found: %s" % HELPFILENAME)
			return None
