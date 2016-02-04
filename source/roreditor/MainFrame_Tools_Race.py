import math, glob
import wx, os, os.path, copy
import pickle
import ogre.renderer.OGRE as ogre
from ShapedControls import ShapedWindow
from ror.rorcommon import *
from ror.settingsManager import rorSettings
from ror.lputils import *
from ror.logger import log

class Race(ShapedWindow):
	
	def __del__(self):
		pass
	
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)
	   
		self.parent = parent
		self._luaParser = None
		self.rordir = rorSettings().rorFolder
					
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 20))
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (0,0)) # Row 0, Col 0
		grid.AddSpacer(spacer_size, (0,3)) # Row 0, Col 2
		
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))

		
		r += 1		 
		self.newRace = wx.Button(self, -1, "new Race", size=wx.Size(100, 20))
		self.newRace.Bind(wx.EVT_BUTTON, self.OnnewRace)
		grid.Add(self.newRace, pos=wx.GBPosition(r, c))
		
		c += 1
		self.modifyRace = wx.Button(self, -1, "Modify Race", size=wx.Size(100, 20))
		self.modifyRace.Bind(wx.EVT_BUTTON, self.OnmodifyRace)
		grid.Add(self.modifyRace, pos=wx.GBPosition(r, c))
		
		r += 1
		c = 1
		l = wx.StaticText(self, -1, "available races:")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		self.racelist = wx.ComboBox(self, -1, "", size=wx.Size(100, 20), style=wx.CB_READONLY)
		self.racelist.Bind(wx.EVT_COMBOBOX , self.Onracelist)
		grid.Add(self.racelist, pos=wx.GBPosition(r, c))

		r += 1
		c = 1		 
		l = wx.StaticText(self, -1, "Objects to spawn (click to go):")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		r += 1
		c = 1
		self.list = wx.ListBox(self, -1, wx.DefaultPosition, wx.Size(250, 180), [], wx.LB_SINGLE | wx.LB_NEEDED_SB)
		self.list.Bind(wx.EVT_LISTBOX, self.OnselectCheckpoint)
		grid.Add(self.list, pos=wx.GBPosition(r, c),
					span=wx.GBSpan(1, 2))
		
		r += 1
		c = 1
		self.endModify = wx.Button(self, -1, "End Modify", size=wx.Size(100, 20))
		self.endModify.Bind(wx.EVT_BUTTON, self.OnendModify)
		grid.Add(self.endModify, pos=wx.GBPosition(r, c))

		c += 1
		self.deleteRace = wx.Button(self, -1, "Delete Race", size=wx.Size(100, 20))
		self.deleteRace.Bind(wx.EVT_BUTTON, self.OndeleteRace)
		grid.Add(self.deleteRace, pos=wx.GBPosition(r, c))

		r += 1		
		c = 1
		self.altitude = wx.CheckBox(self, -1, "Show Altitude of the next Checkpoint")
		self.altitude.Bind(wx.EVT_CHECKBOX, self.Onaltitude)
		grid.Add(self.altitude,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 2))

		r += 1		
		c = 1
		self.isLoop = wx.CheckBox(self, -1, "is circuit race?")
		self.isLoop.Bind(wx.EVT_CHECKBOX, self.OnisLoop)
		grid.Add(self.isLoop,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		# Window padding - bottom
		r += 1
		grid.AddSpacer(spacer_size, (r, c))
	
		self.SetSizerAndFit(grid)
		self._raceIndex = -1
		self.updateSkin()
	
	def updateRaceList(self):
		self.racelist.Clear()
		self.racelist.AppendItems(self._luaParser.getRaceList())
		
	def OnnewRace(self, event):
		dlg = wx.TextEntryDialog(
						self, 'Enter racename (You can use spaces in the name)',
						'New Race:', '')
		
		dlg.SetValue("")
		
		if dlg.ShowModal() == wx.ID_OK and self._luaParser:
			if self._luaParser.newRaceFromTitle(dlg.GetValue()):
				self.raceIndex = len(self._luaParser.races) - 1 
				self.weAreInRace(True)
		
		dlg.Destroy()
		event.Skip()
		
	def OnmodifyRace(self, event):
		if self.raceIndex == -1:
			raise showedWarning("select an item from available races or create a new one")
		self.parent.terrainOgreWin.raceMode = self.raceIndex != -1
		
		event.Skip()
	def weAreInRace(self, value):
		self.newRace.Enable(not value)
		self.modifyRace.Enable(not value)
		self.racelist.Enable(not value)
		self.parent.terrainOgreWin.raceMode = value
				
	def OnendModify(self, event):
		self.weAreInRace(False)
		self._luaParser.races[self._raceIndex].showCheckpoints(False)
		event.Skip()
	def Onracelist(self, event):	
		""" user select a race from combobox """
		self.raceIndex = self.racelist.GetSelection()
		event.Skip()
			
	def updateCheckpoints(self):
		""" routine when selecting from combo and 
			callback when modifying checkpoint position/rotation
		
		"""
		if self.raceIndex != -1:
			self.list.Set(self._luaParser.getCheckpointList(self._raceIndex))
		
	def OnselectCheckpoint(self, event):
		if self.raceIndex != -1:
			checkpointIndex = self.list.GetSelection()
			if checkpointIndex != wx.NOT_FOUND:
				p = self._luaParser.races[self.raceIndex].points[checkpointIndex]['entry']
				self.parent.terrainOgreWin.selected.entry = p
				self.parent.terrainOgreWin.camera.lookAt(p.node.getPosition())
	
	def OndeleteRace(self, event):
		if self.raceIndex != -1:
			self._luaParser.deleteRace(self.raceIndex)
			self.raceIndex = -1
				
		event.Skip()
	def Onaltitude(self, event):
		if self.raceIndex != -1:
			self._luaParser.races[self.raceIndex].showAltitude = event.GetValue()
		event.Skip()
		
	def OnisLoop(self, event):
		if self.raceIndex != -1:
			self._luaParser.races[self.raceIndex].isLoop = event.GetValue()
		event.Skip()

	def OnLeftDown(self, event):
		ShapedWindow.OnLeftDown(self, event)
		event.Skip()
	
	def _getluaParser(self):
		return self._luaParser
		   
	def _setluaParser(self, value):
		self._luaParser = value
		if not value is None:
			self.updateRaceList()
			self.list.Clear()
	
	def _getraceIndex(self):
		return self._raceIndex
		   
	def _setraceIndex(self, value):
		if value == wx.NOT_FOUND: value = -1
		self._raceIndex = value
		if self._luaParser is None:
			self._raceIndex = -1
		enable = self._luaParser is not None and value != -1
		self.altitude.Enable(enable)
		self.isLoop.Enable(enable)
		self.deleteRace.Enable(enable)
		self.modifyRace.Enable(enable)
		
		if self._luaParser:
			self.updateRaceList()
			self.parent.terrainOgreWin.raceMode = value != -1
			if self._raceIndex == -1:
				self.racelist.SetSelection(wx.NOT_FOUND)
				self.list.Clear()
			else:
				self.racelist.SetSelection(value)
				self.updateCheckpoints()
				r = self._luaParser.races[value]
				self.altitude.SetValue(r.showAltitude)
				self.isLoop.SetValue(r.isLoop)
				self._luaParser.raceIndex = self._raceIndex
			self.weAreInRace(self._raceIndex != -1)
	   
	raceIndex = property(_getraceIndex, _setraceIndex,
					 doc="""selecting the index will:
						 update interface""")			
	
	luaParser = property(_getluaParser, _setluaParser, None,
					 doc="""just a pointer""")	
