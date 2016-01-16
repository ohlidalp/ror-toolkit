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


class skinSelector(ShapedWindow):

	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)

		self.parent = parent
		self.rordir = rorSettings().rorFolder

		self.skinList = []
		self.lastcount = 0
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 3))
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		self.mainLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		#self.mainLabel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))


		r += 2
		c = 1
		l = wx.StaticText(self, -1, "available skins:")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		r += 1
		c = 1
		self.list = wx.ListBox(self, -1, wx.DefaultPosition, wx.Size(250, 220), [], wx.LB_SINGLE | wx.LB_NEEDED_SB)
		self.list.Bind(wx.EVT_LISTBOX, self.Onselect)
		grid.Add(self.list, pos=wx.GBPosition(r, c))

		r += 2
		c = 1
		self.btnclose = wx.Button(self, -1, "Close", size=wx.Size(250, 20))
		self.btnclose.Bind(wx.EVT_BUTTON, self.Onclose)
		grid.Add(self.btnclose, pos=wx.GBPosition(r, c))

		self.SetSizerAndFit(grid)
		self.searchSkins()
		self.updateSkin()

	def Onclose(self, event):
		self.Destroy()

	def searchSkins(self):
		self.skinList = []
		self.list.Set([])
		self.path = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ['media', 'gui', 'skins'])
		for x in os.listdir(self.path):
			full = os.path.join(self.path, x)
			if os.path.isdir(full):
				self.skinList.append(x)
		self.list.Set(self.skinList)

	def Onselect(self, event):
		#mouse down on listbox
		s = event.GetString().strip()
		rorSettings().setSetting(TOOLKIT, 'theme', s)
		self.parent.ConfigureSkin()
		for w in wx.GetTopLevelWindows():
			if isinstance(w, ShapedWindow):
				w.updateSkin()
		self.parent.DoUpdate()
		self.parent.Refresh()
		self.parent.Update()
		event.Skip()
