import sys, os, os.path, re
import subprocess 

from deptools import *

# todo remove this hardcoded stuff here!
CONVERTERBIN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\\..\\..\\tools\\OgreCommandLineTools\\OgreXmlConverter.exe"))
REs = [r".*material\s?=[\"\']([a-zA-Z0-9_/\-\\]*)[\"\'].*"]

def readFile(filename):
    f=open(filename, 'r')
    content = f.readlines()
    f.close()
    return content

def convertToXML(filename):
    # try to convert to .msh.xml first!
    cmd = CONVERTERBIN + " " + filename
    print "calling " + cmd
    p = subprocess.Popen(cmd, shell = False, cwd = os.path.dirname(CONVERTERBIN), stderr = subprocess.PIPE, stdout = subprocess.PIPE)
    p.wait()
    print "mesh converted: " + filename

def parseRE(content):
    deps = []
    for line in content:
        for r in REs:
            m = re.match(r, line)
            if not m is None and len(m.groups()) > 0:
                depname = m.groups()[0]
                if not depname in deps:
                    deps.append(depname)
    return deps
            
    
def getDependencies(filename):
    xmlfilename = os.path.join(os.path.dirname(filename), os.path.basename(filename)+".xml")
    if not os.path.isfile(xmlfilename):
        convertToXML(filename)
    try:
        content = readFile(xmlfilename)
    except Exception, e:
        print e
    dep = parseRE(content)
    if len(dep) == 0:
        print "no material found for file " + filename
    else:
        return {
                OPTIONAL:{
                         },
                REQUIRES:{
                           MATERIAL:dep,
                         },
                PROVIDES:{
                           FILE:[filename],
                         },
               }

