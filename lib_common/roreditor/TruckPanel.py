import sys, os, os.path

from ror.logger import log
from ror.settingsManager import rorSettings

import wx
import wx.aui

import cStringIO

class TruckViewPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition,
						  wx.DefaultSize)
		self.parent = parent
		
		vert = wx.BoxSizer(wx.VERTICAL)

		s1 = wx.BoxSizer(wx.HORIZONTAL)
#		self.ObjTransparencySlider = wx.SpinCtrl(self, ID_ChangeMainMeshTrans, "", wx.DefaultPosition, wx.Size(50,20), min=0, max=100, initial=60)
#		s1.Add((1, 1), 1, wx.EXPAND)
#		s1.Add(wx.StaticText(self, -1, "Object Transparency:"))
#		s1.Add(self.ObjTransparencySlider)
#		s1.Add((1, 1), 1, wx.EXPAND)
#		vert.Add(s1, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkMeshVisible = wx.CheckBox(self, -1, "Display Object", wx.DefaultPosition, wx.Size(50, 20))
		self.chkMeshVisible.Bind(wx.EVT_CHECKBOX, self.OnMeshVisible)
		vert.Add(self.chkMeshVisible, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkshowExhaustRefNodes = wx.CheckBox(self, -1, "Display ExhaustRefNodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowExhaustRefNodes.Bind(wx.EVT_CHECKBOX, self.OnshowExhaustRefNodes)
		vert.Add(self.chkshowExhaustRefNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkshowExhaustNodes = wx.CheckBox(self, -1, "Display Exhaust Nodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowExhaustNodes.Bind(wx.EVT_CHECKBOX, self.OnshowExhaustNodes)
		vert.Add(self.chkshowExhaustNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)
		
		self.chkshowHookNodes = wx.CheckBox(self, -1, "Display Hook Nodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowHookNodes.Bind(wx.EVT_CHECKBOX, self.OnshowHookNodes)
		vert.Add(self.chkshowHookNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkshowFrictionNodes = wx.CheckBox(self, -1, "Display Friction Nodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowFrictionNodes.Bind(wx.EVT_CHECKBOX, self.OnshowFrictionNodes)
		vert.Add(self.chkshowFrictionNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkshowContactNodes = wx.CheckBox(self, -1, "Display Contact Nodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowContactNodes.Bind(wx.EVT_CHECKBOX, self.OnshowContactNodes)
		vert.Add(self.chkshowContactNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkshowLoadNodes = wx.CheckBox(self, -1, "Display Load Nodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowLoadNodes.Bind(wx.EVT_CHECKBOX, self.OnshowLoadNodes)
		vert.Add(self.chkshowLoadNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)
		
		self.chkshowNormalNodes = wx.CheckBox(self, -1, "Display Normal Nodes", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowNormalNodes.Bind(wx.EVT_CHECKBOX, self.OnshowNormalNodes)
		vert.Add(self.chkshowNormalNodes, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)	   

		self.chkshowNormalBeams = wx.CheckBox(self, -1, "Display Normal Beams", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowNormalBeams.Bind(wx.EVT_CHECKBOX, self.OnshowNormalBeams)
		vert.Add(self.chkshowNormalBeams, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)	

		self.chkshowInvisibleBeams = wx.CheckBox(self, -1, "Display Invisible Beams", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowInvisibleBeams.Bind(wx.EVT_CHECKBOX, self.OnshowInvisibleBeams)
		vert.Add(self.chkshowInvisibleBeams, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)  
		
		self.chkshowRopeBeams = wx.CheckBox(self, -1, "Display Rope Beams", wx.DefaultPosition, wx.Size(50, 20))
		self.chkshowRopeBeams.Bind(wx.EVT_CHECKBOX, self.OnshowRopeBeams)
		vert.Add(self.chkshowRopeBeams, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chkbeamVisible = wx.CheckBox(self, -1, "Show Beams", wx.DefaultPosition, wx.Size(50, 20))
		self.chkbeamVisible.Bind(wx.EVT_CHECKBOX, self.OnchkbeamVisible)
		vert.Add(self.chkbeamVisible, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

		self.chknodeNumber = wx.CheckBox(self, -1, "Node numbers", wx.DefaultPosition, wx.Size(50, 20))
		self.chknodeNumber.Bind(wx.EVT_CHECKBOX, self.OnchknodeNumber)
		vert.Add(self.chknodeNumber, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)
		
		self.chkautobeam = wx.CheckBox(self, -1, "Auto create Beam", wx.DefaultPosition, wx.Size(50, 20))
		self.chkautobeam.Bind(wx.EVT_CHECKBOX, self.OncreateBeam)
		vert.Add(self.chkautobeam, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)	   

		self.chkHideProps = wx.CheckBox(self, -1, "Hide Props", wx.DefaultPosition, wx.Size(50, 20))
		self.chkHideProps.Bind(wx.EVT_CHECKBOX, self.OnHideProps)
		vert.Add(self.chkHideProps, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)	   
		
#===============================================================================
# 
#===============================================================================
		self.SetSizer(vert)
		self.GetSizer().SetSizeHints(self)
		self.resetControls()
	
	def resetControls(self):
		pass
	def OnHideProps(self, event):
		self.parent.truckEditorOgreWin.hideProps(not event.IsChecked())
		
	def OnchknodeNumber(self, event):
		self.parent.truckEditorOgreWin.visibleNodeNumbers(event.IsChecked())
		event.Skip()
	def OnchkbeamVisible(self, event):	
		print "beam visible"
		self.parent.truckEditorOgreWin.visibleBeams(event.IsChecked())
#		event.Skip()
		
	def OnMainMeshTransChange(self, event):
#		self.parent.odefEditorOgreWin.setMainMeshTrans(event.GetInt())
		event.Skip()
		
	def OnMeshVisible(self, event):
		self.parent.truckEditorOgreWin.showSubmeshs(event.IsChecked())
		event.Skip()

	def OnshowExhaustRefNodes(self, event):
		self.parent.truckEditorOgreWin.showExhaustRefNodes(event.IsChecked())
		event.Skip()

	def OnshowExhaustNodes(self, event):
		self.parent.truckEditorOgreWin.showExhaustNodes(event.IsChecked())
		event.Skip()

	def OnshowHookNodes(self, event):
		self.parent.truckEditorOgreWin.showHookNodes(event.IsChecked())
		event.Skip()

	def OnshowFrictionNodes(self, event):
		self.parent.truckEditorOgreWin.showFrictionNodes(event.IsChecked())
		event.Skip()

	def OnshowContactNodes(self, event):
		self.parent.truckEditorOgreWin.showContactNodes(event.IsChecked())
		event.Skip()
	
	def OnshowLoadNodes(self, event):
		self.parent.truckEditorOgreWin.showLoadNodes(event.IsChecked())		
		event.Skip()
	
	def OnshowNormalNodes(self, event):
		self.parent.truckEditorOgreWin.showNormalNodes(event.IsChecked())	   
		event.Skip()
	def OnshowNormalBeams(self, event):
		self.parent.truckEditorOgreWin.showNormalBeams(event.IsChecked())	
		event.Skip()
	
	def OnshowInvisibleBeams(self, event):
		self.parent.truckEditorOgreWin.showInvisibleBeams(event.IsChecked())
		event.Skip()
	
	def OnshowRopeBeams(self, event):
		self.parent.truckEditorOgreWin.showRopeBeams(event.IsChecked())		
		event.Skip()
	
				
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
	def OncreateBeam(self, event):
		self.parent.truckEditorOgreWin.autoCreateBeam = event.IsChecked()
