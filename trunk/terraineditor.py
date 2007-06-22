#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

if __name__=="__main__": 
    # Import Psyco if available
    try:
        import psyco
        psyco.full()
        #psyco.log()
        #psyco.profile()
    except ImportError:
        pass

    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    import rorterraineditor.MainFrame
    rorterraineditor.MainFrame.startApp()

