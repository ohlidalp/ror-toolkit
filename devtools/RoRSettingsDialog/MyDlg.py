# -*- coding: iso-8859-1 -*-
# Don't modify comment 

import wx
#[inc]add your include files here

#[inc]end your include

class MyDlg(wx.Dialog):
    def __init__(self,parent,id = -1,title = '',pos = wx.Point(0,0),size = wx.Size(500,600),style = wx.DEFAULT_DIALOG_STYLE,name = 'dialogBox'):
        pre=wx.PreDialog()
        self.OnPreCreate()
        pre.Create(parent,id,title,pos,size,wx.CAPTION|wx.SYSTEM_MENU|wx.DIALOG_NO_PARENT|wx.DEFAULT_DIALOG_STYLE,name)
        self.PostCreate(pre)
        self.initBefore()
        self.VwXinit()
        self.initAfter()

    def __del__(self):
        self.Ddel()
        return


    def VwXinit(self):
        self.fileImgBuf=[None] * 1
        self.fileImgBuf[0] = wx.Bitmap("D:/projects/old/rorterraineditor_0_0_3/splash.bmp",wx.BITMAP_TYPE_BMP)
        self.panelBitmapImg0=self.fileImgBuf[0];
        self.SetIcon(wx.Icon("D:/projects/old/rorterraineditor_0_0_3/ror.ico",wx.BITMAP_TYPE_ICO));
        self.SetTitle('RoR Toolkit')
        self.panelBitmap = wx.Panel(self,-1,wx.Point(3,3),wx.Size(500,223))
        self.panelBitmap.SetLabel('RoR Toolkit')
        self.panelBitmap.Bind(wx.EVT_ERASE_BACKGROUND,self.VwXpanelBitmap_VwXEvOnEraseBackground)
        self.txtRoRDir = wx.TextCtrl(self,-1,"",wx.Point(6,137),wx.Size(100,21))
        self.btnSelectRoRDir = wx.Button(self,-1,"",wx.Point(353,137),wx.Size(75,21))
        self.btnSelectRoRDir.SetLabel("SelectRoR")
        self.wxnb11c = wx.Notebook(self,-1,wx.Point(3,281),wx.Size(20,20))
        self.pn12c = wx.Panel(self.wxnb11c,-1,wx.Point(4,22),wx.Size(420,103))
        self.wxnb11c.AddPage(self.pn12c,'tab n°: 0',0)
        self.lblFPS = wx.StaticText(self.pn12c,-1,"",wx.Point(6,6),wx.Size(50,13),wx.ST_NO_AUTORESIZE)
        self.lblFPS.SetLabel("FPS: 30")
        self.sbFPS = wx.ScrollBar(self.pn12c,-1,wx.Point(62,6),wx.Size(20,20),wx.SB_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL,self.sbFPS_VwXEvOnScrollValue,self.sbFPS)
        self.lblWaterTrans = wx.StaticText(self.pn12c,-1,"",wx.Point(6,38),wx.Size(145,20),wx.ST_NO_AUTORESIZE)
        self.lblWaterTrans.SetLabel("Water Transparency: 10%")
        self.sbWaterTrans = wx.ScrollBar(self.pn12c,-1,wx.Point(157,38),wx.Size(20,20),wx.SB_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL,self.sbWaterTrans_VwXEvOnScrollValue,self.sbWaterTrans)
        self.pn21c = wx.Panel(self.wxnb11c,-1,wx.Point(0,0),wx.Size(20,20))
        self.wxnb11c.AddPage(self.pn21c,'tab n°: 1',0)
        self.btnCheckUpdates = wx.Button(self.pn21c,-1,"",wx.Point(3,3),wx.Size(412,25))
        self.btnCheckUpdates.SetLabel("Check for Updates!")
        self.Bind(wx.EVT_BUTTON,self.btnCheckUpdates_VwXEvOnButtonClick,self.btnCheckUpdates)
        self.lblUpdates = wx.StaticText(self.pn21c,-1,"",wx.Point(3,34),wx.Size(412,18),wx.ST_NO_AUTORESIZE)
        self.btnStartTerrain = wx.Panel(self,-1,wx.Point(3,302),wx.Size(428,45))
        self.btnStartRoR = wx.Button(self.btnStartTerrain,-1,"",wx.Point(3,3),wx.Size(20,20))
        self.btnStartRoR.SetLabel("Start RoR")
        self.Bind(wx.EVT_BUTTON,self.btnStartRoR_VwXEvOnButtonClick,self.btnStartRoR)
        self.btnTerrainEditor = wx.Button(self.btnStartTerrain,-1,"",wx.Point(88,3),wx.Size(20,20))
        self.btnTerrainEditor.SetLabel("Terrain Editor")
        self.Bind(wx.EVT_BUTTON,self.btnTerrainEditor_VwXEvOnButtonClick,self.btnTerrainEditor)
        self.btnTruckEditor = wx.Button(self.btnStartTerrain,-1,"",wx.Point(173,3),wx.Size(20,20))
        self.btnTruckEditor.Enable(False)
        self.btnTruckEditor.SetLabel("Truck Editor")
        self.Bind(wx.EVT_BUTTON,self.btnTruckEditor_VwXEvOnButtonClick,self.btnTruckEditor)
        self.btnExit = wx.Button(self.btnStartTerrain,-1,"",wx.Point(343,3),wx.Size(20,20))
        self.btnExit.SetLabel("Exit")
        self.Bind(wx.EVT_BUTTON,self.btnExit_VwXEvOnButtonClick,self.btnExit)
        self.sz4s = wx.BoxSizer(wx.VERTICAL)
        self.sz6s = wx.BoxSizer(wx.HORIZONTAL)
        self.sz13s = wx.BoxSizer(wx.VERTICAL)
        self.sz15s = wx.BoxSizer(wx.HORIZONTAL)
        self.sz18s = wx.BoxSizer(wx.HORIZONTAL)
        self.sz22s = wx.BoxSizer(wx.VERTICAL)
        self.sz26s = wx.BoxSizer(wx.HORIZONTAL)
        self.sz4s.Add(self.panelBitmap,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz4s.SetItemMinSize(self.panelBitmap,20,10)
        self.sz4s.Add(self.sz6s,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz4s.Add(self.wxnb11c,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz4s.Add(self.btnStartTerrain,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz6s.Add(self.txtRoRDir,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz6s.Add(self.btnSelectRoRDir,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz13s.Add(self.sz15s,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz13s.Add(self.sz18s,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz15s.Add(self.lblFPS,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz15s.Add(self.sbFPS,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz18s.Add(self.lblWaterTrans,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz18s.Add(self.sbWaterTrans,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz22s.Add(self.btnCheckUpdates,0,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz22s.Add(self.lblUpdates,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz26s.Add(self.btnStartRoR,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz26s.Add(self.btnTerrainEditor,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz26s.Add(self.btnTruckEditor,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.sz26s.Add(self.btnExit,1,wx.TOP|wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE,3)
        self.SetSizer(self.sz4s);self.SetAutoLayout(1);self.Layout();
        self.pn12c.SetSizer(self.sz13s);self.pn12c.SetAutoLayout(1);self.pn12c.Layout();
        self.pn21c.SetSizer(self.sz22s);self.pn21c.SetAutoLayout(1);self.pn21c.Layout();
        self.btnStartTerrain.SetSizer(self.sz26s);self.btnStartTerrain.SetAutoLayout(1);self.btnStartTerrain.Layout();
        self.Refresh()
        return
    def VwXDrawBackImg(self,event,win,bitMap,opz):
        if (event.GetDC()):
            dc=event.GetDC()
        else: dc = wx.ClientDC(win)
        dc.SetBackground(wx.Brush(win.GetBackgroundColour(),wx.SOLID))
        dc.Clear()
        if (opz==0):
            dc.DrawBitmap(bitMap,0, 0, 0)
        if (opz==1):
            rec=wx.Rect()
            rec=win.GetClientRect()
            rec.SetLeft((rec.GetWidth()-bitMap.GetWidth())   / 2)
            rec.SetTop ((rec.GetHeight()-bitMap.GetHeight()) / 2)
            dc.DrawBitmap(bitMap,rec.GetLeft(),rec.GetTop(),0)
        if (opz==2):
            rec=wx.Rect()
            rec=win.GetClientRect()
            for y in range(0,rec.GetHeight(),bitMap.GetHeight()):
                for x in range(0,rec.GetWidth(),bitMap.GetWidth()):
                    dc.DrawBitmap(bitMap,x,y,0)

    def VwXDelComp(self):
        return
    def VwXpanelBitmap_VwXEvOnEraseBackground(self,event):
        self.VwXDrawBackImg(event,self.panelBitmap,self.panelBitmapImg0,1)
        self.panelBitmap_VwXEvOnEraseBackground(event)
        event.Skip(False)

        return

#[win]add your code here

    def sbWaterTrans_VwXEvOnScrollValue(self,event): #init function
        #[190]Code event VwX...Don't modify[190]#
        #add your code here

        return #end function

    def sbFPS_VwXEvOnScrollValue(self,event): #init function
        #[18f]Code event VwX...Don't modify[18f]#
        #add your code here

        return #end function

    def btnTruckEditor_VwXEvOnButtonClick(self,event): #init function
        #[194]Code event VwX...Don't modify[194]#
        #add your code here

        return #end function

    def btnTerrainEditor_VwXEvOnButtonClick(self,event): #init function
        #[193]Code event VwX...Don't modify[193]#
        #add your code here

        return #end function

    def btnStartRoR_VwXEvOnButtonClick(self,event): #init function
        #[192]Code event VwX...Don't modify[192]#
        #add your code here

        return #end function

    def btnExit_VwXEvOnButtonClick(self,event): #init function
        #[195]Code event VwX...Don't modify[195]#
        #add your code here

        return #end function

    def btnCheckUpdates_VwXEvOnButtonClick(self,event): #init function
        #[191]Code event VwX...Don't modify[191]#
        #add your code here

        return #end function


    def panelBitmap_VwXEvOnEraseBackground(self,event): #init function
        #[504]Code event VwX...Don't modify[504]#
        #add your code here
        event.Skip()

        return #end function


    def initBefore(self):
        #add your code here

        return

    def initAfter(self):
        #add your code here
        self.Centre()
        return

    def OnPreCreate(self):
        #add your code here

        return

    def Ddel(self): #init function
        #[158]Code VwX...Don't modify[157]#
        #add your code here

        return #end function

#[win]end your code
