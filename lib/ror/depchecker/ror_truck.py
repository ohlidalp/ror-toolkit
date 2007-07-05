import os, os.path
from truckparser import *

def getDependencies(filename):
    p = rorparser()
    p.parse(filename)
    if not 'globals' in p.tree.keys():
        print "truck parsing error on file " + filename
    truckfilename = os.path.basename(filename)
    truckname, ext = os.path.splitext(truckfilename)
    matname = p.tree['globals'][0]['data'][2]
    print truckname
    return {
            "depends":{
                       "materials":[matname],
                       #"file":[truckname+'-mini.png']
                      },
            "provide":{
                       "file":[truckfilename]
                      }
           }
