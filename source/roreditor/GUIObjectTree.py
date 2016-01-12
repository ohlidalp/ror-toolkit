from ShapedControls import ShapedWindow
import sys, os, os.path

import wx
import wx.grid
import wx.html
import wx.aui
from ror.settingsManager import *
from ror.rorcommon import *
from ror.lputils import *
from RoRConstants import *
import cStringIO

class RoRObjectTreeCtrl(ShapedWindow):
	def __init__(self, parent, **kwargs):
		ShapedWindow.__init__(self, parent, **kwargs)
		
		self.parent = parent
		#		self._frame = frame
		
		# Auto Open Map stuff
		self.autoOpenItem = None
		self.selectedItem = None
		self.boldedItem = None
		
		self.rordir = rorSettings().rorFolder
		grid = self.grid
		grid.SetEmptyCellSize(wx.Size(120, 40))
		r = 1
		c = 0
		self.mainLabel = wx.StaticText(self, -1, "", size=wx.Size(0, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
		grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))
		
		r = 1
		c = 1
		tree = wx.TreeCtrl(self, -1, size=(250, 300), style=wx.NO_BORDER | wx.TR_HIDE_ROOT)
		grid.Add(tree,
				 pos=wx.GBPosition(r, c))
		self.chkMousePlacement = wx.CheckBox(self, -1, "Place Objects with Middle Mouse Button", wx.DefaultPosition, wx.Size(200, 20))
		self.chkMousePlacement.SetBackgroundColour(ShapedWindow.skinBack)
		self.chkMousePlacement.Bind(wx.EVT_CHECKBOX, self.OnMousePlacement)

		r += 1
		c = 1
		grid.Add(self.chkMousePlacement,
				 pos=wx.GBPosition(r, c))
		
		root = tree.AddRoot("Objects")
		items = []
		
		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
		imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16)))
		tree.AssignImageList(imglist)
		
		self.tree = tree
		self.treeroot = root
		#saves the section node to expand when load finish
		self.scannedExt = ['.terrn', '.truck', '.boat', '.airplane', '.load', '.trailer', '.fixed', '.odef', '.material' , '.mesh', '.cfg', '.machine'  ]
#		allfiles = self.getInstalledFiles(self.scannedExt)
		self._autoOpenMap = rorSettings().getSetting(TOOLKIT, "autoopen")
		t = self.addSection("Terrains", ['*.terrn'], None, True)
		beamobjs = self.tree.AppendItem(self.treeroot, "Beam Objects", 0)
		
		self.addSection("Trucks", ['*.truck'], beamobjs, True)
		self.addSection("Boats", ['*.boat'], beamobjs, True)
		self.addSection("Airplanes", ['*.airplane'], beamobjs, True)
		self.addSection("Loads", ['*.load'], beamobjs, True)
		self.addSection("Trailers", ['*.trailer'], beamobjs, True)
		self.addSection("Statics Structures", ['*.fixed', '*.machine'], beamobjs, True)
		tree.SortChildren(beamobjs)
		o = self.addSection("Objects", ['*.odef'], None, False)
		
		metaobjs = self.tree.AppendItem(self.treeroot, "Meta Files", 0)
		#FIXME: Lepes are needed to load on Object Tree?? spend a lot of time 
#		self.addSection("Materials", ['*.material'], metaobjs, False)
#		self.addSection("Meshes", ['*.mesh'], metaobjs, False)
#		self.addSection("Configurations", ['*.cfg'], metaobjs, False)
		

		
		# no full expand because there are a lot of children
		#expand only first level
#		if t is not None:
#			self.tree.Expand(t) # terrain
#			self.tree.SelectItem(t) #select terrain
#		if o is not None:
#			self.tree.Expand(o) # objects
#		if bo is not None:
#			self.tree.Expand(bo)# beam objects
#		if metaobjs is not None:
#			self.tree.Expand(metaobjs) # materials
 
		

		#		self.GetSizer().SetSizeHints(self)
				
		
		
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelectionChange, self.tree)
		self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClick, self.tree)
		#self.Bind(wx.wxEVT_TREE_BEGIN_DRAG, self.BeginDrag, self.tree)
		
		#initalize variable !!!!
		self.selectedfn = None

		self.SetSizerAndFit(grid)
		self.updateSkin()

	  
	def OnMousePlacement(self, event):
		self.parent.terrainOgreWin.placeWithMouse = not self.parent.terrainOgreWin.placeWithMouse
		event.Skip()
		
	def addSection(self, sectionName, filepattern, parent, UseIngameName):
		""" sectionName, filepattern, parent = None, UseIngameName, files"""
		parent = ifNone(parent, self.treeroot)
		
		files_editable = []
#		files_uneditable=[]
		files = self.getInstalledFiles(filepattern)
		
		for file in files:
			type = 'Zip'
			if file.archive:
				type = file.archive.getType()
#			if type == 'Zip': # Lepes it was 'Filesystem'
			ok = True
			for filecheck in files_editable:
				if filecheck.filename == file.filename:
					ok = False
			if ok:
				files_editable.append(file)
#			else:
#				ok = True
#				for filecheck in files_uneditable:
#					if filecheck.filename == file.filename:
#						ok=False
#				if ok:
#					files_uneditable.append(file)
		log().debug("section %s found %d files" % (sectionName, len(files_editable)))
		section = None
		if len(files_editable) > 0:
			section = self.tree.AppendItem(parent, "%s (%d)" % (sectionName, len(files_editable)), 0)
		
		if len(files_editable) > 0:
