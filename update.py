import sys, os, os.path

def main():
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    guiVersion = True
    if guiVersion:
        import wx
        
        MainApp = wx.PySimpleApp(0) 
        wx.InitAllImageHandlers() #you may or may not need this    

        import ror.svngui
        gui = ror.svngui.svnUpdate(False)
        del gui
    else:
        #non-gui version:
        import ror.svn
        ror.svn.run()

if __name__=="__main__": 
    main()