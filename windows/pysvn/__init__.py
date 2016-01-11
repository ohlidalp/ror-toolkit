'''
 ====================================================================
 Copyright (c) 2003-2006 Barry A Scott.  All rights reserved.

 This software is licensed as described in the file LICENSE.txt,
 which you should have received as part of this distribution.

 ====================================================================
'''
import sys
import UserDict

class PysvnDictBase(UserDict.IterableUserDict):
    def __init__( self, value_dict, name='' ):
        UserDict.IterableUserDict.__init__( self, value_dict )
        self.__name = name
        if self.__name is None:
            print '%s given None as name' % self.__class__.__name__

    def __getattr__( self, name ):
        if name in self.data:
            return self.data[ name ]
        raise AttributeError( "%s instance has no attribute '%s'" % (self.__class__.__name__, name) )

    def __repr__( self ):
        return '<%s %s>' % (self.__class__.__name__, repr(self.__name))


class PysvnDirent(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict, value_dict.get( 'name', None ) )

class PysvnList(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict, value_dict.get( 'path', None ) )

class PysvnEntry(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict, value_dict.get( 'name', None ) )

class PysvnInfo(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict )

class PysvnLock(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict )

class PysvnLog(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict )

class PysvnLogChangedPath(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict )

class PysvnWcInfo(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict )

class PysvnStatus(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict, value_dict.get( 'path', None ) )

class PysvnDiffSummary(PysvnDictBase):
    def __init__( self, value_dict ):
        PysvnDictBase.__init__( self, value_dict, value_dict.get( 'path', None ) )

# An indication that you are interested in the @c kind field
SVN_DIRENT_KIND        = 0x00001

# An indication that you are interested in the @c size field
SVN_DIRENT_SIZE        = 0x00002

# An indication that you are interested in the @c has_props field
SVN_DIRENT_HAS_PROPS   = 0x00004

# An indication that you are interested in the @c created_rev field
SVN_DIRENT_CREATED_REV = 0x00008

# An indication that you are interested in the @c time field
SVN_DIRENT_TIME        = 0x00010

# An indication that you are interested in the @c last_author field
SVN_DIRENT_LAST_AUTHOR = 0x00020

# A combination of all the dirent fields
SVN_DIRENT_ALL         = 0xffffffffl

try:
    maj_min = sys.version_info[:2]

    #
    # use an if tree so that its easy for app makers to
    # find the import that is requires
    #
    if maj_min == (2,3):
        import _pysvn_2_3
        _pysvn = _pysvn_2_3
    elif maj_min == (2,4):
        import _pysvn_2_4
        _pysvn = _pysvn_2_4
    elif maj_min == (2,5):
        import _pysvn_2_5
        _pysvn = _pysvn_2_5
    else:
        raise ImportError( 'Fix pysvn/__init__.py to support python %d.%d' % tuple(maj_min) )

    for key, value in _pysvn.__dict__.items():
        if not key.startswith( '__' ):
            globals()[ key ] = value

except ImportError, e:
    # check for common installation errors that show up as ImportError
    if ': undefined symbol:' in str(e):
        raise ImportError, 'pysvn was built against newer (svn, apr, etc.) libraries then the ones installed on this system. %s' % str(e)
    else:
        raise

def Client( config_dir='' ):
    return _pysvn._Client( config_dir, result_wrappers=globals() )

def Transaction( repos_path, transaction_name ):
    return _pysvn._Transaction( repos_path, transaction_name, result_wrappers=globals() )
