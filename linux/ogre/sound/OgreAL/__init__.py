import sys, os 

if sys.platform == 'win32': 
    os.environ['PATH'] += ';' + __path__[0] 

from _ogreal_ import *