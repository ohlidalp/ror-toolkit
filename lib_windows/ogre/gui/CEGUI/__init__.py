import sys, os 
import warnings
warnings.simplefilter('ignore', RuntimeWarning)

## we need the path for additional CEGUI dll's 
if sys.platform == 'win32': 
    os.environ['PATH'] =  __path__[0] +';' + os.environ['PATH']

elif sys.platform == "linux2":
    ## We need to import the library 
    import ctypes
    ctypes.CDLL("libCEGUIBase.so.1", ctypes.RTLD_GLOBAL)

from _cegui_ import *
## Make sure we are using a sane XML parser
if os.name == 'nt':
    System.setDefaultXMLParserName("ExpatParser")
else:
    System.setDefaultXMLParserName("TinyXMLParser")

warnings.resetwarnings( ) 
