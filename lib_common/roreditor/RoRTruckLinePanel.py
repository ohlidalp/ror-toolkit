
'''
Created on 13/11/2009

@author: Lepes
'''

import sys, os, os.path, inspect

from ror.logger import log
from ror.settingsManager import rorSettings
from ror.truckparser import *
from xml.sax.handler import property_xml_string

import wx
import wx.aui

import cStringIO

MAXCONTROLS = 25

class TruckLinePanel(wx.Panel):
	'''
	Panel with labels and textBoxes to edit a particular line of the TDF
	'''
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition,
						  wx.DefaultSize)
		self.parser = rorparser()
		self.parent = parent
		self.labels = []
		self.ctrls = []  # { <textbox instance>:
		self.ids = []
		self._section = ''
		self.list = None # list of dictionary of the selected section
		grid = wx.GridBagSizer(2, 2) 
		r = 0
		c = 0
		chooseSection = wx.Button(self, -1, "section")
		chooseSection.Bind(wx.EVT_BUTTON, self.OnChooseSection)
		grid.Add(chooseSection,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		l = wx.StaticText(self, -1, " context help:", pos=((10, 10)), size=wx.Size(120, 40), style=wx.TRANSPARENT_WINDOW)
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		c += 1
		self.lblHelp = wx.TextCtrl(self, -1, " <help text>", size=wx.Size(600, 40), style=wx.TE_MULTILINE | wx.TE_READONLY)
	
		grid.Add(self.lblHelp,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 6))
		r += 1
		c = 0
		for i in range(0, MAXCONTROLS):
			self.labels.append(wx.StaticText(self, -1, "", size=wx.Size(120, 20), style=wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE))

			grid.Add(self.labels[i],
					 pos=wx.GBPosition(r, c),
					 span=wx.GBSpan(1, 1))
			
			c += 1
			nid = wx.NewId()
			self.ids.append(nid)
			t = wx.TextCtrl(self, nid, "", style=wx.TE_PROCESS_ENTER)
			t.Bind(wx.wx.EVT_ENTER_WINDOW, self.OnTextCtrlFocus)
			t.Bind(wx.EVT_TEXT_ENTER, self.OnUpdateText)
			self.ctrls.append(t)
			
			grid.Add(self.ctrls[i],
					 pos=wx.GBPosition(r, c),
					 span=wx.GBSpan(1, 1))
			c += 1
			if (i + 1) % 5 == 0:
				c = 0
				r += 1 
		
		self.SetAutoLayout(True) 
		self.SetSizer(grid)
		
	def OnChooseSection(self, evt):
		menu = wx.Menu()
		self.menuitems = {}
		for section in self.parser.sections.keys():
			id = wx.NewId()
			item = menu.Append(id, section)
			self.Bind(wx.EVT_MENU, self.sectionChoosen, item)
			self.menuitems[id] = section
		self.PopupMenu(menu)
		menu.Destroy()
#				print " %d item is %s " %(item.GetId(), self.getRoRName(r.movable))
	def sectionChoosen(self, evt):
		self.section = self.menuitems[evt.GetId()]
		
	def _getsection(self):
		return self._section
		
	def _setsection(self, value):
		self._section = value
		if self.parser.commands.has_key(value):
			self.list = self.parser.commands[value]
		elif self.parser.sections.has_key(value):
			self.list = self.parser.sections[value]
		else:
			raise Exception("section %s is unknown" % value)
		
		i = 0
		self.translator = {}
		for dic in self.list:
			self.labels[i].SetLabel(dic['name'])
			self.translator[dic['name']] = i
			
			i += 1
			if i > len(self.labels): raise Exception(" section %s is greater than labels availables on RoRTruckLinePanel" % value)
		for x in range(0, MAXCONTROLS):								
			if x >= i :
				self.labels[x].Hide()
				self.ctrls[x].Hide()
			else:
				self.labels[x].Show()
				self.ctrls[x].Show()
				
			
		
		
	def _delsection(self):
		del self._section
	
	section = property(_getsection, _setsection, _delsection)
	""" guide section name
	"""

	def OnTextCtrlFocus(self, evt=0, active=True, id=0):
		print "event focused"
		id = evt.GetId()
		if id in self.ids:
			idx = self.ids.index(id)
			lbl = self.labels[idx].GetLabel().replace("_", " ")
			
			if self.section != '':
				if self.parser.sections[self.section][idx].has_key("help"):
					self.lblHelp.SetValue(self.parser.sections[self.section][idx]['help'])
				else: self.lblHelp.SetValue("")
				self.lblHelp.Update()
		evt.Skip()
	def OnUpdateText(self, evt):
		print "event updatetext"
		evt.Skip()
	
	def OnTextCtrlLostFocus(self, evt):
	
		evt.Skip()
		
	def updateTextBoxesFrom(self, los):
		""" receive a LineOfSection object and update texboxes data
		"""
		if self._section != los.section:
			self.section = los.section
		i = 0
		for attr in los.__dict__.keys():
			thevalue = getattr(los, attr, None)
			if self.translator.has_key(attr):
				i = self.translator[attr]
				if thevalue is None: self.ctrls[i].SetValue('')
				else : self.ctrls[i].SetValue(str(thevalue))

class TextBox(wx.TextCtrl):
	def __init__(self, parent, **args):
		wx.TextCtrl.__init__(self, -1, "", style=wx.TE_PROCESS_ENTER)
		
	
		
