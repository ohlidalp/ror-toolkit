'''
Created on 22/02/2010

@author: Lupas
'''

import  wx
import  wx.grid as  gridlib

class rorCellEditor(gridlib.PyGridCellEditor):
	"""
	This is a sample GridCellEditor that shows you how to make your own custom
	grid editors.  All the methods that can be overridden are shown here.  The
	ones that must be overridden are marked with "*Must Override*" in the
	docstring.
	"""
	def __init__(self):
		print "rorCellEditor ctor\n"
		gridlib.PyGridCellEditor.__init__(self)


	def Create(self, parent, id, evtHandler):
		"""
		Called to create the control, which must derive from wx.Control.
		*Must Override*
		"""
		print "rorCellEditor: Create\n"
		self._tc = wx.TextCtrl(parent, id, "")
		self._tc.SetInsertionPoint(0)
		self.SetControl(self._tc)

		if evtHandler:
			self._tc.PushEventHandler(evtHandler)


	def SetSize(self, rect):
		"""
		Called to position/size the edit control within the cell rectangle.
		If you don't fill the cell (the rect) then be sure to override
		PaintBackground and do something meaningful there.
		"""
		print "rorCellEditor: SetSize %s\n" % rect
		self._tc.SetDimensions(rect.x, rect.y, rect.width + 2, rect.height + 2,
							   wx.SIZE_ALLOW_MINUS_ONE)


	def Show(self, show, attr):
		"""
		Show or hide the edit control.  You can use the attr (if not None)
		to set colours or fonts for the control.
		"""
		print "rorCellEditor: Show(self, %s, %s)\n" % (show, attr)
		super(rorCellEditor, self).Show(show, attr)


	def PaintBackground(self, rect, attr):
		"""
		Draws the part of the cell not occupied by the edit control.  The
		base  class version just fills it with background colour from the
		attribute.  In this class the edit control fills the whole cell so
		don't do anything at all in order to reduce flicker.
		"""
		print "rorCellEditor: PaintBackground\n"


	def BeginEdit(self, row, col, grid):
		"""
		Fetch the value from the table and prepare the edit control
		to begin editing.  Set the focus to the edit control.
		*Must Override*
		"""
		print "rorCellEditor: BeginEdit (%d,%d)\n" % (row, col)
		self.startValue = grid.GetTable().GetValue(row, col)
		self._tc.SetValue(self.startValue)
		self._tc.SetInsertionPointEnd()
		self._tc.SetFocus()

		# For this example, select the text
		self._tc.SetSelection(0, self._tc.GetLastPosition())


	def EndEdit(self, row, col, grid):
		"""
		Complete the editing of the current cell. Returns True if the value
		has changed.  If necessary, the control may be destroyed.
		*Must Override*
		"""
		print "rorCellEditor: EndEdit (%d,%d)\n" % (row, col)
		changed = False

		val = self._tc.GetValue()
		
		if val != self.startValue:
			changed = True
			grid.GetTable().SetValue(row, col, val) # update the table

		self.startValue = ''
		self._tc.SetValue('')
		return changed


	def Reset(self):
		"""
		Reset the value in the control back to its starting value.
		*Must Override*
		"""
		print "rorCellEditor: Reset\n"
		self._tc.SetValue(self.startValue)
		self._tc.SetInsertionPointEnd()


	def IsAcceptedKey(self, evt):
		"""
		Return True to allow the given key to start editing: the base class
		version only checks that the event has no modifiers.  F2 is special
		and will always start the editor.
		"""
		print "rorCellEditor: IsAcceptedKey: %d\n" % (evt.GetKeyCode())

		## We can ask the base class to do it
		#return super(rorCellEditor, self).IsAcceptedKey(evt)

		# or do it ourselves
		return (not (evt.ControlDown() or evt.AltDown()) and
				evt.GetKeyCode() != wx.WXK_SHIFT)


	def StartingKey(self, evt):
		"""
		If the editor is enabled by pressing keys on the grid, this will be
		called to let the editor do something about that first key if desired.
		"""
		print "rorCellEditor: StartingKey %d\n" % evt.GetKeyCode()
		key = evt.GetKeyCode()
		ch = None
		if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
					wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
					wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
					]:

			ch = ch = chr(ord('0') + key - wx.WXK_NUMPAD0)

		elif key < 256 and key >= 0 and chr(key) in string.printable:
			ch = chr(key)

		if ch is not None:
			# For this example, replace the text.  Normally we would append it.
			#self._tc.AppendText(ch)
			self._tc.SetValue(ch)
			self._tc.SetInsertionPointEnd()
		else:
			evt.Skip()


	def StartingClick(self):
		"""
		If the editor is enabled by clicking on the cell, this method will be
		called to allow the editor to simulate the click on the control if
		needed.
		"""
		print "rorCellEditor: StartingClick\n"


	def Destroy(self):
		"""final cleanup"""
		print "rorCellEditor: Destroy\n"
		super(rorCellEditor, self).Destroy()


	def Clone(self):
		"""
		Create a new object which is the copy of this one
		*Must Override*
		"""
		print "rorCellEditor: Clone\n"
		return rorCellEditor(self.log)




