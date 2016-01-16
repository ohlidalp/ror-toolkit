import wx, os, os.path, copy
import cPickle
import errno
from time import  *
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS
from math import acos
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.rorcommon import *
from ror.toolkitparser import *
from ror.lputils import *
from RoRTerrainSelection import *

 #TODO: spline should be another class. atm is:

#splines = { 'struid':
#				{
#				 'name': '<username>',
#				 'ctrlpoints':
#				 	[
#						{	'point':[x, y, z ],
#							'sticked': Boolean,
#							'type' : string ('auto', 'road', 'roadborderright'...),
#							'roads':[terrainEntryClass() ],
#						}
#				 	]
#				},
#
#			< another one >
#		}
#
#			'segments':
#			 	[
#					{'roads':[terrainEntryClass() ], 'sticked': Boolean, 'type' : string ('auto', 'road', 'roadborderright'...)},
#					{'roads':[terrainEntryClass() ], 'sticked': Boolean, 'type' : string ('auto', 'road', 'roadborderright'...)},
#			 	]

#
#===============================================================================

#===============================================================================
# si ponemos los puntos de la splineLine no necesitamos autocorrect para nada, es super suave la carretera pero
# entra dentro del terreno
#
# Si usamos los puntos del spline pegados al suelo, necesitamos autocorrect... y mucho.
#===============================================================================

class RoadSystemClass(object):
	def __str__(self):
		msg = 'unused %d ' % len(self.unused)
		msg += 'segments %d =[' % len(self.segments)
		for i in range(len(self.segments)):
			msg += '(%d), ' % len(self.segments[i]['roads'])
		msg += ']'
		return msg
	def __del__(self):
		self.cancelSpline()
		self.lastBlock = None
		self.toolWindow = None
		self.internal.clear()
		if self.AnimState is not None:
			self.destroyAnimation()
		del self.dotwalk
		del self.bb
		#log().debug("deleting RoadSystemClass")

	def __init__(self, toolWindow, ogrewindow):
		self._height = 0.2
		self._toolWindow = toolWindow
		self.ogreWindow = ogrewindow
		self.splineStickedToGround = True
		self.controlDots = []
		self.unused = []
		self.segments = []
		self.spline = None
		self.splineName = None
		self.createMaterials()
		self.strUID = ''
		self._km = 0.0
		self._walkOnRoads = False
		self._offset = ogre.Vector3(0, 5, 0)
		self._ground01 = ogre.Vector3(0, 0.05, 0)
		self.dotwalk = None
		self.lastTimer = None
		self.idxwalk = 0
		self.idxroad = -1
		self._busy = False
		self.idxActualSegment = -1
		self.bb = BoundBoxClass(ogrewindow)
		self.AnimState = None
		self.indent = 0
		self.splines = {}

	def _getkm(self):
		return self._km

	def _setkm(self, value):
		self._km = value

	def _delkm(self):
		del self._km
	def _getwalkOnRoads(self):
		return self._walkOnRoads

	def _setwalkOnRoads(self, value):
		if self.AnimState is not None:
			self.AnimState.setEnabled(False)
			self.destroyAnimation()
			return
		self._walkOnRoads = False
		self.idxwalk = 0
		self.idxroad = -1
#		self.idxwalk, self.idxroad, road = self.nextRoad(0, -1)
		s, r, road = self.nextRoad(0, -1)
		if road is None: return
		p = road.node.getPosition() + self._offset
		if self.dotwalk is None:
			self.dotwalk = self.ogreWindow.createDotAt(p.x, p.y, p.z, CLTRANSGREEN)
		else:
			self.dotwalk.position = p.x, p.y, p.z
		self.dotwalk.visible = False
		self.dotwalk.node.attachObject(self.ogreWindow.camera)
		self.ogreWindow.camera.setPosition(-10, 5, 0)
#		self.ogreWindow.camera.setAutoTracking(True, self.dotwalk.node)
		self.ogreWindow.camera.lookAt(self.dotwalk.node.getPosition() + ogre.Vector3(1000, 5, 0))
		self.animation = self.ogreWindow.sceneManager.createAnimation("CameraTrack", (self.ogreSpline.getNumPoints() - 1) * 100) #length!??
		self.animation.setInterpolationMode(ogre.Animation.IM_SPLINE);
		self.track = self.animation.createNodeTrack(0, self.dotwalk.node)
		# Setup keyframes
