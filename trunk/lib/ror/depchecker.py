#Thomas Fischer 06/07/2007, thomas@thomasfischer.biz
import sys, os, os.path, copy

DEPCHECKPATH = "depcheckerplugins"
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), DEPCHECKPATH))
from deptools import *




class RoRDepChecker:
    def __init__(self, path, mode, dependfilename):
        self.filedeps = {}
        self.dir = path
        self.dependfilename = dependfilename
        self.getfiles()
        self.createDeps()
        self.generateCrossDep()
        
        self.tryGraph()
        
    
    def getSingleDepRecursive(self, file, depth = 0):
        req = [file]
        for filenameA in self.filedeps.keys():
            fileA = self.filedeps[filenameA]
            #for r in 
    
    def generateSingleGraph(self):
        if not self.dependfilename in self.filedeps.keys():
            print "file not found in the dependency tree!"
            sys.exit(0)

    def tryGraph(self):
        try:
            import pydot
            print "pydot found, drawing graphs! beware this can take some time with big graphs!"
            self.drawGraph()
        except ImportError:
            print "pydot not found, not drawing graphs"
            pass   
            
    def drawGraph(self):
        import pydot
        edges = []
        for filenameA in self.filedeps.keys():
            fileA = self.filedeps[filenameA]
            for rel in fileA[REQUIRES][FILE]:
                e = (filenameA, rel)
                edges.append(e)
        
        #edges = [(1,2), (1,3), (1,4), (3,4)]
        graph = pydot.graph_from_edges(edges)
        graph.set_type('digraph')
        graph.simplify = True
        graph.set("resolution", "160")
        graph.set("overlap", "0.2")
        graph.set("shape", "box")
        
        for n in graph.get_node_list():
            n.set('fontsize', 12)
            n.set('style', 'filled')
            n.set('fillcolor', 'lightblue2')
            
        program = "dot" # dot or twopi
        
        graph.write('dependencies.jpg', prog = program, format='jpeg') 
        print "graph successfull written to dependencies.jpg"
        

    def generateCrossDep(self):
        crossdep = 0
        notfound = {MATERIAL:[], FILE:[]}
        newtree = copy.deepcopy(self.filedeps)
        for filenameA in self.filedeps.keys():
            fileA = self.filedeps[filenameA]
            for relation in [REQUIRES, OPTIONAL]:
                for type in TYPES:
                    for reqfile in fileA[relation][type]:
                        found = False
                        for filenameB in self.filedeps.keys():
                            fileB = self.filedeps[filenameB]
                            if filenameA == filenameB:
                                continue
                            #print filenameA, relation, type, reqfile, fileB[PROVIDES][type]
                            if reqfile in fileB[PROVIDES][type]:
                                crossdep += 1
                                newtree[filenameB][REQUIREDBY][FILE].append(filenameA)
                                if not filenameB in fileA[REQUIRES][FILE]:
                                    # found new
                                    newtree[filenameA][REQUIRES][FILE].append(filenameB)
                                found = True
                                break
                        if not found and relation != OPTIONAL:
                            notfound[type].append(reqfile)
        self.filedeps = newtree
        #print  newtree
        if len(notfound[MATERIAL]) == 0 and len(notfound[FILE]) == 0:
            print "### nothing missing, great!"
        else:
            if len(notfound[FILE]) > 0:
                print "### we are missing the following files:"
                print "   " ,str(notfound[FILE])
            if len(notfound[MATERIAL]) > 0:
                print "### we are missing the following materials:"
                print "   " ,str(notfound[MATERIAL])
        print "### found %d files, of which %d have dependencies." % (len(self.files), len(self.filedeps))
        for filename in self.filedeps.keys():
            file = self.filedeps[filename]
            line = "  %-30s " % filename
            linesub = ""
            sublines = []
            if len(file[REQUIRES][FILE]) > 3:
                linesub = "requires: %d files" % (len(file[REQUIRES][FILE]))
            elif len(file[REQUIRES][FILE]) > 0:
                linesub = "requires: %s" % (str(file[REQUIRES][FILE]))
            if linesub != "":
                sublines.append("%-50s" % linesub)
                
            linesub = ""
            if len(file[REQUIREDBY][FILE]) > 3:
                linesub = "required by: %d files" % (len(file[REQUIREDBY][FILE]))
            elif len(file[REQUIREDBY][FILE]) > 0:
                linesub = "required by: %s" % (str(file[REQUIREDBY][FILE]))
            if linesub != "":
                sublines.append("%-50s" % linesub)
            line += ", ".join(sublines)
            print line
        print "### %d files depends on each other" % (crossdep)               
        print "### advanced file dependency check finished"


            #if len(file[PROVIDES]) == 0
    
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
                fn = os.path.join(root, f)
                fl[fn] = {}
        #for fk in fl.keys():
        #    print "%10s %s" % ("", fk)
        #print "found %d files!" % (len(fl.keys()))
        self.files = fl

    def newRelation(self, dep):
        # ensures that each field exists
        tmp = {}
        for rel in RELATIONS:
            tmp[rel] = {}
            for type in TYPES:
                tmp[rel][type] = []
        for rel in dep.keys():
            for type in dep[rel].keys():
                if type == FILE:
                    for f in dep[rel][type]:
                        #print f
                        tmp[rel][type].append(os.path.basename(f))
                else:
                    tmp[rel][type] = dep[rel][type]
        return tmp
        
    def createDeps(self):
        tree = self.filedeps
        print "### dependency checker log following"
        for filename in self.files.keys():
            onlyfilename, extension = os.path.splitext(filename)
            basefilename = os.path.basename(filename)
            dependencies = self.getDependencies(extension, filename)
            #print "DEP "+ basefilename +" / "+str(dependencies)
            if not dependencies is None:
                for relation in dependencies.keys():
                    deps = dependencies[relation]
                    tree[basefilename] = {}
                    tree[basefilename][relation] = {}
                    for type in deps.keys():
                        tree[basefilename] = self.newRelation(dependencies)            
        print "### file dependency check finished"

def usage():
    print "usage: %s <path to inspect> <all or unused or missing>" % os.path.basename(sys.argv[0])
    print "for example: %s c:\\ror\\data missing" % os.path.basename(sys.argv[0])
    print " valid modes:"
    print " 'all' displays all dependencies, inclusive fulfilled ones"
    print " 'missing' displays only unfulfilled dependencies"
    print " 'unused' displays resources that are not in use"
    print " 'dtree <resourcename>'  displays the dependency tree of the given resource name"
    sys.exit(0)
            
def main():
    if not os.path.isdir(sys.argv[1]):
        print "%s is not a valid directory!" % sys.argv[1]
        usage()
    if (len(sys.argv) == 3 and sys.argv[2] in ['all', 'missing', 'unused']) or (len(sys.argv) == 4 and sys.argv[2] in ['dtree']):
        pass
    else:
        print "%s is not a valid mode, or incorrect arguments!" % sys.argv[2]
        usage()
    
    dependfilename = ""
    if len(sys.argv) == 4 and sys.argv[2] in ['dtree'] and sys.argv[3].strip() != "":
        dependfilename = sys.argv[3].strip()
    
    RoRDepChecker(sys.argv[1], sys.argv[2], dependfilename)

if __name__ == "__main__":
    main()
