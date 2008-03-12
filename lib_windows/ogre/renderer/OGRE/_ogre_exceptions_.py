import _ogre_
class OgreException(Exception):
    def __init__( self, app_error ):
        Exception.__init__( self )
        self._pimpl = app_error
    
    def __str__( self ):
        return self._pimpl.getFullDescription()

    def __getattribute__(self, attr):
        my_pimpl = super(OgreException, self).__getattribute__("_pimpl")
        try:
            return getattr(my_pimpl, attr)
        except AttributeError:
            return super(OgreException,self).__getattribute__(attr)

_ogre_.OgreException = OgreException
#this one for backward compatability
_ogre_.Exception = OgreException
_ogre_._Exception_.py_err_class = OgreException
class OgreFileNotFoundException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreFileNotFoundException,self).__getattribute__(attr)

_ogre_._FileNotFoundException_.py_err_class = OgreFileNotFoundException
_ogre_.OgreFileNotFoundException = OgreFileNotFoundException
class OgreIOException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreIOException,self).__getattribute__(attr)

_ogre_._IOException_.py_err_class = OgreIOException
_ogre_.OgreIOException = OgreIOException
class OgreInvalidStateException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreInvalidStateException,self).__getattribute__(attr)

_ogre_._InvalidStateException_.py_err_class = OgreInvalidStateException
_ogre_.OgreInvalidStateException = OgreInvalidStateException
class OgreInvalidParametersException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreInvalidParametersException,self).__getattribute__(attr)

_ogre_._InvalidParametersException_.py_err_class = OgreInvalidParametersException
_ogre_.OgreInvalidParametersException = OgreInvalidParametersException
class OgreUnimplementedException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreUnimplementedException,self).__getattribute__(attr)

_ogre_._UnimplementedException_.py_err_class = OgreUnimplementedException
_ogre_.OgreUnimplementedException = OgreUnimplementedException
class OgreInternalErrorException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreInternalErrorException,self).__getattribute__(attr)

_ogre_._InternalErrorException_.py_err_class = OgreInternalErrorException
_ogre_.OgreInternalErrorException = OgreInternalErrorException
class OgreItemIdentityException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreItemIdentityException,self).__getattribute__(attr)

_ogre_._ItemIdentityException_.py_err_class = OgreItemIdentityException
_ogre_.OgreItemIdentityException = OgreItemIdentityException
class OgreRuntimeAssertionException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreRuntimeAssertionException,self).__getattribute__(attr)

_ogre_._RuntimeAssertionException_.py_err_class = OgreRuntimeAssertionException
_ogre_.OgreRuntimeAssertionException = OgreRuntimeAssertionException
class OgreRenderingAPIException(OgreException):
    def __init__( self, app_error ):
        OgreException.__init__( self, app_error )
    
    def __getattribute__(self, attr):
        return super(OgreRenderingAPIException,self).__getattribute__(attr)

_ogre_._RenderingAPIException_.py_err_class = OgreRenderingAPIException
_ogre_.OgreRenderingAPIException = OgreRenderingAPIException