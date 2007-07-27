#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil, urllib, re

from logger import log
from settingsManager import getSettingsManager

REPOSITORY_URL = "http://repository.rigsofrods.com/files/%(file)s"
TEMPDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "temp"))
DOWNLOADDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "downloaded"))

class ModTool:
    def __init__(self):
        pass
    
    def work(self, mode, targetfile, verbose, dryrun, installtarget=None):
        self.dryrun = dryrun
        self.verbose = verbose
        log().info("### modinstaller started with %s, %s" % (mode, targetfile))
        if mode == "install":
            filename = os.path.abspath(targetfile)
            self.ExtractToTemp(targetfile)
            target = installtarget
            log().info("### validating target ...")
            import ror.depchecker
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
                filenamefound = self.searchFile(filename, TEMPDIR)
                if filenamefound is None:
                    log().error("File %s not found in %s!" % (filename, TEMPDIR))
                    sys.exit(1)
                self.installfile(target, filenamefound, dryrun)
                installcounter += 1
            if dryrun:
                log().info("### would install %d files." % installcounter)
            else:
                log().info("### %d files installed, finished!" % installcounter)
            self.removetemp(False)
            return [target]    

        elif mode == "installall":
            filename = os.path.abspath(targetfile)
            self.ExtractToTemp(targetfile)
            validtargets, invalidtargets = self.getTargets(verbose)
            log().info("### installing %d found modifications:" % (len(validtargets)))
            installcounter = 0
            for target in validtargets:
                log().info("### installing modification '%s'" % target)
                import ror.depchecker
                dc = ror.depchecker.RoRDepChecker(TEMPDIR, "dtree", target, verbose)
                if dc.dstree is None:
                    log().error("no dependenytree for File %s!" % (filename))
                    continue
                for file in dc.dstree:
                    filename = file['filename']
                    filenamefound = self.searchFile(filename, TEMPDIR)
                    if filenamefound is None:
                        log().error("File %s not found in %s!" % (filename, TEMPDIR))
                        sys.exit(1)
                    self.installfile(target, filenamefound, dryrun)
                    installcounter += 1
            if dryrun:
                log().info("### would install %d files." % installcounter)
            else:
                log().info("### %d files installed, finished!" % installcounter)
            self.removetemp(False)
            return validtargets    
        
        elif mode == "installrepo":
            if targetfile.find("://") != -1:
                m = re.match(r"^.*://(.*)$", targetfile)
                if not m is None and len(m.groups()) > 0:
                    targetfile = m.groups()[0].rstrip("/")
                else:
                    log().error("error while installing from repo: wrong URL scheme")
                    return False
            else:
                log().info("manual use, not parsing URL")
            if not self.getRepoFile(targetfile):
                log().error("error while installing from repo.")
                return False
            targetfile = os.path.join(DOWNLOADDIR, targetfile)
            return ModTool().work("installall", targetfile, self.verbose, self.dryrun)
        
        elif mode in ["list", "listall"]:
            filename = os.path.abspath(targetfile)
            self.ExtractToTemp(targetfile)
            validtargets, invalidtargets = self.getTargets(verbose)
            if mode == "listall":
                if len(invalidtargets) > 0:
                    log().info("broken modifications found:")
                    for v in invalidtargets:
                        log().info("  %-20s" % v)
                    log().info("use the --verbose flag to find the missing files!")
                else:
                    log().info("no broken modifications found")

            if len(validtargets) > 0:
                log().info("installable modifications found:")
                for v in validtargets:
                    log().info("  %-20s" % v)
            else:
                log().info("no installable modifications found! :(")           
            # todo : remove workaround!
            self.removetemp(False)
            return validtargets

        elif mode in ["listinstalled"]:
            targets = self.getRoRMods(verbose)
            if len(targets) > 0:
                log().info("### Found Mods:")
                for target in targets:
                    log().info("  "+target)
            else:
                log().info("### No Mods found!")
                
        if mode in ["uninstall"]:
            rorpath = getSettingsManager().getSetting("RigsOfRods", "BasePath")
            log().info("### validating target ...")
            import ror.depchecker
            dc = ror.depchecker.RoRDepChecker(rorpath, "dtree", targetfile, verbose)
            if dc.invalid:
                log().error("### target invalid! (Target not found)")
                log().info("### please use the 'listinstalled' mode to get valid uninstallation targets")
                return None
            
            log().info("### target valid!")

            #print dc.dstree
            newtargets = []
            md5s = dc.readMD5File()
            for file in dc.dstree:
                filename = file['filename']
                if not os.path.basename(filename) in md5s.keys():
                    newtargets.append(filename)
            log().info("### removed %d files from dependency tree." % (len(dc.dstree)-len(newtargets)))
            #print newtargets
            if dryrun:
                log().info("### would uninstall %d file(s):" % len(newtargets))
            else:
                log().info("### uninstalling %d file(s):" % len(newtargets))
            for target in newtargets:
                filenamefound = self.searchFile(target, rorpath)
                if filenamefound is None:
                    log().error("### File not found: %s" % target)
                    continue
                log().info("   %s" % filenamefound)
                if not dryrun:
                    os.unlink(filenamefound)

        return None
        
    def wgetreporthook(self, *arg):
        percentdone = int(((arg[0] * arg[1]) / float(arg[2]))*100)
        if percentdone % 10 == 0:
            log().info("Downloading, % 4d%% done..." % percentdone)
    
    def wget(self, url, filename):
        file, msg = urllib.urlretrieve(url, filename, self.wgetreporthook)
        if os.path.isfile(file):
            return True
        return False
        

    def getRepoFile(self, repofilename):
        if not os.path.isdir(DOWNLOADDIR):
            os.mkdir(DOWNLOADDIR)
        try:
            log().info("trying to download the file %s form the repository..." % repofilename)
            src = REPOSITORY_URL %{"file":repofilename}
            dst = os.path.join(DOWNLOADDIR, repofilename)
            #print src, dst
            return self.wget(src, dst)
        except Exception, err:
            log().error("Error while trying to donwload file from the Repository:")
            log().error(str(err))
            self.removetemp(False)
            return False
    
    def removetemp(self, reporterrors=True):
        if os.path.isdir(TEMPDIR):
            try:
                shutil.rmtree(TEMPDIR)
                #os.rmdir(TEMPDIR)
            except Exception, err:
                if not reporterrors:
                    return
                log().error(str(err))
                log().error("could not remove temporary diretory: %s! please delete by hand." % TEMPDIR)
                sys.exit(1)

    def ExtractToTemp(self, filename):
        file, extension = os.path.splitext(filename)
        self.removetemp(False)
        os.mkdir(TEMPDIR)
        if extension.lower() == ".rar":
            import UnRAR        
            dst = os.path.join(TEMPDIR, os.path.basename(filename))
            shutil.copyfile(filename, dst)
            os.chdir(TEMPDIR)
            UnRAR.Archive(os.path.basename(filename)).extract()
            
            # remove .rar file instantly
            os.unlink(os.path.join(TEMPDIR, os.path.basename(filename)))
            
            # change back to current path
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            return True
        elif extension.lower() == ".zip":
            import UnZIP
            UnZIP.unzip(filename, TEMPDIR)
            return True
        else:
            log().info("copying "+filename+" to "+os.path.join(TEMPDIR, os.path.basename(filename)))
            shutil.copyfile(filename, os.path.join(TEMPDIR, os.path.basename(filename)))
        return False

    def installfile(self, maintarget, srcfile, dryrun):
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

    def searchFile(self, filename, top):
        for root, dirs, files in os.walk(top, topdown=False):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def getTargets(self, verbose):
        import ror.depchecker
        dc = ror.depchecker.RoRDepChecker(TEMPDIR, "getfiles", "", False)
        targets = []
        for file in dc.files:
            filename, extension = os.path.splitext(file)
            if extension.lower() in ['.truck', '.terrn', '.load']:
                targets.append(os.path.basename(file))

        validtargets = []
        invalidtargets = []
        if len(targets) == 0:
            log().info("### no targets found")
            return validtargets, invalidtargets
        
        log().info("### found %d targets, checking them separatly now" % len(targets))
        for target in targets:
            log().info("### checking target %s..." % target)
            dc = ror.depchecker.RoRDepChecker(TEMPDIR, "dtree", target, verbose)
            if dc.everythingfound:
                validtargets.append(target)
            else:
                invalidtargets.append(target)
        return validtargets, invalidtargets

    def getRoRMods(self, verbose):
        import ror.depchecker
        rorpath = getSettingsManager().getSetting("RigsOfRods", "BasePath")
        dc = ror.depchecker.RoRDepChecker(rorpath, "getfiles", "", False)
        targets = []
        for file in dc.files:
            filename, extension = os.path.splitext(file)
            if extension.lower() in ['.truck', '.terrn', '.load']:
                targets.append(os.path.basename(file))
        newtargets = []
        md5s = dc.readMD5File()
        for target in targets:
            if not os.path.basename(target) in md5s.keys():
                newtargets.append(target)
        return newtargets

    