
import wx

_bg_color = wx.Color(254, 184, 0) # Default orange. TODO: Make properly configurable

class ProgressWindow(wx.Frame):
	"""
	Displays a message and progress bar. For general use.
	"""

	def __init__(self, parent, **kwargs):
		import rortoolkit.gui

		# Setup wxPython window
		styles = wx.DEFAULT_FRAME_STYLE
		title = "Task progress | RoRToolkit"
		wx.Frame.__init__(self, parent, -1, title, style=styles, **kwargs)
		self.SetBackgroundColour(_bg_color)
		self.Bind(wx.EVT_CLOSE, self._on_close_window)

		grid = wx.GridBagSizer(2, 2)
		grid.SetEmptyCellSize(wx.Size(110, 3))
		self._sizer = grid
		row = 0
		max_width = 350
		
		# Window padding - sides
		spacer_size = (6,6)
		grid.AddSpacer(spacer_size, (row,0)) # Col 0
		grid.AddSpacer(spacer_size, (row,2)) # Col 2

		row += 1
		lbl_text = "Please wait."
		self._status_text_label = wx.StaticText(self, -1, lbl_text, size = (max_width, 50))
		grid.Add(self._status_text_label, pos=wx.GBPosition(row, 1))

		row += 1
		self._progress_bar = rortoolkit.gui.AutoGaugeWidget(self, size = (max_width, 20))
		grid.Add(self._progress_bar, pos = wx.GBPosition(row, 1))
		self._progress_bar.start_auto_pulse(50)
		
		# Bottom padding
		row += 1
		grid.AddSpacer(spacer_size, (row, 1))

		self.SetSizerAndFit(grid)

	def set_status_text(self, text):
		self._status_text_label.SetLabel(text)

	def setup(self, title, text):
		self.SetTitle(title)
		self.set_status_text(text)
		self._progress_bar.stop_auto_pulse()
		self.SetSizerAndFit(self._sizer)

	def progressbar_autopulse_start(self, interval_milisec):
		self._progress_bar.start_auto_pulse(interval_milisec)

	def _on_close_window(self, event):
		event.Veto() # Closed externally

