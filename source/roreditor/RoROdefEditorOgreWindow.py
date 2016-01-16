#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, math
import ogre.renderer.OGRE as ogre
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.SimpleTruckRepresentation import *
from ror.odefparser import *
from ror.rorcommon import *
from ror.settingsManager import rorSettings

from RoRConstants import *
from RoRVirtualKeys import *
from SelectionAxis import *
from RoRTerrainSelection import *
from ror.lputils import *

NONE = 0
DOT = 1
BOX = 2

#------------------------------------------------------------------------------
# TODO: list:
# Ground points
# docking surface
# attach points
# event Box
# collision Box
#------------------------------------------------------------------------------

mat = {
	'hook'		: "TruckEditor/NodeNormal",
	'ground'	: "TruckEditor/NodeExhaust"
	}

class TreeDropTarget(wx.PyDropTarget):
	def __init__(self, window):
		wx.PyDropTarget.__init__(self)
		self.do = wx.FileDataObject()
		self.SetDataObject(self.do)

	def OnEnter(self, x, y, d):
		print "OnEnter: %d, %d, %d\n" % (x, y, d)
		return wx.DragCopy

	def OnDragOver(self, x, y, d):
		print "OnDragOver: %d, %d, %d\n" % (x, y, d)
		return wx.DragCopy

	def OnLeave(self):
		print "OnLeave\n"

	def OnDrop(self, x, y):
		print "OnDrop: %d %d\n" % (x, y)
		return True

	def OnData(self, x, y, d):
		print "OnData: %d, %d, %d\n" % (x, y, d)
		self.GetData()
		print "%s\n" % self.do.GetFilenames()
		return d


NEWMATNAME = "mysimple/odefeditor/objplaceholder"

class ODefEditorOgreWindow(wxOgreWindow):
	def __init__(self, parent, ID, size=wx.Size(200, 200), **kwargs):
		self.rordir = rorSettings().rorFolder
		self.parent = parent
		wxOgreWindow.__init__(self, parent, ID, "odefEditor", size=size, **kwargs)
		self.initVariables()

	def getautoTracking(self):
		return self._autoTracking

	def setautoTracking(self, value):
		self._autoTracking = value
		self.camera.setAutoTracking(value, self.objnode)


	def _getmode(self):
		return self._mode

	def _setmode(self, value):
		if value in [DOT, BOX, NONE]:
			self._mode = value



	mode = property(_getmode, _setmode,
					 doc=""" DOT, BOX, NONE
					 be aware NONE is a constant""")
	autoTracking = property(getautoTracking, setautoTracking,
				 doc=""" center selected object in screen and
						  WASD keys rotate around the selected object
						  instead of freedom walking.
						  It's a toggle option. """)

	def initVariables(self):
		self._autoTracking = False
		self.objnode = None
		self.objentity = None
		self.boundBox = None
		self.bbresize = None

		self.selected = None
		self.camalpha = 0
		self.radius = 40
		self.dragging = False
		self.boxes = []
		self.entries = {}
		self.objmat = None
		self.randcolors = [0, 0.2, 0.4]
		self.mainOdef = None
		self._autoTracking = False
		self._mode = DOT
		self.aabb = {}
		self.axis = AxisClass(self, ['translation', 'rotation', 'pointer3d']) #before selectionClass
		self.selected = selectionClass(self)
		self.boundBox = BoundBoxClass(self)
		self.bbresize = BoundBoxClass(self, CLRED)

	def newEntry(self, bAssignEvent=False, bAutouuid=False):
		""" Create an odefEntryClass
			bAssignEvent -> Assign ogreWindow property
			bAutouuid -> auto generate uuid to this entry"""
		n = odefEntryClass(self)
