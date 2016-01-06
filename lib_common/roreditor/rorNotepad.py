'''
Created on 07/03/2010

@author: Lepes
'''
import sys, os, os.path

from ror.logger import log
from ror.settingsManager import *
from ror.rorcommon import *
import string, os, os.path, glob
import  wx.lib.multisash    as  sash
import  wx
import  wx.grid as gridlib
import  wx.html as  html
import  wx.lib.wxpTag
from ror.truckparser import *
from RoRGridTable import *
from rorFrame import *
from types import *
from RoRConstants import *
from RoRVirtualKeys import *

import cStringIO
from ror.rorcommon import list_has_value
#fancy menus
import wx.lib.agw.flatmenu as FM
from wx.lib.agw.artmanager import ArtManager, RendererBase, DCSaver
from wx.lib.agw.fmresources import ControlFocus, ControlPressed
from wx.lib.agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR
from FM_renderer import *



class rorNotepad(rorFrame):
	def __init__(self, parent, **args):
		rorFrame.__init__(self, parent, "RoR Notepad", **args)
#		self.grid = sash.MultiSash(self, -1, pos=(0, 0), size=(640, 480))
#		self.grid.SetDefaultChildClass(rorGridEditor)
		self._fontsize = 0
		self.parent = parent
		#_sizer = wx.BoxSizer(wx.VERTICAL)		
		
		self.grid = rorGridEditor(self, **args)
		self.grid.SetScrollLineY(40)
		#self.createToolbar()
		#_sizer.Add(self.toolbar)
		#_sizer.Add(self.grid)
		self.helpWindow = helpFrame(self)
		self.helpWindow.Show(True)
		#self.toolbar.Refresh()
		#self.SetSizer(_sizer)
		self.Show(True)
		


	def _getfontsize(self):
		return self._fontsize
			
	def _setfontsize(self, value):
		self._fontsize = value
		self.grid.fontsize = value
		self.helpWindow.fontsize = value
	
	fontsize = property(_getfontsize, _setfontsize)
	""" increase or decrement font size of help window
	"""
	def createToolbar(self):
		# create some toolbars
		tb_buttons = [
					{'caption': 'Save vehicle', 'shorthelp': 'Save it', 'id': wx.NewId(), 'icontype': 'wx', 'icon' : wx.ART_FILE_SAVE, 'event':self.parent.save },
					{'caption': 'criss cross', 'shorthelp': 'criss cross last four selected nodes', 'id': wx.NewId(), 'icontype': '', 'icon' : '', 'event': self.parent.crisscross },
					{'caption': 'Insert\tctrl + insert', 'shorthelp': 'Insert new row', 'id': wx.NewId(), 'icontype': '', 'icon' : 'newRow', 'event': self.grid.newRow },
					{'caption': 'Del\tctrl + del', 'shorthelp': 'Delete Row', 'id': wx.NewId(), 'icontype': '', 'icon' : '', 'event': self.grid.delRow },
					{'caption': 'Up\tctrl + up', 'shorthelp': 'Move actual row Up', 'id': wx.NewId(), 'icontype': '', 'icon' : 'up', 'event': self.grid.moveUp },
					{'caption': 'Down\tctrl + down', 'shorthelp': 'Move actual row Down', 'id': wx.NewId(), 'icontype': '', 'icon' : 'down', 'event': self.grid.moveDown },
					{'caption': 'Dup\tctrl + d', 'shorthelp': 'Duplicate actual line', 'id': wx.NewId(), 'icontype': '', 'icon' : 'dupplicate', 'event': self.grid.dupplicate },
					{'caption': 'select\tctrl + s', 'shorthelp': 'select beams by node ranges', 'id': wx.NewId(), 'icontype': '', 'icon' : 'select', 'event': self.parent.selectByNodes },
					#{'caption': '', 'shorthelp': '', 'id': wx.NewId(), 'icontype': '', 'icon' : '', 'event': j },
					]
		self.toolbar = FM.FlatMenuBar(self, iconSize=32, spacer=5, options=FM_OPT_SHOW_TOOLBAR)
		for b in tb_buttons:
			if b['icontype'] == 'wx': graphic = wx.ArtProvider_GetBitmap(b['icon'])
			else: graphic = getBitmap(b['icon'])
			
			self.toolbar.AddTool(b['id'], b['caption'], graphic, shortHelp=b['shorthelp'])
			self.Bind(wx.EVT_MENU, b['event'], id=b['id'])
			
		return self.toolbar
	
