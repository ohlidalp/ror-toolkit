import sys, os 
import warnings
warnings.simplefilter('ignore', RuntimeWarning)

## we need the path for additional CEGUI dll's 
if sys.platform == 'win32': 
    os.environ['PATH'] += ';' + __path__[0]
     
from _cegui_ import *
warnings.resetwarnings( ) 
