#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
#Lepes continue his work after 1/08/08

#TODO:
# layer manager
# propper selection tool
# p3d movement with keyboard is currently sick

import wx, os, os.path, wx.lib
import ogre.renderer.OGRE as ogre
from ror.truckparser import *

#from ror.camera import *
from math import pi, sqrt
from ror.logger import log
from ror.settingsManager import rorSettings

from ror.rorcommon import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *

import ogre.renderer.OGRE as Ogre
import ogre.io.OIS as OIS
from RoRVirtualKeys import *
from RoRTerrainSelection import *
from SelectionAxis import *
from ror.lputils import showedError
from rorNotepad import *

import RoRConstants
from pickle import TRUE

#from random import random



class RoRTruckOgreWindow(wxOgre3D):
	def __init__(self, parent, ID, size=wx.Size(200, 200), **kwargs):
		self.parent = parent
		self.rordir = rorSettings().rorFolder
		self.sceneManager = None
		#self.uvFrame = None
		self.clearlist = {'entity':[]}
		self._autoTracking = False
		wxOgre3D.__init__(self, parent, ID, "truck", size=size, **kwargs)
		self.initScene() #minimal initialization
		self.autoCreateBeam = False



	def initScene(self, resetCam=True):
		# reset variables that could be deleted by clearScene
		# use createBasicObjects to initialize variables instead of here :-|

		self.EntityCount = 0

		self.nodeCount = -1
		self.beams = {}
		self.shocks = {}
		self.submeshs = {}
		self.nodepos = []
		self.selection = None
		self.entries = {}
		self.notepad = None
		self.lastnodes = [0, 0, 0, 0] #to criss-cross
		self.lastnodeidx = 3
		self._gridSize = 0.5
		self.StartDragLeftX = 0
		self.StartDragLeftY = 0
		self.highlitLevel = 0
		self.wasDragging = False
		self.activeAnim = []
		self.movingEntry = False
		self.rotatingEntry = False
		self.ShiftIsDown = False
		opt = rorSettings().getSetting(TRUCKEDITOR, 'beam_diameter')
		if opt != '': RoRConstants.BEAM_DIAMETER = float(opt)
		opt = rorSettings().getSetting(TRUCKEDITOR, 'node_numbers')
		if opt != '': RoRConstants.NODE_NUMBERS = float(opt)
		opt = rorSettings().getSetting(TRUCKEDITOR, 'dot_scale')
		if opt != '': RoRConstants.DOT_SCALE = float(opt)

		RoRConstants.BEAM_DIAMETER = min(RoRConstants.BEAM_DIAMETER, 0.9)
		RoRConstants.NODE_NUMBERS = min(RoRConstants.NODE_NUMBERS, 4.0)
		RoRConstants.DOT_SCALE = min(RoRConstants.DOT_SCALE, 4.0)
		self.visited = []

		self.enablephysics = False
		if resetCam:
			self.modeSettings = {}
			self.camMode = "3d"

	def clearScene(self):
		if self.sceneManager is not None:
			#using clearScene forces to recreate all object based on nodes and entities
			if hasattr(self, 'selected'): 	del self.selected
			if hasattr(self, 'axis'):		del self.axis
			if hasattr(self, 'planenode'):	del self.planenode
			if hasattr(self, 'p3d'):		del self.p3d
			if hasattr(self, 'terrainAxis'):del self.terrainAxis
			if self.notepad is not None:
				self.notepad.Destroy()
				del self.parser
				self.notepad = None
				self.parser = None
			self.initScene(False) #delete content of variables
			self.sceneManager.clearScene()


	def close(self):
		rorSettings().setSetting(TRUCKEDITOR, 'beam_diameter', RoRConstants.BEAM_DIAMETER)
		rorSettings().setSetting(TRUCKEDITOR, 'node_numbers', RoRConstants.NODE_NUMBERS)
		rorSettings().setSetting(TRUCKEDITOR, 'dot_scale', RoRConstants.DOT_SCALE)

		self.clearScene()

	def OnFrameStarted(self):
		pass

	def OnFrameEnded(self):
		pass

	def SceneInitialisation(self):
		initResources()

		#get the scenemanager
		if self.sceneManager is None:
			self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

		# create a camera
		self.camera = self.sceneManager.createCamera('Camera')
		self.camera.lookAt(ogre.Vector3(0, 0, 0))
		self.camera.setPosition(ogre.Vector3(3, 2, 5))
		self.camera.nearClipDistance = 0.1
		self.camera.setAutoAspectRatio(True)

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

	def updateEntryPos(self, entry, tuplepos):
		entry.ogrePosition = ogre.Vector3(tuplepos[0], tuplepos[1], tuplepos[2])

	def selectingEntry(self, entry):
		""" when an object is selected this event is triggered
		"""
#		log().debug('entering entry changed')
		if hasattr(entry, 'lineTruck'):
			if entry.lineTruck.section == 'nodes':
				self.lastnodeidx = (self.lastnodeidx + 1) % 4
				self.lastnodes[self.lastnodeidx] = entry.lineTruck.id
		self.positionUpdating(entry)

	def rotationUpdated(self, entry):
		""" called when finished a rotation on a 'prop'
		"""
		# I don't know weather it is a mesh, a wheelmesh or what.
		#FIXME: UPPS
		pass
	def positionUpdating(self, entry):
		""" called everytime an entry is moved
		"""
		p = None
		if entry is not None and hasattr(entry, 'lineTruck') and entry.lineTruck.section == 'nodes': #only nodes and p3d should be updated
			p = entry.ogrePosition
			entry.lineTruck.x = p.x
			entry.lineTruck.y = p.y
			entry.lineTruck.z = p.z
			if len(entry.links) > 0:
				self.updateLinks(entry)
		elif entry is None:
			entry = self.selected.entry
			if entry: p = entry.node.getPosition()

		msg = ["", "", "", ""]
		msg[0] = "GridSize: %.3f" % self.gridSize
		if p is not None:
			msg[1] = "pos: %.3f, %.3f, %.3f" % (p.x, p.y, p.z)
			reldist = p - self.p3d.ogrePosition
			msg[2] = "dist: %.3f, %.3f, %.3f Len: %.3f" % (reldist.x, reldist.y, reldist.z, reldist.length())
		self.parent.updateStatusBar(msg)
	def updateLinks(self, entry):
		""" entry has lineTruck and it is a node
		"""
		for beam in entry.links:
			pos0 = self.parser.findNode(beam.lineTruck.first_node).entry.ogrePosition
			pos1 = self.parser.findNode(beam.lineTruck.second_node).entry.ogrePosition

			midPoint = pos0.midPoint(pos1)
			dist = pos0.distance(pos1)

			beam.node.setPosition(midPoint) #box node on world dimension
			beam.node.lookAt(pos1, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(0, 0, 1))
			beam.node.lookAt(pos1, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(1, 0, 0))
			beam.node.setScale(RoRConstants.BEAM_DIAMETER, dist, RoRConstants.BEAM_DIAMETER)
			beam.node.roll(ogre.Degree(90), ogre.Node.TransformSpace.TS_LOCAL)

	def createBasicObjects(self):
		""" create environment scene:
			Axis
			selected
			p3d
			walls
		"""
		self.axis = AxisClass(self, ['translation', 'rotation'])
		self.axis.arrowScaleFactor = 0.1
		self.axis.entryShow.append('translation')
		self.axis.entryShow.append('rotation')
		self.axis.selectTerrain((0.25, 0.25, 0.25))
		self.selected = selectionClass(self)


		self.p3d = self.newEntryEx("torus.mesh", "mysimple/terrainselect", False, True)
		self.p3d.node.setScale(0.01, 0.01, 0.01)

		self.terrainAxis = AxisClass(self, ['translation']) # to see the origin of the map
		self.terrainAxis.entryShow = ['translation']
		self.terrainAxis.arrowScaleFactor = 0.01
		self.terrainAxis.attachTo(self.smNewNode(randomID()))

		self.node0 = self.smNewNode(randomID())
		self.createGroundPlane()