#		TransformKeyFrame* key = track->createNodeKeyFrame(0); // startposition
		key = self.track.createNodeKeyFrame(0)
		key.setTranslate(self.dotwalk.node.getPosition())
		cont = 0
		for i in range(0, self.ogreSpline.getNumPoints()):
			key = self.track.createNodeKeyFrame(i * 100)
			key.setTranslate(self.ogreSpline.getPoint(i) + ogre.Vector3(0, 2, 0))
		self.AnimState = self.ogreWindow.sceneManager.createAnimationState("CameraTrack")
		self.AnimState.setLoop(False)
		log().info("walking on roads started, let's go...")
		self.AnimState.setEnabled(True)


	def destroyAnimation(self):
		#destroying animation, it destroy all node tracks
		self.ogreWindow.sceneManager.destroyAnimation("CameraTrack")
		self.track = None
		self.animation = None
		self.ogreWindow.sceneManager.destroyAnimationState("CameraTrack") # yeah Ogre use the same name for animation and its AnimState
		self.AnimState = None
		self.dotwalk.node.detachObject(self.ogreWindow.camera)
		self.ogreWindow.camera.setPosition(self.dotwalk.node.getPosition() + self.ogreWindow.camera.getPosition())
		#log().debug('animation destroyed')

	def _delwalkOnRoads(self):
		del self._walkOnRoads
		if self.dotwalk is not None:
			self.dotwalk.autoRemoveFromScene = True
	def _getbusy(self):
		return self._busy

	def _setbusy(self, value):
		if self._busy != value:
			self._busy = value
			self.ogreWindow.showOverlay('POCore/workingSpline', value, forceUpdate=True)

	def _delbusy(self):
		del self._busy

	def _getsegmentSticked(self):
		if self.idxActualSegment < len(self.segments) and self.idxActualSegment > -1:
			return self.segments[self.idxActualSegment]['sticked']
		else: return True

	def _setsegmentSticked(self, value):
		self.segments[self.idxActualSegment]['sticked'] = value
		self.controlDots[self.idxActualSegment].y = self.lastRoadPos(self.idxActualSegment - 1)[0][1]
		self.createSplineLine(None, self.idxActualSegment - 2, self.idxActualSegment + 2)
		self.updateselected()

	def _getactualSegment(self):
		if self.idxActualSegment < len(self.segments):
			return self.segments[self.idxActualSegment]['type']
		else: return 'auto'


	def _setactualSegment(self, value):
		self._actualSegment = value
		self.segments[self.idxActualSegment]['type'] = value
		self.updateSegments(self.idxActualSegment - 2, self.idxActualSegment + 2)
		self.updateselected()
	def updateselected(self):
		#FIXME: a bug that axis goes to the last object that internally was used
		#it is a workaround used
#		self.ogreWindow.selected.entry = self.controlDots[self.idxActualSegment]
#		self.ogreWindow.renderWindow.update()
		pass

	def _delactualSegment(self):
		del self._actualSegment

	actualSegment = property(_getactualSegment, _setactualSegment, _delactualSegment,
					doc="""only available when user select a control dot. It hold
					the segment type the user want to set up""")


	segmentSticked = property(_getsegmentSticked, _setsegmentSticked,
					doc="if false the road will be as a procedural road, else it will be smooth")


	busy = property(_getbusy, _setbusy, _delbusy,
					doc="set overlay to true or false updating renderWindow")


	walkOnRoads = property(_getwalkOnRoads, _setwalkOnRoads, _delwalkOnRoads,
					doc="move camera along the current spline Line to see roads")

	km = property(_getkm, _setkm, _delkm,
					doc="Km of roads added (number of roads * 10)")

	def createMaterials(self):
		""" create materials for:
		   - spline line
		   - selection road material
		It also create all kind of roads on the terrain
		"""
		# some spline material
		if self.spline is None:
			self.ogreSpline = ogre.SimpleSpline()
		self.ogreSpline.clear()
		self.ogreSpline.setAutoCalculate(False)

		if ogre.MaterialManager.getSingleton().getByName("matline") is None:
			mat = ogre.MaterialManager.getSingleton().create("matline", "ToolkitBase")
			mat.setReceiveShadows(False)
			mat.getTechnique(0).setLightingEnabled(True)
			mat.getTechnique(0).getPass(0).setDiffuse(0, 1, 1, 0)
			mat.getTechnique(0).getPass(0).setAmbient(0, 1, 1)
			mat.getTechnique(0).getPass(0).setSelfIllumination(0, 1, 1)

		if ogre.MaterialManager.getSingleton().getByName("matline_ideal") is None:
			mat = ogre.MaterialManager.getSingleton().create("matline_ideal", "ToolkitBase")
			mat.setReceiveShadows(False)
			mat.getTechnique(0).setLightingEnabled(True)
			mat.getTechnique(0).getPass(0).setDiffuse(0, 1, 0, 0)
			mat.getTechnique(0).getPass(0).setAmbient(0, 1, 0)
			mat.getTechnique(0).getPass(0).setSelfIllumination(0, 1, 0)

		# init lines
		self.line = []
		self.linenode = []
		for i in range(0, 3):
			self.line.append(self.ogreWindow.sceneManager.createManualObject("lineobj" + str(i)))
			self.line[i].setCastShadows(False)
			self.line[i].setDynamic(True)
			self.linenode.append(self.ogreWindow.smNewNode(("spline_%s" % str(i))))
			self.linenode[i].attachObject(self.line[i])

		self.internal = {}
		self._createInternal('road')
		self._createInternal('roadborderleft')
		self._createInternal('roadborderright')
		self._createInternal('roadborderboth')
		self._createInternal('roadbridge')

		name = 'roadbridgenopillar' #fake object
		self.internal[name] = {}
		self.internal[name]['normalMaterialName']	 = self.internal['roadbridge']['normalMaterialName']
		self.internal[name]["selMaterialName"] 		 = self.internal['roadbridge']['selMaterialName']

	def _createInternal(self, name):
		r = self.ogreWindow.newEntryEx(name + '.mesh',
											None, True, False, True) #created data !!!

		r.beginUpdate()
		r.data.fileWithExt = name + '.odef'
		r.autoRemoveFromScene = True #loading another map
		r.canBeSelected = False
		self.ogreWindow.checkKnownDimension(r, None)
		self.ogreWindow.entries[str(r.uuid)] = r
		r.visible = False
		r.endUpdate()
		self.internal[name] = {}
		self.internal[name]['object'] = r
		self.internal[name]['normalMaterialName'] = r.entity.getSubEntity(0).getMaterialName()
		self.internal[name]["selMaterialName"] = name + 'selected'
		selmat = ogre.MaterialManager.getSingleton().getByName(name + 'selected')
		if selmat is None:
			selmat = ogre.MaterialManager.getSingleton().create(
												self.internal[name]["selMaterialName"],
												"ToolkitBase")
			mat = ogre.MaterialManager.getSingleton().getByName(r.entity.getSubEntity(0).getMaterialName())
			if not mat is None:
				mat.copyDetailsTo(selmat)
			selmat.setSceneBlending(ogre.SceneBlendFactor.SBF_SOURCE_ALPHA, ogre.SceneBlendFactor.SBF_DEST_ALPHA)
			selmat.setSelfIllumination(1, 0.3, 0)
			selmat.setDiffuse(1, 0.3, 0, 0.9)
			selmat.setAmbient(1, 0.3, 0)
			selmat.setSpecular(1, 0.3, 0, 0.9)

	def createTemp(self, kind, pos, rot):
		selmat = None
		if self.internal.has_key(kind):
			selmat = self.internal[kind]['selMaterialName']

		newroad = terrainEntryClass(self.ogreWindow)
		newroad.uuid = randomID()
		newroad.data = Object()
		newroad.data.fileWithExt = kind + '.odef'
		newroad.node = self.ogreWindow.smNewNode(str(newroad.uuid) + "node")
		newroad.entity = self.internal[kind]['object'].entity.clone(str(newroad.uuid) + "Entity")
		newroad.entity.setMaterialName(selmat)
		newroad.node.attachObject(newroad.entity)

