import os, os.path
from ror.truckparser import *
from deptools import *

def getDependencies(filename):
    p = rorparser()
    p.parse(filename, verbose=False)
    print "getting info for file %s" % filename
    idxglobal = p.sectionStart('globals')
    if idxglobal == -1:
        log().error("truck parsing error on file " + filename + ' cause: Not found globals section')
    truckfilename = os.path.basename(filename)
    truckname, ext = os.path.splitext(truckfilename)
    print p.lines[idxglobal + 1].getTruckLine()
    matname = p.lines[idxglobal + 1].material
    
    # collect props
    props = []
    istart = p.sectionStart('props')
    iend = p.sectionEnd('props')
    
    for i in range(istart + 1, iend - 1):
		props.append(p.lines[i].mesh)
		if p.lines[i].wheel_mesh is not None and p.lines[i].wheel_mesh != '':
			props.append(p.lines[i].mesh_wheel)
    
    #print truckname
    return {
            OPTIONAL:{
                       MATERIAL:["tracks/" + truckname + 'help'],
                       FILE:[truckname + '-mini.png'],
                     },
            REQUIRES:{
                       MATERIAL:[matname],
                       FILE:props,
                     },
            PROVIDES:{
                       FILE:[filename],
                     },
           }
