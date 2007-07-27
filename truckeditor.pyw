#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

def main():
    """
    main method
    """

    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    import ror.settingsManager
    path = ror.settingsManager.getSettingsManager().getSetting("RigsOfRods", "BasePath")
    if not os.path.isfile(os.path.join(path,"RoR.exe")):
        import ror.starter
        ror.starter.startApp()        

    # Import Psyco if available
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    import rortruckeditor.MainFrame
    rortruckeditor.MainFrame.startApp()

    
if __name__=="__main__": 
    main()