#
#		newroad = self.ogreWindow.newEntryEx(kind + '.mesh',
#											selmat,
#											 True, False, True) #created data !!!

		newroad.data.fileWithExt = kind + '.odef'
		newroad.beginUpdate()
		newroad.position = pos
		newroad.rotation = rot
#		newroad.endUpdate() yup
		newroad.autoRemoveFromScene = True
		newroad.canBeSelected = False # don't allow user to move/delete :-P
		newroad.endUpdate()

		return newroad
	def getRoad(self, kind, pos, rot):
		""" reuse latest segments (terrainEntryClass) used before
		This prevent reallocating new memory each time a point is added to the splineLine
		It will only replace the entity if we need a different one.

		Parameters:
		- kind: 'road', 'roadbridge', etc..  (any RoR standard object that .odef and .mesh has the same filename
		- pos: tuple pos
		- rot: tuple rot
		"""
		if len(self.unused) > 0 :
			if self.unused[0].data.name != kind:
				selmat = None
				if self.internal.has_key(kind):
					selmat = self.internal[kind]['selMaterialName']
				mesh = kind
				if mesh == "roadbridgenopillar": mesh = "roadbridge"
				self.unused[0].replaceEntity(kind + '.odef', mesh + '.mesh', selmat)
			self.unused[0].beginUpdate()
			self.unused[0].position = pos
			self.unused[0].rotation = rot
			self.unused[0].visible = True
			self.unused[0].autoRemoveFromScene = True
			self.unused[0].endUpdate()
			return self.unused.pop(0)
		else:
			return self.createTemp(kind, pos, rot)

	def hidesegments(self, fromidx):
		for i in range(fromidx + 1, len(self.segments)):
			self.segments[i]['roads'].visible = False


	def setSplineMode(self, value, strUID=None):
		if not value and strUID is None:
			self._km = 0.0
			self.ogreWindow.splineMode = None
		else:
			self.ogreWindow.splineMode = value
		if strUID is None:
			self.strUID = str(randomID())
		else:
			self.strUID = strUID
			self.restoreSpline(strUID)


	def restoreSpline(self, struid=''):
		if self.splines.has_key(struid):
			try:
				self.busy = True
				self._km = 0.0
				self.entriesToSpline(True)
				self.splineName = self.splines[struid]['name']
				self.strUID = struid
				for i in range(len(self.splines[struid]['ctrlpoints'])):
					seg = self.splines[struid]['ctrlpoints'][i]
					v = ogre.Vector3(seg['point'][0], seg['point'][1], seg['point'][2])
					self.addPoint(v, sticked=seg['sticked'], type=seg['type'])
				self.createSplineLine(startAt=None, fromSegment=0, toSegment=None)
			finally:
				self.busy = False



	def entriesToSpline(self, addToSpline=False):
		if addToSpline: # ogrewindow entries moved to segments
			for k in self.ogreWindow.entries.keys():
				if self.ogreWindow.entries[k].data:
					if self.ogreWindow.entries[k].data.spline == self.strUID:
						e = self.ogreWindow.entries.pop(k)
						if self.internal.has_key(e.data.name):
							e.entity.setMaterialName(self.internal[e.data.name]['selMaterialName'])
						e.OnSelecting = []
						e.OnPositionChanging = []
						e.OnPositionChanged = []
						e.autoRemoveFromScene = True
						e.canBeSelected = False
						e.beginUpdate()
						self.unused.append(e)

						try:
							self.ogreWindow.terrain.objects.remove(e.data)
						except ValueError:
							# orly ???
							pass

		else: # segments moved to ogrewindow entries
			s = 0
			while True:
				if len(self.segments) <= s:
					return
				if len(self.segments[s]['roads']) == 0:
					s += 1
				else:
					e = self.segments[s]['roads'].pop(0)
					if self.internal.has_key(e.data.name):
						e.entity.setMaterialName(self.internal[e.data.name]['normalMaterialName'])
					e.canBeSelected = True
					e.autoRemoveFromScene = False
					e.endUpdate()
					e.data.modified = True
					e.OnSelecting.append(self.ogreWindow.entryChanged)
					e.OnPositionChanging.append(self.ogreWindow.entryChanged)

					e.data.spline = self.strUID
					self.ogreWindow.entries[str(e.uuid)] = e
					self.ogreWindow.terrain.objects.append(e.data)

