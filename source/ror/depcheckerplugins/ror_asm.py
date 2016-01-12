import os, os.path, re
from deptools import *

def getDependencies(filename):
    return {OPTIONAL:{},REQUIRES:{},PROVIDES:{}}
