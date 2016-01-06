import sys, os 
import warnings
warnings.simplefilter('ignore', RuntimeWarning)

# Note that we put the Python-Ogre path first to ensure we don't get strange problems with windows
# picking up the wrong dlls -- Thanks to Pelle for tracking down this issue..
if sys.platform == 'win32': 
    os.environ['PATH'] =  __path__[0] +';' + os.environ['PATH']

from _ogre_ import *
from _ogre_exceptions_ import *


## Note the work around to ensure the Radians and Degree types work correctly
## the problem is the constructors are overloaded in each class and passing a real to 
## Radian actually causes boost to try it as a Degree first, and as Degreee has a 'Real' overload
## it create the Degree and passes it back to Radian -- 
##
## and as it's a lot of work and  overly confusing to fix this in generate_code.py we fix it here
##
def Radian( r=None, d=None ):
    if isinstance( r, _ogre_.Degree ):
        return _ogre_.Radian( r )
    elif isinstance( r, _ogre_.Radian ):
        return _ogre_.Radian().assign( r )
    elif d:
        return _ogre_.Radian( d=d )
    else:
        return _ogre_.Radian( r=r )
       
def Degree( d=None, r=None ):
    if isinstance( d, _ogre_.Radian ):
        return _ogre_.Degree( d )
    elif isinstance( d, _ogre_.Degree ):
        return _ogre_.Degree().assign( d )
    elif r: 
        return _ogre_.Degree (r=r)
    else:
        return _ogre_.Degree( d=d )
        
warnings.resetwarnings( ) 

