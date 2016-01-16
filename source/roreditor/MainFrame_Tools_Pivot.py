# Lepes 

import sys, os, os.path

from ror.logger import log
from ror.settingsManager import rorSettings
from ShapedControls import ShapedWindow

import wx
import wx.aui

import cStringIO


class PivotControlWindow(ShapedWindow):
    def __init__(self, parent, **kwargs):
        skin = 'PivotControls.png'
        ShapedWindow.__init__(self, parent, skinOnlyFilename=skin, **kwargs)
#        self._frame = frame
        self.parent = parent
        grid = wx.GridBagSizer(2, 3) # first row is invisible due skin
        grid.SetEmptyCellSize(wx.Size(40, 40))
        r = 1
        c = 0
        self.mainLabel = wx.StaticText(self, -1, "Pivots Controls", size=wx.Size(120, 20), style=wx.TRANSPARENT_WINDOW | wx.ST_NO_AUTORESIZE)
#        self.mainLabel.Wrap(50)
        self.mainLabel.SetBackgroundColour(self.skinBack)
        self.mainLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        #self.mainLabel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        grid.Add(self.mainLabel, pos=wx.GBPosition(r, c), span=wx.GBSpan(1, 1))

# ----- first row of controls
        self.rotxP = wx.Button(self, -1, label="rot x +", size=wx.Size(40, 40))
        self.rotxP.Bind(wx.EVT_BUTTON, self.OnrotxP)
        r = 1
        c = 1
        grid.Add(self.rotxP,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.up = wx.Button(self, -1, label="UP", size=wx.Size(40, 40))
        self.up.Bind(wx.EVT_BUTTON, self.Onup)
        c += 2
        grid.Add(self.up,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.rotzP = wx.Button(self, -1, label="rot z +", size=wx.Size(40, 40))
        self.rotzP.Bind(wx.EVT_BUTTON, self.OnrotzP)
        c += 2
        grid.Add(self.rotzP,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.resetx = wx.Button(self, -1, label="Reset x", size=wx.Size(40, 40))
        self.resetx.Bind(wx.EVT_BUTTON, self.Onresetx)
        c += 1
        grid.Add(self.resetx,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))


# ------
# ----- second row

        self.rotyP = wx.Button(self, -1, label="rot y +", size=wx.Size(40, 40))
        self.rotyP.Bind(wx.EVT_BUTTON, self.OnrotyP)
        r += 1
        c = 1
        grid.Add(self.rotyP,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))
        self.left = wx.Button(self, -1, label="LEFT", size=wx.Size(40, 40))
        self.left.Bind(wx.EVT_BUTTON, self.Onleft)
        c += 1
        grid.Add(self.left,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.right = wx.Button(self, -1, label="RIGHT", size=wx.Size(40, 40))
        self.right.Bind(wx.EVT_BUTTON, self.Onright)
        c += 2
        grid.Add(self.right,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.rotyM = wx.Button(self, -1, label="rot y -", size=wx.Size(40, 40))
        self.rotyM.Bind(wx.EVT_BUTTON, self.OnrotyM)
        c += 1
        grid.Add(self.rotyM,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.resety = wx.Button(self, -1, label="Reset y", size=wx.Size(40, 40))
        self.resety.Bind(wx.EVT_BUTTON, self.Onresety)
        c += 1
        grid.Add(self.resety,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))


# ------

# -----
        self.rotxM = wx.Button(self, -1, label="rot x -", size=wx.Size(40, 40))
        self.rotxM.Bind(wx.EVT_BUTTON, self.OnrotxM)
        r += 1
        c = 1
        grid.Add(self.rotxM,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.down = wx.Button(self, -1, label="DOWN", size=wx.Size(40, 40))
        self.down.Bind(wx.EVT_BUTTON, self.Ondown)
        c += 2
        grid.Add(self.down,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.rotzM = wx.Button(self, -1, label="rot z -", size=wx.Size(40, 40))
        self.rotzM.Bind(wx.EVT_BUTTON, self.OnrotzM)
        c += 2
        grid.Add(self.rotzM,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

        self.resetz = wx.Button(self, -1, label="Reset z", size=wx.Size(40, 40))
        self.resetz.Bind(wx.EVT_BUTTON, self.Onresetz)
        c += 1
        grid.Add(self.resetz,
                 pos=wx.GBPosition(r, c),
                 span=wx.GBSpan(1, 1))

# ------

        self.SetSizerAndFit(grid)

        self.Refresh()

        return



    def OnrotxP(self, event):
#        f= 0.0
#        f= self.checkValidChars(event.GetString())
#        self.parent.terrainOgreWin.selected.entry.position = (float(self.X.GetValue()), float(self.Y.GetValue()), float(self.Z.GetValue()))
        event.Skip()
        return
    def Onup(self, event):
        event.Skip()
    def OnrotzP(self, event):
        event.Skip()

    def Onleft(self, event):
        event.Skip()
    def OnrotyP(self, event):
        event.Skip()
    def OnrotyM(self, event):
        event.Skip()
    def Onright(self, event):
        event.Skip()


    def OnrotxM(self, event):
        event.Skip()
    def Ondown(self, event):
        event.Skip()
    def OnrotzM(self, event):
        event.Skip()

    def Onresetx(self, event):
        event.Skip()
    def Onresety(self, event):
        event.Skip()
    def Onresetz(self, event):
        event.Skip()

    def OnEditHeightChanged(self, event):
        f = 0.0
        f = self.checkValidChars(event.GetString())
        self.parent.terrainOgreWin.selected.entry.heightFromGround = float(self.heightFromGround.GetValue())
        event.Skip()
        return

    def OnEditrotChanged(self, event):
        f = 0.0
        f = self.checkValidChars(event.GetString())

        self.parent.terrainOgreWin.selected.entry.rotation = (float(self.rotX.GetValue()), float(self.rotY.GetValue()), float(self.rotZ.GetValue()))
        event.Skip()
        return

    def OnVisible(self, event):
        self.parent.terrainOgreWin.selected.entry.visible = self.chkVisible.GetValue()

    def OnEditcommentChanged(self, event):
        #user may include "//" chars for the comment but may not!!
        # I assert doing myself
        # Although TextCtrl process enter key, user may press twice to get a blank line
        line = event.GetString().replace("/", "")
        lines = line.split("\n")

        for i in range(0, len(lines)):
            lines[i] = "// " + lines[i]

        self.parent.terrainOgreWin.selected.entry.data.comments = lines
        event.Skip()
        return

    def updateData(self, entry=None ,
                   doc=""" entry is terrain.selected.entry and
                            may be None to disable Object Inspector"""):

        rotRes = False
        commRes = False
        res = not entry is None
        self.X.SetEditable(res)
        self.Y.SetEditable(res)
        self.Z.SetEditable(res)

        if res:
            commRes = not entry.data is None
            if entry.data:
                rotRes = entry.data.mayRotate

        self.rotX.SetEditable(rotRes)
        self.rotY.SetEditable(rotRes)
        self.rotZ.SetEditable(rotRes)
        self.comments.SetEditable(commRes)
        self.heightFromGround.SetEditable(res)
        self.nameObject.SetLabel("")

        if res:
            x, y , z = entry.position
            rx, ry, rz = entry.rotation

            # avoid flicker
            if not entry.data.name == self.nameObject.GetName():
                self.nameObject.SetLabel(entry.data.name)
            self.X.ChangeValue('%.6f' % x)
            self.Y.ChangeValue('%.6f' % y)
            self.Z.ChangeValue('%.6f' % z)
            self.rotX.ChangeValue('%.6f' % rx)
            self.rotY.ChangeValue('%.6f' % ry)
            self.rotZ.ChangeValue('%.6f' % rz)
            self.heightFromGround.ChangeValue('%.6f' % entry.heightFromGround)
            new = ""
            self.chkVisible.SetValue(entry.visible)
            if commRes:
                new = [x.replace("/", "") for x in entry.data.comments]
            self.comments.SetValue("\n".join(new))
