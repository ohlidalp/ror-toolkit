
import wx

class AutoGaugeWidget(wx.Gauge):
	"""wxPython Gauge with auto-updating indeterminate mode"""

	def __init__(self, parent, size):
		wx.Gauge.__init__(self, parent, size = size)
		self._timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)

	def _on_timer(self, event):
		self.Pulse()

	def start_auto_pulse(self, interval):
		self._timer.Start(interval)

	def stop_auto_pulse(self):
		self._timer.Stop()

