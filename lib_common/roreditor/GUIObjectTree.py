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

		self.tree = tree
		self.treeroot = root
		
		self.addSection("Terrains", ['*.terrn'])
		
		beamobjs = self.tree.AppendItem(self.treeroot, "Beam Objects", 0)
		self.addSection("Trucks", ['*.truck'], beamobjs)
		self.addSection("Boats", ['*.boat'], beamobjs)
		self.addSection("Airplanes", ['*.airplane'], beamobjs)
		self.addSection("Loads", ['*.load'], beamobjs)
		self.addSection("Trailers", ['*.trailer'], beamobjs)

		self.addSection("Objects", ['*.odef'])

		metaobjs = self.tree.AppendItem(self.treeroot, "Meta Files", 0)
		self.addSection("Materials", ['*.material'], metaobjs)
		self.addSection("Meshes", ['*.mesh'], metaobjs)
		self.addSection("Configurations", ['*.cfg'], metaobjs)
		
		# root is hidden, no expand!
		#tree.Expand(root)
		vert.Add(tree, 1, wx.EXPAND, 5)
		self.SetSizer(vert)
		self.GetSizer().SetSizeHints(self)
				
		
		
		# this dows not work :(
		#self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick, self.tree)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelectionChange, self.tree)
		self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClick, self.tree)
		
		#self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.BeginDrag, self.tree)
	
	def addSection(self, sectionName, filepattern, parent=None):
		if parent is None:
			parent = self.treeroot
		
		files=[]
		for pattern in filepattern:
			#print pattern
			newfiles = self.getInstalledFiles(pattern)
			for newfile in newfiles:
				files.append(newfile)
		
		#print files
		
		files_editable=[]
		files_uneditable=[]
		for file in files:
			type = 'FileSystem'
			if file.archive:
				type = file.archive.getType()
			if type == 'FileSystem':
				ok = True
				for filecheck in files_editable:
					if filecheck.filename == file.filename:
						ok=False
				if ok:
					files_editable.append(file)
			else:
				ok = True
				for filecheck in files_uneditable:
					if filecheck.filename == file.filename:
						ok=False
				if ok:
					files_uneditable.append(file)
		
		section = None
		if len(files_editable) > 0 or len(files_uneditable) > 0:
			section = self.tree.AppendItem(parent, "%s (%d)" % (sectionName, len(files_editable) + len(files_uneditable)), 0)
		
		if len(files_editable) > 0:
			section_editable = self.tree.AppendItem(section, "Editable (%d)" % len(files_editable), 0)
			for file in files_editable:
				filenameonly, extension = os.path.splitext(os.path.basename(file.filename))
				if len(filenameonly) > 40:
					filenameonly = filenameonly[40:]
				data = wx.TreeItemData()
				data.SetData(file)
				self.tree.AppendItem(section_editable, filenameonly, 1, data=data)

		if len(files_uneditable) > 0:
			section_noneditable = self.tree.AppendItem(section, "Non-Editable (%d)" % len(files_uneditable), 0)
			for file in files_uneditable:
				filenameonly, extension = os.path.splitext(os.path.basename(file.filename))
				if len(filenameonly) > 40:
					filenameonly = filenameonly[40:]
				data = wx.TreeItemData()
				data.SetData(file)
				self.tree.AppendItem(section_noneditable, filenameonly, 1, data=data)
		
			
	
	def OnLeftDClick(self, event):
		#this is just a shortcut!
		fileinfo = self.tree.GetItemData(event.GetItem()).GetData()        
		if fileinfo is None:
			event.Skip()
			return
		self.selectedfn = fileinfo.filename
		if fileinfo.archive.getType() != 'FileSystem':
			# no action for non editable files!
			return
		filenameonly, extension = os.path.splitext(os.path.basename(fileinfo.filename))
		if extension.lower() == ".odef":
			self.editOdef()
		if extension.lower() == ".terrn":
			self.editTerrain()
		if extension.lower() in ['.truck', '.load', '.trailer', '.airplane', '.boat']:
			self.editTruck()
		
	def OnRightClick(self, event):
		fileinfo = self.tree.GetItemData(event.GetItem()).GetData()        
		if fileinfo is None:
			event.Skip()
			return
		
		self.selectedfn = fileinfo.filename
		if fileinfo.archive.getType() != 'FileSystem':
			# no action for non editable files!
			event.Skip()
			return
		filenameonly, extension = os.path.splitext(os.path.basename(fileinfo.filename))
		
		menu = wx.Menu()
		#create various menu entries
		if extension.lower() == ".odef":
			item_edit_odef = menu.Append(wx.ID_ANY, "Edit in ODef Editor")
			self.Bind(wx.EVT_MENU, self.editOdef, item_edit_odef)
		if extension.lower() == ".terrn":
			item_edit_terrain = menu.Append(wx.ID_ANY, "Edit in Terrain Editor")
			self.Bind(wx.EVT_MENU, self.editTerrain, item_edit_terrain)
		if extension.lower() in ['.truck', '.load', '.trailer', '.airplane', '.boat']:
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
		fileinfo = self.tree.GetItemData(event.GetItem()).GetData()        
		if fileinfo is None:
			event.Skip()
			return
		fn = fileinfo.filename
		self.parent.previewObject(fn)
	
	def getInstalledFiles(self, extension):
		files = []
		filesr = ogre.ResourceGroupManager.getSingleton().findResourceFileInfo("General", extension)
		for file in filesr:
			files.append(file)
		return files
