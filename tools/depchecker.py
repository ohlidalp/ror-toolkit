#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

def usage():
    print "usage: %s <path to inspect> <all or unused or missing>" % os.path.basename(sys.argv[0])
    print "for example: %s c:\\ror\\data missing" % os.path.basename(sys.argv[0])
    print " valid modes:"
    print " 'all' displays all dependencies, inclusive fulfilled ones"
    print " 'missing' displays only unfulfilled dependencies"
    print " 'unused' displays resources that are not in use"
    print " 'dtree <resourcename>'  displays the dependency tree of the given resource name"
    print " 'md5sum' creates the md5sums of all files"
    sys.exit(0)
            
 
def main():
    """
    main method
    """

    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
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

    if len(sys.argv) < 3:
        usage()    
    path = sys.argv[1]
    if path.strip() == "rordir":
        path = ror.settingsManager.getSettingsManager().getSetting("RigsOfRods", "BasePath")
    if not os.path.isdir(path):
        print "%s is not a valid directory!" % path
        usage()
    if (len(sys.argv) == 3 and sys.argv[2] in ['all', 'missing', 'unused', 'record']) or (len(sys.argv) == 4 and sys.argv[2] in ['dtree']):
        pass
    else:
        print "%s is not a valid mode, or incorrect arguments!" % sys.argv[2]
        usage()
    
    import ror.depchecker
    dependfilename = ""
    if len(sys.argv) == 4 and sys.argv[2] in ['dtree'] and sys.argv[3].strip() != "":
        dependfilename = sys.argv[3].strip()
    ror.depchecker.RoRDepChecker(path , sys.argv[2], dependfilename)
    
if __name__=="__main__": 
    main()