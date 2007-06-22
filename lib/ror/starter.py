#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorsettings import *
from ror.rorcommon import *
from settingsdialog import *
from subprocess import Popen
import wx


class SettingsDialog(SettingsDialogBase):
    def VwXinit(self):
        SettingsDialogBase.VwXinit(self)

        self.rordir = getSettings().getRoRDir()
        #print self.rordir
        if not self.rordir is None:
            if self.checkRoRDir(self.rordir):
                self.btnTerrainEditor.Enable(True)
                self.btnStartRoR.Enable(True)
                self.btnTruckEditor.Enable(True)
                self.txtRoRDir.SetValue(self.rordir)
            else:
                self.rordir = ""
                self.txtRoRDir.SetValue("")
                self.btnTerrainEditor.Enable(False)
                self.btnStartRoR.Enable(False)
                self.btnTruckEditor.Enable(False)
        else:
            self.btnTerrainEditor.Enable(False)
            self.btnStartRoR.Enable(False)
            self.btnTruckEditor.Enable(False)
        
    def btnStartRoR_VwXEvOnButtonClick(self, event=None):
        p = Popen(os.path.join(self.rordir, "RoR.exe"), shell=True, cwd=self.rordir)
        sts = os.waitpid(p.pid, 0)

    def btnTruckEditor_VwXEvOnButtonClick(self, event=None):
        import rortruckeditor.MainFrame
        try:
            app = rortruckeditor.MainFrame.startApp()
            del app
        except:
            pass
    
    def btnTerrainEditor_VwXEvOnButtonClick(self, event=None):
        import rorterraineditor.MainFrame
        try:
            app = rorterraineditor.MainFrame.startApp()
            del app
        except:
            pass

    def checkRoRDir(self, fn):
        return os.path.isfile(os.path.join(fn,"RoR.exe"))
        
    def btnSelectRoRDir_VwXEvOnButtonClick(self, event=None):
        dialog = wx.DirDialog(self, "Choose RoR Directory", "")
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            newpath = dialog.GetPath()
            if not self.checkRoRDir(newpath):
                dlg = wx.MessageDialog(self, "RoR.exe not found in that directory!", "Error", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
                
            self.rordir = newpath
            self.txtRoRDir.SetValue(newpath)
            getSettings().setRoRDir(newpath)
            self.btnTerrainEditor.Enable(True)
            self.btnStartRoR.Enable(True)
            
    def btnExit_VwXEvOnButtonClick(self, event=None):
        self.Close()
            
    pass
    
class App(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.main = SettingsDialog(None,-1,'')
        self.main.ShowModal()
        return 0

def main():
    application = App(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
