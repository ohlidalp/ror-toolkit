import wx, math, glob
import sys, os, os.path, errno, gc
import ogre.renderer.OGRE as ogre
#from wxogre.OgreManager import *
#from wxogre.wxOgreWindow import *
from ShapedControls import ShapedWindow
from ror.SimpleTruckRepresentation import *
from ror.odefparser import *
from ror.rorcommon import *
from RoRObjectPreviewOgreWindow import ObjectPreviewOgreWindow
from ror.settingsManager import rorSettings
from ror.logger import log
#import wx.grid
#import wx.html
#import wx.aui
#import cStringIO

class RoRPreviewCtrl(ShapedWindow):
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)

		self.parent = parent
		self.rordir = rorSettings().rorFolder

		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 10))
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)

		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))
		r += 1
		self.objectPreviewWindow = ObjectPreviewOgreWindow(self, "PreviewToolwindow", size=wx.Size(150, 150))
		grid.Add(self.objectPreviewWindow, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 2))

		self.errorLabel = wx.StaticText(self, -1, " ", size=wx.Size(240, 80))
		self.errorLabel.Wrap(230)
		self.errorLabel.SetForegroundColour(wx.RED)
		self.errorLabel.SetBackgroundColour(self.skinBack)
		r += 1
		grid.Add(self.errorLabel,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		self.SetSizerAndFit(grid)


# It works too, but i want the window "minimized"
#		self.SetSize(self.skinSize)
		self.Refresh()

	def loadFile(self, filename):
		try:
			self.error("Loading ...")
#			   self.objectPreviewWindow.Destroy()
#
#			   self.objectPreviewWindow = ObjectPreviewOgreWindow(self, "PreviewToolwindow", size=wx.Size(250, 250))

			self.objectPreviewWindow.loadFile(filename)
		except Exception, err:
			self.error(" Loaded with errors, maybe you can not use this object")
			log().error("RoRPreviewCtrl exception")
			log().error(str(err))
		else:
			self.error("")

#	def OnLeftDown(self,event):
#		ShapedWindow.OnLeftDown(self, event)
#		event.Skip()

	def error(self, text):
		self.errorLabel.SetLabel(text)
		self.errorLabel.Update()

	def clear(self):
		if self.objectPreviewWindow:
			#clear preview
			del self.objectPreviewWindow

	def Destroy(self):
		log().debug("freeing " + self.title)
		if not self.objectPreviewWindow is None:
			self.objectPreviewWindow.Destroy()
			self.objectPreviewWindow = None
