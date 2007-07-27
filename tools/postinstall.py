import sys, os, os.path, subprocess

def getBATFiles():
    batfiles = []
    dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    for filename in os.listdir(dir):
        filenameonly, extension = os.path.splitext(filename)
        if extension.lower() == ".bat":
            batfiles.append(os.path.join(dir, filename))
    return batfiles

def saveFile(filename, lines):
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()

def addPath(filename, installpath):
    basename = os.path.basename(filename)
    filenameonly, extension = os.path.splitext(basename)
    
    # with console
    thispath = os.path.join(installpath, filenameonly+".py")
    pythonpath = "%systemdrive%\python25\python.exe"
    if not os.path.isfile(thispath):
        # without console
        thispath = os.path.join(installpath, filenameonly+".pyw")
        pythonpath = "%systemdrive%\python25\pythonw.exe"
    content = ["@%s %s %%*" % (pythonpath, thispath)]
    saveFile(filename, content)

def main():
    installpath = os.path.dirname(os.path.abspath(__file__))
    for batfile in getBATFiles():
        addPath(batfile, installpath)
    print "Post-Installed all .bat files, please restart the program now!"
    cmd = os.path.join(installpath, sys.argv[1]+".bat")
    subprocess.Popen(cmd, shell = True)
    
if __name__=="__main__":
    main()