#		if bAssignEvent:
#			n.OnPositionChanging = self.entryChanged
		if bAutouuid:
			n.uuid = randomID()
		return n

	def newEntryEx(self, strMeshName, strMaterialName=None, bAssignEvent=False, bAddToEntries=False, parentNode=None):
		""" strMeshName, strMaterialName = None, bAssignEvent = False, bAddToEntries = False, parentNode=None
		 Create a New Entry, that is:
				   - node
				   - entity
				   - attach entity to node
				   - Assign material and mesh to the entity
				   - add to self.entries """

		n = self.newEntry(bAssignEvent, True)
		if parentNode is None:
			n.node = self.smNewNode(str(n.uuid) + "node")
		else:
			n.node = parentNode.createChildSceneNode(str(n.uuid) + "node")

		n.entity = self.smNewEntity(str(n.uuid) + "Entity", strMeshName)
		if strMaterialName:
			n.entity.setMaterialName(strMaterialName)
		n.node.attachObject(n.entity)
		if bAddToEntries:
			self.entries[n.uuid] = n
		return n

	def smNewNode(self, strName,
					doc=""" Scene Manager New Node:
					Create a new SceneNode with given Name """):
		n = self.sceneManager.getRootSceneNode().createChildSceneNode(strName)
		return n

	def smNewEntity(self, strName, strMesh, strMaterialName=None,
					doc=""" Scene Manager New Entity:
					Create a new entity with:
					- Entity Name
					- Mesh Name
					- Material Name (maybe omitted)"""):
		e = self.sceneManager.createEntity(strName, strMesh)
		if strMaterialName:
			e.setMaterialName(strMaterialName)
		return e

	def createDotAt(self, x, y, z, color=CLBLUE, sufix='', parentNode=None):
		p = self.newEntryEx("ellipsoid.mesh", color, False, True, parentNode)
		p.node.setPosition(x, y, z)
		p.name = sufix
		return p

	def createDot(self, entry, corner="", color=CLBLUE, sufix=''):
		""" create a dot on the corner of entry"""
		p = self.newEntryEx("ellipsoid.mesh", color, False, True, entry.node)
		p.data.name = "point_%s" % str(randomID())
		p.name = sufix
		if not entry.details["aabb"].has_key(corner):
			log().error("%s is not a valid corner, please see KnownObjects aabb" % corner)


		pos = entry.details["aabb"][corner]
		p.node.setPosition(pos.x, pos.y, pos.z)
#		p.logPosRot(p.data.name)
		return p

	def createBox(self, odefbox, addToMainObject=False):
		""" odefbox - a box of odefparser.py
			addToMainObject - true if it is a new box that must be linked to the odefClass.boxes
		"""

		matname = "mysimple/odefeditor/transred"
		if odefbox.virtual:
			matname = "mysimple/odefeditor/transgreen"
		matname = self.getNewMat(matname)
		if odefbox.isMesh:
			entry = self.newEntryEx(odefbox.meshName, matname, True, True)
			entry.position = 0, 0, 0
			entry.rotation = -90, 0, 0
			entry.canBeSelected = False
		else:
			entry = self.newEntryEx("beam.mesh", matname, True, True)
			entry.box = odefbox

			midPoint = entry.box.coord0.asVector3.midPoint(entry.box.coord1.asVector3)

			dist = entry.box.coord1.asVector3 - entry.box.coord0.asVector3
			entry.node.setScale(dist.x, dist.y, dist.z)
