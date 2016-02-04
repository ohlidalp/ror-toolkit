# Lepes modification
 
import sys, os, os.path

from ror.logger import log
from ror.settingsManager import rorSettings
from ror.rorcommon import *
from ShapedControls import ShapedWindow
from copyPastePanel import *
import wx
import wx.aui

import cStringIO


class ObjectInspector(ShapedWindow):
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)

		self.parent = parent
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 3))
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (0,0)) # Row 0, Col 0
		grid.AddSpacer(spacer_size, (0,2)) # Row 0, Col 2
		
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))

		self.nameObject = wx.StaticText(self, -1, "", style=wx.ALIGN_CENTRE)
		self.nameObject.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.nameObject.Bind(wx.EVT_LEFT_DOWN, self.OnnameObjectDown)
		r += 1
		c = 1
		grid.Add(self.nameObject,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 2))
		
		l = wx.StaticText(self, -1, "   X", style=wx.TRANSPARENT_WINDOW)
		l.SetForegroundColour(wx.RED)
		r += 1
		c = 1
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		self.X = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.X,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasteX, None)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				
		pan = CopyPasteClass(self) 
		l = wx.StaticText(pan, -1, "   Y")
		l.SetForegroundColour(wx.BLUE)
		pan.addButtons(self.OnCopy, self.OnPastePos, None, 40)
		r += 1
		c = 1
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		self.Y = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.Y,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasteY, None)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		l = wx.StaticText(self, -1, "   Z")
		l.SetForegroundColour(wx.GREEN)
		r += 1
		c = 1
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		self.Z = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.Z,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasteZ, None)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		l = wx.StaticText(self, -1, "   Rot X")
		l.SetForegroundColour(wx.RED)
		r += 1
		c = 1
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		self.rotX = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.rotX,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasterotX, self.OnResetrotX)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		pan = CopyPasteClass(self)
 		l = wx.StaticText(pan, -1, "   Rot Y")
		l.SetForegroundColour(wx.BLUE)
		pan.addButtons(None, self.OnPasterot, self.OnResetrot, 40)
		r += 1
		c = 1
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		self.rotY = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.rotY,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasterotY, self.OnResetrotY)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		l = wx.StaticText(self, -1, "   Rot Z")
		l.SetForegroundColour(wx.GREEN)
		r += 1
		c = 1
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
				 
		self.rotZ = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.rotZ,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasterotZ, self.OnResetrotZ)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		r += 1
		c = 1
		l = wx.StaticText(self, -1, "   Height From Ground")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		self.heightFromGround = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)
		c += 1
		grid.Add(self.heightFromGround,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1)) 
		c += 1
		pan = CopyPasteClass(self)
		pan.addButtons(None, self.OnPasteHeight, self.OnResetHeight)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		r += 1
		c = 1
		self.places = wx.ComboBox(self, -1, choices=hardcoded['ingamemap'], style=wx.CB_READONLY)
