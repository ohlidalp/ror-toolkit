#Lepes
import math, glob
import wx, os, os.path, copy
import pickle
import ogre.renderer.OGRE as ogre
from ShapedControls import ShapedWindow
from ror.rorcommon import *
from ror.settingsManager import *
from ror.lputils import positionClass
from ror.logger import log


class scrolledText(ShapedWindow):
	
	def __init__(self, parent, title, msg, **kwargs):
		ShapedWindow.__init__(self, rorSettings().mainApp, skinOnlyFilename="scrolledtext.png", title=title, **kwargs)
	   
		self.parent = parent
		
			
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 3))
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		self.mainLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))

		
		r = 2
		c = 1		 
		self.text = wx.TextCtrl(self, -1, msg, size=wx.Size(360, 320),
									   style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
		f = self.text.GetFont()
		f.SetFamily(wx.FONTFAMILY_MODERN)
		f.SetFaceName("Courier New")
		self.text.SetFont(f)
		grid.Add(self.text, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))		



		r += 1
		c = 1
		self.btnclose = wx.Button(self, -1, "Close", size=wx.Size(80, 20), pos=(160, 0))
		self.btnclose.Bind(wx.EVT_BUTTON, self.Onclose)
		grid.Add(self.btnclose, pos=wx.GBPosition(r, c))

		self.SetSizerAndFit(grid)
		self.updateSkin()

	def Onclose(self, event):
		self.Destroy()

 