class rortable(gridlib.PyGridTableBase):

	def __init__(self, parent):
		gridlib.PyGridTableBase.__init__(self)
		self.parent = parent
		self.lines = []
		self.maxColumns = 5

	def GetAttr(self, row, col, kind):
		""" set up coloring cells based on their section definition
		"""
#		print " row %d col %d kind %s" % (row, col, str(kind))
		ncol = col
		default = super(rortable, self).GetAttr(row, ncol, kind)		
		coldef = self.parent.parser.getColOfSection(self.lines[row].section, ncol)
		if coldef is None: return default

		if default is None: default = gridlib.GridCellAttr()#wx.RED, wx.WHITE, self.parent.GetDefaultCellFont(), wx.ALIGN_LEFT, wx.ALIGN_CENTER_VERTICAL)
		default.IncRef()
		default.SetOverflow(True)
		if self.lines[row].isHeader:
			default.SetBackgroundColour(wx.CYAN)
			default.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
		else:
			if hasattr(self.lines[row], 'entry') and self.lines[row].entry in self.parent.parent.parent.activeAnim:
				default.SetBackgroundColour(self.parent.highlightColor)
			else: default.SetBackgroundColour(wx.Color(220, 220, 220))
#			default.SetBackgroundColour(wx.Color(220, 220, 220))
			coltype = coldef['type']
			colname = coldef['name']
			if coltype == "string" : 
#				default.SetSize(1, 2)
				default.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
				if colname.find('material') <> -1: 
					default.SetTextColour(wx.NamedColor('#23ab26'))
				elif colname.find("mesh") <> -1: default.SetTextColour(wx.Colour(244, 90, 231))
				else: default.SetTextColour(wx.BLACK)
			elif coltype == "node": 
				default.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
				default.SetTextColour(wx.BLUE)
			elif coltype == "float": 
				default.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
				default.SetTextColour(wx.BLACK)
			elif coltype == "int": 
				default.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
				default.SetTextColour(wx.RED)
			else: 
				default.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
				default.SetTextColour(wx.BLACK)
		return default
		
	def GetNumberRows(self):
		return len(self.lines)

	def GetNumberCols(self):
		return self.maxColumns

	def IsEmptyCell(self, row, col):
		if row >= len(self.lines) or col > self.lines[row].getMaxCols() : return True
		else : return False

	def GetValue(self, row, col):
#		offset = self.colSpan(row, col)
		if self.lines[row].isHeader and col == 0: return self.lines[row].section
		elif self.lines[row].parent.getColOfSection(self.lines[row].section, col) is not None and \
		self.lines[row].parent.getColOfSection(self.lines[row].section, col)['type'] == 'shortcut':
#			if it is a shortcut we want to show the text "CTRL + ALT + F1" instead of "37"
#			although this cell is neither selected nor editing
			if self.lines[row].getColValue(col) is not None: 
				return str(self.parent.shortcuts[int(self.lines[row].getColValue(col)) - 1]) 
		elif self.lines[row].getColValue(col) is not None: return str(self.lines[row].getColValue(col))
		return super(rortable, self).GetValue(row, col)

	def SetValue(self, row, col, value):
