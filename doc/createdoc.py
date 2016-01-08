#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

def main():
    """
    main method
    """
    
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..","lib"))

    import epydoc.cli
    epydoc.cli.cli()


if __name__=="__main__": 
    main()