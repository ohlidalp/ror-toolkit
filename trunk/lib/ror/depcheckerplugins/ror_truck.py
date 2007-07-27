import os, os.path
from ror.truckparser import *
from deptools import *

def getDependencies(filename):
    p = rorparser()
    p.parse(filename, verbose=False)
    if not 'globals' in p.tree.keys():
        log().error("truck parsing error on file " + filename)
    truckfilename = os.path.basename(filename)
    truckname, ext = os.path.splitext(truckfilename)
    matname = p.tree['globals'][0]['data'][2]
    
    # collect props
    props = []
    if 'props' in p.tree.keys():
        for prop in p.tree['props']:
            props.append(prop['data'][-1])
    
    #print truckname
    return {
            OPTIONAL:{
                       MATERIAL:["tracks/"+truckname+'help'],
                       FILE:[truckname+'-mini.png'],
                     },
            REQUIRES:{
                       MATERIAL:[matname],
                       FILE:props,
                     },
            PROVIDES:{
                       FILE:[filename],
                     },
           }