class rorGridEditor(gridlib.Grid):
	def __init__(self, parent, **args):
		gridlib.Grid.__init__(self, parent, -1, **args)
		self.parent = parent
		self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.LeftClickCell)
		self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.RightClickCell)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyEvent)
		self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnSelectRange)
		self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)
#		self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChanged)
		
		self.SetDefaultCellOverflow(True)
		self.SetDefaultCellBackgroundColour(wx.Color(220, 220, 220))
		self.highlightColor = NOTEPAD_HIGHLIGHTCOLOR
		self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
		self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
		self.selCells = []
		self._Row = 0
		self._fontsize = 0
		self.menuItems = {}
	
	def createMenu(self):
		""" popup menu with commands and sections to add"""
		def doMenu(themenu, listOfCaptions, popuphandler=None):
			listOfCaptions.sort()
			for it in listOfCaptions:
				id = wx.NewId()
				self.menuItems[str(id)] = it
				item = themenu.Append(id, it)
				if popuphandler is None: self.Bind(wx.EVT_MENU, self.popupHandler, item)
				else: self.Bind(wx.EVT_MENU, popuphandler, item) 
		self.menu = wx.Menu()
		commands = wx.Menu()
		doMenu(commands, self.parser.commands.keys())
		self.menu.AppendSubMenu(commands, 'commands')
		k = self.parser.sections.keys()
		sections = wx.Menu()
		doMenu(sections, [x for x in k if x not in self.parser.truckSections])
		self.menu.AppendSubMenu(sections, 'sections')
		
		doMenu(self.menu, ['group beams'], self.groupHightlightBeams)
		
		#local variable
		#menuItems = ['set_beam_defaults', ';']
	def groupHightlightBeams(self, evt):
		""" beams highligthed in 3D window are moved into a continous block
		"""
		minIdx, howmany = self.groupBeams(self.parent.parent.activeAnim)
		section = self.insertSection(';', minIdx)
		section.comment_line = 'group'
		footer = self.insertSection(';', minIdx + howmany + 2)
		footer.comment_line = 'end group'
		
		self.Refresh()
		self.Update()
		evt.Skip()
		
	def insertSection(self, sectionOrObj, atRow):
		""" insert a new section notifying Grid
		return the lineOfSection created
		"""
		gr = self.parser.insertLine(atRow, sectionOrObj)
		msg = gridlib.GridTableMessage(self.GetTable(), 			# The table
				gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
				1									   # how many
				)
		self.ProcessTableMessage(msg)	
		return gr
		
	def groupBeams(self, beams):
		""" move all beams into a contigous block
		
		beams is a list of entries
		
		return a tuple
		- the minimun row index used
		- how many beams are in the group
		"""
		minidx = -1
		cont = 0
		if len(beams) > 0:
			idxlist = []
			for e in beams:
				if e.lineTruck.section == 'beams':
					#print e.lineTruck.getTruckLine()
					idx = self.parser.lines.index(e.lineTruck)
					if not idx in idxlist:
						idxlist.append(idx) 
			if len(idxlist) < 2: 
				print "emtpy list to hightlight"
				return
			minidx = min(idxlist)
			print minidx, idxlist
			idxlist.pop(idxlist.index(minidx))
			for i in idxlist:
				item = self.parser.lines.pop(i)
				self.parser.lines.insert(minidx + cont, item)
				cont += 1
				#print "Unit testing: item was at ", i, " now it is at ", self.parser.lines.index(item), " that should be ", minidx 
			return minidx, cont
		
	def popupHandler(self, evt):
		id = evt.GetId()
		section = self.menuItems[str(id)]
		self.insertSection(section, self._Row)
		if self.parser.sections.has_key(section):
			header = self.insertSection(section, self._Row)
			header.isHeader = True
		idx = list_has_key(self.parser.sectionfooter, section)
		if idx > -1:
			self.insertSection(section, self._Row + 1)
	
		evt.Skip()
		
	def setParser(self, parser):
		table = rortable(self)
		self.parser = parser
		#read meshes and material on the same group
		fullpath = parser.filename
		if fullpath != "":
			if not os.path.isdir(fullpath):
				group = ogreGroupFor(fullpath)
				if group != "":
					fullpath = resourceGroupNames[group]
		self.retrieveFiles(fullpath)
		table.FromLinesOfSection(self.parser.lines)
		table.maxColumns = self.parser.maxColumns() + 1
		self.SetTable(table)
		