#			entry.node._updateBounds()
			entry.node.setPosition(midPoint) #box node on world dimension
			self.log("entry.node position node is at " , [midPoint.x, midPoint.y, midPoint.z])
			self.log(" with scale ", [dist.x, dist.y, dist.z])
			if not entry.box.rotation.isZero():
				entry.rotation = entry.box.rotation.asTuple
			self.updateDetails(entry)
		if addToMainObject:
			self.mainOdef.boxes.append(odefbox)
		return entry

	def SceneInitialisation(self):
		initResources()

		#get the scenemanager
		self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

		# create a camera
		self.camera = self.sceneManager.createCamera(str(randomID()) + 'Camera')
		self.camera.lookAt(ogre.Vector3(0, 0, 0))
		self.camera.setPosition(ogre.Vector3(0, 0, 50))
		self.camera.nearClipDistance = 1
		self.camera.setAutoAspectRatio(True)

		#set some default values
		self.sceneDetailIndex = 0
		self.filtering = ogre.TFO_BILINEAR


		# create the Viewport"
		self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0)
		self.viewport.backgroundColour = ogre.ColourValue(128, 128, 128)

		# bind mouse and keyboard
		d = 10.0 #displacement for key strokes
		self.ControlKeyDict = {wx.WXK_LEFT:ogre.Vector3(-d, 0.0, 0.0),
							wx.WXK_RIGHT:ogre.Vector3(d, 0.0, 0.0),
							wx.WXK_UP:ogre.Vector3(0.0, 0.0, -d),
							wx.WXK_DOWN:ogre.Vector3(0.0, 0.0, d),
							wx.WXK_PAGEUP:ogre.Vector3(0.0, d, 0.0),
							wx.WXK_PAGEDOWN:ogre.Vector3(0.0, -d, 0.0)}
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		#self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)
		#create objects
		self.populateScene()

	def loadFile(self, filename):
		self.filename = filename
		filenameonly, extension = os.path.splitext(filename)
		if extension.lower() in [".truck", ".load"]:
			raise showedError("what the hell using odef editor to see a truck or load ??")
			self.clear()
			uuid = randomID()
			try:
				self.objnode, self.objentity, manualobject = createTruckMesh(self.sceneManager, filename, uuid)
			except:
				raise showedError("The file %s has error and couldn't be loaded" % filename)

		elif extension.lower() in [".odef"]:
			self.clear()
			uuid = randomID()
			self.loadodef(filename, uuid)

		if self.objnode:
			self.objnode.showBoundingBox(True)
			self.objnode._updateBounds()
#			backupRot = self.objnode.getOrientation()
#			self.objnode.resetOrientation()
#			self.objnode.pitch(ogre.Degree(90))

			self.aabb = {
				 "nearLeftTop"	  	: self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_TOP),
				 "nearRightTop"	 	: self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_TOP),
				 "nearLeftBottom"   : self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_BOTTOM),
				 "nearRightBottom"  : self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_BOTTOM),
				 "farLeftTop"	   	: self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_LEFT_TOP),
				 "farRightTop"	  	: self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_RIGHT_TOP),
				 "farLeftBottom"	: self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_LEFT_BOTTOM),
				 "farRightBottom"   : self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_RIGHT_BOTTOM),
#				 "nearMiddle"	   : self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_TOP).midPoint(self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_BOTTOM)),
#				 "farMiddle"		: self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_TOP).midPoint(self.objnode._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_BOTTOM)),
				 }
			self.aabb["dimX"] = self.aabb["nearLeftTop"].distance(self.aabb["farLeftTop"])
			self.aabb["dimY"] = self.aabb["nearLeftTop"].distance(self.aabb["nearRightTop"])
			self.aabb["dimZ"] = self.aabb["nearLeftTop"].distance(self.aabb["nearLeftBottom"])
#		self.objnode.resetOrientation()
#		self.objnode.setOrientation(backupRot)

	def loadodef(self, filename, uuid):
		try:
			self.mainOdef = odefClass(filename)
		except Exception, err:
			self.mainOdef = None
			log().error("error while processing odef file %s" % filename)
			log().error(str(err))
			if rorSettings().stopOnExceptions:
				raise

			return
		# create mesh


		self.objnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid + "objnode")
		self.objentity = self.sceneManager.createEntity(uuid + 'objentity', self.mainOdef.meshName)
		self.objnode.attachObject(self.objentity)
		self.objnode.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(-90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)

		try:
			self.objOriginalMat = ogre.MaterialManager.getSingleton().getByName(self.objentity.getSubEntity(0).getMaterialName())
			if self.objmat is None:
				self.objmat = ogre.MaterialManager.getSingleton().getByName(NEWMATNAME)
			self.objOriginalMat.copyDetailsTo(self.objmat)
			# self.objmat = ogre.MaterialManager.getSingleton().getByName(NEWMATNAME)
			self.objmat.setSceneBlending(ogre.SceneBlendFactor.SBF_SOURCE_ALPHA, ogre.SceneBlendFactor.SBF_DEST_ALPHA)
			self.objentity.setMaterialName(NEWMATNAME)
			self.setMainMeshTrans(50)
		except Exception, err:
			log().error("error while creating main odef model")
			log().error(str(err))

		self.objnode.setPosition(0, 0, 0)
		self.createDotAt(0, 0, 0, CLTRANSRED, '0, 0, 0')
		self.objnode.setScale(self.mainOdef.scale)
		log().info(" main Scale " + str(self.mainOdef.scale))
		for i in range(0, len(self.mainOdef.boxes)):
			self.createBox(self.mainOdef.boxes[i])
		log().info("Loaded odef with %d boxes" % len(self.mainOdef.boxes))
			# box added to self.entries
