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


NEWMATNAME = "mysimple/odefeditor/objplaceholder"

class ODefEditorOgreWindow(wxOgreWindow):
	def __init__(self, parent, ID, size = wx.Size(200,200), rordir = "", **kwargs):
		self.rordir = rordir
		self.parent = parent
		self.objnode = None
		self.objentity = None
		self.camalpha = 0
		self.radius = 40
		self.dragging = False
		self.boxes = []
		self.objmat = None
		self.randcolors = [0,0.2,0.4]
		wxOgreWindow.__init__(self, parent, ID, size = size, **kwargs)
		droptarget = TreeDropTarget(self)
		self.SetDropTarget(droptarget)


	def SceneInitialisation(self):
		initResources(self.rordir)

		#get the scenemanager
		self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

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
		d=10.0 #displacement for key strokes
		self.ControlKeyDict={wx.WXK_LEFT:ogre.Vector3(-d,0.0,0.0),
							wx.WXK_RIGHT:ogre.Vector3(d,0.0,0.0),
							wx.WXK_UP:ogre.Vector3(0.0,0.0,-d),
							wx.WXK_DOWN:ogre.Vector3(0.0,0.0,d),
							wx.WXK_PAGEUP:ogre.Vector3(0.0,d,0.0),
							wx.WXK_PAGEDOWN:ogre.Vector3(0.0,-d,0.0)}
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		#self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)
		#create objects
		self.populateScene()

	def loadFile(self, filename):
		self.filename = filename
		filenameonly, extension = os.path.splitext(filename)
		if extension.lower() in [".truck", ".load"]:
			self.free()
			uuid = randomID()
			self.objnode, self.objentity, manualobject = createTruckMesh(self.sceneManager, filename, uuid)
		elif extension.lower() in [".odef"]:
			self.free()
			uuid = randomID()
			self.loadodef(filename, uuid)

	def loadodef(self, filename, uuid):
		try:
			meshname, sx, sy, sz, ismovable, boxes = loadOdef(filename)
		except Exception, err:
			log().error("error while processing odef file %s" % filename)
			log().error(str(err))
			return
		# create mesh
		self.objnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid+"objnode")
		self.objentity = self.sceneManager.createEntity(uuid+'objentity', meshname)
		self.objnode.attachObject(self.objentity)
		self.objnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)

		try:
			self.objOriginalMat = ogre.MaterialManager.getSingleton().getByName(self.objentity.getSubEntity(0).getMaterialName())
			if self.objmat is None:
				self.objmat = ogre.MaterialManager.getSingleton().getByName(NEWMATNAME)
			self.objOriginalMat.copyDetailsTo(self.objmat)
			# self.objmat = ogre.MaterialManager.getSingleton().getByName(NEWMATNAME)
			self.objmat.setSceneBlending(ogre.SceneBlendFactor.SBF_SOURCE_ALPHA, ogre.SceneBlendFactor.SBF_DEST_ALPHA )
			self.objentity.setMaterialName(NEWMATNAME)
			self.setMainMeshTrans(60)
		except:
			pass

		self.objnode.setPosition(0,0,0)
		if not sx is None:
			self.objnode.setScale(sx, sy, sz)
		for box in boxes:

			matname = "mysimple/odefeditor/transred"
			if box.virtual:
				matname = "mysimple/odefeditor/transgreen"
			matname = self.getNewMat(matname)
			box.uuid = randomID()
			box.node = self.sceneManager.getRootSceneNode().createChildSceneNode(box.uuid+"boxnode")
			box.entity = self.sceneManager.createEntity(box.uuid+'boxentity', "beam.mesh")
			box.entity.setMaterialName(matname)
			box.node.attachObject(box.entity)

			if box.rotating:
				rotx = float(box.rotation[0])
				roty = float(box.rotation[1])
				rotz = float(box.rotation[2])
				box.node.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(rotz),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
				box.node.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(roty),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
				box.node.rotate(ogre.Vector3.UNIT_X, ogre.Degree(rotx),relativeTo=ogre.Node.TransformSpace.TS_WORLD)

			x = float(box.coords[0])
			x1 = float(box.coords[1])
			y = float(box.coords[2])
			y1 = float(box.coords[3])
			z = float(box.coords[4])
			z1 = float(box.coords[5])
			xdiff = x1-x
			ydiff = y1-y
			zdiff = z1-z
			box.node.setPosition(x+xdiff/2, y+ydiff/2, z+zdiff/2)
			box.node.setScale(xdiff, ydiff, zdiff)
			self.boxes.append(box)

	def getNewMat(self, basematname):
		uuid = randomID()
		matname = uuid+"mat"
		basemat = ogre.MaterialManager.getSingleton().getByName(basematname)
		mat = ogre.MaterialManager.getSingleton().create(matname, basemat.getGroup())
		basemat.copyDetailsTo(mat)
		#mat = ogre.MaterialManager.getSingleton().getByName(matname)
		for i in range(0,2):
			self.randcolors[i] += 0.1
			if self.randcolors[i] >= 1:
				self.randcolors[i] -= 1
		mat.setDiffuse(self.randcolors[0], self.randcolors[1], self.randcolors[2], 0.8)
		mat.setSpecular(self.randcolors[0], self.randcolors[1], self.randcolors[2], 0.8)
		mat.setSelfIllumination(self.randcolors[0], self.randcolors[1], self.randcolors[2])
		mat.setAmbient(self.randcolors[0], self.randcolors[1], self.randcolors[2])
		print "new material:", matname
		return matname

	def setMainMeshTrans(self, alpha):
		alpha = float(alpha) / float(100)
		self.objmat.setDiffuse(0.5, 1, 0.5, alpha)
		self.objmat.setSpecular(0.5, 1, 0.5, alpha)

	def setMainMeshVisible(self, visible):
		self.objentity.setVisible(visible)

	def setBoxesVisibility(self, type, visible):
		for box in self.boxes:
			if type == "normal" and box.virtual == False:
				box.entity.setVisible(visible)
			elif type == "virtual" and box.virtual == True:
				box.entity.setVisible(visible)

	def free(self):
		for box in self.boxes:
			try:
				box.node.detachAllObjects()
				self.sceneManager.destroySceneNode(box.node.getName())
			except:
				pass
			try:
				self.sceneManager.destroyEntity(box.entity)
			except:
				pass
		self.boxes = []

		try:
			self.sceneManager.destroyAllManualObjects()
		except:
			pass
		try:
			self.objnode.detachAllObjects()
			self.sceneManager.destroySceneNode(self.objnode.getName())
		except:
			pass
		try:
			self.sceneManager.destroyEntity(self.objentity)
		except:
			pass

	def populateScene(self):
		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )
		self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
		self.sceneManager.setSkyDome(True, 'mysimple/terraineditor/previewwindowsky', 4.0, 8.0)

		#self.MainLight = self.sceneManager.createLight('MainLight')
		#self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

		# add some fog
		self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002)

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

	def updateCamera(self):
		return
		if not self.objnode is None:
			self.radius = self.objentity.getBoundingRadius() * 2
			height = self.objentity.getBoundingBox().getMaximum().z
			#pos = self.objnode.getPosition() + ogre.Vector3(0, height*0.4, 0)
			# always look to the center!
			pos = self.objnode.getPosition() + ogre.Vector3(0, height*0.4, 0) + (self.objentity.getBoundingBox().getMinimum() + self.objentity.getBoundingBox().getMaximum() ) / 2
			dx = math.cos(self.camalpha) * self.radius
			dy = math.sin(self.camalpha) * self.radius
			self.camera.setPosition(pos - ogre.Vector3(dx, -5, dy))
			self.camera.lookAt(pos + ogre.Vector3(0, height / 2, 0))

			# disable auto rotation
			#if self.dragging == False:
			#    self.camalpha += math.pi / 720
			if self.camalpha >= 360:
				self.camalpha -= 360


	def OnFrameStarted(self):
		self.updateCamera()
		wxOgreWindow.OnFrameStarted(self)

	def onMouseEvent(self,event):
		self.SetFocus()
		width, height, a, b, c = self.renderWindow.getMetrics()

		if event.RightDown(): #Precedes dragging
			self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click
		if event.GetWheelRotation() != 0:
			zfactor = 0.001
			if event.ShiftDown():
				zfactor = 0.01
			zoom = zfactor * -event.GetWheelRotation()
			self.camera.moveRelative(ogre.Vector3(0,0, zoom))

		if event.Dragging() and event.RightIsDown() and event.ControlDown():
			x,y = event.GetPosition()
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y
			if event.ShiftDown():
				dx = float(dx) / 10
				dy = float(dy) / 10
			else:
				dx = float(dx) / 50
				dy = float(dy) / 50
			self.camera.moveRelative(ogre.Vector3(dx,-dy,0))

		elif event.Dragging() and event.RightIsDown(): #Dragging with RMB
			x,y = event.GetPosition()
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y

			self.camera.yaw(ogre.Degree(dx/3.0))
			self.camera.pitch(ogre.Degree(dy/3.0))
		if event.LeftDown():
			#self.selectnew(event)
			self.StartDragLeftX, self.StartDragLeftY = event.GetPosition() #saves position of initial click
			zfactor = 0.1
			if event.ShiftDown():
				zfactor = 5
			zoom = zfactor * -event.GetWheelRotation()
			self.camera.moveRelative(ogre.Vector3(0,0, zoom))

	def onKeyDown(self,event):
		#print event.m_keyCode
		d = 3
		if event.ShiftDown():
			d = 10
		if event.m_keyCode == 65: # A, wx.WXK_LEFT:
			self.camera.moveRelative(ogre.Vector3(-d,0,0))
		elif event.m_keyCode == 68: # D, wx.WXK_RIGHT:
			self.camera.moveRelative(ogre.Vector3(d,0,0))
		elif event.m_keyCode == 87: # W ,wx.WXK_UP:
			self.camera.moveRelative(ogre.Vector3(0,0,-d))
		elif event.m_keyCode == 83: # S, wx.WXK_DOWN:
			self.camera.moveRelative(ogre.Vector3(0,0,d))
		elif event.m_keyCode == wx.WXK_PAGEUP:
			self.camera.moveRelative(ogre.Vector3(0,d,0))
		elif event.m_keyCode == wx.WXK_PAGEDOWN:
			self.camera.moveRelative(ogre.Vector3(0,-d,0))
		elif event.m_keyCode == 84: # 84 = T
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
		elif event.m_keyCode == 82: # 82 = R
			detailsLevel = [ ogre.PM_SOLID,
							ogre.PM_WIREFRAME,
							ogre.PM_POINTS ]
			self.sceneDetailIndex = (self.sceneDetailIndex + 1) % len(detailsLevel)
			self.camera.polygonMode=detailsLevel[self.sceneDetailIndex]
