#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

if __name__=="__main__": 
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    import rortruckeditor.MainFrame
    rortruckeditor.MainFrame.startApp()
