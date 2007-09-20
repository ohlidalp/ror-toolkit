#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, math
import ogre.renderer.OGRE as ogre
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.SimpleTruckRepresentation import *
from ror.odefparser import *
from ror.rorcommon import *


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

class ObjectPreviewOgreWindow(wxOgreWindow):
	def __init__(self, parent, ID, size = wx.Size(200,200), rordir = "", **kwargs):
		self.rordir = rordir
		self.parent = parent
		self.objnode = None
		self.objentity = None
		self.camalpha = 0
		self.radius = 40
		self.dragging = False
		self.mode = None
		self.logovisible = True
		wxOgreWindow.__init__(self, parent, ID, size = size, **kwargs)
		droptarget = TreeDropTarget(self)
		self.SetDropTarget(droptarget)


	def SceneInitialisation(self):
		addresources = [os.path.join(self.rordir,'data', 'terrains'),
						os.path.join(self.rordir,'data', 'trucks'),
						os.path.join(self.rordir,'data', 'objects')]
		# only init things in the main window, not in shared ones!
		# setup resources
		for r in addresources:
			ogre.ResourceGroupManager.getSingleton().addResourceLocation(r, "FileSystem", "General", False)

		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media", "FileSystem", "General", False)
		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials", "FileSystem", "General", False)
		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/models", "FileSystem", "General", False)
		ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()
		self.createSceneManager()

	def createSceneManager(self, type="object"):
		#get the scenemanager
		self.mode = type
		uuid = randomID()
		if type == "object":
			self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)
		elif type == "terrain":
			self.sceneManager = getOgreManager().createSceneManager(ogre.ST_EXTERIOR_CLOSE)

		# create a camera
		self.camera = self.sceneManager.createCamera(str(randomID())+'Camera')
		self.camera.lookAt(ogre.Vector3(0, 0, 0))
		self.camera.setPosition(ogre.Vector3(0, 0, 100))
		self.camera.nearClipDistance = 1
		self.camera.setAutoAspectRatio(True)

		# create the Viewport"
		self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0)
		self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0)

		# bind mouse and keyboard
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

		#create objects
		self.populateScene()

	def loadFile(self, filename):
		self.filename = filename
		filenameonly, extension = os.path.splitext(filename)
		uuid = randomID()

		#hide logo
		self.logovisible = False

		if extension.lower() in [".truck", ".load"]:
			self.mode="object"
			self.free()
			self.createSceneManager()
			uuid = randomID()
			self.objnode, self.objentity, manualobject = createTruckMesh(self.sceneManager, filename, uuid)
			#print "aaa", self.objnode.getPosition()
		elif extension.lower() in [".odef"]:
			self.mode="object"
			self.free()
			self.createSceneManager()
			self.loadodef(filename, uuid)
		elif extension.lower() in [".terrn"]:
			self.mode="terrain"
			self.free()
			self.createSceneManager("terrain")
			terrain = RoRTerrain(filename)
			cfgfile = os.path.join(os.path.dirname(filename), terrain.TerrainConfig)
			self.objnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid+"objnode")
			self.objnode.setPosition(1500, 0, 1500)
			self.sceneManager.setWorldGeometry(cfgfile)

	def loadodef(self, filename, uuid):
		try:
			meshname, sx, sy, sz, ismovable, boxes = loadOdef(filename)
		except Exception, err:
			log().error("error while processing odef file %s" % filename)
			log().error(str(err))
			return
		# create mesh
		print meshname, sx, sy, sz
		self.objnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid+"objnode")
		self.objentity = self.sceneManager.createEntity(uuid+'objentity', meshname)
		self.objnode.attachObject(self.objentity)
		self.objnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		#self.objnode.setPosition(0,0,0)
		if not sx is None:
			self.objnode.setScale(sx, sy, sz)


	def free(self):
		try:
			self.sceneManager.destroyAllManualObjects()
		except Exception, e:
			log().exception(str(e))

		try:
			self.logotextnode.detachAllObjects()
			self.logowheelnode.detachAllObjects()
			self.sceneManager.destroySceneNode(self.logotextnode.getName())
			self.sceneManager.destroySceneNode(self.logowheelnode.getName())
			self.sceneManager.destroyEntity(self.logotextentity)
			self.sceneManager.destroyEntity(self.logowheelentity)
		except Exception, e:
			log().exception(str(e))
		try:
			#BUG: next line fails and goes to except
			self.objnode.detachAllObjects()
			self.sceneManager.destroySceneNode(self.objnode.getName())
		except Exception, e:
			log().exception(str(e))

		#try:
			#BUG Entering this function alone seams to kill the application.
			#self.sceneManager.destroyEntity(self.objentity)
		#except Exception, e:
			#log().exception(str(e))

		self.renderWindow.removeAllViewports()
		getOgreManager().destroySceneManager(self.sceneManager)

	def populateScene(self):
		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )
		self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
		self.sceneManager.setSkyDome(True, 'mysimple/terraineditor/previewwindowsky', 4.0, 8.0)

		#self.MainLight = self.sceneManager.createLight('MainLight')
		#self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

		# add some fog
		self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.00002)

		# create a floor Mesh
		plane = ogre.Plane()
		plane.normal = ogre.Vector3(0, 1, 0)
		plane.d = 200
		uuid = str(randomID())
		ogre.MeshManager.getSingleton().createPlane(uuid + 'FloorPlane', "General", plane, 200000.0, 200000.0,
													20, 20, True, 1, 50.0, 50.0,ogre.Vector3(0, 0, 1),
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													True, True)

		# create floor entity
		entity = self.sceneManager.createEntity(uuid+'floor', uuid + 'FloorPlane')
		entity.setMaterialName('mysimple/terraineditor/previewwindowfloor')
		self.sceneManager.getRootSceneNode().createChildSceneNode().attachObject(entity)

		if self.logovisible:
			uuid = str(randomID())
			self.logowheelnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid+"logonode")
			self.logowheelentity = self.sceneManager.createEntity(uuid+'logoentity', "logowheel.mesh")
			self.logowheelentity.setMaterialName('mysimple/terrainselect')
			self.logowheelnode.attachObject(self.logowheelentity)
			self.logowheelnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			self.logowheelnode.setScale(0.025, 0.025, 0.025)

			uuid = str(randomID())
			self.logotextnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid+"logonode")
			self.logotextentity = self.sceneManager.createEntity(uuid+'logoentity', "logotext.mesh")
			self.logotextentity.setMaterialName('mysimple/transblue')
			self.logotextnode.attachObject(self.logotextentity)
			self.logotextnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
			self.logotextnode.setScale(0.025, 0.025, 0.025)

		else:
			pass
			#self.logotextnode.setVisible(False)
			#self.logowheelnode.setVisible(False)


	def updateCamera(self):
		if not self.mode is None:
			if self.logovisible:
				self.radius = 100
				pos = self.logotextnode.getPosition()
				lookheight = ogre.Vector3(0,0,0)
				self.logowheelnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(1),relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
			else:
				if self.mode == "object":
					self.radius = self.objentity.getBoundingRadius() * 2
					if self.objentity is None:
						height = 20
					else:
						height = self.objentity.getBoundingBox().getMaximum().z
					rotateheight = ogre.Vector3(0, height * 0.2, 0)
					pos = self.objnode.getPosition() + rotateheight + (self.objentity.getBoundingBox().getMinimum() + self.objentity.getBoundingBox().getMaximum() ) / 2
					lookheight =  ogre.Vector3(0, height / 2, 0)
				elif self.mode == "terrain":
					self.radius = 3000
					rotateheight = ogre.Vector3(0, 1600, 0)
					pos = self.objnode.getPosition() + rotateheight
					lookheight = -rotateheight

			dx = math.cos(self.camalpha) * self.radius
			dy = math.sin(self.camalpha) * self.radius
			self.camera.setPosition(pos - ogre.Vector3(dx, -5, dy))
			self.camera.lookAt(pos + lookheight)
			if self.dragging == False:
				self.camalpha += math.pi / 720
			if self.camalpha >= 360:
				self.camalpha -= 360


	def OnFrameStarted(self):
		if self.logovisible:
			self.logowheelnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(1),relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
		self.updateCamera()
		wxOgreWindow.OnFrameStarted(self)

	def onMouseEvent(self, event):
		#self.SetFocus() #Gives Keyboard focus to the window

		if event.RightDown(): #Precedes dragging
			self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click
		elif event.Dragging() and event.RightIsDown(): #Dragging with RMB
			x,y = event.GetPosition()
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y
			self.camalpha -= float(dx) * (math.pi / 720) * 2
			self.updateCamera()
			self.dragging = True
		else:
			self.dragging = False
		event.Skip()
				