#		for i in range(0, table.maxColumns - 1):
#			self.SetColSize(i, 50)

		self.ForceRefresh()
#		l = self.parser.lines
#		content = []
#		content = getContent(os.path.join(self.currentPath(), 'sections.txt'))
#		print "the following sections are missing in this program"
#		nosec = []
#		for line in content:
#			if self.parser.sectionDef(line.lower().strip()) is None:
#				nosec.append(line.strip() + '\n')
#		saveContent(nosec, os.path.join(self.currentPath(), 'nosec.txt'))

		self.RegisterDataType('string',
							  gridlib.GridCellStringRenderer(),
							  gridlib.GridCellTextEditor())
		
		self.RegisterDataType('material_managed_effect',
							  gridlib.GridCellStringRenderer(),
							  gridlib.GridCellChoiceEditor(managedMaterialEffect, False))
		
		self.RegisterDataType('material',
							  gridlib.GridCellStringRenderer(),
							  gridlib.GridCellChoiceEditor(self.materials, True))
		self.RegisterDataType('mesh',
							gridlib.GridCellStringRenderer(),
							gridlib.GridCellChoiceEditor(self.meshes, True))
		self.RegisterDataType('sound',
							gridlib.GridCellStringRenderer(),
							gridlib.GridCellChoiceEditor(self.sounds, True))

		self.RegisterDataType('shortcut',
							gridlib.GridCellStringRenderer(),
							gridlib.GridCellChoiceEditor(self.shortcuts, False))

		self.RegisterDataType('int',
							gridlib.GridCellNumberRenderer(),
							gridlib.GridCellNumberEditor())
		self.RegisterDataType('node',
							gridlib.GridCellNumberRenderer(),
							gridlib.GridCellNumberEditor())
		self.RegisterDataType('float',
							gridlib.GridCellFloatRenderer(precision=2),
							gridlib.GridCellFloatEditor(precision=3))

		
	def retrieveFiles(self, path):
		self.meshes = []
		self.materials = []
		self.sounds = []
		self.shortcuts = self.getShortcuts()
		
		if not os.path.isdir(path): return
		files = glob.glob(os.path.join(path, '*.*'))
		for file in files:
			if file.endswith('.mesh'):
				self.meshes.append(os.path.split(file)[1])
			elif file.endswith('.material'):
				content = getContent(file)
				for line in content:
					if line.startswith('material '):
						self.materials.append(line.split(' ')[1].replace('\n', ''))
			elif file.endswith('.wav'):
				self.sounds.append(os.path.split(file)[1])

	def currentPath(self):
		print os.path.dirname(os.path.abspath(__file__))
		return os.path.dirname(os.path.abspath(__file__))
		evt.Skip()

	def OnSelectRange(self, event):
		"""Internal update to the selection tracking list"""
		if event.Selecting():
			# adding to the list...
			for row in range(event.GetTopRow(), event.GetBottomRow() + 1):
				for col in range(event.GetLeftCol(), event.GetRightCol() + 1): 
					ele = (row, col)
					if  ele not in self.selCells:
						self.selCells.append(ele)
		else:
			# removal from list
		   for row in range(event.GetTopRow(), event.GetBottomRow() + 1):
				for col in range(event.GetLeftCol(), event.GetRightCol() + 1): 
					ele = (row, col)
					if  ele in self.selCells:
						self.selCells.remove(ele)
