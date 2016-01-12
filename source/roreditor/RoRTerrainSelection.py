# Lepes 2008-12-03
import wx, os, os.path, copy
import errno
import ogre.renderer.OGRE as ogre 

from ror.truckparser import *
from ror.terrainparser import *
from ror.odefparser import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.rorcommon import *
from ror.SimpleTruckRepresentation import *
from RoRVirtualKeys import *
from time import clock
from ror.lputils import *
from math import radians, degrees
from RoRConstants import *
import SelectionAxis

UPPERFACE = ["nearMiddle", "nearLeftTop", "nearRightTop", "farLeftTop", "farRightTop", "centerUp"]
BOTTOMFACE = ["nearLeftBottom", "nearRightBottom", "farLeftBottom", "farRightBottom"]


# this class holds all the needed 3d data and also the underlying object data
# please see RoRObjects.gemsmeta2 class diagram.
class simpleEntryClass(object):
	def __del__(self):
		del self.uuid
		del self.node
		del self.entity
		del self.visible
		del self.OnSelecting
		del self.OnDeselecting
		del self.OnPositionChanged
		del self.OnPositionChanging
				
	def getvisible(self):
		return self.entity.getVisible()
		   
	def setvisible(self, value):
		self.entity.setVisible(value)
	
	def _delvisible(self): pass
	
	def vector(self, text):
		p = self.node.getPosition()
		rx = 0
		ry = 0
		rz = 0
		if hasattr(self, 'getrotation'):
			rx, ry , rz = self.getrotation()
		return "%12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %s" % (p.x, p.y, p.z, rx, ry, rz, text) 
	def logPosRot(self, text):
		log().info(self.vector(text))
	
	def removeFromScene(self):
		#FIXME: maybe this node has other child nodes. truck editor is affected by this issue.
		if hasattr(self.ogreWindow, 'sceneManager'):
			self.node.detachAllObjects()
			self.ogreWindow.sceneManager.destroyEntity(self.entity)
			self.ogreWindow.sceneManager.destroySceneNode(str(self.uuid) + 'node')
		self.node = None
		self.entity = None
	def select(self):
		if len(self._OnSelecting) > 0:
			for x in self._OnSelecting:
				x(self) # execute the method		

	def deselect(self):
		if len(self._OnDeselecting) > 0:
			for x in self._OnDeselecting:
				x(self) # execute the method		

	
	def __init__(self, ogreWindow):
		self._visible = True

		""" clear variables that are 
		ONLY before __init__ method"""
		self.uuid = None
		self.node = None
		self.entity = None
		self.ogreWindow = ogreWindow
		self.allowRotation = True
		self.allowTranslation = True
		self.canBeSelected = True
		self._OnSelecting = []
		self._OnDeselecting = []
		self._OnPositionChanged = []
		self._OnPositionChanging = []
		self._OnRotationChanged = []
	
	def __str__(self):
		msg = ""
		if not self.uuid is None:
			msg = str(self.uuid)
		else:
		   msg = "None uuid"
		if not self.node is None:
			msg += self.vector('')
		return msg

	def _getOnSelecting(self):
		return self._OnSelecting
			
	def _setOnSelecting(self, value):
		self._OnSelecting = value
			
	def _delOnSelecting(self):
		del self._OnSelecting
	def _getOnDeselecting(self):
		return self._OnDeselecting
			
	def _setOnDeselecting(self, value):
		self._OnDeselecting = value
			
	def _delOnDeselecting(self):
		del self._OnDeselecting
	
	def inform(self):
		if self.ogreWindow:
			if len(self.OnPositionChanging) > 0:
				for x in self.OnPositionChanging:
					x(self)
					
	def informRotationChanged(self):
		if self.ogreWindow:
			if len(self._OnRotationChanged) > 0:
				for x in self._OnRotationChanged:
					x(self) # execute the method		
		
	def informPositionChanged(self):
		if self.ogreWindow:
			if len(self._OnPositionChanged) > 0:
				for x in self._OnPositionChanged:
					x(self) # execute the method		
	def _getOnPositionChanged(self):
		return self._OnPositionChanged
			
	def _setOnPositionChanged(self, value):
		self._OnPositionChanged = value
			
	def _delOnPositionChanged(self):
		del self._OnPositionChanged
	
	def _getOnPositionChanging(self):
		return self._OnPositionChanging

	def _setOnPositionChanging(self, value):
		self._OnPositionChanging = value
			
	def _delOnPositionChanging(self):
		del self._OnPositionChanging
	
	def getogrePosition(self):
		return self.node.getPosition()
	
	def setogrePosition(self, value):
		self.node.setPosition(value)
		self.inform()

	def getogreRotation(self):
		return self.node._getDerivedOrientation()
	
	def setogreRotation(self, value):
		self.node.resetOrientation()
		self.node.setOrientation(value)
		self.inform()
	
	def _getOnRotationChanged(self):
		return self._OnRotationChanged
			
	def _setOnRotationChanged(self, value):
		self._OnRotationChanged = value
			
	def _delOnRotationChanged(self):
		del self._OnRotationChanged
			
		
	ogrePosition = property(getogrePosition, setogrePosition,
				 doc=""" ogre.Vector3
				 work directly with ogre and notify changes to ogreWindow""") 
   
	ogreRotation = property(getogreRotation, setogreRotation,
				 doc="Quaternion in ogre angles and notify changes to ogreWindow")					
	visible = property(getvisible, setvisible, _delvisible,
					 doc="""Set/get visible entity and Node""")   
	
	OnDeselecting = property(_getOnDeselecting, _setOnDeselecting, _delOnDeselecting,
					doc="Selection Axis call these callbacks on assignning an entry")

	OnSelecting = property(_getOnSelecting, _setOnSelecting, _delOnSelecting,
					doc="Selection Axis call these callbacks on assignning an entry")
	
	OnPositionChanging = property(_getOnPositionChanging , _setOnPositionChanging, _delOnPositionChanging,
				 doc="holds a list of methods pointers to be executed when position is changed")   
		
	OnPositionChanged = property(_getOnPositionChanged, _setOnPositionChanged, _delOnPositionChanged,
					doc="""Only inform on position changed when mouseLeft Up while dragging an entry
					You can append to this list any callback to be called when executing informPositionChanged()
					""")
	OnRotationChanged = property(_getOnRotationChanged, _setOnRotationChanged, _delOnRotationChanged)
	""" youp 
	"""
	
