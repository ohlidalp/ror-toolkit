import warnings
warnings.simplefilter('ignore', RuntimeWarning)

from _physx_ import *
import ogre.renderer.OGRE as ogre

def NxQuat( arg0=None, arg1=None ):
    if isinstance (arg0, ogre.Quaternion) :
        ret = _physx_.NxQuat()
        ret.w = arg0.w
        ret.x = arg0.x
        ret.y = arg0.y
        ret.z = arg0.z
        return ret    
    elif arg1:
        return _physx_.NxQuat(arg0,arg1)
    elif arg0:
        return _physx_.NxQuat(arg0)    
    return _physx_.NxQuat()
warnings.resetwarnings( ) 
    