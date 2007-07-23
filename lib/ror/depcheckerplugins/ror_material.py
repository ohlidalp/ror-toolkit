import os, os.path, re
import subprocess 
from deptools import *

RE1 = r"^\s*texture.?([a-zA-Z0-9_\-]*\.[a-zA-Z0-9]*)\s?.*"
RE2 = r"\s?material\s?([a-zA-Z0-9_/\-\\]*).?"

def readFile(filename):
    f=open(filename, 'r')
    content = f.readlines()
    f.close()
    return content

def parseRE(content, r):
    vals = []
    for line in content:
        m = re.match(r, line)
        if not m is None and len(m.groups()) > 0:
            valname = m.groups()[0]
            if not valname in vals:
                vals.append(valname)
    return vals
    
def getDependencies(filename):
    content = readFile(filename)
    dep = parseRE(content, RE1)
    prov = parseRE(content, RE2)
    if len(dep) == 0:
        #print "no texture found in material file " + filename
        pass
    if len(prov) == 0:
        print "no material found in material file " + filename        
    else:
        return {
                OPTIONAL:{
                         },
                REQUIRES:{
                           FILE:dep,
                         },
                PROVIDES:{
                           MATERIAL:prov,
                           FILE:[filename],
                         },
               }