#		self.createWalls()

	def getautoTracking(self):
		return self._autoTracking

	def setautoTracking(self, value):
		if value is None:
			self.camera.setAutoTracking(False, self.node0)
		else:
			if self.selected.entry is not None:
				self.camera.setAutoTracking(value, self.selected.entry.node)
				self.showOverlay('POCore/autotrack', value)
			else:
				self.camera.setAutoTracking(value, self.node0)
				self.showOverlay('POCore/autotrack', False)


	autoTracking = property(getautoTracking, setautoTracking,
				 doc=""" center selected object in screen and
						  WASD keys rotate around the selected object
						  instead of freedom walking.
						  It's a toggle option. """)


	def createNodeFrom(self, x=0, y=0, z=0, options='n', mass=20, inlineComment=None):
		l = lineOfSection()
		l.parent = self.parser
		l.setSection('nodes')

		l.x = x
		l.y = y
		l.z = z
		l.options = options
		if inlineComment is not None:
			l.inlineComment = inlineComment
		idx = self.parser.sectionEnd('nodes')
		if idx == -1 : raise Exception('error not found nodes section ends')
		self.notepad.grid.insertSection(l, idx)
		return self.createNode(l)

	def isNodeAt(self, vector3):
		"""
		is a node at this position yet??
		return None or the entry found

		"""
		#FIXME:when a node is moved, it is not reflected here :s
		for e in self.nodepos:
			if vector3.positionEquals(e[0]): #the vector3 where nodes are
				return e[1] #the entry
		return None
	def getMaterial(self, lineTruck):
		""" return the material name for the 'options' property

		this is not good, user can not setup colors :-( but we could use fancy materials
		"""
		#value for any error
		matname = 'TruckEditor/AnimNode'
		if lineTruck.section == 'nodes':
			if lineTruck.options is None:
				matname = "TruckEditor/NodeNormal"
				lineTruck.options = "n"
			elif 'l' in lineTruck.options:
				matname = "TruckEditor/NodeLoad"
			elif 'f' in lineTruck.options:
				matname = "TruckEditor/NodeFriction"
			elif 'x' in lineTruck.options:
				matname = "TruckEditor/NodeExhaust"
			elif 'y' in lineTruck.options:
				matname = "TruckEditor/NodeExhaustReference"
			elif 'c' in lineTruck.options:
				matname = "TruckEditor/NodeContact"
			elif 'h'  in lineTruck.options:
				matname = "TruckEditor/NodeHook"
			else:
				matname = "TruckEditor/NodeNormal"

		elif lineTruck.section in ['commands', 'commands2']:
			 matname = 'TruckEditor/commands'

		elif lineTruck.section == 'beams':
			if lineTruck.options is None:
				matname = "tracks/beam"
				lineTruck.options = 'n'
			elif "i" in lineTruck.options:
				matname = "TruckEditor/BeamInvisible"
			elif "r" in lineTruck.options:
				matname = "TruckEditor/BeamRope"
			else:
				matname = "tracks/beam" # "TruckEditor/BeamNormal"
		elif lineTruck.section in ['shocks', 'shocks2']:
			if lineTruck.options is None:
				matname = 'TruckEditor/ShockNormal'

			elif 'i' in lineTruck.options:
				matname = 'TruckEditor/ShockInvisible'
			else:
				matname = 'TruckEditor/ShockNormal'
		elif lineTruck.section == 'hydros':
			matname = 'TruckEditor/BeamHydros' # huh??

#		log().debug("section: %s will use materialname: %s for line of truck %s" % (lineTruck.section, matname, lineTruck.getTruckLine()))
		return matname

	class highLighter:
		""" highlight a node/beam based on the entry and hightlight recursively level
		"""
		def __init__(self, parent, entry=None, level= -1, bAnimate=True):
			self.visited = []
			""" entry to animate
			recursiving level
			Animate true/false
			"""
			self.visited = []
			self.level = level
			self.parent = parent
			if entry is not None:
				self.highlight(entry, bAnimate)

		def highlight(self, entry, bAnimate):
			self.visited = []
			self.highlightConnected(entry.lineTruck, bAnimate)
			self.visited = []

		def highlightConnected(self, lineTruck, bAnimate=True):
			""" animate all nodes and beams connected to this entry
			obj maybe a lineTruck or entry
			"""
			self.parent.anim(lineTruck, bAnimate)
			if hasattr(lineTruck, 'entry'):
				self.visited.append(lineTruck.entry)
				if hasattr(lineTruck.entry, 'links'):
					if self.level > 0:
						for v in lineTruck.entry.links: # a beam is connected to 2 nodes. 1 node is connected to lot of beams
							if not v in self.visited:
								self.parent.anim(v, bAnimate)
	#								if v.lineTruck.section in BEAMS:
								self.level -= 1
								self.highlightConnected(v.lineTruck, bAnimate) # animate second node of this beam
								self.level += 1 # when a beam is hightligted, two nodes must be hightlited too

			else: "section %s has not an entry property" % lineTruck.section



	def anim(self, obj, bAnimate=True):
		""" animate a single entry or lineTruck

		obj is a lineTruck or entry
		bAnimate True/False
		"""
		e = None
		if isinstance(obj, simpleEntryClass):
			e = obj
		elif isinstance(obj, lineOfSection):
			if not hasattr(obj, 'entry'):
				return
			e = obj.entry
		else: log().debug('not supported object to animate')
		if bAnimate and e is not None:
			e.entity.setMaterialName('TruckEditor/NodeAnim')
			self.activeAnim.append(e)
		elif e is not None and hasattr(e, 'lineTruck') and e.lineTruck is not None:
			e.entity.setMaterialName(self.getMaterial(e.lineTruck))
	def clearAnim(self):
		for x in self.activeAnim:
			self.anim(x, False)
		self.activeAnim = []
	def animNodes(self, lineTruck, bAnimate):
		""" animate all nodes and beams for the current lineTruck
		"""
		coldef = self.parser.sectionDef(lineTruck.section)
		if lineTruck.section in BEAMS:
			self.anim(lineTruck, bAnimate)
		cameraLookPos = None #center the camera point of view to midPoint of all nodes
		for col in coldef:
			if col['type'] == 'node':
				nodeNum = lineTruck.getColValue(col['name'])
				if nodeNum is not None:
					objnode = self.parser.findNode(nodeNum)
					if objnode is not None:
						if bAnimate:
							if cameraLookPos is None: cameraLookPos = objnode.entry.node.getPosition()
							else: cameraLookPos = cameraLookPos.midPoint(objnode.entry.node.getPosition())
							objnode.entry.entity.setMaterialName('TruckEditor/NodeAnim')
							self.activeAnim.append(objnode.entry)
						else:
							objnode.entry.entity.setMaterialName(self.getMaterial(objnode))
		if cameraLookPos is not None and bAnimate:
			self.camera.lookAt(cameraLookPos)

	def createNode(self, node):
		""" receives a lineOfSection object
		"""
		try:
			matname = self.getMaterial(node)
			if node.x is None or node.y is None or node.z is None:
				log().debug("node not created, some coordenate is null")
				return None
			dot = self.createDotAt(node.x, node.y, node.z, matname)
#			print "node at", node.x, node.y, node.z

			setattr(dot, 'lineTruck', node)
			setattr(dot.lineTruck, 'entry', dot)
			node.entry = dot
			self.nodeCount += 1
			dot.lineTruck.id = self.nodeCount
			dot.links = [] #beams attached to this node
			mystr = str(node.id)
			nNumber = dot.node.createChildSceneNode(str(randomID()), ogre.Vector3(0, RoRConstants.NODE_NUMBERS , 0))
			number = {'0':'zero', '1':'one', '2':'two', '3':'trhee', '4':'four', '5':'five', '6':'six', '7':'seven', '8':'eight', '9':'nine'}
			for i in range(len(mystr)):
				if number.has_key(mystr[i]):
					subn = nNumber.createChildSceneNode(str(randomID()), ogre.Vector3(0.5 * i, 0, 0))
					sube = self.smNewEntity(str(randomID()), "%s.mesh" % number[mystr[i]], CLYELLOW)
					subn.attachObject(sube)
			setattr(dot, 'nodeNumber', nNumber)
			if self.isNodeAt(dot.ogrePosition):
				dot.node.yaw(ogre.Degree(30))
			self.nodepos.append([dot.node.getPosition(), dot])
			dot.allowTranslation = True
			dot.OnPositionChanging.append(self.positionUpdating)

			return dot
		except Exception, e:
			log().debug("error creating nodes: " + str(e) + " / " + str(e.__doc__))
