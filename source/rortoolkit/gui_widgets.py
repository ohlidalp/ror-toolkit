
import wx

class ImagePanelWidget(wx.Panel):
	""" creates a panel with an image on it, inherits wx.Panel """
	
	def __init__(self, parent, id, image_file_path):
		wx.Panel.__init__(self, parent, id)
		try:
			image = wx.Image(image_file_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			wx.StaticBitmap(self, wx.ID_ANY, image, (0, 0), (image.GetWidth(), image.GetHeight()))
		except:
			raise RuntimeError("Cannot open image file: " + image_file_path)
