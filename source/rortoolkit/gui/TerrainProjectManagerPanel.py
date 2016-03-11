
import wx

_bg_color = wx.Color(254, 184, 0) # Default orange. TODO: Make properly configurable

class TerrainProjectManagerPanel(wx.Frame):
	def __init__(self, parent, app, **kwargs):
		# Setup wxPython window
		styles = wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW | wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT
		title = "Terrain projects"
		wx.Frame.__init__(self, parent, -1, title, style=styles, **kwargs)
		self.SetBackgroundColour(_bg_color)
		self.Bind(wx.EVT_CLOSE, self._on_close_window)

		self._application = app
		self._selected_project_dirname = None
		self.callback_import_button_pressed = None
		self.callback_open_button_pressed = None

		grid = wx.GridBagSizer(2, 2)
		grid.SetEmptyCellSize(wx.Size(110, 3))
		row = 0
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (row,0)) # Col 0
		grid.AddSpacer(spacer_size, (row,2)) # Col 2

		row += 1
		self._project_count_label = wx.StaticText(self, -1, "No projects found", size=wx.Size(0, 20))
		grid.Add(self._project_count_label, pos=wx.GBPosition(row, 1))

		# Project selector
		# TODO: Use a better suited component
		row += 1
		self._tree = wx.TreeCtrl(self, -1, size=(265, 360), style=wx.NO_BORDER | wx.TR_HIDE_ROOT)
		grid.Add(self._tree, pos=wx.GBPosition(row, 1))
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_item_selected, self._tree)
		self._tree_root = self._tree.AddRoot("Terrains")

		# [Open] button
		row += 1
		self._open_project_button = wx.Button(self, -1, "Open selected project")
		self._open_project_button.Enabled = False
		self._open_project_button.Bind(wx.EVT_BUTTON, self._on_open_button_pressed)
		grid.Add(self._open_project_button, pos=wx.GBPosition(row, 1))

		# [Import] button
		row += 1
		self._import_map_button = wx.Button(self, -1, "Import existing terrain")
		self._import_map_button.Bind(wx.EVT_BUTTON, self._on_import_button_pressed)
		grid.Add(self._import_map_button, pos=wx.GBPosition(row, 1))

		# Bottom padding
		row += 1
		grid.AddSpacer(spacer_size, (row, 1))

		self.SetSizerAndFit(grid)
	
	def populate_project_list(self, project_list):
		for dirname in project_list:
			self._tree.AppendItem(self._tree_root, dirname)
		text = str(len(project_list)) + " projects"
		self._project_count_label.SetLabel(text)

	def _on_import_button_pressed(self, event):
		if self.callback_import_button_pressed is not None:
			fn = self.callback_import_button_pressed
			fn()

	def _on_open_button_pressed(self, event):
		fn = self.callback_open_button_pressed
		if fn is not None:
			fn(self._selected_project_dirname)

	def _on_close_window(self, event):
		event.Veto() # Don't destroy the window!
		self.Hide()

	def _on_tree_item_selected(self, event):
		self._open_project_button.Enable()
		item_id = event.GetItem()
		item_text = self._tree.GetItemText(item_id)
		self._selected_project_dirname = item_text


