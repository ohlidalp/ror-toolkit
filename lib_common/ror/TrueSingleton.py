#Lepes 2009-01-26 
# True implementation of Singleton pattern defined on Python 2.5 guides.


#------------------------------------------------------------------------------ 
#
#  Subclases MUST OVERRIDE init method, if they want to do something after calling the instance. 
#
#------------------------------------------------------------------------------ 

class Singleton(object):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it
    
    def init(self, *args, **kwds):
        pass