#		self.places.Bind(wx.EVT_COMBOBOX, self.Onplaces)
		grid.Add(self.places,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		c += 1
		self.placeName = wx.TextCtrl(self, -1, "", size=wx.Size(100, 20), style=wx.TE_PROCESS_ENTER)	
		self.placeName.Bind(wx.EVT_TEXT_ENTER, self.OnplaceName)
		grid.Add(self.placeName,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		r += 1
		c = 1		 
		l = wx.StaticText(self, -1, "   Object Comment:")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		# a memo for comments will span throw 6 rows and 2 columns of the sizer.
		self.comments = wx.TextCtrl(self, -1, "", size=wx.Size(200, 80), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)	
		r += 1
		c = 1
		grid.Add(self.comments,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 2))

		self.chkVisible = wx.CheckBox(self, -1, "Visible", wx.DefaultPosition, wx.Size(50, 20))
		self.chkVisible.SetValue(True)
		self.chkVisible.Bind(wx.EVT_CHECKBOX, self.OnVisible)
		r += 1
		c = 1
		grid.Add(self.chkVisible,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		self.makeVisible = wx.Button(self, -1, "make all visible", size=wx.Size(100, 20))
		self.makeVisible.Bind(wx.EVT_BUTTON, self.OnmakeVisible)
		grid.Add(self.makeVisible, pos=wx.GBPosition(r, c))

		r += 1
		c = 1
		self.details = wx.Button(self, -1, "Details...", size=wx.Size(100, 20))
		self.details.Bind(wx.EVT_BUTTON, self.Ondetails)
		grid.Add(self.details, pos=wx.GBPosition(r, c))

#		grid.SetFlexibleDirection(wx.BOTH)
#		grid.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
		
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditChanged, self.X)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditChanged, self.Y)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditChanged, self.Z)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditHeightChanged, self.heightFromGround)		
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditrotChanged, self.rotX)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditrotChanged, self.rotY)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditrotChanged, self.rotZ)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEditcommentChanged, self.comments)
		
		# Bottom padding
		r += 1
		grid.AddSpacer(spacer_size, (r, 4))

		self.SetSizerAndFit(grid)
		
		# no need to use wx.Clipboard to copy/paste feature.
		self.clipboard = []
		self.updateSkin()
	def Ondetails(self, evt):
		if self.parent.terrainOgreWin.selected.entry:
			self.parent.terrainOgreWin.ObjectDetails()
		evt.Skip()
		
	def OnnameObjectDown(self, evt):
		self.parent.terrainOgreWin.ObjectDetails()
		evt.Skip()

	def OnCopy(self, evt):		
		self.clipboard = []
		self.clipboard.append(self.X.GetValue())
		self.clipboard.append(self.Y.GetValue())
		self.clipboard.append(self.Z.GetValue())
		self.clipboard.append(self.rotX.GetValue())
		self.clipboard.append(self.rotY.GetValue())
		self.clipboard.append(self.rotZ.GetValue())
		self.clipboard.append(self.heightFromGround.GetValue())
		evt.Skip()
	
	def OnPastePos(self, evt):
		if len(self.clipboard) == 7:
			self.X.SetValue(self.clipboard[0])
			self.Y.SetValue(self.clipboard[1])
			self.Z.SetValue(self.clipboard[2])
			self.updateEntry()
		evt.Skip()
			
	def OnPasteX(self, evt):
		if len(self.clipboard) == 7:
			self.X.SetValue(self.clipboard[0])
			self.updateEntry()
		evt.Skip()
			
	def OnPasteY(self, evt):
		if len(self.clipboard) == 7:
			self.Y.SetValue(self.clipboard[1])
			self.updateEntry()
		evt.Skip()

	def OnPasteZ(self, evt):
		if len(self.clipboard) == 7:
			self.Z.SetValue(self.clipboard[2])
			self.updateEntry()
		evt.Skip()

	def OnPasterot(self, evt):
		if len(self.clipboard) == 7:
			self.rotX.SetValue(self.clipboard[3])
			self.rotY.SetValue(self.clipboard[4])
			self.rotZ.SetValue(self.clipboard[5])
			self.updaterot()
		evt.Skip()

	def OnPasterotX(self, evt):
		if len(self.clipboard) == 7:
			self.rotX.SetValue(self.clipboard[3])
			self.updaterot()
		evt.Skip()

	def OnPasterotY(self, evt):
		if len(self.clipboard) == 7:
			self.rotY.SetValue(self.clipboard[4])
			self.updaterot()
		evt.Skip()			

	def OnPasterotZ(self, evt):
		if len(self.clipboard) == 7:
			self.rotZ.SetValue(self.clipboard[5])
			self.updaterot()
		evt.Skip()		
	
	def OnResetrotX(self, evt):
		self.rotX.SetValue("0.0")
		self.updaterot()
		evt.Skip()	

	def OnResetrotY(self, evt):
		self.rotY.SetValue("0.0")
		self.updaterot()
		evt.Skip()	

	def OnResetrotZ(self, evt):
		self.rotZ.SetValue("0.0")
		self.updaterot()
		evt.Skip()	

	def OnResetrot(self, evt):
		self.rotX.SetValue("0.0")
		self.rotY.SetValue("0.0")
		self.rotZ.SetValue("0.0")
		self.updaterot()
		evt.Skip()	

	def OnResetHeight(self, evt):
		self.heightFromGround.SetValue("0.2")
		self.parent.terrainOgreWin.selected.entry.heightFromGround = 0.2
		evt.Skip()	
	
	def OnPasteHeight(self, evt):
		if len(self.clipboard) == 7:
			self.heightFromGround.SetValue(self.clipboard[6])
			f = self.checkValidChars(self.clipboard[6])
			self.parent.terrainOgreWin.selected.entry.heightFromGround = f
		evt.Skip()	

	def OnplaceName(self, evt):
		""" user used qualifier """
		str = evt.GetString().replace(" ", "_")
		e = self.parent.terrainOgreWin.selected.entry
		if e is not None:
			if  self.places.GetSelection() == 0: # we interpreted that user want to reset values
				e.data.clearAdditionalOptions()
			else:
				e.data.CheckNewAdditionalOptions(self.places.GetValue(), str)
	def OnEditChanged(self, event):
		f = 0.0
		f = self.checkValidChars(event.GetString())
		self.updateEntry()
		event.Skip()
	
	def updateEntry(self):
		if self.parent.terrainOgreWin.selected.entry:
			self.parent.terrainOgreWin.selected.entry.position = (eval(self.X.GetValue()), eval(self.Y.GetValue()), eval(self.Z.GetValue()))


	def OnEditHeightChanged(self, event):
		f = 0.0
		if self.parent.terrainOgreWin.selected.entry:
			f = self.checkValidChars(event.GetString())
			self.parent.terrainOgreWin.selected.entry.heightFromGround = f
		event.Skip()
		
		
	def OnEditrotChanged(self, event):
		f = 0.0
		f = self.checkValidChars(event.GetString())
		self.updaterot()
		event.Skip()
		return
	
	def updaterot(self):
		if self.parent.terrainOgreWin.selected.entry:
			self.parent.terrainOgreWin.selected.entry.rotation = (eval(self.rotX.GetValue()), eval(self.rotY.GetValue()), eval(self.rotZ.GetValue()))

	def OnVisible(self, event):
		if self.parent.terrainOgreWin.selected.entry:
			self.parent.terrainOgreWin.selected.entry.visible = self.chkVisible.GetValue()
		if not self.chkVisible.GetValue():
			self.parent.terrainOgreWin.selectTerrain()
	
	def OnmakeVisible(self, event):		
		
		for e in self.parent.terrainOgreWin.entries.keys():
			if not self.parent.terrainOgreWin.entries[e].visible:
				self.parent.terrainOgreWin.entries[e].visible = True

	def OnEditcommentChanged(self, event):
		#user may include "//" chars for the comment but may not!!
		# I assert doing myself
		# Although TextCtrl process enter key, user may press twice to get a blank line 
		line = event.GetString().replace("/", "")
		lines = line.split("\n")
		
		for i in range(0, len(lines)):
			lines[i] = "// " + lines[i] 
		if self.parent.terrainOgreWin.selected.entry:		
			self.parent.terrainOgreWin.selected.entry.data.comments = lines		 
		event.Skip()
		return					

	def updateData(self, entry=None ,
				   doc=""" entry is terrain.selected.entry and
							may be None to disable Object Inspector"""):
		
		rotRes = False
		commRes = False
		res = not entry is None
		self.places.Enable(False)

		if res:
			commRes = not entry.data is None
			if entry.data:
				rotRes = entry.data.mayRotate

			x, y , z = entry.position
			rx, ry, rz = entry.rotation
			
			self.nameObject.SetLabel(entry.data.name)
			self.X.ChangeValue('%.6f' % x)
			self.Y.ChangeValue('%.6f' % y)
			self.Z.ChangeValue('%.6f' % z)
			self.rotX.ChangeValue('%.6f' % rx)
			self.rotY.ChangeValue('%.6f' % ry)
			self.rotZ.ChangeValue('%.6f' % rz)
			self.heightFromGround.ChangeValue('%.6f' % entry.heightFromGround)
			new = ""
			self.chkVisible.SetValue(entry.visible)
			if commRes:
				new = [x.replace("/", "") for x in entry.data.comments]
			self.comments.SetValue("\n".join(new))
			placeNames = entry.data is not None
			if placeNames:
				if entry.data.allowSection72():
					self.places.Enable(True)
					if len(entry.data.additionalOptions) > 1:
						self.places.SetStringSelection(entry.data.additionalOptions[0])
						self.placeName.ChangeValue(entry.data.additionalOptions[1].replace("_", " "))
					else:
						self.places.SetSelection(0)
						self.placeName.ChangeValue("")
						
		else:
			# look terrain Pos
			x, y, z = self.parent.terrainOgreWin.selected.coords.asTuple
			self.X.ChangeValue('%.6f' % x)
			self.Y.ChangeValue('%.6f' % y)
			self.Z.ChangeValue('%.6f' % z)

#			self.X.ChangeValue('')
#			self.Y.ChangeValue('')
#			self.Z.ChangeValue('')
			self.rotX.ChangeValue('')
			self.rotY.ChangeValue('')
			self.rotZ.ChangeValue('')
			self.comments.SetValue("")
			self.nameObject.SetLabel("< nothing selected >")			
   
