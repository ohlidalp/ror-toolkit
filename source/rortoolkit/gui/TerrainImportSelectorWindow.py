
import wx

_bg_color = wx.Color(254, 184, 0) # Default orange. TODO: Make properly configurable

class TerrainImportSelectorWindow(wx.Frame):
	"""
	Displays a list of .terrn/terrn2 available for import.

	:attribute function callback_terrn_import: 1 parameter: str terrn filename
	:attribute function callback_cancel: no parameters
	"""

	def __init__(self, parent, app, **kwargs):
		import rortoolkit.gui

		# Setup wxPython window
		styles = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
		title = "Import terrain | RoRToolkit"
		wx.Frame.__init__(self, parent, -1, title, style=styles, **kwargs)
		self.SetBackgroundColour(_bg_color)
		self.Bind(wx.EVT_CLOSE, self._on_close_window)

		self._application = app
		self._selected_filename = None
		self.callback_perform_import = None
		self.callback_cancel_import = None

		grid = wx.GridBagSizer(2, 2)
		grid.SetEmptyCellSize(wx.Size(110, 3))
		row = 0
		max_width = 350
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (row,0)) # Col 0
		grid.AddSpacer(spacer_size, (row,2)) # Col 2

		# Project selector
		row += 1
		tree_id = wx.NewId()
		self._tree = wx.TreeCtrl(self, tree_id, size=(max_width, 360), style=wx.NO_BORDER | wx.TR_HIDE_ROOT)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_item_selected, self._tree)
		grid.Add(self._tree, pos=wx.GBPosition(row, 1))
		self._tree_root = self._tree.AddRoot("Terrains")

		row += 1
		self._status_text_label = wx.StaticText(self, -1, "")
		grid.Add(self._status_text_label, pos=wx.GBPosition(row, 1))

		# [Import] button
		row += 1
		self._import_terrn_button = wx.Button(self, -1, "Import selected terrain")
		self._import_terrn_button.Disable()
		self._import_terrn_button.Bind(wx.EVT_BUTTON, self._on_import_button_pressed)
		grid.Add(self._import_terrn_button, pos=wx.GBPosition(row, 1))

		# [Cancel] button
		row += 1
		self._cancel_button = wx.Button(self, -1, "Cancel")
		self._cancel_button.Bind(wx.EVT_BUTTON, self._on_cancel_button_pressed)
		grid.Add(self._cancel_button, pos=wx.GBPosition(row, 1))

		# Bottom padding
		row += 1
		grid.AddSpacer(spacer_size, (row, 1))

		self.SetSizerAndFit(grid)

	def set_status_text(self, text):
		self._status_text_label.SetLabel(text)

	def assign_terrains(self, terrn_list):
		for terrn_filename in terrn_list:
			self._tree.AppendItem(self._tree_root, terrn_filename)
		self.set_status_text("Found {0} terrns".format(len(terrn_list)))

	def _cancel_import(self):
		self.Hide()
		if self.callback_cancel_import is not None:
			fn = self.callback_cancel_import
			fn()
	
	def _on_import_button_pressed(self, event):
		if self.callback_perform_import is not None:
			fn = self.callback_perform_import
			fn(self._selected_filename)

	def _on_cancel_button_pressed(self, event):
		self._cancel_import()

	def _on_close_window(self, event):
		event.Veto() # Don't destroy the window!
		self._cancel_import()

	def _on_tree_item_selected(self, event):
		self._import_terrn_button.Enable()
		item_id = event.GetItem()
		item_text = self._tree.GetItemText(item_id)
		self._selected_filename = item_text
		self.set_status_text("Selected: " + item_text)

