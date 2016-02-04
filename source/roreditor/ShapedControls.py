#Lepes and wx documentation Examples

import wx
import ogre.renderer.OGRE as ogre
from ror.settingsManager import rorSettings
from ror.logger import log
from rorFrame import *

skinBackColor = wx.Color(254, 184, 0)
skinTransparentColor = wx.Color(0, 0, 0)
skinTheme = 'RoR theme' 


class ShapedWindow(rorFrame):
	"""
	Middle layer for RoRToolkit tool panels.
	Obsolete, scheduled for removal.
	Original purpose: draw skinned and bitmap-shaped windows (disabled)
	"""
	
	def __init__(self, parent, title="ShapeW", skinOnlyFilename=None, **kwargs):
		wx_styles = wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW |	wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT
		rorFrame.__init__(self, parent, title, style=wx_styles, **kwargs)
		log().debug("%s is initialising..." % title)
		# perspective is the Perspective menu index (1, 2 or 3)
		self.perspective = 1 
		self.skinSize = (0, 0)
		self.SetAutoLayout(True)
		self.hasShape = False
		self.skinFile = skinOnlyFilename
	
		self.title = title
		
		# min height when you click on the window
		self.smallHeight = 100
		self.delta = (0, 20)
		self.moving = False
		self.Bind(wx.EVT_LEFT_DOWN, 	 self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, 	   self.OnLeftUp)
		self.Bind(wx.EVT_MOTION, 		self.OnMouseMove)

		self.isMouseDownHere = False

		self.grid = wx.GridBagSizer(2, 2) 
#		self.SetSizer(self.grid)
		self.updateSkin()

		log().debug("%s created" % title)

	def updateSkin(self):
		self.SetBackgroundColour(skinBackColor)
		self.Refresh() # wtf about wxWindow.Update and Refresh on help file???? !!!!
		self.Update()  # should be posible for wxWidget to implement 20 more routines to be called for updating a fuc**** paint window?

	def ChangeSize(self):
		pass
		
	def OnLeftDown(self, evt):
		self.isMouseDownHere = True
		self.CaptureMouse()
		x, y = self.ClientToScreen(evt.GetPosition())
		originx, originy = self.GetPosition() 
		dx = x - originx
		dy = y - originy
		self.delta = ((dx, dy))
		
		evt.Skip()

	def OnLeftUp(self, evt):
		self.isMouseDownHere = False
		if self.HasCapture():
			self.ReleaseMouse()
			
		if self.moving:
			self.savePosition()

		
		evt.Skip()

	def OnMouseMove(self, evt):
		# only if he pressed LMB on this window
		self.moving = self.isMouseDownHere and evt.Dragging() and evt.LeftIsDown() 
		if self.moving:
			x, y = self.ClientToScreen(evt.GetPosition())
			fp = (x - self.delta[0], y - self.delta[1])
			self.Move(fp)
		evt.Skip()
		
							 
	def checkValidChars(self, text):
		# we allow mathematic calcs as 3*3, 2.0+10, etc
		try:
			f = eval(text)
		except Exception:
			rorSettings().mainApp.MessageBox('error', "Hey, don't be a bad child and type a valid Float Number")
			raise # keep the bad number at the edit and abort saving the value
		return f		
