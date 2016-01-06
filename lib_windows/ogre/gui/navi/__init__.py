import sys, os 

if sys.platform == 'win32': 
    os.environ['PATH'] =  __path__[0] +';' + os.environ['PATH']

from _navi_ import *