#					del e

	def setUnused(self, fromIdx, fromSegment, toSegment=0):
		if toSegment == 0 : toSegment = fromSegment

		if fromSegment < len(self.segments):
			while fromIdx < len(self.segments[fromSegment]['roads']):
				e = self.segments[fromSegment]['roads'].pop(fromIdx)
				e.visible = False
				self.unused.append(e)

			for x in range(fromSegment + 1, toSegment):
				if x < len(self.segments):
					while len(self.segments[x]['roads']) > 0:
						e = self.segments[x]['roads'].pop(0)
						e.visible = False
						self.unused.append(e)
		#log().debug('unused %d' % len(self.unused))

	def createSplineLine(self, startAt=None, fromSegment=None, toSegment=None):
		if startAt is not None:
			self.addPoint(self.ogreWindow.maxterrainWaterHeight(startAt)[0] + ogre.Vector3(0, 0.1, 0))
		self.ogreSpline.recalcTangents()
		self.drawSplineLines()
		total = clock()
		if fromSegment == None:
			fromSegment = self.ogreSpline.getNumPoints() - 2
		if toSegment == None:
			toSegment = self.ogreSpline.getNumPoints()
		roads = self.updateSegments(fromSegment, toSegment)
		self._km = roads / 100.0
		log().info('Spline writed in %.12f seconds, %d roads' % (clock() - total, roads))


	def insertPointAtSelectedEntry(self, before=True):
		"""
		selected Entry is a Control dot.

		before = True -> insert point before selected entry
		before = False -> insert point after selected entry
		before = None -> delete selected entry
		"""

		v = self.ogreWindow.selected.entry.node._getDerivedPosition()
		pos = int(self.ogreWindow.selected.entry.data.name.split('_')[1])
		self.ogreWindow.boundBox.dockTo(self.ogreWindow.selected.entry)
		self.ogreWindow.selected.entry = None
		if before is None:
			v = None
		elif before == False:
			pos += 1
			v = self.ogreWindow.boundBox.realPos(ogre.Vector3(-15, 0, 0))
		else:
			v = self.ogreWindow.boundBox.realPos(ogre.Vector3(15, 0, 0))
		toselect = pos
		if toselect >= len(self.controlDots) :
			pos = len(self.controlDots) - 1
			toselect = len(self.controlDots)
		elif toselect < 0 :
			pos = 0
			toselect = 0
		self.insertPoint(pos, v, before)
		if v is not None:
			self.ogreWindow.selected.entry = self.controlDots[toselect]

	def insertPoint(self, pos , vector3, before=True):
		""" ogre SimpleSpline does not have methods for inserting points
		so I need to re-create from scratch

		pos - segment index where insertion well be
		vector3 - if is None, ctrl dot will be deleted
		"""
		try:
			self.busy = True
			self.setUnused(0, 0, len(self.segments))
			points = [self.controlDots[x].node._getDerivedPosition() for x in range(len(self.controlDots))]
			if vector3 is None:
				points.pop(pos)
				del self.segments[pos]
			else:
				if before: idx = pos - 1
				else: idx = pos
				self.segments.insert(pos, {'roads':[], 'sticked' : self.segments[idx]['sticked'], 'type':self.segments[idx]['type']})
				points.insert(pos, vector3)
			self.ogreSpline.clear()
			self.deleteControlDots()
			self.ogreWindow.renderWindow.update()
			#destroza todos los segmentos anteriores y posteriores wtf
			print "recreating spline"
			for i in range(len(points)):
				print "adding segment %d, sticked %s" % (i, self.segments[i]['sticked'])
				self.addPoint(points[i], segment=i, sticked=self.segments[i]['sticked'], type=self.segments[i]['type'], override=True)
			self.createSplineLine(None, 0, None)

		finally:
			self.busy = False

	def deleteControlDots(self):
		""" remove all Control dots"""
		for i in range(len(self.controlDots)):
			if self.ogreWindow.entries.has_key(str(self.controlDots[i].uuid)):
				self.ogreWindow.entries.pop(str(self.controlDots[i].uuid))
		self.controlDots = [] #now yes, good bye control dots.


	def addPoint(self, vector3, segment= -1, sticked=None, type=None, override=False):
		self.ogreSpline.addPoint(vector3)
		newp = self.createTemp('road', (vector3.x, vector3.y, vector3.z), (0, 0, 0))
		newp.data.name = 'splinePoint_%d_' % (self.ogreSpline.getNumPoints() - 1) # to start at 0
		self.ogreWindow.entries[str(newp.uuid)] = newp # make selectable
		newp.entity.setMaterialName(self.internal['road']['normalMaterialName'])
		newp.data.mayRotate = False
		newp.canBeSelected = True
		newp.endUpdate() # yeah
		newp.OnPositionChanging.append(self.ogreWindow.entryChanged) #update interface
		newp.OnPositionChanged.append(self.ogreWindow.entryChanged) #update interface
		newp.OnPositionChanged.append(self.splinePointUpdated) #only update spline when no dragging
		newp.OnSelecting.append(self.OnControlDotSelected)
		newp.OnDeselecting.append(self.OnControlDotDeselected)
		if len(self.controlDots) > 0:
			self.controlDots[-1].rorLookAt(newp.position)
		self.controlDots.append(newp)
		if sticked is None	: sticked = self._toolWindow.segmentSticked
		if type is None		: type = self._toolWindow.segmentType
		if override and segment < len(self.segments) and segment > -1:
			self.segments[segment]['sticked'] = sticked
			self.segments[segment]['type'] = type
		elif segment != -1 :
			self.segments.insert(segment, {'roads':[], 'sticked' : sticked, 'type': type})
		else:
			self.segments.append({'roads':[], 'sticked' : sticked, 'type': type})

	def splinePointUpdated(self, entry):
		""" callback if user move a spline Control Dot
		"""

		self.idxActualSegment = int(entry.data.name.split('_')[1])
		log().info('splinePoint updated %d' % self.idxActualSegment)
		v = entry.node._getDerivedPosition()
		self.ogreSpline.updatePoint(self.idxActualSegment, v)
		self.createSplineLine(fromSegment=self.idxActualSegment - 2, toSegment=self.idxActualSegment + 2)
