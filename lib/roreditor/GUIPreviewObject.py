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

        self._frame = frame
        

        vert = wx.BoxSizer(wx.VERTICAL)


        tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.DefaultSize, wx.NO_BORDER)
        
        root = tree.AddRoot("Objects")
        items = []

        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
        tree.AssignImageList(imglist)

        trucks = self.getInstalledTrucks()
        items.append(tree.AppendItem(root, "Trucks", 0))
        for truck in trucks:
            truckname, extension = os.path.splitext(truck)
            tree.AppendItem(items[-1], truckname, 1)

        objects = self.getInstalledObjects()
        items.append(tree.AppendItem(root, "Objects", 0))
        for object in objects:
            objectname, extension = os.path.splitext(object)
            tree.AppendItem(items[-1], objectname, 1)

            
        tree.Expand(root)
        vert.Add(tree, 1, wx.EXPAND, 5)
        self.SetSizer(vert)
        self.GetSizer().SetSizeHints(self)

    def getInstalledTrucks(self):
        files = []
        for filename in os.listdir(TRUCKDIR):
            onlyfilename, extension = os.path.splitext(filename)
            if extension.lower() == ".truck":
                files.append(filename)
        return files

    def getInstalledObjects(self):
        files = []
        for filename in os.listdir(OBJECTDIR):
            onlyfilename, extension = os.path.splitext(filename)
            if extension.lower() == ".odef":
                files.append(filename)
        return files