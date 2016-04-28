import wx, math, glob
import sys, os, os.path
import ogre.renderer.OGRE as ogre
from ShapedControls import ShapedWindow
from ror.rorcommon import *
from ror.settingsManager import rorSettings
from ror.logger import log
from ror.lputils import showedError
from RoRConstants import *


class MapOptionWindow(ShapedWindow):
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)
	   
		self.parent = parent
		self.rordir = rorSettings().rorFolder
			
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 3))
		
		# Window padding
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (0,0)) # Row 0, Col 0
		grid.AddSpacer(spacer_size, (0,2)) # Row 0, Col 2
		
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))
		
		r += 1
		c = 1
		l = wx.StaticText(self, -1, "Ingame menu Map name:", style=wx.TRANSPARENT_WINDOW)
		grid.Add(l, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 2))

		r += 1
		c = 1
		self.mapName = wx.TextCtrl(self, -1, "", size=wx.Size(252, 20), style=wx.TE_PROCESS_ENTER)
		self.mapName.Bind(wx.EVT_TEXT_ENTER, self.OnmapName)
		grid.Add(self.mapName,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 2))


		r += 1
		c = 1
		l = wx.StaticText(self, -1, "Config file (*.cfg):", style=wx.TRANSPARENT_WINDOW)
		grid.Add(l, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))

		c += 1
		self.mapConfig = wx.TextCtrl(self, -1, "", size=wx.Size(120, 20), style=wx.TE_PROCESS_ENTER)
		self.mapConfig.Bind(wx.EVT_TEXT_ENTER, self.OnmapConfig)
		grid.Add(self.mapConfig,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 2))

		r += 1
		c = 1
		self.useCaelum = wx.CheckBox(self, -1, "Use Caelum in this map")
		self.useCaelum.Bind(wx.EVT_CHECKBOX, self.OnuseCaelum)
		grid.Add(self.useCaelum,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		r += 1
		c = 1
		self.chkWaterLevel = wx.CheckBox(self, -1, "Water level (in meters):")
		self.chkWaterLevel.Bind(wx.EVT_CHECKBOX, self.OnCheckWater)
		grid.Add(self.chkWaterLevel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))
		
#		r+=1
		c += 1
		self.waterHeight = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
		self.waterHeight.Bind(wx.EVT_TEXT_ENTER, self.OnwaterHeight)
		grid.Add(self.waterHeight,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		r += 1
		c = 1
		l = wx.StaticText(self, -1, "author information:", style=wx.TRANSPARENT_WINDOW)
		grid.Add(l, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 2))

		r += 1
		c = 1
		self.comments = wx.TextCtrl(self, -1, "", size=wx.Size(252, 150), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)	
		self.comments.Bind(wx.EVT_TEXT_ENTER, self.Oncomments)
		grid.Add(self.comments,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 2))

		r += 1
		self.btdetails = wx.Button(self, -1, "Summary...", size=wx.Size(100, 20))
		self.btdetails.Bind(wx.EVT_BUTTON, self.Onbtdetails)
		grid.Add(self.btdetails, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 4))
		
		# Bottom padding
		r += 1
		grid.AddSpacer(spacer_size, (r, 3))
		
		self.SetSizerAndFit(grid)
		self.updateSkin()
		 

# It works too, but i want the window "minimized"
#		self.SetSize(self.skinSize)
		self.Refresh()
#		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)		
#		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
#		self.Bind(wx.EVT_MOTION, self.OnMouseMove)
		
#	def OnLeftUp(self, event):
#		ShapedWindow.OnLeftUp(self, event)
#		event.Skip()
#
#	def OnMouseMove(self, event):
#		ShapedWindow.OnMouseMove(self, event)
#		event.Skip()
	
	def Onbtdetails(self, evt):
		self.parent.terrainOgreWin.MapStatistics()
	def OnLeftDown(self, event):
		ShapedWindow.OnLeftDown(self, event)
		event.Skip()

	def OnmapName(self, event):
		self.parent.terrainOgreWin.terrain.TerrainName = event.GetString()
		event.Skip()
	
	def updateTerrainWater(self):
		level = self.waterHeight.GetValue().strip()
		if level == "" :
			level = 0.0
		else:
			level = self.checkValidChars(level)
		if not self.chkWaterLevel.GetValue():
			level = 0.0
		self.parent.terrainOgreWin.update_water_plane(level)
		return level
		
	def OnCheckWater(self, event):
		self.waterHeight.Enable(self.chkWaterLevel.GetValue())
		self.updateTerrainWater()
		event.Skip()
		
	def OnwaterHeight(self, event):
		level = self.updateTerrainWater()
		self.waterHeight.ChangeValue("%.1f" % level)
		event.Skip()
		
		
	def OnmapConfig(self, event):
		name = event.GetString().strip()
		if name == "" :
			raise showedError("It is needed a valid config file")
		self.parent.terrainOgreWin.terrain.TerrainConfig = name 
		
		event.Skip()
	def OnuseCaelum(self, event):
		self.parent.terrainOgreWin.terrain.UsingCaelum = event.IsChecked()
		
		event.Skip()
	
	def Oncomments(self, event):
		#user may include "//" chars for the comment but may not!!
		# I assert doing myself
		# Although TextCtrl process enter key, user may press twice to get a blank line 
		line = event.GetString().replace("/", "")
		lines = [ "//" + x for x in line.split("\n")]
	   
		self.parent.terrainOgreWin.author = lines		 
		event.Skip()
		return					

	
	def updateData(self, terrain):
		self.mapName.SetValue(terrain.TerrainName)
		self.mapConfig.SetValue(terrain.TerrainConfig)
		
		# always is False or True
		self.useCaelum.SetValue(terrain.UsingCaelum)
		
		if terrain.WaterHeight:
			w = str(terrain.WaterHeight)
		else:
			w = "0.0"
		self.waterHeight.SetValue(w)
		self.chkWaterLevel.SetValue(w != 0.0)
		