#		FIXME: split Previous segment to ground

	def OnControlDotSelected(self, entry):
		log().info('Control dot selected')
		self._toolWindow.enableInsert(True)
		self.idxActualSegment = int(entry.data.name.split('_')[1])
		if self.idxActualSegment < len(self.segments):
			self._toolWindow.segmentType = self.segments[self.idxActualSegment]['type']
			self._toolWindow.segmentSticked = self.segments[self.idxActualSegment]['sticked']
		#log().debug('control dot selected')6

	def OnControlDotDeselected(self, entry):
		self.idxActualSegment = -1
		self._toolWindow.enableInsert(False)


	def drawSplineLines(self):
		# 1st draw clicked line
		self.line[0].clear()
		self.line[0].begin("matline", ogre.RenderOperation.OT_LINE_STRIP)
		for i in range(0, self.ogreSpline.getNumPoints()):
			point = self.ogreSpline.getPoint(i)
			self.line[0].position(point + ogre.Vector3(0, 1, 0))
		self.line[0].end()

		# 1.5 draw clicked line points
		self.line[2].clear()
		self.line[2].begin("matline", ogre.RenderOperation.OT_LINE_LIST)
		for i in range(0, self.ogreSpline.getNumPoints()):
			point = self.ogreSpline.getPoint(i)
			self.line[2].position(point)
			self.line[2].position(point + ogre.Vector3(0, 2, 0))
		self.line[2].end()

		# 2nd draw ideal line
		self.line[1].clear()
		self.line[1].begin("matline_ideal", ogre.RenderOperation.OT_LINE_STRIP)
		factor = 400
		for i in range(0, self.ogreSpline.getNumPoints() * factor):
			point = self.ogreSpline.interpolate(i / float(self.ogreSpline.getNumPoints() * factor))
			self.line[1].position(point + ogre.Vector3(0, 1, 0))
		self.line[1].end()

	def finishSpline(self):
		#log().debug(self.__str__())
		try:
			self.busy = True
			self.createSplineLine(None, 0, None)# refine entire spline
			self.checkBridgeNoPillar()
			self.entriesToSpline(False)
			#log().debug(' after passed roads to Terrain ' + self.__str__())
			if self.splines.has_key(self.strUID):
				self.splines.pop(self.strUID)
			newsp = {}
			newsp['ctrlpoints'] = []
			newsp['name'] = self.splineName

			for i in range(len(self.controlDots)):