#		self.createDOT(ogre.Vector3(0,0,0), mat['ground'])

	def getNewMat(self, basematname):
		uuid = randomID()
		matname = uuid + "mat"
		basemat = ogre.MaterialManager.getSingleton().getByName(basematname)
		mat = ogre.MaterialManager.getSingleton().create(matname, basemat.getGroup())
		basemat.copyDetailsTo(mat)
		#mat = ogre.MaterialManager.getSingleton().getByName(matname)
		for i in range(0, 2):
			self.randcolors[i] += 0.1
			if self.randcolors[i] >= 1:
				self.randcolors[i] -= 1
		mat.setDiffuse(self.randcolors[0], self.randcolors[1], self.randcolors[2], 0.8)
		mat.setSpecular(self.randcolors[0], self.randcolors[1], self.randcolors[2], 0.8)
		mat.setSelfIllumination(self.randcolors[0], self.randcolors[1], self.randcolors[2])
		mat.setAmbient(self.randcolors[0], self.randcolors[1], self.randcolors[2])
		return matname

	def setMainMeshTrans(self, alpha):
		""" set the main mesh transparent """
		alpha = float(alpha) / float(100)
		self.objmat.setSceneBlending(ogre.SceneBlendFactor.SBF_SOURCE_ALPHA, ogre.SceneBlendFactor.SBF_DEST_ALPHA)
#		self.objmat.setDiffuse(0.5, 1, 0.5, alpha)
#		self.objmat.setSpecular(0.5, 1, 0.5, alpha)

	def setMainMeshVisible(self, visible):
		self.objentity.setVisible(visible)

	def setBoxesVisibility(self, type, visible):
		for e in self.entries:
			if self.entries[e].box: # if it isn't a dot
				if type == "collision" and self.entries[e].box.virtual == False:
					self.entries[e].visible = visible

				elif type == "virtual" and self.entries[e].box.virtual:
					self.entries[e].visible = visible
#				self.entries[e].node.showBoundingBox(False)

	def clear(self):
		self.entries.clear()
		self.sceneManager.clearScene()
		self.initVariables()
#		self.SceneInitialisation()
		self.populateScene()
		#FIXME: ground and sky plane are loose??
# Lepes comment it out
#		for box in self.boxes:
#			try:
#				box.node.detachAllObjects()
#				self.sceneManager.destroySceneNode(box.node.getName())
#			except:
#				pass
#			try:
#				self.sceneManager.destroyEntity(box.entity)
#			except:
#				pass
#
#
#		try:
#			self.sceneManager.destroyAllManualObjects()
#		except:
#			pass
#		try:
#			self.objnode.detachAllObjects()
#			self.sceneManager.destroySceneNode(self.objnode.getName())
#		except:
#			pass
#		try:
#			self.sceneManager.destroyEntity(self.objentity)
#		except:
#			pass
	def __del__(self):
#		del self.sceneManager
		pass

	def populateScene(self):
		self.sceneManager.AmbientLight = ogre.ColourValue(201, 201, 173) #0.7, 0.7, 0.7 )
		self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
		self.sceneManager.setSkyDome(True, 'mysimple/terraineditor/previewwindowsky', 4.0, 8.0)

		#self.MainLight = self.sceneManager.createLight('MainLight')
		#self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

		# add some fog
