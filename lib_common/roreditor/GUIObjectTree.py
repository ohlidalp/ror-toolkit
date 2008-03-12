import sys, os, os.path

import wx
import wx.grid
import wx.html
import wx.aui
import ror.settingsManager
from ror.rorcommon import *

import cStringIO

class RoRObjectTreeCtrl(wx.Panel):
	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition,
						  wx.DefaultSize)

		self.parent = parent
		self._frame = frame
		
		self.rordir = ror.settingsManager.getSettingsManager().getSetting("RigsOfRods", "BasePath")
		initResources(self.rordir)	

		vert = wx.BoxSizer(wx.VERTICAL)


		tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.DefaultSize, wx.NO_BORDER | wx.TR_HIDE_ROOT)
		
		root = tree.AddRoot("Objects")
		items = []

		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
		tree.AssignImageList(imglist)

		terrains = tree.AppendItem(root, "Terrains", 0)
		terrains_editable = tree.AppendItem(terrains, "editable", 0)
		terrains_noneditable = tree.AppendItem(terrains, "Non-Editable", 0)
		
		terrainfiles = self.getInstalledTerrains("*.terrn")
		for terrain in terrainfiles:
			terrainname, extension = os.path.splitext(os.path.basename(terrain))
			data = wx.TreeItemData()
			data.SetData(terrain)
			tree.AppendItem(items[-1], terrainname, 1, data=data)
		

		# root is hidden, no expand!
		#tree.Expand(root)
		vert.Add(tree, 1, wx.EXPAND, 5)
		self.SetSizer(vert)
		self.GetSizer().SetSizeHints(self)
				
		self.tree = tree
		
		# this dows not work :(
		#self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick, self.tree)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelectionChange, self.tree)
		self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClick, self.tree)
		
		#self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.BeginDrag, self.tree)
	def OnLeftDClick(self, event):
		#this is just a shortcut!
		self.selectedfn = self.tree.GetItemData(event.GetItem()).GetData()        
		if self.selectedfn[-4:].lower() == "odef":
			self.editOdef()
		if self.selectedfn[-5:].lower() == "terrn":
			self.editTerrain()
		if self.selectedfn[-5:].lower() == 'truck' or self.selectedfn[-4:].lower() == 'load':
			self.editTruck()
		
	def OnRightClick(self, event):
		self.selectedfn = self.tree.GetItemData(event.GetItem()).GetData()
		if self.selectedfn is None:
			event.Skip()
			return
		
		menu = wx.Menu()
		
		#create various menu entries
		if self.selectedfn[-4:].lower() == "odef":
			item_edit_odef = menu.Append(wx.ID_ANY, "Edit in ODef Editor")
			self.Bind(wx.EVT_MENU, self.editOdef, item_edit_odef)
		if self.selectedfn[-5:].lower() == "terrn":
			item_edit_terrain = menu.Append(wx.ID_ANY, "Edit in Terrain Editor")
			self.Bind(wx.EVT_MENU, self.editTerrain, item_edit_terrain)
		if self.selectedfn[-5:].lower() == 'truck' or self.selectedfn[-4:].lower() == 'load':
			item_edit_truck = menu.Append(wx.ID_ANY, "Edit in Truck Editor")
			self.Bind(wx.EVT_MENU, self.editTruck, item_edit_truck)
		menu.AppendSeparator()
		item_add = menu.Append(wx.ID_ANY, "add to Terrain")
		self.Bind(wx.EVT_MENU, self.addObjectToTerrain, item_add)
			
		self.PopupMenu(menu)
		menu.Destroy()
		
	def editTruck(self, event=None):
		if self.selectedfn is None:
			return
		self.parent.editTruck(self.selectedfn)
	
	def editOdef(self, event=None):
		if self.selectedfn is None:
			return
		self.parent.editODefFile(self.selectedfn)

	def editTerrain(self, event=None):
		if self.selectedfn is None:
			return
		self.parent.openTerrain(self.selectedfn)
		
	def addObjectToTerrain(self, event=None):
		if self.selectedfn is None:
			return
		self.parent.addObjectToTerrain(self.selectedfn)
	#def BeginDrag(self, event):
	#        '''
	#        EVT_TREE_BEGIN_DRAG handler.
	#        '''
	#        self.dragItem = event.GetItem()
	#        fn = self.tree.GetItemData(event.GetItem()).GetData()
	#        if fn is None:
	#            return
	#        #event.Allow()
	#        wx.TreeEvent.Allow(event)
	
	def onTreeSelectionChange(self, event=None):
		fn = self.tree.GetItemData(self.tree.GetSelection()).GetData()
		if fn is None:
			return
		self.parent.previewObject(fn)
	
	def getInstalledFiles(self, extension):
		files = []
		filesr = ogre.ResourceGroupManager.getSingleton().findResourceFileInfo("General", extension)
		for file in filesr:
			files.append(file)
		return files