#					{'point':x, y, z < is a tuple>, 'sticked': Boolean, 'type' : string ('auto', 'road', 'roadborderright'...)},
				newsp['ctrlpoints'].append(
							{'point'	: self.controlDots[i].position,

							 'sticked'	: self.segments[i]['sticked'],
							 'type' 	: self.segments[i]['type']
							}
				)
			self.splines[self.strUID] = newsp
			self.cancelSpline()
			self.ogreWindow.checkSplineLine() # update toolwindow
		finally:
			self.busy = False
	def loadSplines(self, filename):
		self.splines = {}
		file = filename.replace('.terrn', '.splines')
		g = ogreGroupFor(file)
		if g != '':
			filepath = resourceGroupNames[g]
			file = os.path.join(filepath, file)
			input = open(file, 'rb')
			if input:
				self.splines = pickle.load(input)
				input.close()
#				log().info('loaded %d splines' % self.splines.keys().count())
		else: log().debug(" splines file does not exist %s" % filename)


	def saveSplines(self, filename):
		file = filename.replace('.terrn', '.splines')
		#TODO: if file wasn't saved before.. we get an error ==> disable buttons you can not use ("save" and "save and play ror")
		print "self segments file " + file
		output = open(file, 'wb')
		if output:
			pickle.dump(self.splines, output, 0)
			output.close()

	def checkBridgeNoPillar(self):
		s, i, road = self.nextRoad(0, -1)
		ns, ni, nroad = self.nextRoad(s, i)
		ray = ogre.Ray(ogre.Vector3(0, 0, 0), ogre.Vector3(0, -1, 0))
		Q = self.ogreWindow.sceneManager.createRayQuery(ray);
		self.ogreWindow.renderWindow.update()
		offset = ogre.Vector3(0, 0, 0)
		while nroad is not None:
			if road.data.name.startswith('roadbridge'):
				centerUp = self.ogreWindow.localPosToWorld(road, (5, -0.4, 0))# antes (5 + offset.x, -2, 0))
				ray.setOrigin(centerUp)
				Q.setRay(ray)
				Q.setSortByDistance(True)
				result = Q.execute()
#				for z in range(-10, 5):
#					if z < 0 : color = CLTRANSRED
#					else: color = CLCREAM
#					p = ray.getPoint(z)
#					self.ogreWindow.createDotAt(p.x, p.y, p.z, color)
				found = False
				try:
					for r in result:
						if found: break
						if r is not None and r.movable is not None and r.movable.getMovableType() == "Entity":
								name = r.movable.getName()
								rorname = self.ogreWindow.getRoRName(r.movable)
								if rorname.startswith('splinePoint'):
									continue
								if road.entity.getName() == name:
									continue
								elif name.find('waterPlane') > -1:
									continue
								else :
									if r.movable.isAttached():
										found = True