#		self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002)

		#create ray template
		self.rayQuery = self.sceneManager.createRayQuery(ogre.Ray());

		# create a floor Mesh
		plane = ogre.Plane()
		plane.normal = ogre.Vector3(0, 1, 0)
		plane.d = 200
		uuid = str(randomID())
		ogre.MeshManager.getSingleton().createPlane(uuid + 'FloorPlane', "General", plane, 200000.0, 200000.0,
													20, 20, True, 1, 50.0, 50.0, ogre.Vector3(0, 0, 1),
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													True, True)

		# create floor entity
		entity = self.sceneManager.createEntity(uuid + 'floor', uuid + 'FloorPlane')
		entity.setMaterialName('mysimple/terraineditor/previewwindowfloor')
		self.sceneManager.getRootSceneNode().createChildSceneNode().attachObject(entity)



	def updateCamera(self):
		return
		if not self.objnode is None:
			self.radius = self.objentity.getBoundingRadius() * 2
			height = self.objentity.getBoundingBox().getMaximum().z
			#pos = self.objnode.getPosition() + ogre.Vector3(0, height*0.4, 0)
			# always look to the center!
			pos = self.objnode.getPosition() + ogre.Vector3(0, height * 0.4, 0) + (self.objentity.getBoundingBox().getMinimum() + self.objentity.getBoundingBox().getMaximum()) / 2
			dx = math.cos(self.camalpha) * self.radius
			dy = math.sin(self.camalpha) * self.radius
			self.camera.setPosition(pos - ogre.Vector3(dx, -5, dy))
			self.camera.lookAt(pos + ogre.Vector3(0, height / 2, 0))

			# disable auto rotation
			#if self.dragging == False:
			#	self.camalpha += math.pi / 720
			if self.camalpha >= 360:
				self.camalpha -= 360


	def OnFrameStarted(self):
		pass

	def selectnew(self, event):
		x, y = event.GetPosition()
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()
		mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
		self.rayQuery.setRay(mouseRay)
		self.rayQuery.setSortByDistance(True)
		result = self.rayQuery.execute()
		mousePos = None
		selectedSomething = False
		for r in result:
			if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
				if r.movable.getName() in self.axis.arrowNames:
					self.axis.arrow = r.movable
					return

#		if len(self.ignorearray) > 20:
#			self.ignorearray = []
#		self.ignorearray.append("circlepointer")
		for r in result:
			if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":

				name = r.movable.getName()
				realname = name[:-len('Entity')]
#				if name in self.ignorearray:
#					# you cannot select these objects
#					continue
				if not self.entries.has_key(realname): #main entity not selectable
					continue
				elif not self.entries[realname].visible:
					continue
				elif not self.entries[realname].canBeSelected:
					continue
				if not self.selected.entry is None and self.selected.entry.entity.getName() == name:
					continue
				#print r.movable.getMovableType(), r.movable.getName()
				self.selected.type = "object"
				selectedSomething = True
				self.changeSelection(r.movable)
				break
		if not selectedSomething:
			self.selected.coords.asVector3 = self.axis.pointer3d.getPosition()
			self.selected.type = 'terrain'
			self.selected.entry = None
#			print "selecting pointer3D at %.2f %.2f %.2f" %(self.selected.coords.x, self.selected.coords.y, self.selected.coords.z)
		return

	def changeSelection(self, newnode,
						doc=" receive an Entity "):

		key = newnode.getName()[:-len("entity")]
		self.selected.entry = self.entries[key]
		self.boundBox.dockTo(self.selected.entry)
		if self.selected.entry.box:
			print "selected " + self.selected.entry.box.name