#		   self.ConfigureForSelection()
		event.Skip()
	def OnSelectCell(self, event):
		"""Internal update to the selection tracking list"""
		self.selCells = [ (event.GetRow(), event.GetCol())]
		self.Row = event.GetRow()
		old = super(rorGridEditor, self).GetGridCursorCol()
		attr = self.GetTable().GetAttr(self.GetGridCursorRow(), old, 0)
		if attr is not None:
			print "attr get size " , attr.GetSize()
		else: print "attr is none for %d %d" % (self.GetGridCursorRow(), old)
		
		event.Skip()
	def selSameCol(self):
		if len(selCells) == 0 : return False
		for ele in range(0, len(self.selCells) - 1):
			if self.selCells[ele][1] <> self.selCells[ele + 1][1]: return False
		return True
	
	def selSameRow(self):
		if len(selCells) == 0 : return False
		for ele in range(0, len(self.selCells) - 1):
			if self.selCells[ele][0] <> self.selCells[ele + 1][0]: return False
		return True
	
	def GetLabelTextColour(self):
		if self.parser.lines[self.Row].section == uhoh:
			return wx.RED
#	def OnCellChanged(self, evt):
#		# update helpWindow
#		self.Row = evt.GetRow()
#		self.Col = evt.GetCol()
#
#		sec = self.parser.lines[self.Row].section
#		self.parent.helpWindow.section = sec
#
#
#
#		evt.Skip()
#		return
#		# extract help for validvalues, validmultiplevalues and so on
#		if coldef is not None:
#			self.parent.helpWindow.column = coldef['name']
#			thehelp = ""
#			optionList = None
#			if coldef.has_key("help"): thehelp = coldef['help'] 
#			if coldef.has_key("validmultiplevalues"): 
#				optionList = coldef['validmultiplevalues']
#			elif coldef.has_key('validvalues'):
#				optionList = coldef['validvalues']
#			
#			if optionList is not None:
#				if isinstance(optionList, ListType):
#					for element in optionList:
#						if isinstance(element, DictType):
#							thehelp += element['option']
#							if element.has_key('help'):
#								thehelp += ' - ' + element['help']
#							thehelp += '\n'
#						elif isinstance(element, StringType):
#							thehelp += element + ' ' 
#			self.parent.helpWindow.text = thehelp
#				
#		else:
#			self.parent.helpWindow.column = ""
#			self.parent.helpWindow.text = ""
#		evt.Skip()
	def newRow(self):
		self.InsertRows(self.GetGridCursorRow(), 1)
	def delRow(self):
		self.DeleteRows(self.GetGridCursorRow(), 1)
	def moveUp(self):
		if self._Row > 0:
			Skip = False
			i = self._Row
			old = self.parser.lines[self._Row - 1]
			self.parser.lines[self._Row - 1] = self.parser.lines[self._Row]
			self.parser.lines[self._Row] = old
			self.Refresh()
			self.Update()
			self.Row = i - 1
	def moveDown(self):		
		if self._Row < len(self.parser.lines) - 1:
			Skip = False
			i = self._Row
			old = self.parser.lines[self._Row + 1]
			self.parser.lines[self._Row + 1] = self.parser.lines[self._Row]
			self.parser.lines[self._Row] = old
			self.Refresh()
			self.Update()
			self.Row = i + 1
	def dupplicate(self):
		#Duplicate currentLine
		new = self.parser.insertLine(self._Row, self.parser.lines[self._Row])
		if hasattr(new, 'entry'):
			new.entry = None # new object doesn't share 3D object
	
	def OnKeyEvent(self, evt):
		Skip = True
		if evt.m_keyCode == wx.WXK_RETURN or evt.m_keyCode == wx.WXK_NUMPAD_ENTER:
			if evt.ControlDown():   # the edit control needs this key
				evt.Skip()
				return
			self.DisableCellEditControl()
