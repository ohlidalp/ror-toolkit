# by Lepes 2008-10-01
import wx, os, os.path, copy
from types import *

import ogre.renderer.OGRE as ogre
from logger import log
from ror.rorcommon import *
from ror.settingsManager import *

class showedError(Exception):
	def __init__(self, strMessage):
		""" Shown and logged exception with:
		strMessage = message to show on error dialog"""
		self.newMessage = strMessage
		log().error(strMessage)
		dlg = wx.MessageDialog(rorSettings().mainApp,
							   strMessage,
							   "error",
								wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		
	def __str__(self):
		return self.newMessage

class showedWarning(Exception):
	def __init__(self, strMessage):
		""" Shown and logged exception with:
		strMessage = message to show on warning dialog"""
		log().warning(strMessage)
		rorSettings().mainApp.MessageBox("warning", strMessage)


class logTerrainEditorError(Exception):
	def __init__(self, strMessage):
		self.newMessage = strMessage
		log().error(strMessage)
		
	def __str__(self):
		return self.newMessage

def ifNone(AValue, defaultValue, anotherValue=None):
	""" if AValue is None, 
	         return defaultValue
	    else return anotherValue or Avalue (in this order)"""
	if AValue is None: return defaultValue
	else: 
		if anotherValue is None:
			return AValue
		else:
			return anotherValue
	
def getList(value):
	""" accept Tuple, None, List, Vector3 and Quaternion 
	 returnning a python List """
	result = []
	if type(value) is TupleType:
		for i in value:
			result.append(i)
	elif isinstance(value, NoneType):
		result.append(None)
	elif type(value) is ListType:
		result = value
	elif isinstance(value, ogre.Vector3):
		result.append(value.x)
		result.append(value.y)
		result.append(value.z)
	elif isinstance (value, ogre.Quaternion) :
		result.append(value.w)
		result.append(value.x)
		result.append(value.y)
		result.append(value.z)
	else :
		raise Exception("Unknown instance in ror.lputils.getList()")
	return result

class posRotClass(object):
#	values = [] don't touch !!!
	
	def clear(self):
		del self.values
		
	def setValues(self, value):
		""" accept Tuple, None, List, Vector3 and Quaternion 
		 returng a List.
		 
		 If you use a asQuaternion you must be coherent """
		
		self.clear()
		self.values = []
		
		if type(value) is TupleType or type(value) is ListType:
			for i in value:
				self.values.append(i)
		elif isinstance(value, NoneType):
			self.values.append(None)
			self.values.append(None)
			self.values.append(None)
			self.values.append(None)
		elif isinstance(value, ogre.Vector3):
			self.values.append(value.x)
			self.values.append(value.y)
			self.values.append(value.z)
		elif isinstance (value, ogre.Quaternion) :
			self.values.append(value.w)
			self.values.append(value.x)
			self.values.append(value.y)
			self.values.append(value.z)

		else :
			raise Exception("Instance Type not allowed in posRotClass.setValues")
	
	def getasVector3(self):
		if self.values is None:
			self.values = []
			
		if len(self.values) < 3:
			self.append(0)
			self.append(0)
			self.append(0)
		return ogre.Vector3(self.values[0], self.values[1], self.values[2])
		   
	def setasVector3(self, value):
		self.setValues(value)
	   
	def getasTuple(self):
		return self.values[0], self.values[1], self.values[2]
		   
	def setasTuple(self, value):
		self.setValues(value)
	   
	
	def getasList(self):
		return self.values
		   
	def setasList(self, value):
		self.setValues(value)
	
	
	def getasQuaternion(self):
		if len(self.values) != 4:
			raise Exception("we don't have 4 values to convert to Quaternion")
		
		return ogre.Quaternion(self.values[0], self.values[1], self.values[2], self.values[3])
		   
	def setasQuaternion(self, value):
		self.setValues(value)
	
	def isNone(self):   
		return self.values[0] is None
	
	def hasValues(self):
		return self.values[0] is not None
	def nearZero(self, num):
		""" check if num is near Zero < 0.0001 due
		floats imprecision"""
		return abs(num) < 0.0001 
	def format(self, text):
		""" return x, y, z, text"""
		return ("%12.6f, %12.6f, %12.6f, %20s" % (self.values[0], self.values[1], self.values[2], text))

	def leftAlign(self, text):
		""" return text x, y, z"""
		return ("%20.20s %12.6f, %12.6f, %12.6f" % (text, self.values[0], self.values[1], self.values[2]))

	def rightAlign(self, text):
		""" return text x, y, z"""
		return ("%.20s %12.6f, %12.6f, %12.6f" % (text, self.values[0], self.values[1], self.values[2]))
	
	def format2(self):
		""" return x, y, z"""
		return ("%12.6f, %12.6f, %12.6f" % (self.values[0], self.values[1], self.values[2]))		
	def format3(self):
		""" return text x, y, z"""
		return ("%12.3f, %12.3f, %12.3f" % (self.values[0], self.values[1], self.values[2]))		

	
	def isZero(self):
		return not self.isNone() and len(self.values) > 2 and self.nearZero(self.values[0]) \
			   and self.nearZero(self.values[1]) and self.nearZero(self.values[2]) 
	
	def _getasStrList(self):
		return [str(x) for x in self.values]
		   
	def _setasStrList(self, value):
		self.clear()
		self.values = [float(x.strip()) for x in value]
	
	asQuaternion = property(getasQuaternion, setasQuaternion,
					 doc="""You must be coherent.
					 If you set up as Quaternion, then you 
					 shouldn't read as a Tuple """)   
	asList = property(getasList, setasList,
					 doc=""" return a python List with each value""")
	   
	asStrList = property(_getasStrList, _setasStrList,
					 doc="""return a python List with strings in each position
						   Mainly to print values """)
	asVector3 = property(getasVector3, setasVector3,
					 doc="""return ogre.Vector3 filled """)
	asTuple = property(getasTuple, setasTuple,
					 doc="""return a python tuple with x, y, z """)
	


class positionClass(posRotClass):
	
	def __del__(self):
		del self.values
		
	def __str__(self):
		return " " + ", ".join(self.values)

	def __init__(self):
		self.values = [0, 0, 0, 0]
							   
	def _getx(self):
		return self.values[0]
		   
	def _setx(self, value):
		self.values[0] = value
	
	def _gety(self):
		return self.values[1]
		   
	def _sety(self, value):
		self.values[1] = value
	
	def _getz(self):
		return self.values[2]
		   
	def _setz(self, value):
		self.values[2] = value
	   
	z = property(_getz, _setz,
					 doc="""""")
	y = property(_gety, _sety,
					 doc="""""")
	x = property(_getx, _setx,
					 doc="""""")
   
class rotationClass(posRotClass):
	def __del__(self):
		del self.values


	def __str__(self):
		return " " + ", ".join(self.values)

	def __init__(self):
		self.values = [0, 0, 0, 0]
		
	def _getrotx(self):
		return self.values[0]
		   
	def _setrotx(self, value):
		self.values[0] = value
	
	def _getroty(self):
		return self.values[1]
		   
	def _setroty(self, value):
		self.values[1] = value
	
	def _getrotz(self):
		return self.values[2]
		   
	def _setrotz(self, value):
		self.values[2] = value
	   
	rotz = property(_getrotz, _setrotz,
					 doc="""""")
	roty = property(_getroty, _setroty,
					 doc="""""")
	rotx = property(_getrotx, _setrotx,
					 doc="""""")
	
	
#test class 
if __name__ == "__main__": 
	""" easy class to use with ogre in example:
	
	point1 = positionClass()
	point1.asStrList = ["1", "2", "3"] # readed from a text file
	
	myOgreNode.setPosition(point1.asTuple)
	point1.asVector3 = myOgreNode.getPosition() + myOgreNode2.getPosition()
	
	print point1.asStrList 
   
	"""
	
	x = positionClass()
	x.asList = [1, 2, 3]
	print x.x
	del x
	y = positionClass() 
	y.asList = [3, 3, 3]
#	print " ".join(x.asStrList)
	print " ".join(y.asStrList)
	print y.x
	y.asList = [4, 4, 4]
	print y.x
#	print x.x	
		
		