#			raise

	def showSubmeshs(self, value):
		for k in self.submeshs.keys():
			submesh = self.submeshs[k]
			submesh[0].setVisible(value)

	def setSubmeshMode(self, mode):
		pass


	def showExhaustRefNodes(self, value):
		self.visibleOption('nodes', 'y', value)

	def showExhaustNodes(self, value):
		self.visibleOption('nodes', 'x', value)

	def showHookNodes(self, value):
		self.visibleOption('nodes', 'h', value)

	def showFrictionNodes(self, value):
		self.visibleOption('nodes', 'f', value)

	def showContactNodes(self, value):
		self.visibleOption('nodes', 'c', value)

	def showFrictionNodes(self, value):
		self.visibleOption('nodes', 'f', value)
	def showLoadNodes(self, value):
		self.visibleOption('nodes', 'l', value)
	def showNormalNodes(self, value):
		self.visibleOption('nodes', 'n', value)
	def showNormalBeams(self, value):
		self.visibleOption('beams', 'n', value)
		self.visibleOption('beams', 'v', value)
	def showInvisibleBeams(self, value):
		self.visibleOption('beams', 'i', value)
	def showRopeBeams(self, value):
		self.visibleOption('beams', 'r', value)
	def hideProps(self, value):
		self.visibleOption(['flexbodies', 'props'], None, value)

	def visibleOption(self, section, option=None, value=True):
		""" check the 'options' property to make it visible or not
		"""
		if isinstance(section, StringType):
			secList = [section]
		elif isinstance(section, ListType):
			secList = section
		else: raise Exception('needs a list or string')

		for e in self.entries.keys():
			if hasattr(self.entries[e], 'lineTruck'):
				if self.entries[e].lineTruck.section in secList:
					if option is None:
						self.entries[e].visible = value
					elif option in self.entries[e].lineTruck.options:
						self.entries[e].visible = value
						if hasattr(self.entries[e], 'nodeNumber'):
							if self.entries[e].entity.getVisible():
								self.entries[e].nodeNumber.setPosition(0, RoRConstants.NODE_NUMBERS , 0)
							else:
								self.entries[e].nodeNumber.setPosition(0, 0.1, 0.1)
							self.entries[e].nodeNumber.setVisible(value)

	def visibleBeams(self, value=True):
		for e in self.entries:
			if hasattr(e, 'lineTruck'):
				if e.lineTruck.section == 'beams':
					e.visible = value
	def visibleNodeNumbers(self, value):
		for e in self.entries.keys():
			if hasattr(self.entries[e], 'lineTruck'):
				if self.entries[e].lineTruck.section == 'nodes':
						if hasattr(self.entries[e], 'nodeNumber'):
							if self.entries[e].entity.getVisible():
								self.entries[e].nodeNumber.setPosition(0, RoRConstants.NODE_NUMBERS, 0)
							else:
								self.entries[e].nodeNumber.setPosition(0, 0.1, 0.1)
							self.entries[e].nodeNumber.setVisible(value)

	def createBeamFrom(self, node1=0, node2=0, options='n', inlineComment=None):
		l = lineOfSection()
		l.parent = self.parser
		l.setSection('beams')
		l.first_node = node1
		l.second_node = node2
		l.options = options
		if inlineComment is not None:
			l.inlineComment = inlineComment
		idx = self.parser.sectionEnd('beams')
		if idx == -1 : raise Exception('error not found beams section ends')
		self.notepad.grid.insertSection(l, idx)

		return self.createBeam(l)

	def createShockFrom(self, node1=0, node2=0, options=''):
		l = lineOfSection()
		l.parent = self.parser
		l.setSection('shocks')
		l.first_node = node1
		l.second_node = node2
		l.options = options
		idx = self.parser.sectionEnd('shocks')
		if idx == -1 : raise Exception('error not found shocks section ends')
		self.notepad.grid.insertSection(l, idx)

		return self.createShock(l)

	def createCommandFrom(self, node1=0, node2=0):
		l = lineOfSection()
		l.parent = self.parser
		l.setSection('commands')
		l.first_node = node1
		l.second_node = node2
#		l.options = options
		idx = self.parser.sectionEnd('commands')
		if idx == -1 : raise Exception('error not found command section ends')
		self.notepad.grid.insertSection(l, idx)
		return createCommand(l)

	def createCommand(self, obj):
		return self.createBeam(obj)

	def deleteLine(self, obj):
		""" delete a line of section
		- remove 3D objects
		- remove parser.lines object
		- remove links on linked objects
		"""

		pos = self.parser.lines.index(obj)
		sections = ""
		if obj.section == 'nodes':
			#deleting a node must renumber all node number
			id = obj.id
			self.nodeCount -= 1
			for i in range(pos + 1, len(self.parser.lines)):
				l = self.parser.lines[i]
				secdef = l.getDefinition()
				for col in range(0, l.getMaxCols()):
					coldef = l.getDefinition(col)
					if coldef is not None and coldef['type'] == 'node':
						value = l.getColValue(col)
						if value > id and value != 9999 :
							setattr(l, l.getColName(col), value - 1)
						elif value == id:
							if not l.section in BEAMS:
								setattr(l, l.getColName(col), -1)
								log().debug('node to be deleted number: %d was used on section %s at column name %s, changed to "-1"' % (id, l.section, l.getColName(col)))
							sections += l.section + '\n'
		#elif self.parser.lines[pos].section in BEAMS: #beam hydro etc must be removed :(
		self.selected.entry = None #remove selection since it is the actual node
		if hasattr(obj, 'entry') and obj.entry is not None:
			entry = self.entries.pop(str(obj.entry.uuid))
			if obj.section == 'nodes': # used for isNodeAt
				for i in range (len(self.nodepos)):
					if entry == self.nodepos[i][1]:
						del self.nodepos[i]
						break
			self.removeLink(entry)
			entry.lineTruck = None #dec ref count
			entry.links = []
			entry.OnPositionChanging = []
			entry.removeFromScene()  #FIXME: it has child nodes not deleted
			del entry
		self.parser.deleteLine(obj)
		if sections != "":
			log().debug('deleted node was used \non these sections (it is now "-1")' + sections + '\n\n You should save and reload the truck when you\n finish deleting things')

	def removeLink(self, entry):
		""" remove self link to the other entries linked to this entry
		"""
		if len(entry.links) > 0:
			if entry.lineTruck.section in BEAMS:
				# I am a beam that is been deleted, just remove pointers to the nodes attached to me
				for i in range(len(entry.links)):
					try:
						entry.links[i].links.remove(entry)
					except ValueError:
						pass
			elif entry.lineTruck.section == 'nodes':  #a group of beam/shock/etc are connected to this node, deleting node, it also must delete the beam
				for i in range(len(entry.links) - 1, 0, -1):
					 if entry.links[i].lineTruck is not None: # this was deleted yet
					 	self.deleteLine(entry.links[i].lineTruck)

	def createBeam(self, obj):
		""" create a any kind of beam and add links"""
