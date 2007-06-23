#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

def main():
    """
    main method
    """

    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

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