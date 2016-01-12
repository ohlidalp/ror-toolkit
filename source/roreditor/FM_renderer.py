'''
Created on 28/11/2009

extracted from wx.Widgets 2.8.10 demos

@Modified by: Lepes


'''
import wx
import math
import random
import os

import ShapedControls

import sys

try:
	from agw import flatmenu as FM
	from agw.artmanager import ArtManager, RendererBase, DCSaver
	from agw.fmresources import ControlFocus, ControlPressed
	from agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.flatmenu as FM
	from wx.lib.agw.artmanager import ArtManager, RendererBase, DCSaver
	from wx.lib.agw.fmresources import ControlFocus, ControlPressed
	from wx.lib.agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR


if wx.VERSION >= (2, 7, 0, 0):
	import wx.aui as AUI
	AuiPaneInfo = AUI.AuiPaneInfo
	AuiManager = AUI.AuiManager
	_hasAUI = True
else:
	try:
		import PyAUI as AUI
		_hasAUI = True
		AuiPaneInfo = AUI.PaneInfo
		AuiManager = AUI.FrameManager
	except:
		_hasAUI = False

def switchRGBtoBGR(color):

	return wx.Colour(color.Blue(), color.Green(), color.Red())

#------------------------------------------------------------
# A custom renderer class for FlatMenu
#------------------------------------------------------------

class FM_MyRenderer(RendererBase):
	""" My custom style. """
	
	def __init__(self):

		RendererBase.__init__(self)


	def DrawButton(self, dc, rect, state, useLightColours=True):

		if state == ControlFocus:
			penColor = switchRGBtoBGR(ArtManager.Get().FrameColour())
			brushColor = switchRGBtoBGR(ArtManager.Get().BackgroundColour())
		elif state == ControlPressed:
			penColor = switchRGBtoBGR(ArtManager.Get().FrameColour())
			brushColor = switchRGBtoBGR(ArtManager.Get().HighlightBackgroundColour())
		else:   # ControlNormal, ControlDisabled, default
			penColor = switchRGBtoBGR(wx.WHITE_PEN)
			brushColor = switchRGBtoBGR(wx.WHITE_BRUSH)
#			penColor = switchRGBtoBGR(ArtManager.Get().FrameColour())
#			brushColor = switchRGBtoBGR(ArtManager.Get().BackgroundColor())

		# Draw the button borders
		dc.SetPen(wx.Pen(penColor))
		dc.SetBrush(wx.Brush(brushColor))
		dc.DrawRoundedRectangle(rect.x, rect.y, rect.width, rect.height, 4)


	def DrawMenuBarBg(self, dc, rect):

		# For office style, we simple draw a rectangle with a gradient colouring
		vertical = ArtManager.Get().GetMBVerticalGradient()

		dcsaver = DCSaver(dc)

		dc.SetPen(wx.Pen(ShapedControls.skinBackColor))
		dc.SetBrush(wx.Brush(ShapedControls.skinBackColor))
		dc.DrawRectangleRect(rect)


	def DrawToolBarBg(self, dc, rect):

		if not ArtManager.Get().GetRaiseToolbar():
			return

		# fill with gradient
		startColor = ArtManager.Get().GetMenuBarFaceColour()
		dc.SetPen(wx.Pen(ShapedControls.skinBackColor))
		dc.SetBrush(wx.Brush(ShapedControls.skinBackColor))
		dc.DrawRectangle(rect.x, rect.y, rect.GetWidth(), rect.GetHeight())
