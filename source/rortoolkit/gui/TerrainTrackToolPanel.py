
import wx

_bg_color = wx.Color(254, 184, 0) # Default orange. TODO: Make properly configurable

class TerrainTrackToolPanel(wx.Frame):
	"""
	TrackTool state and controls.
	Work in progress.
	"""

	def __init__(self, parent, **kwargs):
		import rortoolkit.gui

		# Setup wxPython window
		styles = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.FRAME_NO_TASKBAR
		title = "Track tool | RoRToolkit"
		wx.Frame.__init__(self, parent, -1, title, style=styles, **kwargs)
		self.SetBackgroundColour(_bg_color)
		self.Bind(wx.EVT_CLOSE, self._on_close_window)

		grid = wx.GridBagSizer(2, 2)
		grid.SetEmptyCellSize(wx.Size(110, 3))
		row = 0
		max_width = 350
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (row,0)) # Col 0
		grid.AddSpacer(spacer_size, (row,2)) # Col 2

		row += 1
		self._cursor_pos_label = wx.StaticText(self, -1, "")
		grid.Add(self._cursor_pos_label, pos=wx.GBPosition(row, 1))

		# Bottom padding
		row += 1
		grid.AddSpacer(spacer_size, (row, 1))

		self.SetSizerAndFit(grid)

	def set_cursor_pos_text(self, text):
		self._cursor_pos_label.SetLabel(text)

	def _on_close_window(self, event):
		event.Veto() # Don't destroy the window!
