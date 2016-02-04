import wx, math, glob
import sys, os, os.path
import ogre.renderer.OGRE as ogre
from ShapedControls import ShapedWindow
from ror.rorcommon import *
from ror.settingsManager import rorSettings
from ror.logger import log
from ror.lputils import showedError
from RoRConstants import *


class RoadSystemWindow(ShapedWindow):
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)
	   
		self.parent = parent
		self.rordir = rorSettings().rorFolder
		
		self._splines = []	
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(10, 3))
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (0,0)) # Row 0, Col 0
		grid.AddSpacer(spacer_size, (0,8)) # Row 0, Col 2
		
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))

		r += 2 
		l = wx.StaticText(self, -1, 'Splines:', size=wx.Size(60, 20), style=wx.TRANSPARENT_WINDOW)
		grid.Add(l, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 2))

		c += 2 #span
		self.cboSpline = wx.ComboBox(self, -1, size=wx.Size(170, 20), style=wx.CB_READONLY)
		self.cboSpline.Bind(wx.EVT_COMBOBOX, self.OncboSpline)
		grid.Add(self.cboSpline,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 4))
		
		r += 1
		c -= 2
		self.createSpline = wx.Button(self, -1, "Create new road", size=wx.Size(100, 20))
		self.createSpline.Bind(wx.EVT_BUTTON, self.OncreateSpline)
		grid.Add(self.createSpline, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))


		r += 1
		c += 1
		self.changeName = wx.Button(self, -1, "Change Spline name")
		self.changeName.Bind(wx.EVT_BUTTON, self.OnchangeName)
		grid.Add(self.changeName, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))


		r += 1
		self.pauseSpline = wx.Button(self, -1, "Pause - allow to modify control points")
		self.pauseSpline.Bind(wx.EVT_BUTTON, self.OnpauseSpline)
		grid.Add(self.pauseSpline, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))
		
		r += 1
		self.insertBefore = wx.Button(self, -1, "Insert control point Before")
		self.insertBefore.Bind(wx.EVT_BUTTON, self.OninsertBefore)
		grid.Add(self.insertBefore, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))
		
		r += 1
		self.deleteControlPoint = wx.Button(self, -1, "Delete control point")
		self.deleteControlPoint.Bind(wx.EVT_BUTTON, self.OndeleteControlPoint)
		grid.Add(self.deleteControlPoint, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))

		r += 1
		self.insertAfter = wx.Button(self, -1, "Insert control point After")
		self.insertAfter.Bind(wx.EVT_BUTTON, self.OninsertAfter)
		grid.Add(self.insertAfter, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))

		r += 1
		l = wx.StaticText(self, -1, 'segment Type:', size=wx.Size(80, 20), style=wx.TRANSPARENT_WINDOW)
		grid.Add(l, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 2))
		
		c += 2
		self.cbosegmentType = wx.ComboBox(self, -1, size=wx.Size(130, 20),
									choices=['auto', 'road', 'roadborderleft', 'roadborderright', 'roadborderboth', 'roadbridge', 'roadbridgenopillar'],
												style=wx.CB_READONLY)
		self.cbosegmentType.SetSelection(0)
		self._segmentType = 'auto'
		self.cbosegmentType.Bind(wx.EVT_COMBOBOX, self.OncbosegmentType)
		grid.Add(self.cbosegmentType,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 4))

		r += 1
		c -= 2
		self.chkSmooth = wx.CheckBox(self, -1, "stick to ground", wx.DefaultPosition, wx.Size(100, 20))
		self.chkSmooth.SetValue(True)
		self._segmentSticked = True
		self.chkSmooth.Bind(wx.EVT_CHECKBOX, self.Onsmooth)
		grid.Add(self.chkSmooth, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))

		r += 1
		self.finishSpline = wx.Button(self, -1, "Finish - Accept the road")
		self.finishSpline.Bind(wx.EVT_BUTTON, self.OnfinishSpline)
		grid.Add(self.finishSpline, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))

		r += 1
		self.deleteSpline = wx.Button(self, -1, "Delete - Decline actual road")
		self.deleteSpline.Bind(wx.EVT_BUTTON, self.OndeleteSpline)
		grid.Add(self.deleteSpline, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))
		
		r += 1
		self.walk = wx.Button(self, -1, "Walk on roads")
		self.walk.Bind(wx.EVT_BUTTON, self.Onwalk)
		grid.Add(self.walk, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 2))

		r += 1
		self.purgue = wx.Button(self, -1, "Purgue spline forever")
		self.purgue.Bind(wx.EVT_BUTTON, self.Onpurgue)
		grid.Add(self.purgue, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 3))

		self.enableCreateSpline(True)
		self.enableInsert(False)
		
		# Window padding - bottom
		r += 1
		grid.AddSpacer(spacer_size, (r,c))
		
		self.SetSizerAndFit(grid)
		 
		self.updateSkin()

	def OnLeftDown(self, event):
		ShapedWindow.OnLeftDown(self, event)
		event.Skip()

	def OnfromGround(self, event):
		height = self.checkValidChars(event.GetString().strip())
		if self.parent.terrainOgreWin.roadSystem:
			self.parent.terrainOgreWin.roadSystem.height = height
		event.Skip()
		
	def Onangle(self, event):
		angle = self.checkValidChars(event.GetString().strip())
		if self.parent.terrainOgreWin.roadSystem:
			self.parent.terrainOgreWin.roadSystem.smoothAngle = angle
		event.Skip()

	def OncreateSpline(self, event):
		self.toggleSpline()
		event.Skip()
	
	def OnpauseSpline(self, event):
		self.toggleSpline()
		event.Skip()
	
	def toggleSpline(self):
		if self.parent.terrainOgreWin.splineMode is None:
			self.parent.terrainOgreWin.roadSystem.setSplineMode(not self.parent.terrainOgreWin.splineMode, None) 
			self.enableCreateSpline(False)
		else: #pause it
			self.parent.terrainOgreWin.splineMode = not self.parent.terrainOgreWin.splineMode
		
	def Onsmooth(self, event):
		self.parent.terrainOgreWin.roadSystem.segmentSticked = self.chkSmooth.GetValue()
		event.Skip()
	def OnchangeName(self, event):
		dlg = wx.TextEntryDialog(
						self, 'Enter spline name (You can use spaces in the name).\n It will change when you finish the spline.',
						'New name:', '')
		
		dlg.SetValue("")
		
		if dlg.ShowModal() == wx.ID_OK:
		 	self.parent.terrainOgreWin.roadSystem.splineName = dlg.GetValue()		
	def OnfinishSpline(self, event):
		self.parent.terrainOgreWin.roadSystem.finishSpline()
		self.enableCreateSpline(True)
		event.Skip()

	def OndeleteSpline(self, event):
		self.parent.terrainOgreWin.roadSystem.cancelSpline()
		self.enableCreateSpline(True)
		event.Skip()
	
	
	def OninsertBefore(self, event):
		self.parent.terrainOgreWin.roadSystem.insertPointAtSelectedEntry(before=True)
		event.Skip()		
	
	def OndeleteControlPoint(self, event):
		self.parent.terrainOgreWin.roadSystem.insertPointAtSelectedEntry(before=None)
		event.Skip()
		
	def OninsertAfter(self, event):
		self.parent.terrainOgreWin.roadSystem.insertPointAtSelectedEntry(before=False)
		event.Skip()
		
	def OncbosegmentType(self, event):
		self.parent.terrainOgreWin.roadSystem.actualSegment = self.cbosegmentType.GetStringSelection()
		event.Skip()
	def Onwalk(self, event):
		self.parent.terrainOgreWin.roadSystem.walkOnRoads = not self.parent.terrainOgreWin.roadSystem.walkOnRoads 
		event.Skip()
		
	def Onpurgue(self, event):
		self.parent.terrainOgreWin.roadSystem.purgueSpline()
		event.Skip()
	
	def enableInsert(self, value):
		self.insertAfter.Enable(value)
		self.deleteControlPoint.Enable(value)
		self.insertBefore.Enable(value)
		self.cbosegmentType.Enable(value)
		
	def enableCreateSpline(self, value):	
			self.createSpline.Enable(value)
			self.cboSpline.Enable(value)
			self.changeName.Enable(not value)
			self.chkSmooth.Enable(not value)
			self.pauseSpline.Enable(not value)
			self.deleteSpline.Enable(not value)
			self.finishSpline.Enable(not value)
			self.purgue.Enable(not value)
			self.walk.Enable(not value)
			if value:
				self.cboSpline.SetSelection(0)
			else:
				self.chkSmooth.SetValue(self.parent.terrainOgreWin.roadSystem.segmentSticked)
	
	def getActualUID(self):
		sel = self.cboSpline.GetSelection()
		strUID = None
		if sel > 0 :
			 strUID = self._splines[0][sel]		
		return strUID
	
	def OncboSpline(self, evt):
		strUID = self.getActualUID()
		self.parent.terrainOgreWin.roadSystem.setSplineMode(strUID is not None, strUID)
		self.enableCreateSpline(strUID is None)
		
	def _getsplines(self):
		return self._splines
			
	def _setsplines(self, value):
		self._splines = value # [ [uuids], [userNames]] 
		self.cboSpline.Clear()
		value[0].insert(0, 'None')
		value[1].insert(0, 'None')
		self.cboSpline.AppendItems(value[1])
			
	def _delsplines(self):
		del self._splines
	
	def _getsegmentType(self):
		return self.cbosegmentType.GetStringSelection()
			
	def _setsegmentType(self, value):
		if not self.cbosegmentType.SetStringSelection(value):
			self.cbosegmentType.SetSelection(0)
			
	def _getsegmentSticked(self):
		return self._segmentSticked
			
	def _setsegmentSticked(self, value):
		self._segmentSticked = value
		self.chkSmooth.SetValue(value)
			
	def _delsegmentSticked(self):
		del self._segmentSticked
	
	segmentSticked = property(_getsegmentSticked, _setsegmentSticked, _delsegmentSticked,
					doc="")

	segmentType = property(_getsegmentType, _setsegmentType,
					doc="only update combobox")

	
	splines = property(_getsplines, _setsplines, _delsplines,
					doc="")

		
