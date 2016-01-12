import os, os.path, re
import subprocess 
from deptools import *

def readFile(filename):
    f=open(filename, 'r')
    content = f.readlines()
    f.close()
    return content
   
def getDependencies(filename):
    content = readFile(filename)
    dep = content[0].strip()
    return {
            OPTIONAL:{
                     },
            REQUIRES:{
                       FILE:[dep],
                     },
            PROVIDES:{
                       FILE:[filename],
                     },
           }