import sys, zipfile, os, os.path

def unzip(file, dir):
    try:
        os.mkdir(dir)
    except:
        pass
    try:
        zfobj = zipfile.ZipFile(file)
        for name in zfobj.namelist():
            if name.endswith('/'):
                os.mkdir(os.path.join(dir, name))
            else:
                dirnow = dir
                dirnow = dirnow.replace("/", "\\")
                subdirs = name.split("/")
                if len(subdirs) > 0:
                    for subdir in subdirs:
                        dirnow = os.path.join(dirnow, subdir)
                if not os.path.isdir(os.path.dirname(dirnow)):
                    os.mkdir(os.path.dirname(dirnow))
                outfile = open(dirnow, 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
    except Exception, err:
        print str(err)
        return