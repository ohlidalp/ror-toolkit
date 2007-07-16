import os, os.path, re
import subprocess 
from deptools import *
#540, 55, 1690, 0, 43, 0, truck	wahoo.truck
RE1 = r"^.*,.*,.*,.*,.*,.*,(.*)$"

def readFile(filename):
    f=open(filename, 'r')
    content = f.readlines()
    f.close()
    return content

def parseRE(content, r):
    vals = []
    i = 0
    for line in content:
        i += 1
        m = re.match(r, line)
        if not m is None and len(m.groups()) > 0:
            valname = m.groups()[0]
            valname = valname.replace("\t", " ")
            valnameg = valname.strip().split(" ")
            valname = valnameg[0].strip()
            if valname == "truck":
                valname = valnameg[-1].strip()
            if not valname in vals:
                if valname.find("observatory") > 0:
                    print valnameg
                    import time
                    time.sleep(10)
                vals.append(valname)
    # remove position info
    del vals[0]
    for i in range(0, len(vals)):
        if vals[i].find(".") == -1:
            vals[i] += ".odef"
    #print vals
    return vals
    
def getDependencies(filename):
    content = readFile(filename)
    dep = parseRE(content, RE1)
    if len(dep) == 0:
        print "no objects found in terrain file " + filename
    else:
        return {
                OPTIONAL:{
                         },
                REQUIRES:{
                           FILE:dep,
                         },
                PROVIDES:{
                           FILE:[filename],
                         },
               }