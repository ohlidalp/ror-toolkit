import sys, os 

# Note that we put the Python-Ogre path first to ensure we don't get strange problems with windows
# picking up the wrong dlls -- Thanks to Pelle for tracking down this issue..
if sys.platform == 'win32': 
    os.environ['PATH'] =  __path__[0] +';' + os.environ['PATH']

from _ogredshow_ import *
