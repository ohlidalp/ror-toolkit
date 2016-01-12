import os, os.path, re
import subprocess 
from deptools import *

def getDependencies(filename):
    return {OPTIONAL:{},REQUIRES:{},PROVIDES:{}}
