'''
Created on 11/03/2010

@author: Lupas
'''
import wx
from ror.settingsManager import *

class rorFrame(wx.Frame):
	""" a Frame window that 
	- save position on closing
	- restore position
	
	it checks if out of screen (due resolution changed)
	
	"""
	def __init__(self, parent, title, **args):
		wx.Frame.__init__(self, parent, -1, title, **args)
		self.title = title
		self.restorePosition()
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self._parent = parent
		
	def restorePosition(self):
		if rorSettings().has_section(self.title):
			l, t = self.checkOutOfScreen(int (rorSettings().getSetting(self.title, "left")), int (rorSettings().getSetting(self.title, "top")))
			self.SetPosition(wx.Point(l, t))
			if rorSettings().has_key(self.title, "width"):
				w = int(rorSettings().getSetting(self.title, "width"))
				h = int(rorSettings().getSetting(self.title, "height"))
				self.SetSize((w, h))  

	def checkOutOfScreen(self, left, top):
		rect = wx.Display(0).GetGeometry()
		if left < 0 : left = 0
		elif left > rect.GetWidth(): left = 0
		
		if top < 0 : top = 0
		if top > rect.GetHeight(): top = 0
		return left, top

	def savePosition(self):
		p = self.GetPosition()
		rorSettings().setSetting(self.title, "left", p.x) 
		rorSettings().setSetting(self.title, "top", p.y) 
		w, h = self.GetSize()
		rorSettings().setSetting(self.title, "width", w) 
		rorSettings().setSetting(self.title, "height", h)
		
	def Destroy(self):
		self.savePosition()
		super(rorFrame, self).Destroy()
		
	def OnClose(self, event):
		pass # TODO: Hide the panel and update associated toolbar button