class terrainEntryClass(simpleEntryClass):
	def __del__(self):
		if self._autoRemoveFromScene: self.removeFromScene()
		del self.heightFromGround
		self.deleteData()
		del self.oldOgrePosition
		super(terrainEntryClass, self).__del__()
	
	def deleteData(self):
		self.data.deleted = True
		found = False
		if self.data is not None:
			try:
				if self.ogreWindow:
					if self.ogreWindow.terrain:
						if self.ogreWindow.terrain.objects:
							self.ogreWindow.terrain.objects.remove(self.data)
			except ValueError:
				# orly ???
				pass
#			if not found: print 'terrainEntryClass found the terrain.data to free? %s' % str(found)
			del self.data  #decrement reference count 
	
	def removeFromScene(self):
		try:
			self.OnPositionChanging = []
			self.OnSelecting = []
#			log().debug('deleting from memory %s' % self.data.name)
			super(terrainEntryClass, self).removeFromScene()
		except Exception, err:
			log().error('error deleting entry %s' % str(self.uuid))
			if self.data:
				log().error('error deleting data %s' % str(self.data.name))
			log().error(str(err))
			raise 
	
	def __init__(self, ogreWindow):
		simpleEntryClass.__init__(self, ogreWindow)
		self.data = None
		self.manual = None
		self.oldOgrePosition = ogre.Vector3(0, 0, 0)
		# difference from actual position and the last one.
		
		self._height = 0
		self._deleted = False
		self._terrainHeight = 0
	
		self._x = 0.0
		self._y = 0.0 
		self._z = 0.0
		self._rotationX = 0
		self._rotationY = 0
		self._rotationZ = 0
		self._beginUpdate = 0
		self._autoRemoveFromScene = False

	def __str__(self):
		msg = ""
		if self.data:
			msg = self.data.name + " "
		else:
			msg = "< No data > "
		if self.node:
			msg += self.vector(" ")
		else:
			msg += " < No Node > "
		return msg		 
	
	def replaceEntity(self, odefFilename, meshName, newMaterialName=None):
		""" standard RoR objects have the same filename, it only vary on extension but...
		we can not guarantee that for all objects.
		
		"""
		self.node.detachAllObjects()
		self.ogreWindow.sceneManager.destroyEntity(self.entity)
		self.data.fileWithExt = odefFilename
		self.entity = self.ogreWindow.sceneManager.createEntity(str(self.uuid) + "Entity", meshName)
		if newMaterialName is not None:
			self.entity.setMaterialName(newMaterialName)
		self.node.attachObject(self.entity)
		if self.data:
			self.data.modified = True


	def getposition(self):
		p = self.node.getPosition()
		return p.x, p.y, p.z

	def select(self):
		if self._beginUpdate > 0 : return
		super(terrainEntryClass, self).select()

	def deselect(self):
		if self._beginUpdate > 0 : return
		
		super(terrainEntryClass, self).deselect()
		
	def inform(self):   
		
		self.data.position = self.position
		self.data.rotation = self._rotationX, self._rotationY, self._rotationZ
		if self._beginUpdate > 0 : return
		super(terrainEntryClass, self).inform()

	def setposition(self, value):
		"""first set up node position, if it fail, nothing happens
		#entity must exist"""
		self._x, self._y, self._z = value
		if self.node is None or self.data is None:
			log().error("Entry.node or Entry.data is not Assigned !!")
			return
		if self.data:
			self.node.setScale(self.data.scale)
		self.oldOgrePosition = self.node.getPosition()
		self.node.setPosition(value)		
		self.calcheight()
		
		self.inform()
	def _delposition(self): pass
	
	def getrotation(self):
		if self.node is None or self.data is None:
			return 
		self.node.setScale(1, 1, 1)
		if not self.data.ext.lower() in noRotateExt:
			self.node.rotate(ogre.Vector3(1, 0, 0), radians(90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		rot = self.node._getDerivedOrientation()
		rot.normalise()
		self._rotationZ = degrees(rot.getYaw(False).valueRadians()) 
		self._rotationY = degrees(rot.getRoll(False).valueRadians())
		self._rotationX = degrees(rot.getPitch(False).valueRadians())
		if not self.data.ext.lower() in noRotateExt:
			self.node.rotate(ogre.Vector3(1, 0, 0), radians(-90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		self.node.setScale(self.data.scale)

#		self._rotationX = round(self._rotationX, 2)
#		self._rotationY = round(self._rotationY, 2)
#		self._rotationZ = round(self._rotationZ, 2)

		return self._rotationX, self._rotationY, self._rotationZ

	   
	def setrotation(self, value):
		""" value is in file coordenates """
				
		if self.node is None or self.data is None:
			return
		self._rotationX, self._rotationY, self._rotationZ = value
		self.node.setScale(1, 1, 1)
		self.node.resetOrientation()
		
		rot = ogre.Quaternion(1, 0, 0, 0)
		if abs(self._rotationX) > 0.001:
			rot = rot * ogre.Quaternion(ogre.Degree(self._rotationX), ogre.Vector3(1, 0, 0))
		if abs(self._rotationY) > 0.001:
			rot = rot * ogre.Quaternion(ogre.Degree(self._rotationY), ogre.Vector3(0, 1, 0))
		if abs(self._rotationZ) > 0.001:						
			rot = rot * ogre.Quaternion(ogre.Degree(self._rotationZ), ogre.Vector3(0, 0, 1))
		self.node.rotate(rot) #RoR source code
		if not self.data.ext.lower() in noRotateExt:
			self.node.pitch(ogre.Degree(-90)) #RoR source code
		self.node.setScale(self.data.scale)
			
		self.oldOgrePosition = self.node.getPosition()
		self.inform()
				
	def _delrotation(self):	
		del self._rotationX
		del self._rotationY
		del self._rotationZ

	def rorLookAt(self, pos):
		""" make an object look to the position of pos
		pos maybe vector3 or tuple
		
		return a tuple: rx, ry, rz
		"""
		if isinstance(pos, TupleType):
			vector3 = ogre.Vector3(pos[0], pos[1], pos[2])
		elif isinstance(pos, ogre.Vector3):
			vector3 = pos
		else:
			raise showedError("TerrainentryClass.rorLookAt need a vector3 or tuple!!")
		
		self.node.resetOrientation()
		self.node.lookAt(vector3, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(0, 0, 1))
		self.node.lookAt(vector3, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(0, 1, 0))
		self.node.lookAt(vector3, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(1, 0, 0))
		rx, ry, rz = self.getrotation()
		# it is really strange that it works :-P
		self.rotation = 0.0, ry, -rz
		self.inform()
		return 0.0, ry, -rz
	def roadLookAt(self, lookAt, lastRy):
		""" 
		Look At vector3 and move the road as RoR mobile 
		attach point compliant
		
		return the new position and rotation of this road six-tuple
		"""
		if isinstance(lookAt, TupleType):
			vector3 = ogre.Vector3(pos[0], pos[1], pos[2])
		elif isinstance(lookAt, ogre.Vector3):
			vector3 = pos
		else:
			raise showedError("TerrainentryClass.roadLookAt need a vector3 or tuple!!")
		rx, ry, rz = self.rorLookAt(lookAt)
		
		if lastRy - ry > 0.0: neg = 1.0
		elif lastRy - ry < 0.0: neg = -1.0
		else: neg = 0.0

		lleft = self.node.getPosition() + ogre.Quaternion(ogre.Degree(ry), ogre.Vector3(0, 1, 0)) * ogre.Vector3(0.0, 0.0, neg * 4.5);			
		self.node.setPosition(ogre.Quaternion(ogre.Degree(lastRy - ry), ogre.Vector3(0, 1, 0)) * (self.node.getPosition() - lleft) + lleft)
		p = self.node._getDerivedPosition()
		rx, ry, rz = self.getrotation()
		rx = 0.0
		self.rotation = 0.0, ry, -rz
		rx, ry, rz = self.getrotation()
		# it is really strange that it works :-P
		self.rotation = 0.0, ry, -rz
		self.inform()
		return p.x, p.y, p.z, 0.0, ry, -rz
		
	def translate(self, tuplePos):
		self.node.translate(tuplePos)
		
	def vector(self, text):
		x, y, z = self.getposition()
		rx, ry, rz = self.rotation
		return "%12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %s" % (x, y, z, rx, ry, rz, text) 
	def logPosRot(self, text):
		log().info(self.vector(text))

	def getogreRotation(self):
		if self.node is None or self.data is None:
			return

		return self.node._getDerivedOrientation()
	   
	def setogreRotation(self, value):
		""" value is a Quaternion"""
		if self.node is None or self.data is None:
			return

		self.node.resetOrientation()
		self.node.setOrientation(value)
		self.node._updateBounds()
		self.oldOgrePosition = self.node.getPosition()		
		self.inform()
	def _delogreRotation(self): pass

	def getogrePosition(self):
		if self.node is None or self.data is None:
			return

		return self.node.getPosition()
	   
	def setogrePosition(self, value):
		if self.node is None or self.data is None:
			return

		if self.data and self.data.scale:
			self.node.setScale(self.data.scale)
		self.oldOgrePosition = self.node.getPosition()
		self.node.setPosition(value)
		self._x, self._y, self._z = value.x, value.y, value.z
		self.calcheight()
		self.inform()
	def _delogrePosition(self): pass
	
	def calcheight(self):
		if self._beginUpdate > 0 : 
			self._height = 0.0
			return 		
		if self.node is None or self.data is None:
			self._height = 0.0
			return

		if self.ogreWindow:
			p = self.node._getDerivedPosition()
			x = p.x
			y = p.y
			z = p.z
			self._terrainHeight = self.ogreWindow.getTerrainHeight(ogre.Vector3(x, y, z))
			if self._terrainHeight is None:
				self._terrainHeight = 0
				self._height = 0
				#debug messages
				msg = "Can not calc terrainHeight at pos "
				if self.node:
					msg += self.vector(" ") 
				if self.ogreWindow:
					if self.ogreWindow.terrain:
						msg += " on terrain %s" % self.ogreWindow.terrain.filename
				log().info(msg)
			else:
				self._height = y - self._terrainHeight
	def maxHeightOfVertices(self, vertices=["nearMiddle"]):
		if self.node is None or self.data is None:
			return 0.0

		h = []
		self.ogreWindow.boundBox.dockTo(self)
		for v in vertices:
			h.append(self.ogreWindow.boundBox.dots[v].heightFromGround)
		h.sort(reverse=True)
		return h[0]

	def getheight(self):
		self.calcheight() 
		return self._height
	   
	def setheight(self, value):
		x, y, z = self.getposition()
		self.calcheight()
		self.position = x, self._terrainHeight + value, z
	def _delheight(self): del self._height
	
	def getdetails(self):
		if self.data.name in self.ogreWindow.knownObjects.keys():
			return self.ogreWindow.knownObjects[self.data.name]
		else:
			log().error("doesn't exist details of %s" % self.data.name)
		#posible exception
	def _deldetails(self): pass
		
	def _getdeleted(self):
		return self._deleted
		   
	def _setdeleted(self, value):
		self._deleted = value
		if self.data:
			self.data.deleted = value
		if value: 
			self.oldOgrePosition = self.node.getPosition()
			self.inform()
	def _deldeleted(self): del self._deleted
	
	def _getautoRemoveFromScene(self):
		return self._autoRemoveFromScene
			
	def _setautoRemoveFromScene(self, value):
		self._autoRemoveFromScene = value
			
	def _delautoRemoveFromScene(self):
		del self._autoRemoveFromScene
	
	def _getx(self):
		return self._x
			
	def _setx(self, value):
		self._x = value
		self.setposition((self._x, self._y, self._z))
		
	def _delx(self):
		del self._x
	def _gety(self):
		return self._y
			
	def _sety(self, value):
		self._y = value
		self.setposition((self._x, self._y, self._z))
			
	def _dely(self):
		del self._y
	
	def _getz(self):
		return self._z
			
	def _setz(self, value):
		self._z = value
		self.setposition((self._x, self._y, self._z))
			
	def _delz(self):
		del self._z
	
	def _getrz(self):
		return self._rotationZ
			
	def _setrz(self, value):
		self._rotationZ = value
		self.setrotation((self._rotationX, self._rotationY, self._rotationZ))
	def _delrz(self):
		del self._rotationZ
	
	def _getry(self):
		return self._rotationY
			
	def _setry(self, value):
		self._rotationY = value
		self.setrotation((self._rotationX, self._rotationY, self._rotationZ))
		
	def _delry(self):
		del self._rotationY
	
	def _getrx(self):
		return self._rotationX
			
	def _setrx(self, value):
		self._rotationX = value
		self.setrotation((self._rotationX, self._rotationY, self._rotationZ))
			
	def _delrx(self):
		del self._rotationX

	rx = property(_getrx, _setrx, _delrx,
					doc="")

	ry = property(_getry, _setry, _delry,
					doc="")

	rz = property(_getrz, _setrz, _delrz,
					doc="")

	
	x = property(_getx, _setx, _delx,
					doc="")

	y = property(_gety, _sety, _dely,
					doc="")
	z = property(_getz, _setz, _delz,
					doc="")

	


	autoRemoveFromScene = property(_getautoRemoveFromScene, _setautoRemoveFromScene, _delautoRemoveFromScene,
					doc="an entry object that free ogre resources when is no longer needed")


	
	deleted = property(_getdeleted, _setdeleted, _deldeleted,
					 doc="""Inform on delete this object""")
	  
   
	details = property(getdetails, None, _deldetails,
					 doc="""pointer to ogreWindow.KnownObjects dictionary""")
   
	heightFromGround = property(getheight, setheight, _delheight,
				 doc="Height of (0,0,0) object coordenates from terrain ground")
	position = property(getposition, setposition, _delposition,
				 doc=""" easy to use a tuple x, y, z
						 with RoR coordenates """)

	rotation = property(getrotation, setrotation, _delrotation,
				 doc=""" tuple rx, ry, rz 
						 with RoR rotation angles
						 that is, .terrn coords""") 


	def beginUpdate(self):
		self._beginUpdate += 1
	def endUpdate(self):
		self._beginUpdate -= 1
		if self._beginUpdate < 0 : self._beginUpdate = 0
	def copyDetailsTo(self, target):
		target.heightFromGround = self.heightFromGround
		target.position = self.position
		target.ogreRotation = self.ogreRotation
		target.OnSelecting = [x for x in self._OnSelecting]
		target.OnDeselecting = [x for x in self._OnDeselecting]
		target.OnPositionChanging = [x for x in self._OnPositionChanging]
		if self.data and target.data:
			target.data.spline = self.data.spline
			target.data.comments = [x for x in self.data.comments]
	def changeParentTo(self, parent=None):
		"""Change the parent of the entry
		   and the object will stay in the same 
		   position of the map
		""" 
		if parent is None:
			parent = self.ogreWindow.sceneManager.getRootSceneNode()
		else:
			newpos = self.node._getDerivedPosition() - parent._getDerivedPosition() 
			self.node.setPosition(newpos)
		actualparent = self.node.getParentSceneNode()
		if actualparent is not None:
			if actualparent == parent : return
			actualparent.removeChild(self.node)
 	
		parent.addChild(self.node)

class selectionClass(object):
	""" Manage OgreWindow selected Object """
	def __del__(self):
		self._entry = None
		self.entries = []
		if hasattr(self._ogreWindow, 'sceneManager'): self._ogreWindow.sceneManager.destroySceneNode("multiselectNode")
		del self.coords
		del self.axis
		
	def __init__(self, ogreWindow):
		self._ogreWindow = ogreWindow
		self._entry = None
		self._coords = positionClass()

		""" used when we need multiselection option
		f.e.: RoRTruckOgrewindow"""
		self.entries = [] #holds selected entries
		self._mouseOffset = ogre.Vector3(0, 0, 0)
		self.axis = self._ogreWindow.axis
		self.multiselectNode = ogreWindow.smNewNode("multiselectNode")
		 
	def _getentry(self):
		if self._entry is None:
			self._mouseOffset.x = 0
			self._mouseOffset.y = 0
			self._mouseOffset.z = 0
			
		return self._entry
	def add(self, entry):
		""" add an entry to multiselection 
		It changes the parentSceneNode too"""
		if not(entry in self.entries):
			if entry.data.name in FIXEDENTRIES: return
			else:
				self.entries.append(entry)
				log().debug('adding to selection ' + entry.data.name)
				entry.canBeSelected = False
#				self.multiselectNode.showBoundingBox(True)
		if len(self.entries) == 1 : 
			self.multiselectNode.setPosition(entry.node._getDerivedPosition())
			self._ogreWindow.axis.attachTo(self.multiselectNode)
			self._entry.OnPositionChanging.append(self.translateSelection)
		entry.changeParentTo(self.multiselectNode)
		entry.node.showBoundingBox(True)
		
#		self.multiselectNode._updateBounds()
#		self.multiselectNode.showBoundingBox(True)

	def translateSelection(self, entry):
		""" on moving visual sphere, we must move multiselect node"""
		offset = entry.node.getPosition() - entry.oldOgrePosition
		self.multiselectNode.setPosition(entry.node.getPosition())# since multiselect node is misplaced from selectionBox, first drag will make ajump
		self.multiselectNode.setOrientation(entry.ogreRotation)
		

	def _unselectItem(self, entry):
		entry.beginUpdate()
		pos = entry.node._getDerivedPosition()
		rot = entry.node._getDerivedOrientation()
		entry.node.showBoundingBox(False)
		entry.changeParentTo(None)
		entry.ogrePosition = pos
		entry.ogreRotation = rot
		entry.canBeSelected = True
		entry.endUpdate()
		
	def remove(self, entry=None):
		""" remove the entry from selected group or removeAll if entry is None"""
		log().debug('removing selection')
		if self._entry:
			try:
				idx = self._entry.OnPositionChanging.index(self.translateSelection)
				del self._entry.OnPositionChanging[idx]
			except ValueError:
				pass
			
		removeAll = entry == None
		if not removeAll:
			try:
				idx = self.entries.index(entry)
			except ValueError:
				return # not found
			self._unselectItem(self.entries[idx])
			del self.entries[idx]
		else:
			for e in self.entries:
				self._unselectItem(e)
			self.entries = []
	def copy(self):
		pass
				
	def paste(self):
		pos = self.coords.asVector3
		pos.y += 0.2
		tmp = self.entries[:]
		self.remove()
		for e in tmp:
			if e.data.fileWithExt != '.odef':  #FIXED ENTRIES: RORCAMERA...
				new = self._ogreWindow.addGeneralObject(e.data.fileWithExt, (e.position), (e.rotation))
				self.add(new)

		
	def _setentry(self, value):
		if len(self.entries) > 0 : self.remove()
		if self._entry and self._entry.node:
			self._entry.node.showBoundingBox(False)
			self._entry.deselect()
		self._entry = value
		self.axis.entryShow = []
		if value:
			if self._entry != self.axis.arrow:
				self.axis.arrowScaleFactor = self._entry.entity.getBoundingRadius() / 100		
			if self._entry.allowTranslation:
				self.axis.entryShow = ['translation']
			else: self.axis.entryShow = []	
			if value.node:
				self._entry.node.showBoundingBox(True)
				self._coords.asVector3 = self._entry.node._getDerivedPosition()
				if self._entry.allowRotation:
					self.axis.entryShow.append('rotation')
			self.axis.attachTo(self._entry.node)
			self._entry.select()
		else:
			self.axis.selectTerrain(self.coords.asTuple)
				
	def _delentry(self):
		del self._entry
		
		
	def _getCoords(self):
		return self._coords
	   
	def _setCoords(self, value):
		self._coords = value
	
	def _delCoords(self):
		del self._coords
	
	def _getmouseOffset(self):
		return self._mouseOffset
		   
	def _setmouseOffset(self, value):
		self._mouseOffset = value
	
	def _delmouseOffset(self): del self._mouseOffset
	
	def _getentity(self):
		return self._entity
			
	def _setentity(self, value):
		self._entity = value
	def _delentity(self): del self._entity
	
	entity = property(_getentity, _setentity, _delentity,
						doc=""" used by replaceEntity """)
	   
	mouseOffset = property(_getmouseOffset, _setmouseOffset, _delmouseOffset,
					 doc=""" ogre.Vector3
						   When selecting with mouse it holds
						   offset between mouse Position and (0,0,0) 
						   coordenate of the selected Object.
						   
						   Useful when dragging with FREEDOM mode""")
	coords = property(_getCoords, _setCoords, _delCoords,
				 doc=" x, y, z")
	
	entry = property(_getentry, _setentry, _delentry,
				 doc="""entry selected
						 when non multiselect""")   
   

class odefEntryClass(simpleEntryClass):
	def __init__(self, ogreWindow):
		simpleEntryClass.__init__(self, ogreWindow)
		self.box = None
		self.name = ''
		self.details = {}
		self.oldOgrePosition = None
		self._rotationX = None
		self._rotationY = None
		self._rotationZ = None
	def __str__(self):
		msg = self.name
		if not self.box is None:
			msg += ' box: ' + self.box.__str__()
		elif self.node:
			msg += "pos %.3f,%.3f, %.3f" % self.getposition()  
		return msg
	def getposition(self):
		p = self.node.getPosition()
		return p.x, p.y, p.z

	def setposition(self, value):
		"""first set up node position, if it fail, nothing happens
		#entity must exist"""

		if self.node is None :
			log().error("Entry.node is not Assigned !!")
		self.oldOgrePosition = self.node.getPosition()
		self.node.setPosition(value)		
		
	def getrotation(self):
		rot = self.node._getDerivedOrientation()
		rot.normalise()
		self._rotationZ = degrees(rot.getYaw(False).valueRadians()) 
		self._rotationY = degrees(rot.getRoll(False).valueRadians())
		self._rotationX = degrees(rot.getPitch(False).valueRadians())

		self._rotationX = round(self._rotationX, 2)
		self._rotationY = round(self._rotationY, 2)
		self._rotationZ = round(self._rotationZ, 2)

		return self._rotationX, self._rotationY, self._rotationZ
	
	def setrotation(self, value):
		""" value is in file coordenates """
		self._rotationX, self._rotationY, self._rotationZ = value
#		self.node.setScale(1,1,1) really needed ?=?
		self.node.resetOrientation()
		
		rot = ogre.Quaternion(ogre.Degree(self._rotationX), ogre.Vector3(1, 0, 0)) * \
			ogre.Quaternion(ogre.Degree(self._rotationY), ogre.Vector3(0, 1, 0)) * \
			ogre.Quaternion(ogre.Degree(self._rotationZ), ogre.Vector3(0, 0, 1))
					

		self.node.rotate(rot) #RoR source code

	def getogreRotation(self):
		return self.node._getDerivedOrientation()
	   
	def setogreRotation(self, value):
		""" value is a Quaternion"""
		self.node.resetOrientation()
		self.node.setOrientation(value)
		self.node._updateBounds()

	ogreRotation = property(getogreRotation, setogreRotation,
				 doc="Quaternion in ogre angles")

   
	position = property(getposition, setposition,
				 doc=""" easy to use a tuple x, y, z
						 with RoR coordenates """)

	rotation = property(getrotation, setrotation,
				 doc=""" tuple rx, ry, rz 
						 with RoR rotation angles
						 that is, .terrn coords""") 



	
class BoundBoxClass(object):
	""" 
	Concept: a MainNode that has 8 (or more) child nodes, each child node is a vertice of Ogre.AABB that
				define the entity size. If we want to know the position and rotation of the vertice nearLeftTop of an 
				entity, we dock the mainNode to the terrainEntryClass and then we can retrieve 
				DERIVED position and rotation of each vertice. 
	
	Implementation: we use terrainEntryClass for all vertices and mainNode,
					so we can show a coloured ball entity for debugging purpose
	"""
 
	def __init__(self, ogrewindow, color=CLCREAM):
		self.color = color
		self._ogrewindow = ogrewindow
		self.mainEntry = ogrewindow.createDotAt(0, 0, 0, CLTRANSGREEN, 'boundBox MainNode')
		self.mainEntry.autoRemoveFromScene = False
		self.dots = None #dictionary aabb as knownObjects, but each element is an entry
		self.child = self.mainEntry.node.createChildSceneNode(str(randomID()))
		self.mainEntry.visible = rorSettings().rorDebug
	def __del__(self):
		#mainEntry has child nodes... we wait Ogre delete it !
		pass
	
	def realPos(self, vector3):
		""" receives a vector3 or tuple with coordenates in local axes of the 
		EntryClass it is docked to.
		
			return derivedPosition vector3.
		"""
		if isinstance(vector3, TupleType):
			v = ogre.Vector3(vector3[0], vector3[1], vector3[2])
		else:
			v = vector3
		self.child.setPosition(v)
		return self.child._getDerivedPosition()
		
	def _createDotsfromAABB(self, aabb):
		self.dots = {}
		for corner in aabb.keys():
			e = self._ogrewindow.createDotAt(0, 0, 0, self.color, corner, self.mainEntry.node)
			e.autoRemoveFromScene = False
			e.visible = rorSettings().rorDebug
			self.dots[corner] = e
	
	def _updateDotsPositions(self, entry, aabb=None):
		if aabb is None:
			aabb = entry.details["aabb"]
		if self.dots is None : 
				self._createDotsfromAABB(aabb)
		for pos in aabb.keys():
			self.dots[pos].node.setPosition(aabb[pos])

	def dockToFilename(self, strFilename='road', atPosition=(0, 0, 0)):
		for e in self._ogrewindow.entries.keys():
			if not self._ogrewindow.entries[e].data is None:
				if self._ogrewindow.entries[e].data.name == strFilename:
					self._updateDotsPositions(self._ogrewindow.entries[e])
					self.mainEntry.position = atPosition
					return True
		return False
					
		
	def dockTo(self, entry, posAtZero=False, atPos=None, aabb=None):
		"""
		Main function to dock this object to the desired EntryClass
		After that, you can use any method.
		"""
		if aabb is not None:
			self._updateDotsPositions(entry, aabb)
		elif entry.details:
			self._updateDotsPositions(entry)
		
		if posAtZero:
			self.mainEntry.position = 0, 0, 0	
		else:
			if atPos is not None:
				self.mainEntry.position = atPos
			else:
				self.mainEntry.position = entry.position
		self.mainEntry.node.resetOrientation()
		self.mainEntry.ogreRotation = entry.ogreRotation
	def Min(self, v1, v2):
		if v1.x - v2.x <= 0.00000001 and v1.y - v2.y <= 0.00000001 and v1.z - v2.z <= 0.00000001: return v1 
		else: return v2
	def Max(self, v1, v2):
		if v1.x - v2.x <= 0.00000001 and v1.y - v2.y <= 0.00000001 and v1.z - v2.z <= 0.00000001: return v2 
		else: return v1

	def getMinimum(self):
		x = self.dots["nearLeftTop"].node._getDerivedPosition()
		for v in self.dots.keys():
			x = self.Min(x, self.dots[v].node._getDerivedPosition())
		return x

	def getMaximum(self):
		y = self.dots["nearLeftTop"].node._getDerivedPosition()
		for v in self.dots.keys():
			y = self.Max(y, self.dots[v].node._getDerivedPosition())
		return y
	
	def terrainWaterHeight(self, corners=["nearMiddle", "farMiddle"]):
		""" Calc the max height of corners keeping in mind
		terrain level and water level (if terrain support it)
		
		returnn float"""
		heights = []
		w = self._ogrewindow.terrain.WaterHeight
		if w is None: w = 0.0
		for corner in corners:
			h = self._ogrewindow.getTerrainHeight(self.dots[corner].node._getDerivedPosition())
			if h is None: h = 0.0
			if h < w : heights.append(w)
			else : heights.append(h)
		heights.sort(reverse=True)
		return heights[0]

	def intersect(self, vector3OrEntry):
		""" return True if the vector3 or EntryClass (the node of) passed
		is in the BoundingBox
		"""
		if isinstance(vector3OrEntry, simpleEntryClass):
			vector = vector3OrEntry.node._getDerivedPosition()
		elif isinstance(vector3OrEntry, ogre.Vector3):
			vector = vector3OrEntry
		else:
			raise showedError("BoundBox.intersect need a vector3 or Entry !!")
			
		mMinimum = self.getMinimum()
		mMaximum = self.getMaximum()
		return (vector.x >= mMinimum.x  and  vector.x <= mMaximum.x  and 
				vector.y >= mMinimum.y  and  vector.y <= mMaximum.y  and 
				vector.z >= mMinimum.z  and  vector.z <= mMaximum.z)


	def debug(self, msg=""):
		for corner in self.dots.keys():
			p = self.dots[corner].node._getDerivedPosition()
			log().debug("%20s %12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %12.6f" % (msg, p.x, p.y, p.z, rx, ry, rz))

	def maxHeightOfVertices(self, vertices=["nearMiddle"]):
		""" just return the max Y coordenate of the vertices passed
		
		Don't keep in mind terrain nor water level
		
		return float """
		h = []
		for v in vertices:
			h.append(self.dots[v].node._getDerivedPosition().y)
		h.sort(reverse=True)
		return h[0]

	def maxHeightOfGround(self, vertices=["nearMiddle"]):
		"""just return the max height FROM ground of all vertices
		
		return float """
		h = []
		for v in vertices:
			h.append(self.dots[v].heightFromGround)
		h.sort(reverse=True)
		return h[0]			 
