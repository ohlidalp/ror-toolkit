
import wx

_bg_color = wx.Color(254, 184, 0) # Default orange. TODO: Make properly configurable

class TerrainImportSelectorWindow(wx.Frame):
	"""
	Displays a list of .terrn/terrn2 available for import.

	:attribute function callback_terrn_import: 1 parameter: str terrn filename
	:attribute function callback_cancel: no parameters
	"""

	def __init__(self, parent, app, **kwargs):
		# Setup wxPython window
		styles = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
		title = "Import terrain | RoRToolkit"
		wx.Frame.__init__(self, parent, -1, title, style=styles, **kwargs)
		self.SetBackgroundColour(_bg_color)
		self.Bind(wx.EVT_CLOSE, self._on_close_window)

		self._application = app
		self.callback_terrn_import = None
		self.callback_cancel = None

		grid = wx.GridBagSizer(2, 2)
		grid.SetEmptyCellSize(wx.Size(110, 3))
		row = 0
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (row,0)) # Col 0
		grid.AddSpacer(spacer_size, (row,2)) # Col 2

		row += 1
		lbl_style = wx.ST_NO_AUTORESIZE | wx.TRANSPARENT_WINDOW
		lbl_text = "Searching for terrains..."
		self._status_text_label = wx.StaticText(self, -1, lbl_text, size=wx.Size(0, 20), style=lbl_style)
		grid.Add(self._status_text_label, pos=wx.GBPosition(row, 1))

		# Project selector
		# TODO: Use a better suited component
		row += 1
		self._tree = wx.TreeCtrl(self, -1, size=(265, 360), style=wx.NO_BORDER | wx.TR_HIDE_ROOT)
		grid.Add(self._tree, pos=wx.GBPosition(row, 1))
		self._tree_root = self._tree.AddRoot("Terrains")

		# [Import] button
		row += 1
		self._import_terrn_button = wx.Button(self, -1, "Import selected terrain")
		self._import_terrn_button.Enabled = False
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
		import os.path
		for terrn_filename in terrn_list:
			self._tree.AppendItem(self._tree_root, terrn_filename)

	def _cancel_import(self):
		self.Hide()
		if self.callback_cancel is not None:
			fn = self.callback_cancel
			fn()
	
	def _on_import_button_pressed(self, event):
		pass # TODO

	def _on_cancel_button_pressed(self, event):
		self._cancel_import()

	def _on_close_window(self, event):
		event.Veto() # Don't destroy the window!
		self._cancel_import()