#		search RoR source code "beam.mesh
		try:
			if obj.first_node is None or obj.second_node is None: return

			first = self.parser.findNode(obj.first_node)
			if first is None:
				log().debug("a Beam doesn't been created because first node doesn't exists, meshwheels??")
				return
			first = first.entry
			second = self.parser.findNode(obj.second_node)
			if second is None:
				log().debug("a Beam doesn't been created because first node doesn't exists, meshwheels??")
				return
			second = second.entry
			beam = self.createBox(first.ogrePosition, second.ogrePosition, True, self.getMaterial(obj))
			setattr(beam, 'lineTruck', obj)
			setattr(beam.lineTruck, 'entry', beam)
			first.links.append(beam)
			second.links.append(beam)
			beam.links.append(first)
			beam.links.append(second)
			return beam
		except Exception, e:
			log().debug("error creating beam: " + str(e) + " / " + str(e.__doc__) + " for obj: " + obj.section + "  " + obj.getTruckLine())
			raise

	def createBox(self, pos0, pos1, addToEntries=False, matname='tracks / beam'):
		"""
		pos0 - Vector3
		pos1 - Vector3
		AddtoEntries - bool
		material name - string
		"""
		entry = self.newEntryEx("beam.mesh", matname, True, addToEntries)
		entry.links = []
		midPoint = pos0.midPoint(pos1)

		dist = pos0.distance(pos1)

		entry.node.setPosition(midPoint) #box node on world dimension
		entry.node.lookAt(pos1, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(0, 0, 1))
		entry.node.lookAt(pos1, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(1, 0, 0))
		entry.node.setScale(RoRConstants.BEAM_DIAMETER, dist, RoRConstants.BEAM_DIAMETER)
		entry.node.roll(ogre.Degree(90), ogre.Node.TransformSpace.TS_LOCAL)


		return entry

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


	def createShock(self, obj):
		try:
			if obj.first_node is None or obj.second_node is None: return

			f = self.parser.findNode(obj.first_node).entry
			s = self.parser.findNode(obj.second_node).entry

			shock = self.createBeam(f.ogrePosition, s.ogrePosition, True, self.getMaterial(obj))
			return shock

		except Exception, e:
			log().debug("error creating shock: " + str(e) + " / " + str(e.__doc__))
			raise

	def createSubMeshGroup(self, tree, smg, smgid):
		#print smg
		try:
			# read in nodes
			nodes = {}
			for nodeobj in tree['nodes']:
				if nodeobj.has_key('type'):
					continue
				node = nodeobj['data']
				nodes[int(node[0])] = ogre.Vector3(float(node[1]), float(node[2]), float(node[3]))

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
			sm = self.sceneManager.createManualObject("manualsmg" + idstr)
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
		except Exception, e:
			log().debug("error creating submesh-group: " + str(e) + " / " + str(e.__doc__))

	def makeSimpleBox(self, size, pos, orient):
		## base mass on the size of the object.
		mass = size.x * size.y * size.z * 2.5

		box1 = self.sceneManager.createEntity("Entity" + str(self.EntityCount), "cap_mid.mesh")
		self.clearlist['entity'].append("Entity" + str(self.EntityCount))

		self.EntityCount += 1
		box1node = self.sceneManager.getRootSceneNode().createChildSceneNode()
		box1node.attachObject(box1)
		box1node.setScale(size.x, size.y, size.z)
		box1node.setPosition(pos)

		box1.setMaterialName("mysimple/terrainselect")
		box1.setCastShadows(False)


	def populateScene(self):
#		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7)

		fadeColour = (0.1, 0.1, 0.1)
#		self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002)
		#self.sceneManager.setFog(ogre.FOG_LINEAR, fadeColour, 0.001, 5000.0, 10000.0)
		self.renderWindow.getViewport(0).BackgroundColour = fadeColour

		self.sceneManager.AmbientLight = color('BACKGROUND')
		self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
		self.sceneManager.setSkyDome(True, 'mysimple/truckEditorSky', 4.0, 8.0)

		self.MainLight = self.sceneManager.createLight('MainLight')
		self.MainLight.setPosition (ogre.Vector3(20, 80, 130))
		#create ray template
		self.raySceneQuery = self.sceneManager.createRayQuery(Ogre.Ray());

	def selectNew(self, event):
		x, y = event.GetPosition()
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()

		self.clearAnim()
		mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
		self.raySceneQuery.setRay(mouseRay)
		self.raySceneQuery.setSortByDistance(True)
		result = self.raySceneQuery.execute()

		selectedSomething = False
#		if len(self.ignorearray) > 20:
#			self.ignorearray = []
		#is axis?
		for r in result:
			if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
				if r.movable.getName() in self.axis.arrowNames:
					self.axis.arrow = r.movable
					return None

		for r in result:
			if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
				name = r.movable.getName()

				if self.entries.has_key(name[:-len("entity")]):
					cur = name[:-len("entity")]
					if not self.entries[cur].visible: continue
					if hasattr(self.entries[cur], 'lineTruck'):
						if self.entries[cur].lineTruck.section == 'beams': continue # no beams select :-|
					return self.entries[cur]
		return None

	def createGroundPlane(self):
		return
		plane = ogre.Plane()
		plane.normal = ogre.Vector3(0, 1, 0)
		plane.d = 2
		planesize = 200
		# see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
		mesh = ogre.MeshManager.getSingleton().createPlane('GroundPlane', "General", plane, planesize, planesize,
													20, 20, True, 1, 50.0, 50.0, ogre.Vector3(0, 0, 1),
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													True, True)
		entity = self.sceneManager.createEntity('GroundPlaneEntity', 'GroundPlane')
		entity.setMaterialName('tracks / IngameEditor / Grid1')
		self.planenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
		self.planenode.attachObject(entity)


	def LoadTruck(self, fn):
# Lepes: testing
#		if not os.path.isfile(fn):
#			print "truck file not found: "+fn
#			return
		self.clearScene()
		self.initScene(True)
		self.createBasicObjects()
		self.filename = fn
		truckname = os.path.basename(fn)

		self.parser = rorparser()
		self.notepad = rorNotepad(self)

		self.parser.parse(fn)
		self.notepad.grid.setParser(self.parser)
#		if not 'nodes' in p.tree.keys() or not 'beams' in p.tree.keys() :
#			return False

#		self.tree = p.tree
		self.beams = []
		beamcounter = 0
		shockcounter = 0
		self.Create3DFromLines(self.parser.lines)

		#temp var
#		return p.tree

	def createWalls(self):
		n = self.newEntryEx('beam.mesh', 'tracks / IngameEditor / Grid1', False, True, suffix="XYwall") #CLRED
		n.allowTranslation = True
		n.canBeSelected = True
		n.node.setScale(10, 10, 0)
#		n.node.setPosition(-15, -15, 0)

		n2 = self.newEntryEx('beam.mesh', 'tracks / IngameEditor / Grid1', False, True, suffix="YZwall") #CLGREEN
		n2.allowTranslation = True
		n2.canBeSelected = True
		n2.node.setScale(0, 10, 10)
#		n2.node.setPosition(0, -15, -15)

		n3 = self.newEntryEx('beam.mesh', 'tracks / IngameEditor / Grid1', False, True, suffix="XZwall") #CLGREEN
		n3.allowTranslation = True
		n3.canBeSelected = True
		n3.node.setScale(10, 0.1, 10)
#		n3.node.setPosition(0, -10, 0)


	def Create3DFromLines(self, lines):
		try:
			wheels = []
			mwheels = []
			for obj in lines:
				if obj.isHeader : continue
				if obj.section == "nodes":
					self.createNode(obj)
				elif obj.section in BEAMS:#"beams":
					self.createBeam(obj)
				elif obj.section in ['props', 'flexbodies']:
					if obj.ref_node is None or obj.x_node is None or obj.y_node is None:
						log().debug('prop: %s some axes node is  None: %s' % (obj.meshname, obj.getTruckLine()))
						continue
					self.createProp(obj)

				elif obj.section == 'wheels':
					wheels.append(obj)
				elif obj.section == 'meshwheels':
					mwheels.append(obj)

				#no rotation yet
#				pfff, need a lot of RoR source code to be translate to python :(