#			section_editable = self.tree.AppendItem(section, "Editable (%d)" % len(files_editable), 0)
			for file in files_editable:
				filenameonly, extension = os.path.splitext(os.path.basename(file.filename))
				if len(filenameonly) > 40:
					filenameonly = filenameonly[40:]
				data = wx.TreeItemData()
				data.SetData(file)
				if UseIngameName:
					tmp = loadResourceLine(file.filename, 0)
					if tmp != "":
						filenameonly = tmp
					
				theitem = self.tree.AppendItem(section, filenameonly.lower(), 1, data=data)
				if self.autoOpenMap == file.filename:
					self.selectedItem = theitem
					self.autoOpenMap = file.filename #make it bold
			self.tree.SortChildren(section)

#		if len(files_uneditable) > 0:
#			section_noneditable = self.tree.AppendItem(section, "Non-Editable (%d)" % len(files_uneditable), 0)
#			for file in files_uneditable:
#				filenameonly, extension = os.path.splitext(os.path.basename(file.filename))
#				if len(filenameonly) > 40:
#					filenameonly = filenameonly[40:]
#				data = wx.TreeItemData()
#				data.SetData(file)
#				self.tree.AppendItem(section_noneditable, filenameonly.lower(), 1, data=data)
#			self.tree.SortChildren(section_noneditable)
		if section is not None:
			self.tree.SortChildren(section)
		return section
			
	def OnRightClick(self, event):
		fileinfo = self.tree.GetItemData(event.GetItem()).GetData()		
		if fileinfo is None:
			print "fileinfo is none"
			event.Skip()
			return
		
		self.selectedfn = fileinfo.filename
#		if fileinfo.archive.getType() != 'FileSystem':
#			# no action for non editable files!
#			event.Skip()
#			return
		filenameonly, extension = os.path.splitext(os.path.basename(fileinfo.filename))
		print " file and extension " , filenameonly, extension
		menu = wx.Menu()
		#create various menu entries
		if extension.lower() == ".odef":
			item_edit_odef = menu.Append(wx.ID_ANY, "Edit in ODef Editor")
			self.Bind(wx.EVT_MENU, self.editOdef, item_edit_odef)
			
			m = menu.Append(wx.ID_ANY, "Replace Selected(s)")
			self.Bind(wx.EVT_MENU, self.replaceSelection, m)
		if extension.lower() == ".terrn":
			item_edit_terrain = menu.Append(wx.ID_ANY, "Edit in Terrain Editor")
			self.Bind(wx.EVT_MENU, self.editTerrain, item_edit_terrain)
			
			item_autoOpen_terrain = menu.Append(wx.ID_ANY, "Auto-Open at Start up")
			self.Bind(wx.EVT_MENU, self.AutoOpenTerrain, item_autoOpen_terrain)

			item_DisableAutoOpen_terrain = menu.Append(wx.ID_ANY, "Disable Auto-Open")
			self.Bind(wx.EVT_MENU, self.disableAutoOpenTerrain, item_DisableAutoOpen_terrain)

		if extension.lower() in VALIDSTRUCKS:
			item_edit_truck = menu.Append(wx.ID_ANY, "Edit in Truck Editor")
			self.Bind(wx.EVT_MENU, self.editTruck, item_edit_truck)
		
		menu.AppendSeparator()
		item_add = menu.Append(wx.ID_ANY, "add to Terrain")
		self.Bind(wx.EVT_MENU, self.addObjectToTerrain, item_add)
			
		self.PopupMenu(menu)
		menu.Destroy()
		event.Skip()
		
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
	
	def AutoOpenTerrain(self, event):
		self.autoOpenMap = self.selectedfn
		event.Skip()
		
	def disableAutoOpenTerrain(self, event):
		self.autoOpenMap = ""
		event.Skip()
		
	def addObjectToTerrain(self, event=None):
		if self.selectedfn is None:
			return
		#MainFrame add the object to the terrain
		self.parent.addObjectToTerrain(self.selectedfn)
	#def BeginDrag(self, event):
	#		'''
	#		EVT_TREE_BEGIN_DRAG handler.
	#		'''
	#		self.dragItem = event.GetItem()
	#		fn = self.tree.GetItemData(event.GetItem()).GetData()
	#		if fn is None:
	#			return
	#		#event.Allow()
	#		wx.TreeEvent.Allow(event)
	
	def replaceSelection(self, event):
		self.parent.terrainOgreWin.replaceSelectionWith(self.selectedfn)
		
	def onTreeSelectionChange(self, event=None):
		fileinfo = self.tree.GetItemData(event.GetItem()).GetData()		
		if fileinfo is None:
			event.Skip()
			return
		fn = fileinfo.filename
		self.parent.previewObject(fn)
		self.selectedfn = fn
		self.selectedItem = event.GetItem()
		event.Skip()
	
	def getInstalledFiles(self, extensions):
		files = []
#		extensions = " ".join('*'+x for x in extension)
		for ext in extensions:
			for group in resourceGroupNames.keys():
				filesr = ogre.ResourceGroupManager.getSingleton().findResourceFileInfo(group, extension)
				#			print filesr
				for file in filesr:
					files.append(file)
		return files

	
	def _getautoOpenMap(self):
		return self._autoOpenMap
			
	def _setautoOpenMap(self, value):
		""" _autoOpenMap holds the terrain file "aspen.terrn"
		    boldedItem and selectedItem holds the treeCtrl Item
		    or None
		"""
		if self.boldedItem:
			self.tree.SetItemBold(self.boldedItem, False)
		if self.selectedItem:
			self.tree.SetItemBold(self.selectedItem, True)
			self.boldedItem = self.selectedItem
		rorSettings().setSetting(TOOLKIT, "autoopen", value)			
			
		self._autoOpenMap = value
		
	autoOpenMap = property(_getautoOpenMap, _setautoOpenMap,
						doc="""un/set bold the terrain item that will be autoOpened""")