#			c = self.GetGridCursorCol()
			r = self.GetGridCursorRow()
			if evt.ShiftDown(): sum = -1
			else: sum = 1
			c = self.GetGridCursorCol() + sum
			if c == -1 : 
				r += sum
				c = self.parser.lines[r].getMaxCols() - 1
			elif c == self.parser.lines[r].getMaxCols():
				r += sum
				c = 0
			while self.GetTable().lines[r].isHeader:
				if r == len(self.GetTable().lines) - 1 or r == 0: break
				else:r += sum
			self.SetGridCursor(r, c)
			self.MakeCellVisible(r, c)
			if self.CanEnableCellControl():
				self.EnableCellEditControl()
			return
		
		elif evt.m_keyCode == wx.WXK_F12 :
			for a in self.selCells:
				print str(a)
		elif evt.m_keyCode == wx.WXK_INSERT and evt.ControlDown():
			self.newRow()
		elif evt.m_keyCode == wx.WXK_DELETE and evt.ControlDown():
			self.delRow()
		
		elif evt.m_keyCode == wx.WXK_UP and evt.ControlDown():
			self.moveUp()
		elif evt.m_keyCode == wx.WXK_DOWN and evt.ControlDown():				
			self.moveDown()
		elif evt.m_keyCode == WXK_D and evt.ControlDown():
			self.dupplicate()
		elif evt.m_keyCode == wx.WXK_F1:
			
		# 	saving truck

			content = []
			sec = "title"
			l = self.parser.lines
			for i in range(len(l)):
#				if sec != l[i].section and not l[i].isCommand:
#					sec = l[i].section
#					if self.parser.blankLineBeforeSection : content.append('\n')
#					if not l[i].isCommand:
#						content.append(l[i].section + '\n')
				content.append(l[i].getTruckLine() + '\n')
			saveContent(content, os.path.join(self.currentPath(), 'new_generated.truck'))
		
		if Skip: evt.Skip()
			
	def RightClickCell(self, evt):
		self.createMenu()
		self.PopupMenu(self.menu)
		self.menu.Destroy()
		evt.Skip()
	def onMouseEvent(self, evt):
		# change Grid Font size 
		if evt.ControlDown() and evt.GetWheelRotation() != 0:
			self.Parent.fontsize = (evt.GetWheelRotation() / abs(evt.GetWheelRotation()))
			self.MakeCellVisible(self.Row, self.GetGridCursorCol())
		else:
			evt.Skip()
	def LeftClickCell(self, evt):
		evt.Skip()
	
	def _getRow(self):
		return self._Row
			
	def _setRow(self, value):
		self.animNodes(self._Row, False)
		self._Row = value
		sec = self.parser.lines[self.Row].section
		if sec == ';' or self.parser.lines[self.Row].isHeader:
			#get all entries and highlit on 3D window
			r = self._Row + 1
			self.parent.parent.clearAnim()
			if r < len(self.parser.lines): 
				section = self.parser.lines[r].section
				while r < len(self.parser.lines):
					if self.parser.lines[r].section == section:
						self.parent.parent.anim(self.parser.lines[r], True)
					else: break
					r += 1
		else:
			self.animNodes(self._Row, True)
		if sec is not None: self.parent.helpWindow.section = sec
#		w = 100
# changing column width when you click on a cell is sick !!

