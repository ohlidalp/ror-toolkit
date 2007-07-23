#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from ror.logger import log
from ror.settingsManager import getSettingsManager

TEMPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")

def removetemp(reporterrors=True):
    if os.path.isdir(TEMPDIR):
        try:
            shutil.rmtree(TEMPDIR)
        except Exception, err:
            if not reporterrors:
                return
            log().error(str(err))
            log().error("could not remove temporary diretory: %s! please delete by hand." % TEMPDIR)
            sys.exit(1)

def ExtractToTemp(filename):
    file, extension = os.path.splitext(filename)
    removetemp()
    if extension.lower() == ".rar":
        import UnRAR        
        os.mkdir(TEMPDIR)
        dst = os.path.join(TEMPDIR, os.path.basename(filename))
        shutil.copyfile(filename, dst)
        os.chdir(TEMPDIR)
        UnRAR.Archive(os.path.basename(filename)).extract() 
        # change back to current path
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        return True
    elif extension.lower() == ".zip":
        import UnZIP
        UnZIP.unzip(filename, TEMPDIR)
        return True
    else:
        shutil.copyfile(filename, dst)
    return False

def installfile(maintarget, srcfile, dryrun):
    file, extension = os.path.splitext(maintarget)
    rorpath = getSettingsManager().getSetting("RigsOfRods", "BasePath")
    
    if extension in ['.truck', '.load']:
        path = os.path.join(rorpath, "data", "trucks")
    elif extension in ['.terrn']:
        path = os.path.join(rorpath, "data", "terrains")
    else:
        path = rorpath
    if dryrun:
        log().info("would install %s to %s" % (os.path.basename(srcfile), path))
    else:
        log().info("installing %s to %s" % (os.path.basename(srcfile), path))
        shutil.copyfile(srcfile, os.path.join(path, os.path.basename(srcfile)))

def searchFile(filename, top):
    for root, dirs, files in os.walk(top, topdown=False):
        if filename in files:
            return os.path.join(root, filename)
    return None

def usage():
    print "usage (general): %s <filename> <mode> <additionaloptions> [--verbose] [--dryrun]" % (os.path.basename(sys.argv[0]))
    print "<filename> list"
    print " list all found and valid modifications in filename"
    print ""
    print "<filename> listall --verbose"
    print " list all found modifications in filename (valid and invalid)"
    print ""
    print "<filename> installall --verbose"
    print " install all found modifications in filename"
    print ""
    print "<filename> install <modification> --verbose"
    print " install a certain modifications in filename (valid and invalid)"
    print ""
    print "notes: the --verbose option is optional to increase the output for debugging"
    print "       the --dryrun option just prints out which files would be copied/installed."
    sys.exit(0)

def getTargets(verbose):
    import ror.depchecker
    dc = ror.depchecker.RoRDepChecker(TEMPDIR, "getfiles", "", verbose)
    targets = []
    for file in dc.files:
        filename, extension = os.path.splitext(file)
        if extension.lower() in ['.truck', '.terrn', '.load']:
            targets.append(os.path.basename(file))

    validtargets = []
    invalidtargets = []
    for target in targets:
        dc = ror.depchecker.RoRDepChecker(TEMPDIR, "dtree", target, verbose)
        if dc.everythingfound:
            validtargets.append(target)
        else:
            invalidtargets.append(target)
    return validtargets, invalidtargets

    
def main():
    if len(sys.argv) < 3:
        usage()
    
    targetfile = sys.argv[1]
    if not os.path.isfile(targetfile):
        log().error("%s is not a valid target filename!" % targetfile)
        usage()

    mode = sys.argv[2]
    if not mode in ['list', 'listall', 'install', 'installall']:
        usage()
    if len(sys.argv) < 4 and mode in ['install']:
        usage()
    
    # get optional flags
    verbose = False
    dryrun = False
    for option in sys.argv:
        if option == "--verbose":
            verbose = True
        if option == "--dryrun":
            dryrun = True


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
        
    filename = os.path.abspath(targetfile)
    ExtractToTemp(filename)
    
    if mode == "install":
        target = sys.argv[3]
        import ror.depchecker
        log().info("### validating target ...")
        dc = ror.depchecker.RoRDepChecker(TEMPDIR, "dtree", target, verbose)
        if dc.invalid:
            log().error("### target invalid!")
            log().info("### please use the list mode to get valid targets")
            usage()
        
        log().info("### target valid!")
        #print dc.dstree
        installcounter = 0
        for file in dc.dstree:
            filename = file['filename']
            filenamefound = searchFile(filename, TEMPDIR)
            if filenamefound is None:
                log().error("File %s not found in %s!" % (filename, TEMPDIR))
                sys.exit(1)
            installfile(target, filenamefound, dryrun)
            installcounter += 1
        if dryrun:
            log().info("### would install %d files." % installcounter)
        else:
            log().info("### %d files installed, finished!" % installcounter)
    
    elif mode == "installall":
        validtargets, invalidtargets = getTargets(verbose)
        log().info("### installing %d found modifications:" % (len(validtargets)))
        installcounter = 0
        for target in validtargets:
            log().info("### installing modification '%s'" % target)
            dc = ror.depchecker.RoRDepChecker(TEMPDIR, "dtree", target, verbose)
            for file in dc.dstree:
                filename = file['filename']
                filenamefound = searchFile(filename, TEMPDIR)
                if filenamefound is None:
                    log().error("File %s not found in %s!" % (filename, TEMPDIR))
                    sys.exit(1)
                installfile(target, filenamefound, dryrun)
                installcounter += 1
        if dryrun:
            log().info("### would install %d files." % installcounter)
        else:
            log().info("### %d files installed, finished!" % installcounter)

    elif mode in ["list", "listall"]:
        validtargets, invalidtargets = getTargets(verbose)
        if mode == "listall":
            if len(invalidtargets) > 0:
                print "broken modifications found:"
                for v in invalidtargets:
                    print "  %-20s" % v
                print "use the --verbose flag to find the missing files!"
            else:
                print "no broken modifications found:"

        if len(validtargets) > 0:
            print "installable modifications found: "
            for v in validtargets:
                print "  %-20s" % v
        else:
            print "no installable modifications found! :("            
    removetemp(False)
    

if __name__=="__main__":
    main()