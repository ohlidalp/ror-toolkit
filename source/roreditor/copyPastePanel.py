import wx

class CopyPasteClass(wx.Panel):
	def __init__(self, parent, **kwards):
		""" parent, backgroundColor, **kwards"""
		wx.Panel.__init__(self, parent, -1, **kwards)

	def addButtons(self, OnCopy, OnPaste, OnReset, lastLeft=0):
		""" events that will define how many buttons it will have
		
		first is the event called on Copy pressed button
		second is the event called on Paste pressed button
		third is the event called on Reset pressed button
		
		if any of the events is None, the button will not be created. 
		"""
		
		if OnCopy is not None:
			self.copy = wx.Button(self, -1, "C", pos=wx.Point(lastLeft, 0), size=wx.Size(20, 20))
			self.copy.Bind(wx.EVT_BUTTON, OnCopy)
			lastLeft += 20

		if OnPaste is not None:
			self.paste = wx.Button(self, -1, "P", pos=wx.Point(lastLeft, 0), size=wx.Size(20, 20))
			self.paste.Bind(wx.EVT_BUTTON, OnPaste)
			lastLeft += 20

		if OnReset is not None:
			self.reset = wx.Button(self, -1, "R", pos=wx.Point(lastLeft, 0), size=wx.Size(20, 20))
			self.reset.Bind(wx.EVT_BUTTON, OnReset)
			lastLeft += 20
		
