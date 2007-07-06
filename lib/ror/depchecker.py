#Thomas Fischer 06/07/2007, thomas@thomasfischer.biz
import sys, os, os.path

#DIR = "C:\\games\\RoR-0.31a\\data"
DEPCHECKPATH = "depcheckerplugins"

class RoRDepChecker:
    def __init__(self, path, mode):
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), DEPCHECKPATH))
        self.deptree = {'materials':{},'file':{}}
        self.dir = path
        self.getfiles()
        self.createDepGraph()
        self.viewDepGraph(mode)
        
        
    def getDependencies(self, extension, filename):
        try:
            #print "trying to use module: %s" % "ror_" + extension.lstrip(".")
            mod = __import__("ror_" + extension.lstrip("."))
        except ImportError, e:
            #print "module not found!"
            #print e
            return
            pass
            
        return mod.getDependencies(filename)

        
    def getfiles(self):
        fl = {}
        for root, dirs, files in os.walk(self.dir):
            for f in files:
                if f in fl.keys():
                    print "double file found: %s!" % (f)
                    continue                
                fl[f] = {}
                fl[f]['filename'] = os.path.join(root, f)
        #for fk in fl.keys():
        #    print "%30s: %s" % (fk, fl[fk]['filename'])
        print "found %d files!" % (len(fl.keys()))
        self.files = fl


    def viewDepGraph(self, mode = "all"):
        displayedfiles = 0
        str = ""
        str += "-------------------------------------------------------------\n"
        if mode == "all":
            str += "--- Dependency tree for %s \n" % (self.dir)
        elif mode == "unused":
            str += "--- Unused resources for %s \n" % (self.dir)
        elif mode == "missing":
            str += "--- Missing requirements for %s \n" % (self.dir)
        str += "-------------------------------------------------------------\n"
        for fk in self.deptree.keys():
            str += "--------- Category:  %-20s -------------------\n" % fk
            for k in self.deptree[fk].keys():
                req = self.deptree[fk][k]['depends']
                if len(req) > 0:
                    reqstr = ", ".join(req)
                else:
                    reqstr = "None"
                found = self.deptree[fk][k]['provide']
                if len(found) > 0:
                    foundstr = ", ".join(found)
                else:
                    foundstr = "None"
                display = False
                if mode == "all":
                    display = True
                elif mode == "unused":
                    display = (len(found) > 0 and len(req) == 0)
                elif mode == "missing":
                    display = (len(req) > 0 and len(found) == 0)
                if display:
                    displayedfiles += 1
                    if mode == "all":
                        str += "%40s: %16s%-10s\n%41s %16s%-10s\n" % (k, "required by: ", reqstr, "", "provided by: ", foundstr)
                    elif mode == "unused":
                        str += "%40s: %16s%-10s\n" % (k, "provided by: ", foundstr)
                    elif mode == "missing":
                        str += "%40s: %16s%-10s\n" % (k, "required by: ", reqstr)
        if displayedfiles > 0:
            print str
        elif displayedfiles == 0:
            if mode == "all":
                print "No resources found at all!"
            elif mode == "unused":
                print "No resources unused!"
            elif mode == "missing":
                print "No resources missing!"

        
        
    def createDepGraph(self):
        #extlist = []
        for fk in self.files.keys():
            fn, ext = os.path.splitext(fk)
            filename = self.files[fk]['filename']
            dep = self.getDependencies(ext, filename)
            keywords = ['provide', 'depends']
            if not dep is None:
                for kw in keywords:
                    if kw in dep.keys():
                        for pk in dep[kw].keys():
                            for p in dep[kw][pk]:
                                #print kw, pk, p
                                if not p in self.deptree[pk].keys():
                                    self.deptree[pk][p] = {keywords[0]:[], keywords[1]:[]}
                                self.deptree[pk][p][kw].append(fk)
                
            
            #if not ext in extlist:
            #    extlist.append(ext)
        #print extlist
            

def usage():
    print "usage: %s <path to inspect> <all or unused or missing>" % os.path.basename(sys.argv[0])
    print "for example: %s c:\\ror\\data missing" % os.path.basename(sys.argv[0])
    print " * all will display all dependencies, inclusive met ones"
    print " * missing will display only unfulfilled dependencies"
    print " * unused will display resources that are not in use"
    sys.exit(0)
            
def main():
    if len(sys.argv) != 3:
        usage()
    if not os.path.isdir(sys.argv[1]):
        print "%s is not a valid directory!" % sys.argv[1]
        usage()
    if not sys.argv[2] in ['all', 'missing', 'unused']:
        print "%s is not a valid mode!" % sys.argv[2]
        usage()
    RoRDepChecker(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
