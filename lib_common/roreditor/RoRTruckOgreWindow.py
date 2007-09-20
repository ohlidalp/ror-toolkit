#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
# see revision 67 for new camera changes!!

import wx, os, os.path
import ogre.renderer.OGRE as ogre
from ror.truckparser import *

#from ror.camera import *

from ror.logger import log
from ror.settingsManager import getSettingsManager

from ror.rorcommon import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *

import ogre.renderer.OGRE as Ogre
import ogre.physics.OgreNewt as OgreNewt
import ogre.io.OIS as OIS

TIMER = 25
#from random import random

class RoRTruckOgreWindow(wxOgreWindow):
	def __init__(self, parent, ID, size = wx.Size(200,200), **kwargs):
		self.parent = parent
		self.rordir = getSettingsManager().getSetting("RigsOfRods", "BasePath")
		self.World = OgreNewt.World()
		self.sceneManager = None
		self.uvFrame = None
		self.clearlist = {'entity':[]}
		self.bodies = []
		self.initScene()
		wxOgreWindow.__init__(self, parent, ID, size = size, **kwargs)

	def initScene(self, resetCam = True):
		if not self.sceneManager is None:
			self.sceneManager.destroyAllManualObjects()
		self.EntityCount = 0


		# try to clear things up
		try:
			if self.nodes != {}:
				for n in self.nodes:
					n[0].detachAllObjects()
					self.sceneManager.destroySceneNode(n[0].getName())
		except:
			pass
		try:
			for e in self.clearlist['entity']:
				print e
				self.sceneManager.destroyEntity(e)
		except:
			pass
		try:
			self.uvFrame.Close()
		except:
			pass
		self.nodes = {}
		self.beams = {}
		self.shocks = {}
		self.submeshs = {}
		self.selection = None
		self.enablephysics = False
		if resetCam:
			self.modeSettings = {}
			self.camMode = "3d"


	def __del__ (self):
		## delete the world when we're done.
		del self.bodies
		del self.World


	def OnFrameStarted(self):
		if self.enablephysics:
			self.World.update(TIMER)
			self.updateBeams()
		pass

	def OnFrameEnded(self):
		pass

	def SceneInitialisation(self):
		
    	#TODO This section is not platform independent, needs to be fixed.
		addresources = [self.rordir+"\\data\\trucks",self.rordir+"\\data\\objects"]
		# only init things in the main window, not in shared ones!
		# setup resources
		for r in addresources:
			ogre.ResourceGroupManager.getSingleton().addResourceLocation(r, "FileSystem", "General", False)

		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media", "FileSystem", "General", False)
		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials", "FileSystem", "General", False)
		ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/models", "FileSystem", "General", False)
		ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()

		#get the scenemanager
		self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

		# create a camera
		self.camera = self.sceneManager.createCamera('Camera')
		self.camera.lookAt(ogre.Vector3(0, 0, 0))
		self.camera.setPosition(ogre.Vector3(0, 0, 3))
		self.camera.nearClipDistance = 0.1
		self.camera.setAutoAspectRatio(False)

		# this is aperions new cam, but its much too buggy, so removed :((
		#self.camera2 = Camera(self.sceneManager.getRootSceneNode(), self.camera)

		# create the Viewport"
		self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0)
		self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0)

		#set some default values
		self.sceneDetailIndex = 0
		self.filtering = ogre.TFO_BILINEAR

		# bind mouse and keyboard
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

		#create objects
		self.populateScene()


	def createNode(self, node):
		try:
			id = int(node[0])
			pos = ogre.Vector3(float(node[1]),float(node[2]),float(node[3]))
			if len(node) == 5:
				option = node[4]
			else:
				option = None

				# 0.05
			size = 0.1
			mass = 0.5 * size

			inertia = OgreNewt.CalcBoxSolid( mass, size )

			box1node = self.sceneManager.getRootSceneNode().createChildSceneNode()
			box1 = self.sceneManager.createEntity("NodeEntity"+str(self.EntityCount), "ellipsoid.mesh" )
			self.clearlist['entity'].append("NodeEntity"+str(self.EntityCount))
			self.EntityCount += 1
			box1node.attachObject( box1 )
			box1node.setScale(size)
			box1.setNormaliseNormals(True)

			col = OgreNewt.Ellipsoid( self.World, size )
			bod = OgreNewt.Body(self.World, col)
			self.bodies.append (bod)

			del col

			bod.attachToNode( box1node )
			bod.setMassMatrix( mass, inertia )
			bod.setStandardForceCallback()

			if option == 'l':
				matname = "TruckEditor/NodeLoad"
			elif option == 'f':
				matname = "TruckEditor/NodeFriction"
			elif option == 'x':
				matname = "TruckEditor/NodeExhaust"
			elif option == 'y':
				matname = "TruckEditor/NodeExhaustReference"
			elif option == 'c':
				matname = "TruckEditor/NodeContact"
			elif option == 'h':
				matname = "TruckEditor/NodeHook"
			else:
				matname = "TruckEditor/NodeNormal"
			box1.setMaterialName(matname)
			box1.setCastShadows(False)

			bod.setPositionOrientation(pos, Ogre.Quaternion.IDENTITY )
			self.nodes[id] = [box1node, option, node]
			return bod
		except:
			pass

	def showSubmeshs(self, value):
		for k in self.submeshs.keys():
			submesh = self.submeshs[k]
			submesh[0].setVisible(value)

	def setSubmeshMode(self, mode):
		pass


	def showExhaustRefNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "y":
				node[0].setVisible(value)

	def showExhaustNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "x":
				node[0].setVisible(value)

	def showHookNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "h":
				node[0].setVisible(value)

	def showFrictionNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "f":
				node[0].setVisible(value)

	def showContactNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "c":
				node[0].setVisible(value)

	def showFrictionNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "f":
				node[0].setVisible(value)

	def showLoadNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "l":
				node[0].setVisible(value)

	def showNormalNodes(self, value):
		for k in self.nodes.keys():
			node = self.nodes[k]
			if node[1] == "" or node[1] == "n" or node[1] is None:
				node[0].setVisible(value)

	def showNormalBeams(self, value):
		for k in self.beams.keys():
			beam = self.beams[k]
			if beam[3] == "" or beam[3] == "n" or beam[3] == "v" or beam[3] is None:
				beam[0].setVisible(value)

	def showInvisibleBeams(self, value):
		for k in self.beams.keys():
			beam = self.beams[k]
			if beam[3] == "i":
				beam[0].setVisible(value)

	def showRopeBeams(self, value):
		for k in self.beams.keys():
			beam = self.beams[k]
			if beam[3] == "r":
				beam[0].setVisible(value)


	def createBeam(self, id0, id1, id2, options):
		try:
			pos1 = self.nodes[id1][0].getPosition()
			pos2 = self.nodes[id2][0].getPosition()

			idstr = str(id0) + str(id1) + str(id2)
			line =  self.sceneManager.createManualObject("manual"+idstr)
			if options == "i":
				mat = "TruckEditor/BeamInvisible"
			elif options == "r":
				mat = "TruckEditor/BeamRope"
			else:
				mat = "TruckEditor/BeamNormal"
			line.begin(mat, ogre.RenderOperation.OT_LINE_LIST)
			line.position(pos1)
			line.position(pos2)
			line.end()
			line.setCastShadows(False)
			line.setDynamic(True)
			linenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
			linenode.attachObject(line)
			self.beams[id0] = [linenode, id1, id2, options, line]
			print id0
		except:
			pass

	def updateBeams(self):
		for bk in self.beams.keys():
			beam = self.beams[bk]
			line = beam[4]
			id1 = beam[1]
			id2 = beam[2]
			try:
				pos1 = self.nodes[id1][0].getPosition()
				pos2 = self.nodes[id2][0].getPosition()
				line.beginUpdate(0)
				line.position(pos1)
				line.position(pos2)
				line.end()
			except Exception, e:
				print str(e)
				continue


	def createShock(self, id0, id1, id2, options):
		try:
			pos1 = self.nodes[id1][0].getPosition()
			pos2 = self.nodes[id2][0].getPosition()

			idstr = str(id0) + str(id1) + str(id2)
			line =  self.sceneManager.createManualObject("manual"+idstr)
			if options == "i":
				mat = "TruckEditor/ShockInvisible"
			else:
				mat = "TruckEditor/ShockNormal"
			line.begin(mat, ogre.RenderOperation.OT_LINE_LIST)
			line.position(pos1)
			line.position(pos2)
			line.end()
			line.setCastShadows(False)
			linenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
			linenode.attachObject(line)
			self.shocks[id0] = [linenode, id1, id2, options, line]
		except:
			pass

	def createSubMeshGroup(self, tree, smg, smgid):
		#print smg
		try:
			# read in nodes
			nodes = {}
			for nodeobj in tree['nodes']:
				if nodeobj.has_key('type'):
					continue
				node = nodeobj['data']
				nodes[int(node[0])] = ogre.Vector3(float(node[1]),float(node[2]),float(node[3]))

			# read in UVs then
			uv = {}
			for data in smg['texcoords']:
				tex = data['data']
				uv[int(tex[0])] = [float(tex[1]), float(tex[2])]

			# and create the triangles

			#print tree['globals'][0]['data'][2]
			matname = tree['globals'][0]['data'][2]
			#print matname

			idstr = str(smgid)
			sm = self.sceneManager.createManualObject("manualsmg"+idstr)
			sm.begin(matname, ogre.RenderOperation.OT_TRIANGLE_LIST)

			for data in smg['cab']:
				cab = data['data']
				if len(cab) == 0:
					continue
				#print nodes, cab
				sm.position(nodes[int(cab[0])])
				sm.textureCoord(uv[int(cab[0])][0], uv[int(cab[0])][1])
				sm.position(nodes[int(cab[1])])
				sm.textureCoord(uv[int(cab[1])][0], uv[int(cab[1])][1])
				sm.position(nodes[int(cab[2])])
				sm.textureCoord(uv[int(cab[2])][0], uv[int(cab[2])][1])
			sm.end()
			sm.setCastShadows(False)

			# set culling mode for that material
			mat = ogre.MaterialManager.getSingleton().getByName(matname)
			if not mat is None:
				mat.setCullingMode(Ogre.CullingMode.CULL_NONE)

			smnode = self.sceneManager.getRootSceneNode().createChildSceneNode()
			smnode.attachObject(sm)

			self.submeshs[smgid] = [smnode, smgid, smg, sm]
		except:
			pass

	def makeSimpleBox( self, size, pos,  orient ):
		## base mass on the size of the object.
		mass = size.x * size.y * size.z * 2.5

		## calculate the inertia based on box formula and mass
		inertia = OgreNewt.CalcBoxSolid( mass, size )

		box1 = self.sceneManager.createEntity("Entity"+str(self.EntityCount), "cap_mid.mesh" )
		self.clearlist['entity'].append("Entity"+str(self.EntityCount))

		self.EntityCount += 1
		box1node = self.sceneManager.getRootSceneNode().createChildSceneNode()
		box1node.attachObject( box1 )
		box1node.setScale( size )
		box1.setNormaliseNormals(True)

		col = OgreNewt.Box( self.World, size )
		bod = OgreNewt.Body( self.World, col )
		del col

		bod.attachToNode( box1node )
		bod.setMassMatrix( mass, inertia )
		bod.setStandardForceCallback()

		box1.setMaterialName( "mysimple/terrainselect" )
		box1.setCastShadows(False)

		bod.setPositionOrientation( pos, orient )

		return bod


	def populateScene(self):
		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )

		fadeColour = (0.8, 0.8, 0.8)
		self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002)
		#self.sceneManager.setFog(ogre.FOG_LINEAR, fadeColour, 0.001, 5000.0, 10000.0)
		self.renderWindow.getViewport(0).BackgroundColour = fadeColour

		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )
		self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
		self.sceneManager.setSkyDome(True, 'mysimple/truckEditorSky', 4.0, 8.0)

		self.MainLight = self.sceneManager.createLight('MainLight')
		self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

		self.createGroundPlane()

		stat_col = OgreNewt.TreeCollisionSceneParser( self.World )
		stat_col.parseScene( self.planenode, True )
		bod = OgreNewt.Body( self.World, stat_col )
		self.bodies.append(bod)
		del stat_col

	def createTestRope(self):
		## make a simple rope.
		size = Ogre.Vector3(5,0.5,0.5)
		pos = Ogre.Vector3(0,20,0)
		orient = Ogre.Quaternion.IDENTITY

		## loop through, making bodies and connecting them.
		parent = None
		child = None

		for x in range (5):
			## make the next box.
			child = self.makeSimpleBox(size, pos, orient)
			self.bodies.append(child)

			## make the joint right between the bodies...
			if (parent):
				joint = OgreNewt.BallAndSocket( self.World, child, parent, pos-Ogre.Vector3(size.x/2,0,0) )

			else:
				## no parent, this is the first joint, so just pass NULL as the parent, to stick it to the "world"
				joint = OgreNewt.BallAndSocket( self.World, child, None, pos-Ogre.Vector3(size.x/2,0,0) )

			## offset pos a little more.
			pos += Ogre.Vector3(size.x,0,0)

			## save the last body for the next loop!
			parent = child

			## NOW - we also have to kepe copies of the joints, otherwise they get deleted !!!
			self.bodies.append (joint)

	def createGroundPlane(self):
		plane = ogre.Plane()
		plane.normal = ogre.Vector3(0, 1, 0)
		plane.d = 2
		planesize = 200000
		# see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
		mesh = ogre.MeshManager.getSingleton().createPlane('GroundPlane', "General", plane, planesize, planesize,
													20, 20, True, 1, 50.0, 50.0, ogre.Vector3(0, 0, 1),
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													True, True)
		entity = self.sceneManager.createEntity('groundent', 'GroundPlane')
		entity.setMaterialName('mysimple/truckEditorGround')
		self.planenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
		self.planenode.attachObject(entity)

		#col = OgreNewt.TreeCollision(self.World, self.planenode, True)
		groundthickness = 50
		boxsize = ogre.Vector3(planesize, groundthickness, planesize)
		col = OgreNewt.Box(self.World, boxsize )
		bod = OgreNewt.Body( self.World, col )
		self.bodies.append(bod)
		bod.setPositionOrientation( Ogre.Vector3(0.0, -groundthickness - plane.d, 0.0), Ogre.Quaternion.IDENTITY )
		del col


	def LoadTruck(self, fn):
		if not os.path.isfile(fn):
			print "truck file not found: "+fn
			return
		self.filename = fn
		truckname = os.path.basename(fn)
		p = rorparser()
		p.parse(fn)
		if not 'nodes' in p.tree.keys() or not 'beams' in p.tree.keys() :
			return False

		self.initScene()
		self.CreateTruck(p.tree)
		self.createTestRope()
		return p.tree


	def reLoadTruck(self):
		if not os.path.isfile(self.filename):
			return
		p = rorparser()
		p.parse(self.filename)
		if not 'nodes' in p.tree.keys() or not 'beams' in p.tree.keys() :
			return False

		self.initScene(resetCam=False)
		self.CreateTruck(p.tree)

	def CreateTruck(self, tree):
		try:
			nodes = {}
			for nodeobj in tree['nodes']:
				if nodeobj.has_key('type'):
					continue
				node = nodeobj['data']
				nodes[int(node[0])] = ogre.Vector3(float(node[1]),float(node[2]),float(node[3]))
				self.createNode(node)


			beamcounter = 0
			for beamobj in tree['beams']:
				if beamobj.has_key('type'):
					continue
				#print beamobj
				beam = beamobj['data']
				#print beam
				if len(beam) == 3:
					option = beam[2]
				else:
					option = None
				#print beam
				try:
					self.createBeam(beamcounter, int(beam[0]),int(beam[1]), option)
					beamcounter += 1
				except:
					pass


			if 'shocks' in tree.keys():
				shockcounter = 0
				for shockobj in tree['shocks']:
					if shockobj.has_key('type'):
						continue
					shock = shockobj['data']
					if len(shock) == 8:
						option = shock[7]
					else:
						option = None
					#print beam
					try:
						self.createShock(shockcounter, int(shock[0]),int(shock[1]), option)
					except:
						pass
					shockcounter += 1

			smgcounter = 0
			for smg in tree['submeshgroups']:
				print "loading submesh: ", smgcounter
				self.createSubMeshGroup(tree, smg,smgcounter)
				smgcounter += 1

			from UVFrame import *
			self.uvFrame = UVFrame(self, wx.ID_ANY, "")
			self.uvFrame.setTree(tree)
			self.uvFrame.Show()
		except:
			pass

	def onMouseEvent(self,event):
		width, height, a, b, c = self.renderWindow.getMetrics()

		# if event.MiddleDown():
			# self.StartDragX, self.StartDragY = event.GetPosition()

		# if event.Dragging() and event.MiddleDown():
			# if not self.selection is None:
				# n = self.mainWindow.mSelected.getParentNode()
				# pos = n.getPosition()
			# else:
				# pos = Ogre.Vector3(0, 20, 0)
			# self.camera.lookAt(pos)
			# mx,my = event.GetPosition()
			# mx = self.StartDragX - mx
			# alpha = (math.pi / 720) * mx
			# dx = math.cos(alpha) * self.radius
			# dy = math.sin(alpha) * self.radius
			# self.camera.setPosition(pos - ogre.Vector3(dx, -5, dy))

		mode = self.camera.getProjectionType() == Ogre.ProjectionType.PT_PERSPECTIVE
		if mode:
			if event.RightDown(): #Precedes dragging
				self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click
			if event.GetWheelRotation() != 0:
				zfactor = 0.001
				if event.ShiftDown():
					zfactor = 0.01
				zoom = zfactor * -event.GetWheelRotation()
				self.camera.moveRelative(ogre.Vector3(0,0, zoom))

			"""
			# new cam code:
			if event.Dragging() and event.RightIsDown():
				x,y = event.GetPosition()

				dx = self.StartDragX - x
				dy = self.StartDragY - y
				self.StartDragX, self.StartDragY = x, y
				if event.ShiftDown():
					dx = float(dx) / 10
					dy = float(dy) / 10
				self.camera2.move(ogre.Vector3(dx,dy,0), event.ControlDown())
			"""

			# old cam code:
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

			if event.LeftDown() and event.ControlDown() and not self.mSelected is None:
				pos = self.getPointedPosition(event)
				if not pos is None:
					self.TranslateNode.setPosition(pos)
					self.RotateNode.setPosition(pos)
					self.mSelected.getParentNode().setPosition(pos)
				return
			if event.LeftDown():
				#self.selectnew(event)
				self.StartDragLeftX, self.StartDragLeftY = event.GetPosition() #saves position of initial click
				zfactor = 0.1
				if event.ShiftDown():
					zfactor = 5
				zoom = zfactor * -event.GetWheelRotation()
				self.camera.moveRelative(ogre.Vector3(0,0, zoom))
		else:
			if event.GetWheelRotation() != 0:
				zfactor = 0.001
				if event.ShiftDown():
					zfactor = 0.01
				zoom = zfactor * -event.GetWheelRotation()
				if self.camera.getNearClipDistance() + zoom > 0:
					self.camera.setNearClipDistance(self.camera.getNearClipDistance() + zoom)

			if event.RightDown():
				self.StartDragX, self.StartDragY = event.GetPosition()
			if event.Dragging() and event.RightIsDown():
				x,y = event.GetPosition()
				dx = self.StartDragX - x
				dy = self.StartDragY - y
				self.StartDragX, self.StartDragY = x, y
				if event.ShiftDown():
					dx = float(dx) / 30
					dy = float(dy) / 30
				else:
					dx = float(dx) / 60
					dy = float(dy) / 60
				self.camera.moveRelative(ogre.Vector3(dx,-dy,0))
		event.Skip()

	def changeDisplayMode(self, mode):

		if mode == self.camMode:
			pass

		#save settings
		self.modeSettings[self.camMode] = [self.camera.getPosition(), self.camera.getOrientation(), self.camera.getNearClipDistance()]

		cammode = self.camera.getProjectionType() == Ogre.ProjectionType.PT_PERSPECTIVE
		if mode in self.modeSettings.keys():
			# restore settings
			self.camera.setPosition(self.modeSettings[mode][0])
			self.camera.setOrientation(self.modeSettings[mode][1])
			self.camera.setNearClipDistance(self.modeSettings[mode][2])

		if mode == "3d":
			if not cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_PERSPECTIVE)
			if not mode in self.modeSettings.keys():
				# set default settings
				self.camera.setNearClipDistance(0.1)
				self.camera.setPosition(Ogre.Vector3(0,0,1))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		elif mode == "orthleft":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(5)
				self.camera.setPosition(Ogre.Vector3(0,0,100))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		elif mode == "orthright":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(5)
				self.camera.setPosition(Ogre.Vector3(0,0,-100))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		elif mode == "orthrear":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(5)
				self.camera.setPosition(Ogre.Vector3(100,0,0))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		elif mode == "orthfront":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(5)
				self.camera.setPosition(Ogre.Vector3(-100,0,0))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		elif mode == "orthtop":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(5)
				self.camera.setPosition(Ogre.Vector3(0.1,100,0))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		elif mode == "orthbottom":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(5)
				self.camera.setPosition(Ogre.Vector3(0.1,-100,0))
				self.camera.lookAt(Ogre.Vector3(0,0,0))

		self.camMode = mode

	def onKeyDown(self,event):
		#print event.m_keyCode
		d = 0.05
		if event.ShiftDown():
			d = 0.5
		mode = self.camera.getProjectionType() == Ogre.ProjectionType.PT_PERSPECTIVE
		if mode:
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
			elif event.m_keyCode == 81: # Q, wx.WXK_LEFT:
				self.enablephysics = not self.enablephysics
		else:
			if event.m_keyCode == 65: # A, wx.WXK_LEFT:
				self.camera.moveRelative(ogre.Vector3(-d,0,0))
			elif event.m_keyCode == 68: # D, wx.WXK_RIGHT:
				self.camera.moveRelative(ogre.Vector3(d,0,0))
			elif event.m_keyCode == 87: # W ,wx.WXK_UP:
				self.camera.moveRelative(ogre.Vector3(0,d,0))
			elif event.m_keyCode == 83: # S, wx.WXK_DOWN:
				self.camera.moveRelative(ogre.Vector3(0,-d,0))



		if event.m_keyCode == 340: # F1
			self.changeDisplayMode("3d")
		elif event.m_keyCode == 341: # F2
			self.changeDisplayMode("orthleft")
		elif event.m_keyCode == 342: # F3
			self.changeDisplayMode("orthright")
		elif event.m_keyCode == 343: # F4
			self.changeDisplayMode("orthfront")
		elif event.m_keyCode == 344: # F5
			self.changeDisplayMode("orthrear")
		elif event.m_keyCode == 345: # F6
			self.changeDisplayMode("orthtop")
		elif event.m_keyCode == 346: # F7
			self.changeDisplayMode("orthbottom")
		event.Skip()