#		offset = self.colSpan(row, col)
		
		if row >= len(self.lines) or col > self.lines[row].getMaxCols() + 1 : # inlineComment 
			raise Exception("row is greater than maximum rows")
		if self.lines[row].isHeader and col == 0: return 
		else:
			#Value is unicode string
			theValue = None
			coltype = self.parent.parser.getColOfSection(self.lines[row].section, col)['type']
			if coltype == 'int' or coltype == 'node': theValue = int(value)
			elif coltype == 'float': theValue = float(value)
			elif coltype == 'string': theValue = str(value)
			elif coltype == 'shortcut': theValue = self.parent.shortcuts.index(value) + 1
			else: theValue = value 
			toinform3D = theValue != self.lines[row].getColValue(col) and self.lines[row].section == 'nodes' and self.lines[row].entry is not None
			setattr(self.lines[row], self.lines[row].getColName(col), theValue)
			if toinform3D:
				l = self.lines[row]
				self.lines[row].entry.node.setPosition(l.x, l.y, l.z)
				self.lines[row].entry.inform() 
			

	def GetColLabelValue(self, col):
#		offset = self.colSpan(self.parent.GetGridCursorRow(), col)
		if col >= self.lines[self.parent.Row].getMaxCols(): return ""
		else: return self.lines[self.parent.Row].getColName(col).replace("_", " ")
	
	def GetRowLabelValue(self, row):
		""" actual section
		"""
		return self.lines[row].section
	
	def InsertRows(self, pos=0, numRows=1):	
		for i in range(0, numRows):
			self.parent.parser.insertLine(pos)
		msg = gridlib.GridTableMessage(self, 			# The table
				gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
				numRows									   # how many
				)

		self.GetView().ProcessTableMessage(msg)
		
		return True
	
	def DeleteRows(self, pos=0, numRows=1):
		for i in range(0, numRows):
			self.parent.parent.parent.deleteLine(self.parent.parser.lines[pos])
		msg = gridlib.GridTableMessage(self, 			# The table
				gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, # what we did to it
				numRows									   # how many
				)

		self.GetView().ProcessTableMessage(msg)

		return True

	
#	 Called to determine the kind of editor/renderer to use by
#	 default, doesn't necessarily have to be the same type used
#	 natively by the editor/renderer if they know how to convert.

	def GetTypeName(self, row, col):
		coldef = self.parent.parser.getColOfSection(self.lines[row].section, col)
		if coldef is not None:
			if coldef['type'] == 'shortcut': return 'shortcut'
			elif coldef['name'].find('material') != -1 : return 'material'
			elif coldef['name'].find('mesh') != -1 : return 'mesh'
			elif coldef['name'].find('sound') != -1 : return 'sound'
			elif coldef['name'] == 'effect' : return 'material_managed_effect'
			else: return coldef['type']
		else: return gridlib.GRID_VALUE_STRING

	# Called to determine how the data can be fetched and stored by the
	# editor and renderer.  This allows you to enforce some type-safety
	# in the grid.
#	def CanGetValueAs(self, row, col, typeName):
#		coldef = self.parent.parser.getColOfSection(self.lines[row].section, col)['name']
#		return coldef.find('material') != -1 
#
#	def CanSetValueAs(self, row, col, typeName):
#		return self.CanGetValueAs(row, col, typeName)	
	
#-----------------------end override methods----------------------------------------------------
	def colSpan(self, row, col):
		""" string columns are span 2 columns, so return the real grid column
		"""
		
		return 0
		
		
		cont = 0 
		realCol = 0
		while cont <= col:
			coldef = self.parent.parser.getColOfSection(self.lines[row].section, cont)
			if coldef is not None:
				if coldef['type'] == 'string':
					realCol += 1
			cont += 1
		return realCol
	
	def sameSection(self, Row1, Row2):
		return self.lines[Row1].section == self.lines[Row2].section
	
	def FromLinesOfSection(self, LinesOfSection):
		self.lines = LinesOfSection
