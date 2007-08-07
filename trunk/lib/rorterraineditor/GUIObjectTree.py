import sys, os, os.path

import wx
import wx.grid
import wx.html
import wx.aui
import ror.settingsManager

import cStringIO

RORPATH = ror.settingsManager.getSettingsManager().getSetting("RigsOfRods", "BasePath")
DATADIR     = os.path.join(RORPATH, "data")
TRUCKDIR    = os.path.join(DATADIR, "trucks")
TERRAINDIR  = os.path.join(DATADIR, "terrains")
OBJECTDIR   = os.path.join(DATADIR, "objects")

class RoRObjectTreeCtrl(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition,
                          wx.DefaultSize)

        self.parent = parent
        self._frame = frame
        

        vert = wx.BoxSizer(wx.VERTICAL)


        tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.DefaultSize, wx.NO_BORDER | wx.TR_HIDE_ROOT)
        
        root = tree.AddRoot("Objects")
        items = []

        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
        tree.AssignImageList(imglist)

        trucks = self.getInstalledTrucks()
        items.append(tree.AppendItem(root, "Trucks", 0))
        for truck in trucks:
            truckname, extension = os.path.splitext(os.path.basename(truck))
            data = wx.TreeItemData()
            data.SetData(truck)
            tree.AppendItem(items[-1], truckname, 1, data=data)

        loads = self.getInstalledLoads()
        items.append(tree.AppendItem(root, "Loads", 0))
        for load in loads:
            loadname, extension = os.path.splitext(os.path.basename(load))
            data = wx.TreeItemData()
            data.SetData(load)
            tree.AppendItem(items[-1], loadname, 1, data=data)
            
        objects = self.getInstalledObjects()
        items.append(tree.AppendItem(root, "Objects", 0))
        for object in objects:
            objectname, extension = os.path.splitext(os.path.basename(object))
            data = wx.TreeItemData()
            data.SetData(object)
            tree.AppendItem(items[-1], objectname, 1, data=data)

        # root is hidden, no expand!
        #tree.Expand(root)
        vert.Add(tree, 1, wx.EXPAND, 5)
        self.SetSizer(vert)
        self.GetSizer().SetSizeHints(self)
                
        self.tree = tree
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelectionChange, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClick, self.tree)
        
        #self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.BeginDrag, self.tree)
    def OnLeftDClick(self, event):
        self.selectedfn = self.tree.GetItemData(event.GetItem()).GetData()
        self.addStuff()
        
    def OnRightClick(self, event):
        self.selectedfn = self.tree.GetItemData(event.GetItem()).GetData()
        if self.selectedfn is None:
            event.Skip()
            return
        
        menu = wx.Menu()
        item_add = menu.Append(wx.ID_ANY, "add to Terrain")
        self.Bind(wx.EVT_MENU, self.addStuff, item_add)
        if self.selectedfn[-4:].lower() == "odef":
            #create odef menu entry
            item_edit_odef = menu.Append(wx.ID_ANY, "Edit in ODef Editor")
            self.Bind(wx.EVT_MENU, self.editOdef, item_edit_odef)
        self.PopupMenu(menu)
        menu.Destroy()
        
    def editOdef(self, event=None):
        if self.selectedfn is None:
            return
        self.parent.editODefFile(self.selectedfn)
        
    def addStuff(self, event=None):
        if self.selectedfn is None:
            return
        self.parent.addStuff(self.selectedfn)
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
        
    def getInstalledTrucks(self):
        files = []
        for filename in os.listdir(TRUCKDIR):
            onlyfilename, extension = os.path.splitext(filename)
            if extension.lower() == ".truck":
                files.append(os.path.join(TRUCKDIR, filename))
        files.sort()
        return files

    def getInstalledLoads(self):
        files = []
        for filename in os.listdir(TRUCKDIR):
            onlyfilename, extension = os.path.splitext(filename)
            if extension.lower() == ".load":
                files.append(os.path.join(TRUCKDIR, filename))
        files.sort()
        return files

    def getInstalledObjects(self):
        files = []
        for filename in os.listdir(OBJECTDIR):
            onlyfilename, extension = os.path.splitext(filename)
            if extension.lower() == ".odef":
                files.append(os.path.join(OBJECTDIR, filename))
        files.sort()
        return files