#			newlines = "nodes\n"
#			for x in tree['nodes']:
#				newlines += x['obj'].getTruckLine(self.parser) + '\n'
#			newlines += '\nbeams\n'
#			for x in tree['beams']:
#				newlines += x['obj'].getTruckLine(self.parser) + '\n'
#			newlines = ''
#			oldkey = 'title'
#			print tree.keys()
#			required = ['title', 'globals', 'nodes', 'beams', 'cameras', 'cinecam']
#			newlines += self.getSections(required)
#			nonrequired = []
#			for x in tree.keys():
#				if not x in required:
#					nonrequired.append(x)
#
#			newlines += self.getSections(nonrequired)
#			log().debug('New generated .truck file\n' + newlines)
#			smgcounter = 0
#			for smg in tree['submeshgroups']:
#				print "loading submesh: ", smgcounter
#				self.createSubMeshGroup(tree, smg,smgcounter)
#				smgcounter += 1

			#from UVFrame import *
			#self.uvFrame = UVFrame(self, wx.ID_ANY, "")
			#self.uvFrame.setTree(tree)
			#self.uvFrame.Show()
		except Exception, e:
			log().debug("error creating 3D objects from Lines of section: " + str(e) + " / " + str(e.__doc__))
			raise
		try:
			if len(wheels) > 0:
				log().debug('creating %d wheels' % len(wheels))
				for o in wheels:
					self.addWheel(o)
			if len(mwheels) > 0:
				log().debug('creating %d Mesh wheels' % len(mwheels))
				for o in mwheels:
					self.addMeshWheel(o)
		finally:
			mwheels = [] #ref count
			wheels = []

	def addMeshWheel(self, obj):
		enode1 = self.parser.findNode(obj.node1).entry
		enode2 = self.parser.findNode(obj.node2).entry
		center = (enode1.ogrePosition + enode2.ogrePosition) / 2.0
		axis = (enode1.ogrePosition - enode2.ogrePosition)
		axis.normalise()
		rim = self.newEntryEx(obj.meshname, None, True, True, suffix='MeshRim')
		rim.ogrePosition = center

		raxis = axis
		if obj.side != 'r': #reverse rim is true
			raxis = -raxis
		p = ogre.Vector3(0, 0, 0)
		snode = self.parser.findNode(obj.rigidity_node)
		if snode is not None: p = snode.entry.ogrePosition
		ray = p - enode1.ogrePosition
		onormal = raxis.crossProduct(ray)
		onormal.normalise()
		ray = raxis.crossProduct(onormal)
		rim.ogreRotation = ogre.Quaternion(raxis, onormal, ray)

	def addWheel(self, obj):
		"""
		"""
		enode1 = self.parser.findNode(obj.node1).entry
		enode2 = self.parser.findNode(obj.node2).entry
		width = (enode1.ogrePosition - enode2.ogrePosition).length()
		obj.width = width # we change it !
		if enode1.ogrePosition.z < enode2.ogrePosition.z:
			tmp = enode1
			enode1 = enode2
			enode2 = tmp
		axis = enode2.ogrePosition - enode1.ogrePosition
		axis.normalise()
		rayvec = axis.perpendicular() * obj.radius
		rayrot = ogre.Quaternion(ogre.Degree(-360.0 / float(obj.raycount * 2)), axis)
		wheelnodes = []
		for i in range(0, obj.raycount):
			raypoint = enode1.ogrePosition + rayvec
			rayvec = rayrot * rayvec
			print "raypoint ", raypoint.x, " " , raypoint.y, " ", raypoint.z
			wheelnodes.append(self.createNodeFrom(raypoint.x, 	raypoint.y, raypoint.z))

			raypoint = enode2.ogrePosition + rayvec
			rayvec = rayrot * rayvec
			wheelnodes.append(self.createNodeFrom(raypoint.x, 	raypoint.y, raypoint.z))
		# add beams
		for i in range(0, obj.raycount):
			#bounded
			self.createBeamFrom(enode1.lineTruck.id, wheelnodes[i * 2].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(enode2.lineTruck.id, wheelnodes[i * 2 + 1].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(enode2.lineTruck.id, wheelnodes[i * 2].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(enode1.lineTruck.id, wheelnodes[i * 2 + 1].lineTruck.id, 'n', inlineComment=RWHEELS)
			#reinforcement
			self.createBeamFrom(wheelnodes[i * 2].lineTruck.id, wheelnodes[i * 2 + 1].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(wheelnodes[i * 2].lineTruck.id, wheelnodes[i * 2].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(wheelnodes[i * 2].lineTruck.id, wheelnodes[((i + 1) % obj.raycount) * 2].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(wheelnodes[i * 2 + 1].lineTruck.id, wheelnodes[((i + 1) % obj.raycount) * 2 + 1].lineTruck.id, 'n', inlineComment=RWHEELS)
			self.createBeamFrom(wheelnodes[i * 2 + 1].lineTruck.id, wheelnodes[((i + 1) % obj.raycount) * 2 ].lineTruck.id, 'n', inlineComment=RWHEELS)

	def getSections(self, sections):
		lines = '\n'
		for x in range(len(sections)):
			try:
				if self.tree.has_key(sections[x]):
					print "generating line for " + sections[x]
					lines += '\n % s\n' % sections[x]
					for l in range(len(self.tree[sections[x]])):
						lines += self.tree[sections[x]][l]['obj'].getTruckLine(self.parser) + '\n'
			except Exception, e:
				print "error with section %s" % sections[x], str(e) + " / " + str(e.__doc__)
				continue
		return lines

	def createProp(self, obj):
		""" receives a lineOfSection props or flexbodies


		"""
		#FIXME: how to create all meshes related to this obj, maybe a mesh, wheelmesh, airfol...
		mesh = self.newEntryEx(obj.mesh, None, True, True, False, None)
		mesh.allowRotation = True
		mesh.allowTranslation = True
		setattr(obj, 'entry', mesh)
		setattr(mesh, 'lineTruck', obj)
		mesh.OnRotationChanged.append(self.rotationUpdated)
		self.updateProp(obj, mesh)

	def updateProp(self, obj, mesh):
		""" update position and rotation of the prop
		It also create the matrix3 of axes
		"""
		normal = ogre.Vector3(0, 0, 0)
		refpos = self.parser.findNode(obj.ref_node).entry.ogrePosition
		xpos = self.parser.findNode(obj.x_node).entry.ogrePosition
		ypos = self.parser.findNode(obj.y_node).entry.ogrePosition
		xoff = xpos #* obj.offsetx
		yoff = ypos #* obj.offsety
		zoff = obj.offsetz

		#beam.cpp::updateProps()
		normal = (ypos - refpos).crossProduct(xpos - refpos)
		normal.normalise()
		mposition = refpos + obj.offsetx * (xpos - refpos) + obj.offsety * (ypos - refpos)
		refx = xpos - refpos
		refx.normalise()
		refy = refx.crossProduct(normal)
		mesh.node.setPosition(mposition + normal * obj.offsetz)
		q = ogre.Quaternion(ogre.Degree(obj.rotz), ogre.Vector3(0, 0, 1)) * ogre.Quaternion(ogre.Degree(obj.roty), ogre.Vector3(0, 1, 0)) * ogre.Quaternion(ogre.Degree(obj.rotx), ogre.Vector3(1, 0, 0))
		#	 ogre.Quaternion(xaxis, yaxis, zaxis) yes !!! z and y vectors are interchanged
		ori = ogre.Quaternion(refx, normal, refy) * q
		mesh.node.setOrientation(ori)
#		mesh.axes =
#		print "original degrees %.3f,%.3f,%.3f, " % (obj.rotx, obj.roty, obj.rotz)
#		print "getting rotations"
#		theOr = mesh.node.getOrientation()
#		theOr.FromRotationMatrix(mesh.axesMatrix)
#		print "pitch " + str(theOr.getPitch().valueDegrees())
#		print "roll " + str(theOr.getRoll().valueDegrees())
#		print "yaw " + str(theOr.getYaw().valueDegrees())


	def controlArrows(self, event):
		x, y = event.GetPosition()
		forcex = -(int((self.StartDragLeftX - x) / 5) * self._gridSize)

		self.StartDragLeftX, self.StartDragLeftY = x, y
		if event.GetWheelRotation() != 0:
			forcex = float(event.GetWheelRotation()) / (event.GetWheelDelta() * 2.0)

#		if event.ShiftDown():
		forcex /= 10
		LockSteps = event.AltDown()
		forceDegree = ogre.Degree(forcex).valueRadians()

		if self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[0]:
			 self.translateSelected(ogre.Vector3(forcex, 0, 0), LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[1]:
			self.translateSelected(ogre.Vector3(0, 0, forcex), LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[2]:
			self.translateSelected(ogre.Vector3(0, forcex, 0), LockSteps)

		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[3]:
			self.rotateSelected(ogre.Vector3(1, 0, 0), forceDegree, LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[4]:
			self.rotateSelected(ogre.Vector3(0, 1, 0), forceDegree, LockSteps)
		elif self.selected.axis.arrow.getName() == self.selected.axis.arrowNames[5]:
			self.rotateSelected(ogre.Vector3(0, 0, 1), forceDegree, LockSteps)

	def translateSelected(self, vector, steps=False,
		doc=""" vector is an offset to translate to
				 steps is something like align to grid"""):

		if not self.selected.entry:
			return
		self.movingEntry = True
		newpos = self.selected.entry.node._getDerivedPosition() + vector
#		self.log('translating ', vector)
		if steps:
			stepsize = self.gridSize
			newpos.x += (newpos.x % stepsize)
#			newpos.y += (newpos.y % stepsize)
			newpos.z += (newpos.z % stepsize)

#			if newpos.x != 0.0:
#				newpos.x = round(newpos.x / 10.0, 1) * 10.0
#			if newpos.y != 0.0:
#				newpos.y = round(newpos.y / 10.0, 1) * 10.0
#			if newpos.z != 0.0:
#				newpos.z = round(newpos.z / 10.0, 1) * 10.0

		self.selected.entry.ogrePosition = newpos #.x, newpos.y, newpos.z)
#		self.selected.entry.node.setPosition(x, y, z)
		self.selected.axis.attachTo(self.selected.entry.node)
#		self.addObjectToHistory(self.selected.entry)

	def rotateSelected(self, axis, amount, steps=True):
		if not self.selected.entry:
			return
		self.rotatingEntry = True
		self.selected.entry.node.rotate(axis, amount, relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
		newrot = self.selected.entry.node._getDerivedOrientation()
#		self.selected.entry.node.setOrientation(newrot)
#		self.addObjectToHistory(self.selected.entry)
#		self.selected.entry.data.modified = True
#		self.selected.entry.node.setOrientation(newrot)
		self.selected.axis.rotateNode.setOrientation(newrot)

	def onMouseEvent(self, event):
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()

		if event.LeftDown() or event.RightDown() or event.MiddleDown():
			self.SetFocus()
			self.StartDragX, self.StartDragY = event.GetPosition()
			self.StartDragLeftX, self.StartDragLeftY = event.GetPosition()
		if self.selected.axis.arrow is not None and event.Dragging() and event.LeftIsDown() and not event.ControlDown():
			self.controlArrows(event)
		else:
			self.selected.axis.arrow = None
			if self.movingEntry and self.selected.entry is not None:
				self.selected.entry.informPositionChanged()
				self.movingEntry = False
			if self.rotatingEntry and self.selected.entry is not None:
				self.selected.entry.informRotationChanged()
				self.rotatingEntry = False


		mode = self.camera.getProjectionType() == Ogre.ProjectionType.PT_PERSPECTIVE
		if mode:
			if event.ControlDown() and event.GetWheelRotation() != 0:
				#decrease/increase pointer grid size
				if event.ShiftDown(): increase = 0.01
				else: increase = 0.1
				if event.GetWheelRotation() < 0: factor = -1
				else: factor = 1
				self.gridSize += factor * increase
			elif event.GetWheelRotation() != 0:
				# zoom factor
				zfactor = 0.001
				if event.ShiftDown():
					zfactor = 0.01
				zoom = zfactor * -event.GetWheelRotation()
				self.camera.moveRelative(ogre.Vector3(0, 0, zoom))
			elif event.Dragging() and event.MiddleIsDown():
				self.wasDragging = True
				x, y = event.GetPosition()
				dx = self.StartDragX - x
				dy = self.StartDragY - y
				self.StartDragX, self.StartDragY = x, y
				offset = ogre.Vector3(dx / 50.0, -dy / 50.0, 0)

				if self.selected.entry is not None:
					self.camera.setAutoTracking(True, self.selected.entry.node)
					n = self.selected.entry.node.getPosition()
#					self.showOverlay('POCore / autotrack', value)
				else:
					self.camera.setAutoTracking(True, self.node0)
					n = self.node0.getPosition()
#					self.showOverlay('POCore / autotrack', False)

				dist = self.camera.getPosition().distance(n)

				self.camera.moveRelative(offset)
				newdist = self.camera.getPosition().distance(n)
				if newdist != dist:
					self.camera.moveRelative(ogre.Vector3(0, 0, dist - newdist))
			elif event.MiddleUp():
				self.autoTracking = False
				self.wasDragging = False

			elif event.Dragging() and event.RightIsDown():
				self.wasDragging = True
				x, y = event.GetPosition()
				dx = self.StartDragX - x
				dy = self.StartDragY - y
				self.StartDragX, self.StartDragY = x, y
				self.autoTracking = False
				self.camera.yaw(ogre.Degree(-dx / 3.0))
				self.camera.pitch(ogre.Degree(-dy / 3.0))

			elif event.RightUp() and not self.wasDragging:
				# move p3d to the pointing entry
				e = self.selectNew(event)
				if e is not None:
					self.p3d.node.setPosition(e.node.getPosition())
					self.positionUpdating(None)
#					self.log("p3d at", self.p3d.node.getPosition())
			elif event.LeftDown():
				preventry = self.selected.entry
				e = self.selectNew(event)
				if self.selected.entry is not None and e != preventry and self.selected.entry is not self.p3d and not self.ShiftIsDown:
					self.clearAnim() #remove animated selection
				elif self.selected.entry is not None and e != preventry and self.selected.entry is not self.p3d and self.ShiftIsDown:
					self.anim(e)
					if preventry not in self.activeAnim: self.anim(preventry)

				self.selected.entry = e

			elif event.LeftUp() or event.RightUp():
				self.wasDragging = False
		event.Skip()

	def changeDisplayMode(self, mode):

		if mode == self.camMode:
			pass

		#save settings
		self.modeSettings[self.camMode] = [self.camera.getPosition(), self.camera.getOrientation(), self.camera.getNearClipDistance()]
		w = self.camera.getOrthoWindowWidth()
		h = self.camera.getOrthoWindowHeight()
#		self.log("ortho window w, h ", [w, h])
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
				self.camera.setNearClipDistance(.1)
				self.cameraNode.setPosition(Ogre.Vector3(0, 0, 1))
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		elif mode == "orthleft":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(0.1)
				self.camera.setPosition(Ogre.Vector3(0, 0, 1))
				self.camera.setOrthoWindow(6, 6)
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		elif mode == "orthright":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(.1)
				self.camera.setPosition(Ogre.Vector3(0, 0, -1))
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		elif mode == "orthrear":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(.1)
				self.camera.setPosition(Ogre.Vector3(1, 0, 0))
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		elif mode == "orthfront":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(.1)
				self.camera.setPosition(Ogre.Vector3(-1, 0, 0))
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		elif mode == "orthtop":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(.1)
				self.camera.setPosition(Ogre.Vector3(0.1, 1, 0))
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		elif mode == "orthbottom":
			if cammode:
				self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
			if not mode in self.modeSettings.keys():
				self.camera.setNearClipDistance(.1)
				self.camera.setPosition(Ogre.Vector3(0.1, -1, 0))
				self.camera.lookAt(Ogre.Vector3(0, 0, 0))

		self.camMode = mode

	def log(self, text, param=[]):
		""" easy log any floating values, for example:
			self.log(" data position is:", [data.x, data.y, data.z])
			self.log(" vector3", vector)
		"""
		if isinstance(param, ogre.Vector3):
			param = [param.x, param.y, param.z]

		log().info(text.ljust(17) + " " + " ".join(["%.6f" % x for x in param]))
	def save(self):
		lastsection = "title"
		visitedSections = ['title']
		text = []
		try:
			text = ""
			for line in self.parser.lines:
				l = line.getTruckLine()
				if l != "": # don't save wheel nodes and beams created dynamically
					text += l + '\n'
		finally:
			fullpath = ogreGroupFor(self.filename)
			f = None
			if fullpath != "":
				fullpath = os.path.join(resourceGroupNames[fullpath], self.filename)

			if fullpath == "":
				pause("saving at c:\\ because ogreGroup")
				f = open("c:\\new.truck", 'w')
			else: f = open(fullpath, 'w')
			f.writelines(text)
			f.close()
	def crisscross(self):
		if self.selected.entry is not None:
			#avoid doubles:
			idx = self.parser.sectionStart('beams')
			idxe = self.parser.sectionEnd('beams')
			if self.lastnodes[0] == self.lastnodes[2]:
				log().info("avoiding to create a 0-length beam from nodes %d to %d" % (self.lastnodes[0], self.lastnodes[2]))
			if self.lastnodes[1] == self.lastnodes[3]:
				log().info("avoiding to create a 0-length beam from nodes %d to %d" % (self.lastnodes[1], self.lastnodes[3]))

			log().info("creating beam from nodes %d to %d" % (self.lastnodes[0], self.lastnodes[2]))
			self.createBeamFrom(self.lastnodes[0], self.lastnodes[2], 'v')
			log().info("creating beam from nodes %d to %d" % (self.lastnodes[1], self.lastnodes[3]))
			self.createBeamFrom(self.lastnodes[1], self.lastnodes[3], 'v')
#				self.selected.entry.node.roll(ogre.Degree(90), ogre.Node.TransformSpace.TS_LOCAL)
#				log().debug('roll 90 (X)')
	def selectByNodes(self, dummy):
			# select by nodes
			dlg = wx.TextEntryDialog(
							self, 'Enter a valid node ranges separated by space\n\n for example: 1-10 44 minus 8 3-5\n will return 1, 2, 6, 7, 9, 10, 44\n\n because nodes especified after "minus" keyword are excluded from list',
							'Select beams by node Range:', '')

			dlg.SetValue("")

			if dlg.ShowModal() == wx.ID_OK:
				rangeNodes = dlg.GetValue()
				r = self.parser.expandNodeRange(rangeNodes)
				beams = []
				for l in self.parser.lines:
					if l.section == 'beams':
						if l.first_node in r and l.second_node in r:
							#beams.append(l.entry)
							self.anim(l)



	def onKeyDown(self, event):
		#print event.m_keyCode
		d = self.gridSize
		self.ShiftIsDown = event.ShiftDown() # used on shift+ leftclick
		if event.ShiftDown():
			d = 1
		mode = self.camera.getProjectionType() == Ogre.ProjectionType.PT_PERSPECTIVE
		if mode and not event.ControlDown():
			translate = None
			if event.m_keyCode == WXK_D:
				translate = ogre.Vector3(d, 0, 0)
			elif event.m_keyCode == WXK_A:
				translate = ogre.Vector3(-d, 0, 0)
			elif event.m_keyCode == WXK_W:
				translate = ogre.Vector3(0, 0, -d)
			elif event.m_keyCode == WXK_S:
				translate = ogre.Vector3(0, 0, d)
			elif event.m_keyCode == WXK_V:
				translate = ogre.Vector3(0, -d, 0)
			elif event.m_keyCode == WXK_F:
				translate = ogre.Vector3(0, d, 0)
			elif event.m_keyCode == WXK_P:
				if not self.p3d.node is None:
					self.log("p3d at ", self.p3d.node.getPosition())

			if False and translate is not None:
					#trying to move pointer from camera point of view

					# camera orientation without Yaw, so the rotation is on XZ plane
#					q = ogre.Quaternion(self.camera.getOrientation().getPitch(), ogre.Vector3(0, 0, 1)) * ogre.Quaternion(self.camera.getOrientation().getRoll(), ogre.Vector3(0, 1, 0))
				q = ogre.Quaternion(self.camera.getOrientation().getYaw(), ogre.Vector3(0, 1, 0))
				oldp = self.p3d.node.getPosition()
				angle = self.camera.getOrientation().getYaw().valueDegrees()
				# I hate this following code :s
				oldtrans = ogre.Vector3(translate.x, translate.y, translate.z)
				translate = self.p3d.node.getPosition() + q * translate
				if (-90 < angle and angle < 90) and (event.m_keyCode == WXK_D or event.m_keyCode == WXK_A):
					translate.z = oldtrans.z
#				elif (angle < -90 and angle > -180) or ( and (event.m_keyCode == WXK_D or event.m_keyCode == WXK_A):
#					# now fit to grid
				self.log("translate ", translate)


				translate.x = translate.x - (oldp.x - translate.x) + ((translate.x) % self._gridSize)
				translate.z = translate.z - (oldp.z - translate.z) + ((translate.z) % self._gridSize)
				self.log(" rounded ? ", translate)

				self.p3d.node.setPosition(translate)
				translate = None
			if translate is not None:
#				self.p3d.logPosRot("p3d adjust on X ")
				self.p3d.node.translate(translate)
				self.p3d.inform()
				self.positionUpdating(None)
			if event.m_keyCode == WXK_T:
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
			elif event.m_keyCode == WXK_R and not event.ControlDown(): # 82 = R
				detailsLevel = [ ogre.PM_SOLID,
								ogre.PM_WIREFRAME,
								ogre.PM_POINTS ]
				self.sceneDetailIndex = (self.sceneDetailIndex + 1) % len(detailsLevel)
				self.camera.polygonMode = detailsLevel[self.sceneDetailIndex]
			elif event.m_keyCode == WXK_S and event.ControlDown():
				# CTRL + S ==> summary
				d = self.parser.getSummary()
				msg = "filename %s\ndirectory %s\n" % (self.filename, resourceGroupNames[ogreGroupFor(self.filename)])
				msg += "element count for each section:\n"
				msg += " %20s      %s\n" % ('section', 'element')
				msg += "-" * 35 + "\n"

				for k in d:
					msg += "%20s %6d\n" % (k, d[k])
				showInfo("Truck summary", msg)
#		else:
#			if event.m_keyCode == WXK_D: # A, wx.WXK_LEFT:
#				self.camera.moveRelative(ogre.Vector3(d, 0, 0))
#			elif event.m_keyCode == WXK_A: # D, wx.WXK_RIGHT:
#				self.camera.moveRelative(ogre.Vector3(-d, 0, 0))
#			elif event.m_keyCode == WXK_W: # W ,wx.WXK_UP:
#				self.camera.moveRelative(ogre.Vector3(0, 0, -d))
#			elif event.m_keyCode == WXK_S: # S, wx.WXK_DOWN:
#				self.camera.moveRelative(ogre.Vector3(0, 0, d))
#			elif event.m_keyCode == WXK_V:
#				self.camera.moveRelative(ogre.Vector3(0, d, 0))
#			elif event.m_keyCode == WXK_F:
#				self.camera.moveRelative(ogre.Vector3(0, -d, 0))



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

		elif event.m_keyCode == WXK_Q: # C
			# Q ==> autotracking
			if self._autoTracking == None:
				self._autoTracking = False
			self.autoTracking = not self.autoTracking
			p = self.camera.getPosition()
			for e in self.entries:
				if hasattr(self.entries[e], "nodeNumber"):
					self.rorLookAt(self.entries[e].nodeNumber, p)

		elif event.m_keyCode == wx.WXK_SPACE:
			p = self.p3d.node.getPosition()
#			self.axis.selectTerrain((p.x, p.y, p.z))
			new = self.isNodeAt(p)
			if new is None:
				new = self.createNodeFrom(p.x, p.y, p.z)
			if self.autoCreateBeam and self.selected.entry is not None :
				if not hasattr(self.selected.entry, 'lineTruck'): showedError('selected object is not a node, please select a node to join to')
				self.createBeamFrom(new.lineTruck.id, self.selected.entry.lineTruck.id)
#				self.createBox(self.selected.entry.node.getPosition(), p, False)
			self.selected.entry = new
		elif event.m_keyCode == WXK_X:
			# X ==> criss cross latest 4 nodes
			self.crisscross()
		elif event.m_keyCode == WXK_Y:
			if self.selected.entry is not None:
				self.selected.entry.node.yaw(ogre.Degree(30), ogre.Node.TransformSpace.TS_LOCAL)
				log().debug('yaw 30 (Y)')
		elif event.m_keyCode == WXK_Z:
			if self.selected.entry is not None:
				self.selected.entry.node.pitch(ogre.Degree(30), ogre.Node.TransformSpace.TS_LOCAL)
				log().debug('pitch 30 (Z)')
		elif event.m_keyCode == WXK_E and event.ControlDown():
			# save and reload
			self.save()
			self.LoadTruck(self.filename)

		elif event.m_keyCode == WXK_E: #text editor
			self.save()
		elif event.m_keyCode == wx.WXK_NUMPAD_ADD and event.ShiftDown():
			#highlight level increased
			self.highlitLevel += 2
			self.highLighter(self, self.selected.entry, self.highlitLevel, True)
			self.notepad.grid.Refresh()
			self.notepad.grid.Update()
		elif event.m_keyCode == wx.WXK_NUMPAD_SUBTRACT and event.ShiftDown():
			#highlight level decreased
			if self.highlitLevel > 0:
				self.highlitLevel -= 2
				self.clearAnim()
				self.highLighter(self, self.selected.entry, self.highlitLevel, True)
				self.notepad.grid.Refresh()
				self.notepad.grid.Update()

		elif event.m_keyCode == wx.WXK_NUMPAD_ADD and event.AltDown():
			#beam diameter increase
			RoRConstants.BEAM_DIAMETER *= 1.1
			for e in self.entries.keys():
				if hasattr(self.entries[e], 'lineTruck'):
					if self.entries[e].lineTruck.section in BEAMS:
						self.entries[e].node.setScale(ogre.Vector3(RoRConstants.BEAM_DIAMETER, self.entries[e].node.getScale().y , RoRConstants.BEAM_DIAMETER))


		elif event.m_keyCode == wx.WXK_NUMPAD_SUBTRACT and event.AltDown():
			#BEAM DIAMETER size decreased
			RoRConstants.BEAM_DIAMETER *= 0.9
			for e in self.entries.keys():
				if hasattr(self.entries[e], 'lineTruck'):
					if self.entries[e].lineTruck.section in BEAMS:
						self.entries[e].node.setScale(ogre.Vector3(RoRConstants.BEAM_DIAMETER, self.entries[e].node.getScale().y, RoRConstants.BEAM_DIAMETER))
		elif event.m_keyCode == wx.WXK_NUMPAD_ADD:
			#ball node size increase
			sphere = event.ControlDown()
			if sphere:RoRConstants.DOT_SCALE *= 1.1
			else: RoRConstants.NODE_NUMBERS *= 1.1
			for e in self.entries.keys():
				if hasattr(self.entries[e], 'nodeNumber'):
					if sphere: self.entries[e].node.setScale(ogre.Vector3(RoRConstants.DOT_SCALE, RoRConstants.DOT_SCALE, RoRConstants.DOT_SCALE))
					else: self.entries[e].nodeNumber.setScale(ogre.Vector3(RoRConstants.NODE_NUMBERS, RoRConstants.NODE_NUMBERS, RoRConstants.NODE_NUMBERS))


		elif event.m_keyCode == wx.WXK_NUMPAD_SUBTRACT:
			#ball node size decreased
			sphere = event.ControlDown()
			if sphere:RoRConstants.DOT_SCALE *= 0.9
			else: RoRConstants.NODE_NUMBERS *= 0.9
			for e in self.entries.keys():
				if hasattr(self.entries[e], 'nodeNumber'):
					if sphere: self.entries[e].node.setScale(ogre.Vector3(RoRConstants.DOT_SCALE, RoRConstants.DOT_SCALE, RoRConstants.DOT_SCALE))
					else: self.entries[e].nodeNumber.setScale(ogre.Vector3(RoRConstants.NODE_NUMBERS, RoRConstants.NODE_NUMBERS, RoRConstants.NODE_NUMBERS))
		elif event.m_keyCode == WXK_H and event.AltDown():
			for e in self.entries:
				self.entries[e].visible = True
		elif event.m_keyCode == WXK_H and event.ControlDown():
			for e in self.entries:
				self.entries[e].visible = (self.entries[e] in self.activeAnim)

		elif event.m_keyCode == WXK_H:
			for e in self.entries:
				self.entries[e].visible = not(self.entries[e] in self.activeAnim)
		elif event.m_keyCode == WXK_S and event.ControlDown():
			self.selectByNodes(0)
			self.renderWindow.update()
		event.Skip()

	def rorLookAt(self, node, pos):
		""" make a road look to the position of pos
		pos maybe vector3 or tuple
		"""
		if isinstance(pos, TupleType):
			vector3 = ogre.Vector3(pos[0], pos[1], pos[2])
		elif isinstance(pos, ogre.Vector3):
			vector3 = pos
		else:
			raise showedError("TerrainentryClass.rorLookAt need a vector3 or tuple!!")

		node.resetOrientation()
#		node.lookAt(vector3, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(0, 1, 0))
		node.lookAt(vector3, ogre.Node.TransformSpace.TS_WORLD, ogre.Vector3(0, 0, 1))

	def newEntry(self, bAssignEvent=False, bAutouuid=False):
		""" bAssignEvent -> Assign ogreWindow property
			bAutouuid -> auto generate uuid to this entry"""
		n = simpleEntryClass(self)
		if bAssignEvent:
			n.OnSelecting.append(self.selectingEntry)
		if bAutouuid:
			n.uuid = randomID()
		n.allowRotation = False #no rotation axes
		n.allowTranslation = False #no translation axes
		return n

	def newEntryEx(self, strMeshName, strMaterialName=None, bAssignEvent=False, bAddToEntries=False, bCreateData=False, parentNode=None, suffix=""):
		""" strMeshName, strMaterialName = None, bAssignEvent = False, bAddToEntries = False, bCreateData = False, parentNode = None
		Create a New Entry, that is:
				   - node
				   - entity
				   - attach entity to node
				   - Assign material and mesh to the entity
				   - Create object Data (
				   - add to self.entries """

		n = self.newEntry(bAssignEvent, True)
		if parentNode is None:
			n.node = self.smNewNode(str(n.uuid) + "node")
		else:
			n.node = parentNode.createChildSceneNode(str(n.uuid) + "node")
		n.entity = self.smNewEntity(suffix + str(n.uuid) + "Entity", strMeshName)
		if strMaterialName:
			n.entity.setMaterialName(strMaterialName)
		n.node.attachObject(n.entity)
		if bAddToEntries:
			self.entries[suffix + str(n.uuid)] = n
		return n

	def smNewEntity(self, strName, strMesh, strMaterialName=None,
					doc=""" strName, strMesh, strMaterialName =None
					Scene Manager New Entity:
					Create a new entity with:
					- Entity Name
					- Mesh Name
					- Material Name (maybe omitted)"""):
		e = self.sceneManager.createEntity(strName, strMesh)
		if strMaterialName:
			e.setMaterialName(strMaterialName)
		return e

	def createDotAt(self, x, y, z, color=CLBLUE, sufix='', parentNode=None):
		p = self.newEntryEx("ellipsoid.mesh", color, True, True)
		p.node.setPosition(x, y, z)
		p.node.setScale(RoRConstants.DOT_SCALE, RoRConstants.DOT_SCALE, RoRConstants.DOT_SCALE)
		p.name = sufix
		return p

	def Vector3(self, v):
		return ogre.Vector3(v.x, v.y, v.z)

	def specialGetRotationTo(self, src, dest):
		""" based on Beam.cpp::specialGetRotationTo"""
		# Based on Stan Melax's article in Game Programming Gems

		# Copy, since cannot modify local
		v0 = self.Vector3(src);
		v1 = self.Vector3(dest)
		v0.normalise()
		v1.normalise()
		q = ogre.Quaternion(1, 0, 0, 0)

		c = self.Vector3(v0.crossProduct(v1))

		#// NB if the crossProduct approaches zero, we get unstable because ANY axis will do
		#// when v0 == -v1
		d = v0.dotProduct(v1)
		#// If dot == 1, vectors are the same
		if (d >= 1.0):
			return ogre.Quaternion(1, 0 , 0 , 0)
		if d < -0.999999 :
			#// Generate an axis
			axis = ogre.Vector3(1, 0, 0).crossProduct(src)
			if axis.isZeroLength(): #// pick another if colinear
				axis = ogre.Vector3(0, 1, 0).crossProduct(src)
			axis.normalise();
			q.FromAngleAxis(Radian(pi), axis);
		else:
			s = sqrt((1 + d) * 2);
			if s == 0 : return ogre.Quaternion(1, 0, 0, 0)
			invs = 1 / s;


			q.x = c.x * invs;
			q.y = c.y * invs;
			q.z = c.z * invs;
			q.w = s * 0.5;
		return q

	def getPointedPosition(self, event):
		x, y = event.GetPosition()
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()
		mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
#		ray = ogre.Ray(ogre.Vector3(0, 0,0), ogre.Vector3(0,-1,0))
		Q = self.sceneManager.createRayQuery(ogre.Ray());
		self.renderWindow.update()
		Q.setSortByDistance(True)
		#Perform the scene query
		lastOnFloor = None
		result = Q.execute()
#		for z in range(-10, 10):
#			if z < 0 : color = CLTRANSRED
#			else: color = CLCREAM
#			p = mouseRay.getPoint(z)
#			dot = self.createDotAt(p.x, p.y, p.z, color)
#			if p.y > 0.0: lastOnFloor = dot
		found = False
		try:
			log().debug("searching for intersections")
			for r in result:
				if r is not None and r.movable is not None and r.movable.getMovableType() == "Entity":
						name = r.movable.getName()
						log().debug("collision with %s" % name)
						if name.find('wall') > -1:
							if self.entries.has_key(name[:-6]):
								if lastOnFloor is not None:
									p = lastOnFloor.node.getPosition()
									self.log(" FOUND at ", p)
								found = True

				else: log().debug(" ray doesn't have more entities")
		except:
			found = False
			raise

		self.sceneManager.destroyQuery(Q)


	def _getautoCreateBeam(self):
		return self._autoCreateBeam

	def _setautoCreateBeam(self, value):
		self._autoCreateBeam = value

	def _getgridSize(self):
		return self._gridSize

	def _setgridSize(self, value):
		self._gridSize = value
		self.positionUpdating(None)

	def _delgridSize(self):
		del self._gridSize


	gridSize = property(_getgridSize, _setgridSize, _delgridSize)
	""" steps of pointer 3D movement
	"""

	autoCreateBeam = property(_getautoCreateBeam, _setautoCreateBeam,
						doc="""Create beam when adding a node and there is a previous node""")
