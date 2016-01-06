#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz

import repoclient
from logger import log
from settingsManager import *
import wx, wx.grid, wx.html, os, os.path, base64, sys
from datetime import *

class HtmlRenderer(wx.grid.PyGridCellRenderer):
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
       
        text = grid.GetCellValue(row, col)
       
        if isSelected:
            bg = grid.GetSelectionBackground()
        else:
            bg = attr.GetBackgroundColour()
       
        bmp = wx.EmptyBitmap(*rect[2:4])
        mem_dc = wx.MemoryDC(bmp)
        mem_dc.SetBackground(wx.Brush(bg, wx.SOLID))
        mem_dc.Clear()
       
        renderer = wx.html.HtmlDCRenderer()
        renderer.SetDC(mem_dc, 0)
        renderer.SetSize(*rect[2:4])
        renderer.SetHtmlText(text)
        renderer.Render(0, 0, [0])
       
        mem_dc.SelectObject(wx.NullBitmap)
       
        dc.DrawBitmap(bmp, 0, 0) 

class HtmlImageRenderer(wx.grid.PyGridCellRenderer):
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
       
        text = grid.GetCellValue(row, col)
       
        if isSelected:
            bg = grid.GetSelectionBackground()
        else:
            bg = attr.GetBackgroundColour()
       
        bmp = wx.EmptyBitmap(*rect[2:4])
        mem_dc = wx.MemoryDC(bmp)
        mem_dc.SetBackground(wx.Brush(bg, wx.SOLID))
        mem_dc.Clear()

        renderer = wx.html.HtmlDCRenderer()
        renderer.SetDC(mem_dc, 0)
        renderer.SetSize(*rect[2:4])
        renderer.SetHtmlText("<img src='http://repository.rigsofrods.com/uimages/%s.thumb.png' />" % (text))
        renderer.Render(0, 0, [0])
       
        mem_dc.SelectObject(wx.NullBitmap)
       
        dc.DrawBitmap(bmp, 0, 0) 
        
class ImageRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self, bmp):
        wx.grid.PyGridCellRenderer.__init__(self)
        self.bmp = bmp

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        if isSelected:
            bg = grid.GetSelectionBackground()
        else:
            bg = attr.GetBackgroundColour()
        dc.DrawRectangle(rect.x - 1, rect.y - 1, rect.width + 2, rect.height + 2)
        dc.DrawBitmap(self.bmp, rect.x, rect.y)
        
    def GetBestSize(self, grid, attr, dc, row, col):
        return wx.Size(self.bmp.GetWidth() + 2, self.bmp.GetHeight() + 2)

    def Clone(self):
        return ImageRenderer

class RepoClientTest(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.grid_1 = wx.grid.Grid(self, -1, size=(1, 1))
        try:
            self.data = repoclient.getFiles(-1)
        except Exception, err:
            log().error(err)
            dlg = wx.MessageDialog(self, "Repository Server is unavailable right now. Please note that the server is in a beta stage and that it is not online every time.", "Info", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.Close()
            return
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Repository Client")
        self.SetSize((400, 400))
        self.grid_1.CreateGrid(len(self.data['data']),len(self.data['field'])) 
        
        bmp = wx.Image("ror.ico", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #self.grid_1.SetCellRenderer(1, 1, ImageRenderer(bmp))
        #self.grid_1.SetCellRenderer(2, 1, ImageRenderer(bmp))
        
        index = 0 
        for item in self.data['field']:
            self.grid_1.SetColLabelValue(index, item[0]) 
            index += 1 
        for row in range(len(self.data['data'])):
            #print row
            for col in range(len(self.data['data'][row])): 
                values = self.data['data'][row][col] 
                if self.data['field'][col][0] == "filesize":
                    values = "%0.2f MB" % (float(values)/1024/1024)
                elif self.data['field'][col][0] == "description":
                    values = "%s" % (base64.b64decode(values))
                    self.grid_1.SetCellRenderer(row, col, wx.grid.GridCellAutoWrapStringRenderer())
                elif self.data['field'][col][0] == "date_added":
                    reftime = datetime ( 1970, 1, 1, 0, 0, 0 )
                    delta = timedelta ( 0, int(values) )
                    t = reftime + delta
                    values = str(t)
                    #self.grid_1.SetCellRenderer(row, col, ImageRenderer(bmp))
                elif self.data['field'][col][0] == "filesize":
                    values = "%0.2f MB" % (float(values)/1024/1024)
                
                self.grid_1.SetCellValue(row, col, str(values)) 
        
        self.grid_1.AutoSize()
   
    def __do_layout(self):
        sizer_1 =wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.grid_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()

def main():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = RepoClientTest(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
        
if __name__ == "__main__":
    main()