#										r.movable.getParentSceneNode().showBoundingBox(True)
				except:
					found = False
				if found :
					road.data.fileWithExt = 'roadbridgenopillar.odef'
					nroad.data.fileWithExt = 'roadbridgenopillar.odef'
					#log().debug('seg %d idx %d HAS BEEN FOUND A NO PILLAR' % (s, i))
					found = False
					s = ns
					i = ni
					road = nroad
					ns, ni, nroad = self.nextRoad(s, i)
				else:
					road.data.fileWithExt = 'roadbridge.odef'
			s = ns
			i = ni
			road = nroad
			ns, ni, nroad = self.nextRoad(s, i)

		self.ogreWindow.sceneManager.destroyQuery(Q)

	def purgueSpline(self):
		self.cancelSpline()
		if self.splines.has_key(self.strUID):
			self.splines.pop(self.strUID)
			self.ogreWindow.checkSplineLine()

	def cancelSpline(self):
		self.ogreSpline.clear()
		self.splineName = None
		self.ogreWindow.splineMode = None
		self.ogreWindow.selectTerrain()
		self.deleteControlDots()
		self.segments = [] #good bye temp roads :)
		self.unused = [] #good bye unused roads
		self.line[0].clear()
		self.line[1].clear()
		self.line[2].clear()

	def previousRoad(self, segment, idx):
		idx -= 1
		result = -1, -1, None  #prev_segment, prev_idx, road
		if segment >= len(self.segments): return result
		if idx >= len(self.segments[segment]['roads']):
			idx = len(self.segments[segment]['roads']) - 1
		if idx < 0 :
			while segment > -1 and len(self.segments) > segment and idx <= 0:
				segment -= 1
				idx = len(self.segments[segment]['roads']) - 1
		if segment == -1: return result
		if len(self.segments[segment]['roads']) > idx and idx >= 0:
			return segment, idx, self.segments[segment]['roads'][idx]
		return result

	def nextRoad(self, ASegment=0, Aidx=0):
		"""
		return a tuple

		segment, idx, theNextRoad entry

		segment could be None if there are no next road
		"""
		if len(self.segments) > 0 and ASegment < len(self.segments):
			segment = ASegment
		else: segment = None
		idx = Aidx + 1
		if segment is None : return None, idx, None
		while segment < len(self.segments) and idx >= len(self.segments[segment]['roads']):
			segment += 1
			idx = 0
		if segment < len(self.segments) and idx < len(self.segments[segment]['roads']):
			return segment, idx, self.segments[segment]['roads'][idx]
		return None, idx, None



	def angle(self, v1, v2):
		v1.normalise()
		v2.normalise()

		cosalpha = v1.dotProduct(v2)
		radian = ogre.Radian(acos(cosalpha))
		alpha = ogre.Degree(radian).valueDegrees()
		return alpha

	def autocorrect(self, dif, atSegment, atIdx):
		s, i, prevroad = self.previousRoad(atSegment, atIdx)
		if prevroad is not None and abs(dif > 0.001):
			rx, ry, alpha = prevroad.rorLookAt(self.segments[atSegment]['roads'][atIdx].node.getPosition())
			if abs(alpha) < 10 : #+ road.rz
				dif = 0.0
			else:
				if dif > 0.0 :
					prevroad.y += 0.2
					dif -= 0.2
				else:
					prevroad.y -= 0.2
					dif += 0.2
				#log().debug(self.indent * ' ' + 'seg %d idx %d : new height %.3f (dif %.3f)' % (s, i, prevroad.y, dif))

			self.autocorrect(dif, s, i)
			if len(self.segments) > atSegment and len(self.segments[atSegment]['roads']) > atIdx:
				#log().debug('  looking At segment %d idx %d ' % (atSegment, atIdx))
				rx, ry, rz = prevroad.rotation
				orz = rz

				x, y, z, rx, ry, rz = prevroad.roadLookAt(self.segments[atSegment]['roads'][atIdx].node._getDerivedPosition(), ry)
				#log().debug('road seg %d idx %d rotating old rz %.3f new rz %.3f' % (s, i, orz, rz))
				self.bb.dockTo(prevroad)
				self.selectRoadType(self.bb, prevroad, s)
		elif prevroad is not None and dif == 0.0 :
			prevroad.rorLookAt(self.segments[atSegment]['roads'][atIdx].node.getPosition())

	def selectRoadType(self, boundBox, entry=None, atSegment= -1):
		if self.segments[atSegment]['type'] in self.internal.keys(): objName = self.segments[atSegment]['type']
		else: #'auto'
			objName = 'road'
			hleft = boundBox.maxHeightOfGround(["nearLeftTop", "farLeftTop"])
			hright = boundBox.maxHeightOfGround(["nearRightTop", "farRightTop"])
			# RoR hardcoded heights:
			if hleft > 0.6 and hleft < 4.0: objName = 'roadborderleft'
			if hright > 0.6 and hleft < 4.0:
				if objName == 'roadborderleft': objName = 'roadborderboth'
				else : objName = 'roadborderright'
			if hleft > 4.0 or hright > 4.0:
				objName = 'roadbridge'

		if entry is not None and entry.data.name != objName:
			entry.replaceEntity(objName + '.odef', objName + '.mesh', self.internal[objName]["selMaterialName"])
		return objName

	def lastRoad(self, idx):
		"""
		return a tuple
		isControlDot, entry
		boolean, terrainEntryClass
		"""
		if idx < 0 : idx = 0
		if len(self.controlDots) > 0:
			result = True, self.controlDots[idx]
		else:
			result = False, None
		if len(self.segments) > idx :
			if len(self.segments[idx]['roads']) > 0:
				result = False, self.segments[idx]['roads'][len(self.segments[idx]['roads']) - 1]
		return result
	def lastRoadPos(self, idx):
		"""
		idx - segment index


		return the attach point for the next road
		return ry of last road
		"""
		isDot, entry = self.lastRoad(idx)
		if isDot:
			return entry.position, 0.0
		else:
			self.ogreWindow.boundBox.dockTo(entry)
			p = self.ogreWindow.boundBox.dots["farMiddle"].node._getDerivedPosition()
			return (p.x, p.y, p.z), entry.ry

	def updateSegments(self, fromSegment, toSegment):
		if fromSegment < 0 : fromSegment = 0
		if toSegment > self.ogreSpline.getNumPoints() - 1 : toSegment = self.ogreSpline.getNumPoints() - 1
		#log().debug('updating segments from %d to %d, len(segments) %d' % (fromSegment, toSegment, len(self.segments)))
		if fromSegment == toSegment : return 0.0
		splinePoints = []
		self.setUnused(0, fromSegment, toSegment)
#===============================================================================
#		#splineLine in 3 phasses
#===============================================================================
		#log().debug('len entries %d, len segments %d' % (len(self.ogreWindow.entries.keys()), len(self.segments)))
		factor = 1
		times = {}
		maxIsWater = False
		tctrl = clock()
#===============================================================================
#		#phasse 1: create splinepoints to follow the green line
#					based on distance of two consecutive ogre Simple spline Points
#===============================================================================
		for i in range(fromSegment, toSegment):
			factor = float(self.ogreSpline.getPoint(i).distance(self.ogreSpline.getPoint(i + 1))) / 10
			p = self.ogreSpline.getPoint(i + 1)
			for j in range(0, int(factor)):
				point = self.ogreSpline.interpolate(i, j / factor)
				minh = self.ogreWindow.maxterrainWaterHeight(point)
				minh[0] += self._ground01
				if self.segments[i]['sticked'] or minh[0].y > point.y:
					minh.append(i) # minh = [vector3, isWaterHeight, Spline_segment_number]
					splinePoints.append(minh)
				else:
					splinePoints.append([point + self._ground01, False, i]) # [vector3, isWaterHeight, Spline_segment_number]
