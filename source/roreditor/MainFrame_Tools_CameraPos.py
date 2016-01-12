#Lepes 
#===============================================================================
# Make this window visible when a Map is loaded into RoRTerrainOgreWindow
# since CameraWindow need to know where the camera is.
# 
# 
# 
#===============================================================================
import math, glob
import wx, os, os.path, copy
import pickle
import ogre.renderer.OGRE as ogre
from ShapedControls import *
from ror.rorcommon import *
from ror.settingsManager import rorSettings
from ror.lputils import positionClass
from ror.logger import log

class CameraWindow(ShapedWindow):
	
	def __del__(self):
		self.saveCamera()
	
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)
	   
		self.parent = parent
		self.rordir = rorSettings().rorFolder
			

		self.cameraList = []
		# self.cameraList = [ {'name': "camera 1", 'pos': tupleType, 'dir': tupleType ]
		self.lastcount = 0
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(110, 3))
		r = 1
		c = 1
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		#self.mainLabel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))

		
		r += 2
		c = 1		 
		l = wx.StaticText(self, -1, " add a New camera Bookmark called:")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		r += 1
		c = 1
		self.cameraName = wx.TextCtrl(self, -1, "", size=wx.Size(250, 20), style=wx.TE_PROCESS_ENTER)
		self.cameraName.Bind(wx.EVT_TEXT_ENTER, self.OnText)
		grid.Add(self.cameraName,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		r += 1
		c = 1
		self.add = wx.Button(self, -1, "add New camera Position", size=wx.Size(250, 20))
		self.add.Bind(wx.EVT_BUTTON, self.Onadd)
		grid.Add(self.add, pos=wx.GBPosition(r, c))

		r += 2
		c = 1		 
		l = wx.StaticText(self, -1, "Available cameras (left click to go)")
		grid.Add(l,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		r += 1
		c = 1
		# don't sort camera names due inconsistent with self.cameraList
		self.list = wx.ListBox(self, -1, wx.DefaultPosition, wx.Size(250, 180), [], wx.LB_SINGLE | wx.LB_NEEDED_SB)
		self.list.Bind(wx.EVT_LISTBOX, self.Onselect)
		grid.Add(self.list, pos=wx.GBPosition(r, c))

		r += 1
		c = 1
		self.deleteCamera = wx.Button(self, -1, "Delete selected camera or last one", size=wx.Size(250, 20))
		self.deleteCamera.Bind(wx.EVT_BUTTON, self.Ondelete)
		grid.Add(self.deleteCamera, pos=wx.GBPosition(r, c))
		
		r += 1
		c = 1
		# create a panel to put some static labels and TextCtrl on the same row.
		pan = wx.Panel(self, -1, size=wx.Size(250, 20))

		l = wx.StaticText(pan, -1, " normal Velocity", pos=wx.Point(0, 0), size=wx.Size(80, 20))

		self.normalVel = wx.TextCtrl(pan, -1, "", pos=wx.Point(80, 0), size=wx.Size(40, 20), style=wx.TE_PROCESS_ENTER)
		self.normalVel.Bind(wx.EVT_TEXT_ENTER, self.OnnormalVel)
		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))

		r += 1
		c = 1
		pan = wx.Panel(self, -1, size=wx.Size(250, 20))
		
		l = wx.StaticText(pan, -1, " SHIFT Velocity", pos=wx.Point(0, 0), size=wx.Size(80, 20))

		self.shiftVel = wx.TextCtrl(pan, -1, "", pos=wx.Point(80, 0), size=wx.Size(40, 20), style=wx.TE_PROCESS_ENTER)
		self.shiftVel.Bind(wx.EVT_TEXT_ENTER, self.OnshiftVel)

		grid.Add(pan,
				 pos=wx.GBPosition(r, c),
				 span=wx.GBSpan(1, 1))
		
		self.SetSizerAndFit(grid)
		self.updateSkin()
		 



	def loadCamera(self, terrnFile):
		self.cameraList = []
		self.list.Set([])
		barename, self.ext = os.path.splitext(os.path.basename(terrnFile))
		self._file = rorSettings().concatToToolkitHomeFolder(['cameras', '%s.txt' % barename], True)
		
		try:
			if os.path.isfile(self._file):
				input = open(self._file, 'rb')
				if input:
					self.cameraList = pickle.load(input)
					input.close()
				log().info("loaded %d camera Bookmarks" % len(self.cameraList))
		except:
			self.cameraList = []
			log().info("cameraBookmark couldn't be loaded")
			
		self.lastcount = len(self.cameraList)
		self.list.Set(self.getValues())
		
	def getValues(self):
		v = []
		for i in range(0, len(self.cameraList)):
			v.append(self.cameraList[i]['name'])
		self.cameraName.ChangeValue("camera %03d" % self.lastcount)
		return v
		
	def saveCamera(self, terrnFile=None):
		if self.cameraList and (len(self.cameraList) > 0):
			log().debug("saving %d cameras" % len(self.cameraList))
			if terrnFile is not None:
				barename, self.ext = os.path.splitext(os.path.basename(terrnFile))
				self._file = rorSettings().concatToToolkitHomeFolder(['cameras', '%s.txt' % barename], True)
			output = open(self._file, 'wb')
			if output:
				pickle.dump(self.cameraList, output, 0)
				output.close()
				log().debug("cameras saved to %s" % self._file)

		
	def OnLeftDown(self, event):
		ShapedWindow.OnLeftDown(self, event)
		event.Skip()
		
	def Onadd(self, event):
		# add new bookmark
		s = self.cameraName.GetValue().strip()

		p, d = self.parent.terrainOgreWin.getCamera()
		self.cameraAdd(s, p, d)  #replace selection
		event.Skip()				


	def cameraExists(self, cameraName):
		for i in range(0, len(self.cameraList)):
			if cameraName == self.cameraList[i]['name']:
				return i
		return - 1
	
	def cameraAdd(self, name, tuplePos=(0, 0, 0), tupleDir=(0, 0, 0)):			
		idx = self.cameraExists(name)
		if idx > -1:
			self.cameraList[idx] = {'name' : name, 'pos': tuplePos, 'dir': tupleDir }
		else:
			self.cameraList.append({'name' : name, 'pos': tuplePos, 'dir': tupleDir })
		v = self.getValues()
		self.list.Set(v) # maintain syncrhonization
		self.lastcount += 1
		self.cameraName.ChangeValue("camera %03d" % self.lastcount)		
	
	def Onselect(self, event):
		#mouse down on listbox
		s = event.GetString().strip()
		for i in range (0, len(self.cameraList)):
			if s == self.cameraList[i]['name']:
				self.parent.terrainOgreWin.setCamera(self.cameraList[i]['pos'], \
														self.cameraList[i]['dir'])
			
		event.Skip()
		
	def OnText(self, event):
		# return key on camera Text control
		self.Onadd(event)
		event.Skip()
			
	def OnnormalVel(self, event):	
		vel = ShapedWindow.checkValidChars(self, event.GetString())
		self.parent.terrainOgreWin.cameraVel = vel
		event.Skip()

	def OnshiftVel(self, event):	
		vel = ShapedWindow.checkValidChars(self, event.GetString())
		self.parent.terrainOgreWin.cameraShiftVel = vel
		event.Skip()
	def updateVelocity(self, normalVel, shiftVel):
		if normalVel > 0.0:
			self.normalVel.SetValue("%.1f" % normalVel)
		if shiftVel > 0.0:
			self.shiftVel.SetValue("%.1f" % shiftVel)
		
	def Ondelete(self, evt):
		# delete selected camera position
		sel = self.list.GetSelection()
		l = len(self.cameraList)
		if sel == wx.NOT_FOUND and l > 0:
			sel = l - 1
		if sel < l:
			del self.cameraList[sel]
			self.list.Set(self.getValues())
		if len(self.cameraList) == 0:
			self.lastcount = 0
		
		evt.Skip()		
	
	 
