'''
Created on 07/04/2009

@author: Lepes
'''
import wx, os, os.path, copy
import cPickle
import errno
import ogre.renderer.OGRE as ogre 
from ror.rorcommon import *
from RoRVirtualKeys import *
from ror.lputils import *
from roreditor.RoRConstants import *
from ror.logger import log

#===============================================================================
# Rotation and selection pivots uses ARROW_SCALE_xxxFACTOR to adapt the size of
# the pivot to the selected object:
# min factor now is using the axis size of a road object
# max factor now is using the axis size of an runway object 
#===============================================================================
ARROW_SCALE_MINFACTOR = 0.01
ARROW_SCALE_MAXFACTOR = 1.3


class AxisTranslationArrow:
	"""
	Represents a manipulation arrow to move selection along 1 axis.
	
	:attribute string           _material_instance_name:
	:attribute ogre.MaterialPtr _material_instance:
	:attribute string           _ogre_scenenode_name:
	:attribute ogre.SceneNode   _ogre_scenenode:
	
	:author: Petr Ohlidal a.k.a. 'only_a_ptr', 01/2016
	"""
	
	def __init__(self, common_scenenode, axis_name, arrow_entity_name, ogre_scenemanager):
		self._axis_name = axis_name
		
		# Create our own material instances (to enable individual transparency adjustment)
		if axis_name == "X":
			common_mat_name = "mysimple/transred"
		elif axis_name == "Y":
			common_mat_name = "mysimple/transgreen"
		elif axis_name == "Z":
			common_mat_name = "mysimple/transblue"
		
		common_mat = ogre.MaterialManager.getSingleton().getByName(common_mat_name)
		self._material_instance_name = "rortoolkit/editor_arrow_" + axis_name
		self._material_instance = common_mat.clone(self._material_instance_name)
		common_sel_mat = ogre.MaterialManager.getSingleton().getByName(common_mat_name + "sel")
		self._material_highlight_name = self._material_instance_name + "sel"
		self._material_highlight_instance = common_sel_mat.clone(self._material_highlight_name)
		
		# Mk scene node
		self._ogre_scenenode_name = "movearrowsnode" + axis_name + randomID()
		self._ogre_scenenode = common_scenenode.createChildSceneNode(self._ogre_scenenode_name)
		
		# Mk entity
		self._ogre_entity = ogre_scenemanager.createEntity(arrow_entity_name, "axis.mesh")
		self._ogre_entity.setMaterialName(self._material_instance_name)
			
		# Attach and rotate
		# Cloned code by Lepes
		self._ogre_scenenode.attachObject(self._ogre_entity)
		if axis_name == "X":
			self._ogre_scenenode.rotate(ogre.Vector3(0, 1, 0), ogre.Degree(-90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		elif axis_name == "Y":
			self._ogre_scenenode.rotate(ogre.Vector3(0, 1, 0), ogre.Degree(-180), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		elif axis_name == "Z":
			self._ogre_scenenode.rotate(ogre.Vector3(0, 1, 0), ogre.Degree(-90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			self._ogre_scenenode.rotate(ogre.Vector3(0, 0, 1), ogre.Degree(90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)	


class AxisClass(object):
	'''
	Create:
	- 1 node translateNode with 3 3D Axis 
	- 1 node rotateNode with 3 3D arrows to rotate the object
	- 1 node terrainNode with the cylinder
	
	It will use smNewNode, smNewEntity methods and "entries" properties from the ogrewindow
	'''
	#TODO: pointer3d not finished

	def __init__(self, ogrewindow, whatVisible):
		"""
		:param ogrewindow: OGRE window who manage this axis.
		:param list[string] whatVisible: list of arrows you want to be visible 
		                                 ['translation', 'rotation', 'terrain']
		"""
		self._ogrewindow = ogrewindow
		self.translateNode = None
		self.rotateNode = None
		self.terrainNode = None
		self.pointer3d = None
		self._rotateNodeOffset = ogre.Vector3(0, 0, 0) #(1, 1, 1)		
		self._scale = 0, 0, 0
		self._arrow = None
		self._arrowScaleFactor = 0.10
		self.normalScale = 1, 1, 1
		
		
		#what the actual entry is allowed to show
		self.entryShow = []
		self._selectedArrow = None
		self.arrowNames = ['movearrowsX-' + randomID(), 'movearrowsY-' + randomID(), 'movearrowsZ-' + randomID(), 'rotatearrowsX-' + randomID(), 'rotatearrowsY-' + randomID() , 'rotatearrowsZ-' + randomID()]
		# what is allowed to be visible
		self._allowedToShow = whatVisible[:] #new copy
		self._createArrows()
		
	
	def __del__(self):
		self.rotateNode = None
		self.translateNode = None
		self.terrainNode = None
		self.pointer3d = None
		
		
	def _getrotateNodeOffset(self):
		return self._rotateNodeOffset
		
			
	def _setrotateNodeOffset(self, value):
		self._rotateNodeOffset = value
		
	
	def _getscale(self):
		return self._scale
		
			
	def _setscale(self, value):
		self._scale = value
		if not self.terrainNode is None:
			self.terrainNode.setScale(value)
		if not self.translateNode is None:
			self.translateNode.setScale(value)
		if not self.rotateNode is None:
			self.rotateNode.setScale(value)
		if not self.pointer3d is None:
			self.pointer3d.setScale(value)
		
	
	def _getarrow(self):
		return self._arrow
		
			
	def _setarrow(self, value):
		if value != self._arrow:
			if self._arrow is not None:
				self._deselectarrow(self._arrow)
			self._arrow = value
			if self._arrow is not None:
				self._selectarrow(self._arrow)
	
	
	def _getarrowScaleFactor(self):
		return self._arrowScaleFactor
		
			
	def _setarrowScaleFactor(self, value):
		if value > ARROW_SCALE_MAXFACTOR:
			value = ARROW_SCALE_MAXFACTOR

		
		if value < ARROW_SCALE_MINFACTOR:
			value = ARROW_SCALE_MINFACTOR

		self._arrowScaleFactor = value
		self.normalScale = self._arrowScaleFactor, self._arrowScaleFactor, self._arrowScaleFactor
		self.rotateNodeOffset = ogre.Vector3(self._arrowScaleFactor * 20 , self._arrowScaleFactor * 10, self._arrowScaleFactor * 30)
	
		
	arrowScaleFactor = property(_getarrowScaleFactor, _setarrowScaleFactor,
						doc=""" It is a dynamic scale factor to 
								adapt pivot size to the selected object
								between a minimum and maximum values:
								ARROW_SCALE_MINFACTOR = 0.1
								ARROW_SCALE_MAXFACTOR = 0.5
								""")
	
	
	arrow = property(_getarrow, _setarrow,
						doc="""holds the last selection arrow ENTITY or None""")
	
		
	scale = property(_getscale, _setscale,
						doc="""Tuple Scale of all nodes""")
						
						
	rotateNodeOffset = property(_getrotateNodeOffset, _setrotateNodeOffset,
						doc="""Offset to misplace rotate arrows from translation axis""")
	
						
	def setArrowScaleFactor(self, factor, node):
		self.arrowScaleFactor = factor
		self.attachTo(node)
		
		
	def _createArrows(self):
		if not self.translateNode is None:
			log().debug("SelectionAxis._createArrows: Axes are already created !!")
			showedError("Axes already created")
		# main node is always required
		n = self._ogrewindow.smNewNode("movearrowsnode" + randomID()) 
		n.setScale(0, 0, 0)
		n.setPosition(0, 0, 0)
		self.translateNode = n
		
		#translation nodes
		if 'translation' in self._allowedToShow:
			scene_mgr = self._ogrewindow.getOgreSceneManager()
			self._axis_arrows = {}
			self._axis_arrows["X"] = AxisTranslationArrow(n, "X", self.arrowNames[0], scene_mgr)
			self._axis_arrows["Y"] = AxisTranslationArrow(n, "Y", self.arrowNames[1], scene_mgr)
			self._axis_arrows["Z"] = AxisTranslationArrow(n, "Z", self.arrowNames[2], scene_mgr)
			
		#rotation nodes
		if 'rotation' in self._allowedToShow:
			offset = 7
			
			nr = self._ogrewindow.smNewNode("rotatearrowsnode" + randomID()) 
			nr.setScale(0, 0, 0)
			nrx = nr.createChildSceneNode("rotatearrowsnodeX" + randomID())
			erx = self._ogrewindow.smNewEntity(self.arrowNames[3], "roundarrow.mesh", "mysimple/transred") 
			nrx.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(-90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			nrx.setScale(1, 1, 1)
			nrx.setPosition(0, 0, offset)
			nrx.attachObject(erx)
	
			nry = nr.createChildSceneNode("rotatearrowsnodeY" + randomID())
			ery = self._ogrewindow.smNewEntity(self.arrowNames[4], "roundarrow.mesh", "mysimple/transblue") 
			nry.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(180).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			nry.rotate(ogre.Vector3(0, 1, 1), ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			nry.setInheritOrientation(True)
			nry.setScale(1, 1, 1)
			nry.attachObject(ery)
			nry.setPosition(0, 0 , 0)
		
		
			nrz = nr.createChildSceneNode("rotatearrowsnodeZ" + randomID())
			erz = self._ogrewindow.smNewEntity(self.arrowNames[5], "roundarrow.mesh", "mysimple/transgreen") 

			nrz.setScale(1, 1, 1)
			nrz.attachObject(erz)
			nrz.setPosition(0, 0, 0)
			self.rotateNode = nr
			self.rotateNode.setPosition(0, 0, 0)
		
		# terrain selection node
		if 'terrain' in self._allowedToShow:
			nt = self._ogrewindow.smNewNode("terrainselectnode" + randomID()) 
			et = self._ogrewindow.smNewEntity("circlepointer-" + randomID(), "cylinder.mesh", "mysimple/terrainselect") 
			nt.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			nt.attachObject(et)
			self.terrainNode = nt
		
		if 'pointer3d' in self._allowedToShow:
#												strMeshName, strMaterialName = None, bAssignEvent = False, bAddToEntries = False, bCreateData = False, parentNode=None):
			p3d = self._ogrewindow.newEntryEx("torus.mesh", "mysimple/terrainselect", False, True)
			self.pointer3d = p3d.node			
			self.pointer3d.setScale(0.05, 0.05, 0.05)
	
		self.scale = 0, 0, 0
		

	def attachTo(self, node):
		''' reattach axis and rotation arrows to the node'''
		self.scale = 0, 0, 0
		if node:
			pos = node._getDerivedPosition() 
			ori = node._getDerivedOrientation()
			if 'translation' in self.entryShow and 'translation' in self._allowedToShow:
				self.translateNode.setPosition(pos)
				self.translateNode.setScale(self.normalScale)
			if 'rotation' in self.entryShow and 'rotation' in self._allowedToShow:
				self.rotateNode.setPosition(pos + self._rotateNodeOffset)
				self.rotateNode.setOrientation(ori)
				self.rotateNode.setScale(self.normalScale)
				

	def selectTerrain(self, positionTuple):
		if 'terrain' in self._allowedToShow:
			self.attachTo(None)
			if positionTuple[0] is not None and positionTuple[1] is not None and positionTuple[2] is not None:
				self.terrainNode.setPosition(positionTuple[0], positionTuple[1] + 0.5, positionTuple[2])
				self.terrainNode.setScale(0.2, 0.2, 0.2)
	
		if 'pointer3d' in self._allowedToShow:
			self.pointer3d.setPosition(positionTuple)
			s = 0.05
			self.pointer3d.setScale(s, s, s)
			

	def _selectarrow(self, arrow):
		"""
		:param ogre.Entity arrow: Any handle (axis/rotation/terrain)
		"""
		if arrow is not None:
			mat_name = arrow.getSubEntity(0).getMaterialName()
			if mat_name[ -3:] != "sel":
				arrow.setMaterialName(mat_name + "sel")
				
			
	def _deselectarrow(self, arrow):
		"""
		:param ogre.Entity arrow: Any handle (axis/rotation/terrain)
		"""
		if arrow is not None:
			if self.arrow.getSubEntity(0).getMaterialName()[ -3:] == "sel":
				self.arrow.setMaterialName(self.arrow.getSubEntity(0).getMaterialName()[:-3])
		