#				p = splinePoints[-1][0]
#				self.ogreWindow.createDotAt(p.x, p.y, p.z, CLBLUE)
		#log().debug('created %d splinePoints' % len(splinePoints))
		times['create ctrl points'] = clock() - tctrl
		objName = ""
		i = 0
		prevRot = 0, 0, 0
		Finished = False
		lastRy = 0.0
		lastRz = 0.0
		lastY = 0.0
		counter = 0
		prevroad = None
		newroad = None
		createsignal = -10
		addfinalcomment = False
#		debug time doing the main bucle
		times['jumping'] = 0.0
		times['rotating'] = 0.0
		times['height'] = 0.0
		times['toolkit'] = 0.0
		times['adding_entry'] = 0.0
#===============================================================================
#		# phasse 2: create roads
#===============================================================================
		(x, y, z), lastRy = self.lastRoadPos(fromSegment - 1)
		test = ogre.Vector3(x, y, z)
		objName = 'road'
		while True:
			t = clock()
# maybe user want a road -0.1 meters bellow water level... is it need to check this?
#			if splinePoints[i][1]: # water level is greater than terrain at this point
#				objName = "roadbridge"
#			else:
#				objName = "road"
			test.x = x
			test.y = y
			test.z = z
			while test.squaredDistance(splinePoints[i + 1][0]) < 49:
				#skip spline Point that are too nearest that causes Ogre to rotate the road 180 degrees
				if i == len(splinePoints) - 2 or splinePoints[i][2] == toSegment + 1:
					# last point reached, exiting!!
					sum = 0.0
					for k in times.keys():
						#log().debug(' time spent %s: %.12f' % (k, times[k]))
						sum += times[k]
					#log().debug('sum of all times %.3f', sum)
					totalroads = 0
					for se in range(len(self.segments)):
						totalroads += len(self.segments[se]['roads'])
					s, r, lastroad = self.previousRoad(len(self.segments) - 1 , len(self.segments[len(self.segments) - 1 ]['roads']))

					if lastroad is not None and addfinalcomment:
						self.AddSplineNameToComment(lastroad)
					return totalroads

				i += 1
			t1 = clock()
			times['jumping'] = times['jumping'] + (t1 - t)
			self.ogreWindow.boundBox.dockTo(self.internal[objName]['object'], atPos=(x, y, z))
			e = self.ogreWindow.boundBox.mainEntry
			if counter == 0 :
				rx, ry, rz = e.rorLookAt(splinePoints[i + 1][0])# + self._ground01)# yeah two times :(
				lastRy = ry
			x, y, z, rx, ry, rz = e.roadLookAt(splinePoints[i + 1][0], lastRy) # + self._ground01, lastRy)
#			log().debug("counter %d, lastRy %9.3f newRy %9.3f dif %9.3f" % (counter, lastRy, ry, ry - lastRy))
			t2 = clock()
			times['rotating'] = times['rotating'] + (t2 - t1)
#			objName = self.selectRoadType(self.ogreWindow.boundBox, None

			newroad = self.getRoad(objName, (x, y, z), (rx, ry, rz))
			if counter == 0 and fromSegment == 0 :
				self.AddSplineNameToComment(newroad)
				addfinalcomment = True

			counter += 1
			self.segments[splinePoints[i][2]]['roads'].append(newroad)
			self.selectRoadType(self.ogreWindow.boundBox, newroad, splinePoints[i][2])
			t4 = clock()
			times['adding_entry'] = times['adding_entry'] + (t4 - t2)
			t3 = clock()
			if self.segments[splinePoints[i][2]]['sticked']:
				hmin = self.ogreWindow.boundBox.terrainWaterHeight(UPPERFACE) + self._ground01.y
				if counter > 2:
					newroad.y += hmin - y
					if len(splinePoints) > i + 1: splinePoints[i][0].y += hmin - y
					#log().debug("entering at autocorrect seg:idx  (%.d:%.d) " % (splinePoints[i][2], len(self.segments[splinePoints[i][2]]['roads']) - 1))
					self.indent += 1
					self.autocorrect(hmin - y , splinePoints[i][2], len(self.segments[splinePoints[i][2]]['roads']) - 1)
					self.indent -= 1
			times['height'] = times['height'] + (clock() - t3)
			lastY = y
#			if abs(ry - lastRy) > 15.0:
#				if prevroad is not None:
#					self.ogreWindow.boundBox.dockTo(prevroad)
#					newroad.node.setPosition(self.ogreWindow.boundBox.realPos((5, 0, 0)))
#					newroad.roadLookAt(splinePoints[i + 1][0], lastRy)
#					self.ogreWindow.boundBox.dockTo(newroad)
			p = self.ogreWindow.boundBox.dots["farMiddle"].node._getDerivedPosition()
			prevroad = newroad
			lastRy = ry
			lastRz = rz
			t5 = clock()
			t6 = clock()
			times['toolkit'] += (t6 - t5)
			x, y, z = p.x, p.y, p.z

		return counter

	def AddSplineNameToComment(self, road):
		"""
		always delete comment if it had any :(
		"""
		if road is not None:
			if self.splineName is not None:
				road.data.comments = ['// this road belong to splineName:%s' % self.splineName]
			else:
				road.data.comments = ['// this road belong to spline:%s' % self.strUID]
