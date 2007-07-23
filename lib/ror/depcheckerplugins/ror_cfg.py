import os, os.path, re
import subprocess 
from deptools import *

REs = [r"^WorldTexture=(.*)$", r"^DetailTexture=(.*)$", r"^Heightmap.image=(.*)$"]

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
            valname = valname.strip()
            return valname
    return None
    
def getDependencies(filename):
    content = readFile(filename)

    # ignore standart configuration files
    file = os.path.basename(filename).lower()
    if file in ['editor.cfg', 'resources.cfg', 'ror.cfg', 'wavefield.cfg', 'plugins.cfg', 'ogre.cfg']:
        return {OPTIONAL:{},REQUIRES:{},PROVIDES:{}}
    
    dep = []
    for re in REs:
        tmp = parseRE(content, re)
        if not tmp is None:
            dep.append(tmp)
        else:
            print "ERROR !!! required value not found in terrain config file %s!" % filename

    if len(dep) == 0:
        print "no configuration found in terrain config file " + filename
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