#		self.selected.entry.entity.getParentSceneNode().showBoundingBox(True)

	def getPointedPosition(self, event,
						doc=""" return Vector3 """):
		x, y = event.GetPosition()
		self.log("x , y : ", [x, y])
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()
		mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
		myRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
		myRaySceneQuery.setRay(mouseRay)
		result = myRaySceneQuery.execute()
		if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
			return result[0].worldFragment.singleIntersection
		return None

	def onMouseEvent(self, event):
		self.SetFocus()
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()

		if event.RightDown(): #Precedes dragging
			self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click
		if event.GetWheelRotation() != 0:
			zfactor = 0.001
			if event.ShiftDown():
				zfactor = 0.01
			zoom = zfactor * -event.GetWheelRotation()
			self.camera.moveRelative(ogre.Vector3(0, 0, zoom))

		if event.Dragging() and event.RightIsDown() and event.ControlDown():
			x, y = event.GetPosition()
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y
			if event.ShiftDown():
				dx = float(dx) / 10
				dy = float(dy) / 10
			else:
				dx = float(dx) / 50
				dy = float(dy) / 50
			self.camera.moveRelative(ogre.Vector3(dx, -dy, 0))

		elif event.Dragging() and event.RightIsDown(): #Dragging with RMB
			x, y = event.GetPosition()
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y

			self.camera.yaw(ogre.Degree(dx / 3.0))
			self.camera.pitch(ogre.Degree(dy / 3.0))

		if event.LeftDown():
			self.selectnew(event)
			self.StartDragLeftX, self.StartDragLeftY = event.GetPosition() #saves position of initial click

		self.controlArrows(event)
		event.Skip()

	def log(self, text, param=[]):
		""" easy log any floating values, for example:
			self.log(" data position is:", [data.x, data.y, data.z]) """
		log().info(text.ljust(17) + " ".join(["%.6f" % x for x in param]))

	def controlArrows(self, event):
		if self.selected.axis.arrow is None:
			return

		forcex = float(0)
		forcey = float(0)
		if event.Dragging() and event.LeftIsDown():
			x, y = event.GetPosition()
			forcex = float(self.StartDragLeftX - x)
			forcey = float(self.StartDragLeftY - y)
			self.StartDragLeftX, self.StartDragLeftY = event.GetPosition()

		forcex /= 2
		forcey /= 2
		if event.ShiftDown():
			forcex /= 10
			forcey /= 10

		LockSteps = event.AltDown()
		forceDegree = ogre.Degree(forcex).valueRadians()

		if not event.Dragging():
			return

		if self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[0]:
			 self.translateSelected(ogre.Vector3(forcex, 0, 0), LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[1]:
			self.translateSelected(ogre.Vector3(0, 0, forcex), LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[2]:
			self.translateSelected(ogre.Vector3(0, forcex, 0), LockSteps)

		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[3]:
			self.rotateSelected(ogre.Vector3(0, 1, 0), forceDegree, LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[4]:
			self.rotateSelected(ogre.Vector3(1, 0, 0), forceDegree, LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[5]:
			self.rotateSelected(ogre.Vector3(0, 0, 1), forceDegree, LockSteps)


	def translateSelected(self, vector, steps=True,
		doc=""" vector is an offset to translate to
				 steps is something like align to grid"""):

		if not self.selected.entry:
			return
		newpos = self.selected.entry.node._getDerivedPosition() + vector
		self.selected.entry.node.setPosition(newpos)
		if not self.selected.entry.box is None:
			self.log('moving entry %s to pos ' % self.selected.entry.box.name, [newpos.x, newpos.y, newpos.z])
		else:
			self.log('moving entry to pos ', [newpos.x, newpos.y, newpos.z])
		self.selected.axis.attachTo(self.selected.entry.node)
		self.updateDetails(self.selected.entry)
#		self.addObjectToHistory(self.selected.entry)

	def rotateSelected(self, axis, amount, steps=True):
		if not self.selected.entry:
			return
		self.selected.entry.node.rotate(axis, amount, relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
		newrot = self.selected.entry.node.getOrientation()

		# todo: get this working!
		if False:
			print amount
			stepsize = 10
			rotzz = -ogre.Radian(newrot.getYaw()).valueDegrees()
			rotz = rotzz - (rotzz % stepsize)
			rotyy = ogre.Radian(newrot.getRoll()).valueDegrees()
			roty = rotyy - (rotyy % stepsize)
			rotxx = ogre.Radian(newrot.getPitch()).valueDegrees()
			rotx = rotxx - (rotxx % stepsize)
			print rotx, roty, rotz, rotxx, rotyy, rotzz
			self.virtualMoveNode.resetOrientation()
			self.virtualMoveNode.rotate(ogre.Vector3(0, 0, 1), ogre.Degree(rotz).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			self.virtualMoveNode.rotate(ogre.Vector3(0, 1, 0), ogre.Degree(roty).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			self.virtualMoveNode.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(rotx).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)

			newrot = self.selected.entry.node.getOrientation()

		self.selected.entry.node.setOrientation(newrot)
		self.selected.entry.ogreRotation = newrot
		self.selected.axis.rotateNode.setOrientation(newrot)
		self.updateDetails(self.selected.entry)

	def onKeyDown(self, event):
		#print event.m_keyCode
		d = 3
		scale = 0.1
		if event.ShiftDown():
			d = 10
			scale = 5
		if event.m_keyCode == WXK_D: # A, wx.WXK_LEFT:
			self.camera.moveRelative(ogre.Vector3(-d, 0, 0))
		elif event.m_keyCode == WXK_A: # D, wx.WXK_RIGHT:
			self.camera.moveRelative(ogre.Vector3(d, 0, 0))
		elif event.m_keyCode == WXK_W: #wx.WXK_UP: # W
			self.camera.moveRelative(ogre.Vector3(0, 0, -d))
		elif event.m_keyCode == WXK_S: # S, wx.WXK_DOWN:
			self.camera.moveRelative(ogre.Vector3(0, 0, d))
		elif event.m_keyCode == WXK_V: #wx.WXK_PAGEUP:
			self.camera.moveRelative(ogre.Vector3(0, d, 0))
		elif event.m_keyCode == WXK_F: #wx.WXK_PAGEDOWN:
			self.camera.moveRelative(ogre.Vector3(0, -d, 0))
		elif event.m_keyCode == WXK_T: # 84 = T
			if self.filtering == ogre.TFO_BILINEAR:
				self.filtering = ogre.TFO_TRILINEAR
				self.Aniso = 1
			elif self.filtering == ogre.TFO_TRILINEAR:
				self.filtering = ogre.TFO_ANISOTROPIC
				self.Aniso = 8
			else:
				self.filtering = ogre.TFO_BILINEAR
				self.Aniso = 1
			ogre.MaterialManager.getSingleton().setDefaultTextureFiltering(self.filtering)
			ogre.MaterialManager.getSingleton().setDefaultAnisotropy(self.Aniso)
		elif event.m_keyCode == WXK_P:
			if self.selected:
				self.selected.entry.logPosRot(self.selected.entry.name)
		elif event.m_keyCode == WXK_R: # 82 = R
			self.setWireframe()
		elif event.m_keyCode == WXK_Q:
			self.autoTracking = not self.autoTracking
		elif event.m_keyCode == wx.WXK_F1:
			for s in self.entries:
				if self.entries[s].box:
					self.entries[s].box.debug("box coordenate")
					self.boundBox.debug("derived Position")

				else:
					p = self.entries[s].node._getDerivedPosition()
					log().info("node at %2.1f, %2.1f, %2.1f" % (p.x, p.y, p.z))
		elif event.m_keyCode == wx.WXK_F2:
			""" create attach point"""
			x, y, z = self.axis.pointer3d.getPosition()
			e = self.createDotAt(x, y, z, CLBLUE, "attach_point")
			self.selected.entry = e
		elif event.m_keyCode == wx.WXK_F3:
			s = '\n'
			for i in range(0, len(self.mainOdef.boxes)):
				s += self.mainOdef.boxes[i].getOdefboxString()

			showInfo("BoxCoords", " boxcoords coordenates for odef file:" + s)
		elif event.m_keyCode == wx.WXK_F4:
			if self.selected:
				if self.selected.entry:
					n = self.selected.entry.node
					n.setScale(n.getScale() + ogre.Vector3(scale, 0, 0))
					self.updateDetails(self.selected.entry)
		elif event.m_keyCode == wx.WXK_F6:
			if self.selected:
				if self.selected.entry:
					n = self.selected.entry.node
					n.setScale(n.getScale() + ogre.Vector3(0, scale, 0))
					self.updateDetails(self.selected.entry)
		elif event.m_keyCode == wx.WXK_F8:
			if self.selected:
				if self.selected.entry:
					n = self.selected.entry.node
					n.setScale(n.getScale() + ogre.Vector3(0, 0, scale))
					self.updateDetails(self.selected.entry)
		elif event.m_keyCode == wx.WXK_F5:
			if self.selected:
				if self.selected.entry:
					n = self.selected.entry.node
					n.setScale(n.getScale() - ogre.Vector3(scale, 0, 0))
					self.updateDetails(self.selected.entry)
		elif event.m_keyCode == wx.WXK_F7:
			if self.selected:
				if self.selected.entry:
					n = self.selected.entry.node
					n.setScale(n.getScale() - ogre.Vector3(0, scale, 0))
					self.updateDetails(self.selected.entry)
		elif event.m_keyCode == wx.WXK_F9:
			if self.selected:
				if self.selected.entry:
					n = self.selected.entry.node
					n.setScale(n.getScale() - ogre.Vector3(0, 0, scale))
					self.updateDetails(self.selected.entry)
		elif event.m_keyCode == wx.WXK_F12:
			ob = odefbox(None)
			ob.coord0.asVector3 = self.axis.pointer3d.getPosition()
			ob.coord1.asVector3 = ob.coord0.asVector3 + ogre.Vector3(1, 1, 1)
			ob.virtual = False
			e = self.createBox(ob, True)
			self.selected.entry = e


		event.Skip()
	def updateDetails(self, entry):
		"""boxes are size changed, we need to know new bounding box
		"""
		r = entry.rotation
		p = entry.position # child nodes need to be around entry.node !!!
		entry.position = 0, 0, 0
		entry.rotation = 0, 0, 0 #different from terrain Editor wtf?
		entry.node._updateBounds()
		if entry.box:
		# if it is a DOT, then don't create aab
			entry.details = {
				 "aabb" : {
						 "nearLeftTop"	  : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_TOP),
						 "nearRightTop"	 : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_BOTTOM),
						 "nearLeftBottom"   : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_LEFT_TOP),
						 "nearRightBottom"  : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_LEFT_BOTTOM),
						 "farLeftTop"	   : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_TOP),
						 "farRightTop"	  : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_BOTTOM),
						 "farLeftBottom"	: entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_RIGHT_TOP),
						 "farRightBottom"   : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.FAR_RIGHT_BOTTOM),
						 "nearMiddle"	   : entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_TOP).midPoint(entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_LEFT_BOTTOM)),
						 "farMiddle"		: entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_TOP).midPoint(entry.node._getWorldAABB().getCorner(ogre.AxisAlignedBox.NEAR_RIGHT_BOTTOM)),
								 }
						 }
			entry.details["long"] = entry.details["aabb"]["nearLeftTop"].distance(entry.details["aabb"]["farLeftTop"])
			entry.details["wide"] = entry.details["aabb"]["nearLeftTop"].distance(entry.details["aabb"]["nearRightTop"])
			entry.details["height"] = entry.details["aabb"]["nearLeftTop"].distance(entry.details["aabb"]["nearLeftBottom"])

			self.bbresize.dicty = {}
			self.bbresize.dicty["up"] = entry.details["aabb"]["nearLeftTop"].midPoint(entry.details["aabb"]["farRightTop"])
			self.bbresize.dicty["down"] = entry.details["aabb"]["nearLeftBottom"].midPoint(entry.details["aabb"]["farRightBottom"])
			self.bbresize.dicty["left"] = entry.details["aabb"]["nearLeftTop"].midPoint(entry.details["aabb"]["farLeftBottom"])
			self.bbresize.dicty["right"] = entry.details["aabb"]["nearRightTop"].midPoint(entry.details["aabb"]["farRightBottom"])
			self.bbresize.dicty["front"] = entry.details["aabb"]["nearLeftTop"].midPoint(entry.details["aabb"]["nearRightBottom"])
			self.bbresize.dicty["back"] = entry.details["aabb"]["farLeftTop"].midPoint(entry.details["aabb"]["farRightBottom"])

		entry.position = p
		entry.rotation = r
		if entry.box:
			self.boundBox.dockTo(entry)
			#update odefbox size
			entry.box.coord0.asVector3 = self.boundBox.getMinimum() #+ entry.node.getPosition()
			entry.box.coord1.asVector3 = self.boundBox.getMaximum() #+ entry.node.getPosition()
			entry.box.rotation.asTuple = entry.rotation

			self.bbresize.dockTo(entry, atPos=p, aabb=self.bbresize.dicty)
#		for c in self.boundBox.dots.keys():
#			entry.details["aabb"][c] = self.boundBox.dots[c].node._getDerivedPosition()
			# now details has the global coordenates, the real size of the bounding box




	def setWireframe(self):

		detailsLevel = [ogre.PM_SOLID, ogre.PM_WIREFRAME, ogre.PM_POINTS]
		self.sceneDetailIndex = (self.sceneDetailIndex + 1) % len(detailsLevel)
		self.camera.polygonMode = detailsLevel[self.sceneDetailIndex]