#		for i in range(0, self.parser.lines[self._Row].getMaxCols() - 1):
#			coldef = self.parser.getColOfSection(sec, i)
#			if coldef is not None:
#				if coldef['type'] == 'int' or coldef['type'] == 'node': w = 75
#				elif coldef['type'] == 'float' : w = 80
#				elif coldef['type'] == 'string': w = 200
#			self.SetColSize(i, w + (self._fontsize))
		self.ForceRefresh()	

	def _delRow(self):
		del self._Row
	
	def animNodes(self, row, value):
		if row < len(self.parser.lines):
			self.parent.parent.animNodes(self.parser.lines[row], value)

	def _getfontsize(self):
		return self._fontsize
			
	def _setfontsize(self, value):
		font = self.GetDefaultCellFont()
		self._fontsize = font.GetPointSize() + value 
		font.SetPointSize(self._fontsize)  
		self.SetDefaultCellFont(font)
		self.SetDefaultRowSize(self._fontsize * 2 , True)
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		self.SetLabelFont(font)
		self.SetRowLabelSize(self._fontsize * 10)
		self.ForceRefresh()
	
	def getShortcuts(self):
		""" shortcuts used on commands, commands2, etc.
		we return a list used as a combobox to choose the text to show
		instead the number of the key
		"""
		result = []
		for i in range(0, 48):
			text = 'F' + str((i % 12) + 1)
			if i >= 36:   text = 'CTRL + ALT + ' + text
			elif i >= 24: text = 'ALT + ' + text
			elif i >= 12: text = 'CTRL + ' + text
			result.append(text)
		return result
	fontsize = property(_getfontsize, _setfontsize)
	""" increasement of point size  
	"""	
	Row = property(_getRow, _setRow, _delRow)

class helpFrame(rorFrame):
	def __init__(self, parent, **args):
		rorFrame.__init__(self, parent, "Help Window", **args)
		self.myhtml = html.HtmlWindow(self, -1)#, style=wx.NO_FULL_REPAINT_ON_RESIZE)
		self.loaded = False
		self.file = ""
		path = os.path.join(os.path.dirname(__file__), 'tdf.htm')
		if os.path.isfile(path):
			self.myhtml.LoadPage(path)
			self.file = path
			self.loaded = True
		else:
			path = os.path.join(os.path.dirname(__file__), 'default.htm')
			self.myhtml.LoadPage(path)
			
			
#		self.html.SetRelatedFrame(frame, self.titleBase + " -- %s")
		return

		grid = wx.GridBagSizer(2, 2)
		grid.SetFlexibleDirection(wx.BOTH)
		r = 0
		c = 0
		self.txt = wx.TextCtrl(self, -1, " <help text>", style=wx.TE_MULTILINE | wx.TE_READONLY)
		grid.Add(self.txt, pos=wx.GBPosition(r, c), span=wx.GBSpan(2, 1), flag=wx.EXPAND)
		grid.AddGrowableRow(0)
		grid.AddGrowableCol(0)
		
#		self.SetSizerAndFit(grid)
		self.Layout()
		self.AutoLayout = True
	
	def _getsection(self):
		return self.lblSection.GetLabel()
			
	def _setsection(self, value):
		if self.loaded:
			if self.myhtml.HasAnchor(value.title()): self.myhtml.ScrollToAnchor(value.title())
			#only a few of anchor are in lowercase
			elif self.myhtml.HasAnchor(value): self.myhtml.ScrollToAnchor(value)
			elif len(value) > 2: 
				if self.myhtml.HasAnchor(value.capitalize()): self.myhtml.ScrollToAnchor(value.capitalize())
#			else: print "web help for not found, searched ' % s' and ' % s'" % (value, value.title())
#			page = self.file + '#' + value.title()
#			self.myhtml.LoadPage(page)

	def _getcolumn(self):
		return self.lblColumn.GetLabel()
			
	def _setcolumn(self, value):
#		self.lblColumn.SetLabel("Column: " + value)
		pass
		
			
	def _gettext(self):
		return self.txt.GetValue()
			
	def _settext(self, value):
		self.txt.SetValue(value)

	def _getfontsize(self):
		return self._fontsize
			
	def _setfontsize(self, value):
#		for x in [self.txt ]:#,self.lblSection, self.lblColumn, ]:
#			font = x.GetFont()
#			font.SetPointSize(font.GetPointSize() + value)
#			x.SetFont(font)
#		self.Refresh()
		pass

	fontsize = property(_getfontsize, _setfontsize)
	""" increase or decrement font size of help window
	"""

		
	text = property(_gettext, _settext)
	""" set help text
	"""
	section = property(_getsection, _setsection)
	"""set up label of section 
	"""
	column = property(_getcolumn, _setcolumn)
	""" set column label
	"""
