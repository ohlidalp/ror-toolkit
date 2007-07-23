import os, os.path, re
import subprocess 
from deptools import *
#540, 55, 1690, 0, 43, 0, truck	wahoo.truck

RE1 = r"^.*,.*,.*,.*,.*,.*,(.*)$"

RE2 = r"^(.*\.cfg)$"

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
                try:
                    # workaround to ignore float numbers in here!
                    str(int(valname.replace(".",""))) == valname.replace(".","")
                except:
                    vals.append(valname)
    # remove position info
    if len(vals) > 0:
        del vals[0]
        for i in range(0, len(vals)):
            if vals[i].find(".") == -1:
                vals[i] += ".odef"
    return vals

def parseRE2(content, r):
    vals = []
    i = 0
    for line in content:
        i += 1
        m = re.match(r, line)
        if not m is None and len(m.groups()) > 0:
            valname = m.groups()[0]
            valname = valname.strip()
            return valname
    return None
    
def getDependencies(filename):
    content = readFile(filename)
    dep = parseRE(content, RE1)
    cfgfilename = parseRE2(content, RE2)
    if not cfgfilename is None:
        dep.append(cfgfilename)

    terrnname, ext = os.path.splitext(os.path.basename(filename))
    
    if len(dep) == 0:
        print "no objects found in terrain file " + filename
    else:
        return {
                OPTIONAL:{
                           FILE:[terrnname+'-mini.png'],
                         },
                REQUIRES:{
                           FILE:dep,
                         },
                PROVIDES:{
                           FILE:[filename],
                         },
               }