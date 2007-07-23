import os.path, sys, installmod, time


def getFiles(top):
    fl = {}
    for root, dirs, files in os.walk(top):
        for f in files:
            fn = os.path.join(root, f)
            fl[fn] = {}
    for fk in fl.keys():
        print "%10s %s" % ("", os.path.basename(fk))
        
    print "found %d files!" % (len(fl.keys()))
    return fl

def main():
    dir = sys.argv[1]
    mode = sys.argv[2]
    files = getFiles(dir)
    valid={}
    counter = 0
    countervalid = 0
    for file in files.keys():
        print "## %s (%d/%d)##############################################" % (os.path.basename(file), counter, len(files))
        counter += 1
        mods = installmod.work(mode, file, True, False)
        if len(mods) == 0:
            print "!!! INVALID: ", os.path.basename(file)
        else:
            print "VALID: ", os.path.basename(file)            
            valid[file] = mods
        print "#######################################################################"
        time.sleep(0.01)
    print "################################################"
    print "################################################"
    print "################################################"
    for f in valid.keys():
        print f, valid[f]
    print "%d of %d files containing valid mods!" % (len(valid), len(files))
    

if __name__=="__main__":
    main()