#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz

import wx, os, os.path
from time import  *
import ogre.renderer.OGRE as ogre
from ror.truckparser import *
from ror.terrainparser import *
from ror.odefparser import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.rorcommon import *
from ror.SimpleTruckRepresentation import *
from RoRVirtualKeys import *
from math import acos, radians, degrees, fmod
from ror.lputils import *
from roreditor.RoRTerrainSelection import *
from roreditor.RoRConstants import *
from MainFrame_Tools_MapOptions import *
from SelectionAxis import *
from ror.logger import log
from RoRRoadSystem import *
from RoRConstants import *
from ror.luaparser import *

SLOW_DOWN_FACTOR = 0.75


#===============================================================================
# when using Block Mode, it is the maximum Z rotation angle allowed between two 
# consecutive piece of roads. If you want roads that a long Bus or a long truck 
# with trailer can drive on, just reduce this angle in degree.
#
# Min Value: 3 (suggested but it could be lower)
# Max Value: 20 (suggested but it could be upper)
#===============================================================================
MAX_SMOOTH_ANGLE = 9

#===============================================================================
#  if SPACE is keep pressed, I should add a pause before adding next block
#  min value = 0
#  max value = 10 
#===============================================================================
PAUSE_PER_SECOND = 0


class HistoryEntryClass(object):
	uuid = None
	position = None
	rotation = None

class MyDropTarget(wx.PyDropTarget):
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
	
class RoRTerrainOgreWindow(wxOgreWindow):

	def __init__(self, parent, ID, size=wx.Size(200, 200), maininstance=None, **kwargs): 
		self.terrain = None
	
		self.commandhistory = []
		self.historypointer = 0
	
		self.entries = {}

		self._mouse_drag_start_screen_x = int(0)
		self._mouse_drag_start_screen_y = int(0)
		self.knownObjects = {}
		""" dictionary that holds detailed info about
			all objects that we have on Terrain.
		
			It allow us to know Bounding Bounds Vertices of 
			all objects without querying every time is needed and
			On the other hand, it will allow to control how many 
			instances we have on the map, useful to control SpawnZone
			objects when added, so we can give and unique Name to them"""

		self._object_tree_window = None
		self.roadSystem = None
		log().debug(" Main terrain ogre window is being created")
		self.maininstance = maininstance
		if not maininstance is None:
			self.sceneManager = maininstance.sceneManager

		self.parent = parent
		self.size = size
		self.kwargs = kwargs
		self.ID = ID
		wxOgreWindow.__init__(self, self.parent, self.ID, "terrainEditor", size=self.size, **self.kwargs)

	def getObjectInspector(self):
		return self.parent.ObjectInspector
	
	def getObjectTree(self):
		return self.parent._object_tree_window
	
	def _getMapOptions(self):
		return self.parent.MapOptions
		
	def getselected(self):
		return self._selected

	def setselected(self, value):
		self._selected = value
	def delselected(self):
		del  self._selected

	def getautoTracking(self):
		return self._autoTracking

	def setautoTracking(self, value):
		self._autoTracking = value
		self.entryChanged(self.selected.entry)
		self.showOverlay('POCore/autotrack', value)

	def getcameraCollision(self):
		if "_cameraCollision" in self.__dict__:
			return self._cameraCollision
		else: # May happen if exception is raised during startup
			return False

	def setcameraCollision(self, value):
		self._cameraCollision = value

	def getplaceWithMouse(self):
		return self._placeWithMouse

	def setplaceWithMouse(self, value):
		self._placeWithMouse = value

	def getcurrentStatusMsg(self):
		return self._currentStatusMsg

	def setcurrentStatusMsg(self, value):
		self._currentStatusMsg = value
		msg = ["", "" , "", ""]
		if self.selected.entry is not None:
			msg[0] = value
			msg[1] = "%s %s" % (self.selected.entry.data.name, " ".join(self.selected.entry.data.additionalOptions))
			posx, posy, posz = self.selected.entry.position
			rotx, roty, rotz = self.selected.entry.rotation
			msg[2] = ("%d, %0.2f, %0.2f, %0.2f / %0.2f, %0.2f, %0.2f" % (self.selected.entry.data.line, posx, posy, posz, rotx, roty, rotz))
			
			self.parent.updateStatusBar(msg)
	
	def _getroad(self):
		return self.parent.RoadSystem

	def _getcameraBookmark(self):
		return self.parent.cameraBookmark

	def _getusePopup(self):
		if self._usepopup == None: 
			p = rorSettings().getSetting(TOOLKIT, usePopupToSelect)
			if p in ["", "TRUE", "true", "1", "True"]:
				self._setusePopup(True)
				return True
			elif p in ['False', 'false', 'FALSE', '0']:
				return False	
		else:
			return self._usepopup

	def _setusePopup(self, value):
		if self._usepopup != value:
			rorSettings().setSetting(TOOLKIT, usePopupToSelect, value)
			self._usepopup = value

	def _getcameraVel(self):
		if self._cameraVel == None:
			r = rorSettings().getSetting(TOOLKIT, cameraVelocity)
			if r == "" : r = 0.5
			self._cameraVel = float(r)
		return self._cameraVel

	def _setcameraVel(self, value):
		if not value == self._cameraVel:
			rorSettings().setSetting(TOOLKIT, cameraVelocity, value)
		self._cameraVel = value		

	def _getcameraShiftVel(self):
		if self._cameraShiftVel == None:
			r = rorSettings().getSetting(TOOLKIT, cameraShiftVelocity)
			if r == "" : r = 20.0
			self._cameraShiftVel = float(r)
		return self._cameraShiftVel

	def _setcameraShiftVel(self, value):
		if not value == self._cameraShiftVel:
			rorSettings().setSetting(TOOLKIT, cameraShiftVelocity, value)
		self._cameraShiftVel = value

	def _getsplineMode(self):
		return self._splineMode

	def _setsplineMode(self, value):
		self.showOverlay('POCore/spline', False)
		self.showOverlay('POCore/splinepause', False)
		self._splineMode = value
		if value is not None:
			if value:
				self.showOverlay('POCore/spline', True)
				self._setGuiCaption('POCore/splineKm', ' %.2f Km' % self.roadSystem.km)
			else:
				self.showOverlay('POCore/splinepause', True)

	def _delsplineMode(self):
		del self._splineMode

	splineMode = property(_getsplineMode, _setsplineMode, _delsplineMode,
					doc="")

	cameraShiftVel = property(_getcameraShiftVel, _setcameraShiftVel,
					 doc="""camera velocity factor when pressing Shift""")

	cameraVel = property(_getcameraVel, _setcameraVel,
					 doc="""camera Velocity""")

	cameraBookmark = property(_getcameraBookmark,
					 doc=""" pointer to camera Bookmark window""")

	road = property(_getroad,
					 doc="""access to Road System (tool) Window""")

	currentStatusMsg = property(getcurrentStatusMsg, setcurrentStatusMsg,
					 doc="""update Status Bar""")

	placeWithMouse = property(getplaceWithMouse, setplaceWithMouse,
					 doc="""Object Preview set up this property to place
							 objects directly on terrain 
							 
							 LMB in terrain but selecting a previous one
							 MMB without selecting any previous object,
								 always create a new one.
							 
							 """)
	
	cameraCollision = property(getcameraCollision, setcameraCollision,
				 doc="""When True Camera will not go throw terrain ground,
						if False, camera has freedom to move elsewhere.
						useful for some bad designed objects that first
						position is underground""")
	
	autoTracking = property(getautoTracking, setautoTracking,
				 doc=""" center selected object in screen and use
						  WASD keys rotate the camera around the selected object
						  instead of freedom walking.
						  It's a True/False option. """)
	
	selected = property(getselected, setselected, delselected,
				 doc="""Selected Object or Terrain
						 may be terrain, object, RoRCharacter or RoRCamera""")

	ObjectTree = property(getObjectTree,
						  doc=" Access to Object Tree, it is a pointer ;-)")

	ObjectInspector = property(getObjectInspector,
				 doc=" Access to Object Inspector Frame, it is a pointer ;-)")

	MapOptions = property(_getMapOptions,
					 doc=""" Edit first 4 lines of terrn file""")

	usePopup = property(_getusePopup, _setusePopup,
					 doc="""Use popup menu to show what objects are through the ray""")

	def finalize_init(self):
		"""
		Init; must be called before object is used 
		but after toolkit media were loaded
		"""
		import rortoolkit.mouse_3d 
		self._mouse_world_transforms = rortoolkit.mouse_3d.MouseWorldTransforms(self.camera, self.renderWindow)

		self._resetVariables()
		if self.cameraBookmark:
			self.cameraBookmark.updateVelocity(self.cameraVel, self.cameraShiftVel)

	def export_ogre17_terrain_config(self):
		"""
		reads Ogre::TerrainSceneManager (obsolete) config file.
		Exports a dict of settings
		:returns: Dict{Key:str => value:str}
		"""
		# Miniparser
		import ror.rorcommon
		lines = ror.rorcommon.loadResourceFile(self.terrain.TerrainConfig)
		data = {}
		for line in lines:
			line = line.strip()
			if len(line) > 0:
				if line[0] != "#":
					segments = line.split("=")
					if len(segments) == 2:
						data[segments[0].strip()] = segments[1].strip()
		return data

	def export_terrain_project(self):
		"""
		Exports an terrain.project.TerrainProject object from currently active terrain.
		:returns: Tuple: TerrainProject, dict (export data)
		"""
		import copy
		import rortoolkit.terrain
		project = rortoolkit.terrain.TerrainProject()
		tsm_conf = self.export_ogre17_terrain_config()
		
		# Helper functions to read TerrainSceneManager config
		def tsm_val(key):
			if key in tsm_conf:
				return tsm_conf[key]
			else:
				return None

		def tsm_bool(key):
			val = tsm_val(key)
			if val is None:
				return None
			else:
				return (tsm_val(key).strip().lower() in ["true", "yes"])

		def tsm_int(key):
			val = tsm_val(key)
			if val is None:
				return None
			else:
				return int(tsm_val(key))
		
		def tsm_float(key):
			val = tsm_val(key)
			if val is None:
				return None
			else:
				return float(tsm_val(key))

		project.header["format_version"] = 1
		project.header["name"          ] = self.terrain.TerrainName
		project.header["technical_name"] = self.terrain.name
		project.header["authors"       ] = copy.deepcopy(self.terrain.author)
		
		project.visuals["use_caelum"              ] = self.terrain.UsingCaelum
		project.visuals["sky_color_rgb"           ] = self.terrain.SkyColor
		project.visuals["cubemap_name"            ] = self.terrain.cubemap
		project.visuals["full_map_diffuse_texture"] = tsm_val("WorldTexture")
		project.visuals["full_map_detail_texture" ] = tsm_val("DetailTexture")
		project.visuals["detail_texture_num_tiles"] = tsm_val("DetailTile")
		
		project.physics["global_gravity"          ] = None
		project.physics["global_water_height"     ] = self.terrain.WaterHeight
		project.physics["use_heightmap"           ] = True # Always true for .terrn
		project.physics["heightmap_size"          ] = tsm_int("Heightmap.raw.size")
		project.physics["heightmap_bpp"           ] = tsm_int("Heightmap.raw.bpp")
		project.physics["heightmap_flip"          ] = tsm_bool("Heightmap.flip")
		project.physics["heightmap_vertical_scale"] = tsm_float("MaxHeight")
		
		project.gameplay["spawn_pos_truck_xyz"    ] = self.terrain.TruckStartPosition.asTuple
		project.gameplay["spawn_pos_camera_xyz"   ] = self.terrain.CameraStartPosition.asTuple
		project.gameplay["spawn_pos_character_xyz"] = self.terrain.CharacterStartPosition.asTuple
		
		project.ogre_legacy_tsm["page_size_vertices"  ] = tsm_int("PageSize")
		project.ogre_legacy_tsm["tile_size_vertices"  ] = tsm_int("TileSize")
		project.ogre_legacy_tsm["max_pixel_error"     ] = tsm_int("MaxPixelError")
		project.ogre_legacy_tsm["page_size_world_x"   ] = tsm_int("PageWorldX")
		project.ogre_legacy_tsm["page_size_world_z"   ] = tsm_int("PageWorldZ")
		project.ogre_legacy_tsm["max_mipmap_level"    ] = tsm_int("MaxMipMapLevel")
		project.ogre_legacy_tsm["use_vertex_normals"  ] = tsm_bool("VertexNormals")
		project.ogre_legacy_tsm["vertex_program_morph"] = tsm_bool("VertexProgramMorph")
		project.ogre_legacy_tsm["lod_morph_start"     ] = tsm_float("LODMorphStart")

		# Objects (only those successfully spawned)
		for entry in self.entries.values():
			# Filter
			if entry.data.barename == "": # Generated object
				continue
			# Create
			if entry.data.isBeam:
				o = rortoolkit.terrain.TerrainRigObject()
			else:
				o = rortoolkit.terrain.TerrainStaticObject()
			# Export data
			o.position_xyz        = (entry.ogrePosition.x, entry.ogrePosition.y, entry.ogrePosition.z)
			o.rotation_quaternion = (entry.ogreRotation.x, entry.ogreRotation.y, entry.ogreRotation.z, entry.ogreRotation.w)
			o.rotation_rx_ry_rz   = entry.rotation
			o.filename            = entry.data.fileWithExt
			o.type                = entry.data.type
			o.extra_options       = entry.data.additionalOptions
			o.editor_settings["imported_from_terrn"] = True
			# Persist
			if entry.data.isBeam:
				project.rig_objects.append(o)
			else:
				project.static_objects.append(o)

		# Rigs (all, including failed)
		for data in self.terrain.beamobjs:
			if data not in self.entries.values():
				o = rortoolkit.terrain.TerrainRigObject()
				o.position_xyz        = (data.x, data.y, data.z)
				o.rotation_rx_ry_rz   = (data.rotx, data.roty, data.rotz)
				o.filename            = data.fileWithExt
				o.type                = data.type
				o.extra_options       = data.additionalOptions
				o.editor_settings["imported_from_terrn"] = True
				o.editor_settings["imported_from_terrn_offline"] = True
				project.rig_objects.append(o)

		# Gather export data
		export_data = {}
		export_data["heightmap_filename"] = tsm_val("Heightmap.image")

		return project, export_data

	def export_heightmap(self, src_filename, dst_path):
		"""
		:param str src_filename: Input filename, will be searched in OGRE resource system
		:param str dst_path: Output file path, will be written to directly.
		"""
		import os.path
		import rortoolkit.resources
		import zipfile
		import shutil

		# NOTE: Binary reading from OGRE DataStream is mysterious (unsigned int buf?)
		# we must manually extract the heightmap from zipfile.
		zip_path = rortoolkit.resources.get_resource_zip_path(src_filename)
		if not zipfile.is_zipfile(zip_path):
			raise Exception("Terrain import failed: Cannot read source ZIP archive: " + str(zip_path))
		zip_file = zipfile.ZipFile(zip_path)
		zip_info = zip_file.getinfo(src_filename)
		zip_dst_dir = os.path.dirname(dst_path)
		extracted_path = zip_file.extract(src_filename, zip_dst_dir)
		if not os.path.isfile(extracted_path):
			raise Exception("Terrn import failed, cannot read extracted heightmap:" + str(extracted_path))
		shutil.move(extracted_path, dst_path)
	
	def newEntry(self, bAssignEvent=False, bAutouuid=False):
		""" bAssignEvent -> Assign ogreWindow property
			bAutouuid -> auto generate uuid to this entry"""
		n = terrainEntryClass(self)
		if bAssignEvent:
			n.OnSelecting.append(self.entryChanged)
			n.OnPositionChanging.append(self.entryChanged)
		if bAutouuid:
			n.uuid = randomID()
		return n

	def newEntryEx(self, strMeshName, strMaterialName=None, bAssignEvent=False, bAddToEntries=False, bCreateData=False, parentNode=None, suffix=''):
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
			n.node = self.smNewNode(suffix + str(n.uuid) + "node")
		else:
			n.node = parentNode.createChildSceneNode(suffix + str(n.uuid) + "node")
		n.entity = self.smNewEntity(suffix + str(n.uuid) + "Entity", strMeshName)
		if bCreateData:
			import rortoolkit.terrain
			n.data = rortoolkit.terrain.EditorObject()
		if strMaterialName:
			n.entity.setMaterialName(strMaterialName)
		n.node.attachObject(n.entity)
		if bAddToEntries:
			self.entries[n.uuid] = n
		return n

	def smNewNode(self, strName,
					doc=""" Scene Manager New Node:
					Create a new SceneNode with given Name """):
		return  self.sceneManager.getRootSceneNode().createChildSceneNode(strName)

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

	def localPosToWorld(self, entry, localTupleOrVector):
		if isinstance(localTupleOrVector, TupleType):
			v = ogre.Vector3(localTupleOrVector[0], localTupleOrVector[1], localTupleOrVector[2])
		elif isinstance(localTupleOrVector, ogre.Vector3):
			v = localTupleOrVector
		else:
			raise Exception('coordenate is not vector3 or tuple')
		return ogre.Quaternion(ogre.Degree(entry.ry), ogre.Vector3(0, 1, 0)) * v + entry.node._getDerivedPosition()

	def OnFrameStarted(self):
		try:
			if self.cameraCollision:
				self.cameraLandCollision()
			if self.roadSystem is not None:
				if self.roadSystem.AnimState is not None:
					if self.roadSystem.AnimState.hasEnded(): # I don't know when an animation will finish  :-|
						self.roadSystem.walkOnRoads = False
					elif self.roadSystem.AnimState.getEnabled():
						self.roadSystem.AnimState.addTime(0.5)
						self.camera.lookAt(self.roadSystem.dotwalk.node.getPosition())
	
			# axes size related to camera distance
			if self.selected.entry is not None and self.selected.entry != self.selected.axis.arrow:
				d = self.selected.entry.node._getDerivedPosition().distance(self.camera.getPosition())
				self.axis.setArrowScaleFactor(d / 150, self.selected.entry.node)
			#move cam a bit

			""" DEBUG STATEMENTS t
			kp = self.keyPress
			pos = self.moveVector
			print "MV: %.3f %.3f %.3f\tKP: %.3f %.3f %.3f" % (pos.x,pos.y,pos.z,kp.x,kp.y,kp.z)
			"""
			self.moveVector += self.keyPress
			self.camera.moveRelative(self.moveVector)
			self.moveVector *= SLOW_DOWN_FACTOR # each iteration slow the movement down by some factor
			if self.statisticsOn:
				self.updateStatistics()
		except Exception:
			log().error('terrainOgreWindow.OnFrameStarted')
			raise
	
	def OnFrameEnded(self): 
		return True
		
	def getOgreSceneManager(self):
		return self.sceneManager
	
	def cameraLandCollision(self):
		try:
			camPos = self.camera.getPosition()
			terrainHeight = self.getTerrainHeight(camPos)
			if ((terrainHeight + 1) > camPos.y):
				self.camera.setPosition(camPos.x, terrainHeight + 1, camPos.z)
		except:
			if rorSettings().stopOnExceptions:
				raise 

	def SceneInitialisation(self):
		log().debug("terrain SceneInitialization started")
		self.sceneManager = getOgreManager().createSceneManager(ogre.ST_EXTERIOR_CLOSE)

		# create a camera
		cameraUUID = randomID()
		self.camera = self.sceneManager.createCamera(str(cameraUUID) + "camera")
		self.camera.lookAt(ogre.Vector3(0, 0, 0)) 
		self.camera.setPosition(ogre.Vector3(0, 0, 0))
		
		# dont set this too low, or you will get z-fights!!
		self.camera.nearClipDistance = 0.4 # 2
		self.camera.setAutoAspectRatio(True) 
		
		# create the Viewport"
		self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0) 
		self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0) 

		#set some default values
		self.sceneDetailIndex = 0
		self.filtering = ogre.TFO_BILINEAR
		# bind mouse and keyboard
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown) 
		self.Bind(wx.EVT_KEY_UP, self.onKeyUp) 
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

		
		self.splineMode = None
		log().debug("SceneInitialization finished")
		self.populateScene()
		
	def updateWaterPlane(self, fLevel=0.0):
		""" receives a float number where water plane should be"""
		self.terrain.WaterHeight = fLevel
		if self.waterentity is None:
			self.createWaterPlane()
		self.waterentity.setVisible(fLevel != 0.0)
		#BUGFIX: plane node is centered, but plane mesh no!
		x = ifNone(self.terrain.worldX, 1500, self.terrain.worldX / 2)
		z = ifNone(self.terrain.worldZ, 1500, self.terrain.worldZ / 2)
		self.waternode.setPosition(x, fLevel + 200, z)
	
	def createWaterPlane(self):
		if self.terrain.WaterHeight is None:
			return
		plane = ogre.Plane() 
		plane.normal = ogre.Vector3(0, 1, 0) 
		plane.d = 200 
		# see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
		waterid = str(randomID())
		mesh = ogre.MeshManager.getSingleton().createPlane('waterPlane' + waterid, "General", plane, 3000, 3000,
													20, 20, True, 1, 200.0, 200.0, ogre.Vector3(0, 0, 1),
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													True, True)
		self.waterentity = self.smNewEntity("waterPlane" + waterid + "entity", "waterPlane" + waterid, 'mysimple/water')
		self.waternode = self.smNewNode('waterNode')
		self.waternode.attachObject(self.waterentity) 
	
	def getPositionRotation(self, obj):
		""" obj is a Scenenode
		"""
		scale = obj.getScale()
		obj.setScale(1, 1, 1)
		obj.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		pos = obj.getPosition()
		rot = obj.getOrientation()
		rot.normalise()
		obj.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(-90), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
		obj.setScale(scale)

		rotx = ogre.Radian(rot.getPitch(False)).valueDegrees()
		roty = ogre.Radian(rot.getRoll(False)).valueDegrees()
		rotz = -ogre.Radian(rot.getYaw(False)).valueDegrees() 
		return pos.x, pos.y, pos.z, rotx, roty, rotz
	
	def zoomCamera(self, fromVector, toVector):
		""" move camera relatively toVector -> fromVector and
			keep camera distance from ground"""
		p = self.camera.getPosition()
		sum = self.getTerrainHeight(p)
		if sum:
			hcamera = p.y - sum
		else:
			hcamera = 0
		r = (toVector - fromVector)
		f = p + r
		sum = self.getTerrainHeight(f)
		if sum is None:
			log().info("can not move camera")
		else:
			f.y = hcamera + self.getTerrainHeight(f)
			self.camera.setPosition(f)
		return

	def getRoRName(self, entity):
		key = entity.getName()[:-len("entity")]
		if self.entries.has_key(key): 
			if self.entries[key].data:
				return self.entries[key].data.name
		return ""

	def getEntry(self, entity):
		key = entity.getName()[:-len("entity")]
		if self.entries.has_key(key):
			return self.entries[key]
		else:
			return None
	
	def changeSelection(self, newnode,
						doc=" receive an Entity "):
		self.deselectSelection()
		key = newnode.getName()[:-len("entity")]
		self.selected.entry = self.entries[key]
	
	def entryChanged(self, entry):
		"""Update Object Inspector and statusBar
		value may be None to disable ObjectInspector"""
		
		self.camera.setAutoTracking(False)
		if entry:
			self.ObjectInspector.updateData(entry)
			self.parent.updateStatusBar([entry.data.name, str(entry.position), str(entry.rotation), ""])
#			self.axis.attachTo(entry.node)
			if self.autoTracking:
				self.camera.setAutoTracking(True, entry.node)

	def specialEntryChanged(self, entry):
		""" Asigned to:
		- TrucStartPosition
		- cameraStartPosition
		- characterStartPosition
		so this event will be triggered only
		when these objects positions are modified
		"""
		if entry:
			x, y, z = entry.position
			if entry.data.name == RORCAMERA:
				self.terrain.CameraStartPosition.asTuple = x, y, z
				self.cameraBookmark.cameraAdd(RORCAMERA,
											self.terrain.CameraStartPosition.asTuple,
											(0, 0, 0))

			elif entry.data.name == RORCHARACTER:
				self.terrain.CharacterStartPosition.asTuple = x, y, z
				self.cameraBookmark.cameraAdd(RORCHARACTER,
												self.terrain.CharacterStartPosition.asTuple,
												(0, 0, 0))
			elif entry.data.name == RORTRUCK:
				self.terrain.TruckStartPosition.asTuple = x, y, z
				self.cameraBookmark.cameraAdd(RORTRUCK,
											self.terrain.TruckStartPosition.asTuple,
											(0, 0, 0))

	def _resetVariables(self):
		self.terrain = None
		self.commandhistory = []
		self.historypointer = 0
		self.statisticsOn = False
		self.entries = {}
		self.raceMode = False
		self._mouse_drag_start_screen_x = int(0)
		self._mouse_drag_start_screen_y = int(0)
		self.knownObjects = {}
		self.preLoad = {}
		self.axis = AxisClass(self, ['translation', 'rotation', 'terrain']) #before selectionClass
		self.axis.entryShow.append('translation')
		self.axis.entryShow.append('rotation')
		self.axis.entryShow.append('terrain')
		self._selected = selectionClass(self)
		self.ignorearray = []
		self._autoTracking = False
		self.keyPress = ogre.Vector3(0, 0, 0)
		self.moveVector = ogre.Vector3(0, 0, 0)
		self._cameraCollision = False
		self.update_mouse_placement_mode()
		self._currentStatusMsg = ""
		self.loadMisplacedObjects()
		self.waterentity = None
		self._usepopup = None
		self._cameraVel = None
		self._cameraShiftVel = None
		self._RMBHere = False
		self.boundBox = BoundBoxClass(self)
		self.boundBox.mainEntry.beginUpdate() # never inform
		self.cameraQuick = False
		self._splineMode = None
		self.selectionBox = None
		self.sphere = None
		self.movingEntry = False
		
	def update_mouse_placement_mode(self):
		if self._object_tree_window is not None: # The 'ObjectTree' window is created later than this class.
			self._placeWithMouse = self._object_tree_window.chkMousePlacement.IsChecked()

	def loadMisplacedObjects(self):
		file = rorSettings().concatToToolkitHomeFolder(['config', 'editorConf.txt'], True)
		self.preLoad = {}
		# TODO: allow to load multiple files, so community can share these files.
		if os.path.isfile(file):
			input = open(file, 'rb')
			if input:
				log().debug("Preload file exists, loading")
				self.preLoad = pickle.load(input)
				input.close()
	
	def close(self):
		log().debug("closing terrain Ogre Window")
		if self.preLoad:
			file = rorSettings().concatToToolkitHomeFolder(['config', 'editorConf.txt'], True)
			output = open(file, 'wb')
			if output:
				pickle.dump(self.preLoad, output, 0)
				output.close()
		self.clear()
	
	def clear(self):
		# FIXME: Lepes this should be looked
		if self.autoTracking:
			self.autoTracking = False 
		self.knownObjects.clear()
		for e in self.entries: self.entries[e].autoRemoveFromScene = True
		self.entries.clear()
		del self.entries
		del self.boundBox
		del self.roadSystem
		del self.terrain
		del self.selected #before Axis Class
		del self.axis
		self.sceneManager.clearScene()
	
	def Destroy(self):
		self.clear()
		if hasattr(self, 'sceneManager'):
			self.sceneManager.destroyQuery(self.selectionRaySceneQuery)
			self.sceneManager.destroyQuery(self.terrainRaySceneQuery)
		rorcommon.deleteFilelist()

	def getCamera(self):
		p = self.camera.getPosition()
		d = self.camera.getDirection()
		return (p.x, p.y, p.z), (d.x, d.y, d.z)
	
	def setCamera(self, position, direction, minusZ=0):
		""" called by CameraBookmark toolwindow
		position - Tuple
		direction - Tuple
		minusZ - allow to move back camera n units
		"""
		
		x, y, z = position
		if minusZ != 0:
			z -= minusZ
		self.camera.setPosition(x, y, z)
		self.camera.setDirection(direction)
		
	def updateDataStructures(self):
		for uuid in self.entries.keys():
			entry = self.entries[uuid]
			if entry.data:
				# avoid imprecision of rotation angles issue
				if entry.data.modified:
					x, y, z, rotx, roty, rotz = self.getPositionRotation(entry.node)
					if entry.data.ext.lower() in noRotateExt:
						rotx -= 90
					entry.data.position = x, y, z
					entry.data.rotation = rotx, roty, rotz
	
	def SaveTerrain(self, fn=None):
		if self.splineMode is not None:
			self.roadSystem.finishSpline()
		self.roadSystem.saveSplines(fn)
		if self.lua.modified:
			self.lua.save(fn) #temp file 
		self.updateDataStructures()
		res = False
		if not self.terrain is None:
			self.cameraBookmark.saveCamera(fn)
			res = self.terrain.save(fn)
			if res: 
				self.currentStatusMsg = "Terrain saved"
			else:
				self.currentStatusMsg = "saving Error"
		return res
	
	def load_terrain_from_project(self, project_dir_name):
		import rortoolkit.terrain
		import rortoolkit.resources

		# Close previously open terrain
		if self.terrain is not None:
			self.clear()
			self._resetVariables()

		# Load project
		project = rortoolkit.terrain.load_project_from_directory(project_dir_name)

		# Setup resources
		project.export_ogre_tsm_config()
		rortoolkit.resources.setup_terrain_project_resources(project)
		rortoolkit.resources.load_builtin_resources()
		rortoolkit.resources.init_all_installdir_resources()

		# create editor context
		self.terrain = rortoolkit.terrain.TerrainEditorContext.create_from_project(project)

		# Configure legacy OGRE TerrainSceneManager
		self.sceneManager.setWorldGeometry(rortoolkit.terrain.OGRE_TSM_CONFIG_FILENAME)

		# Water
		self.createWaterPlane()

		# Sky box
		if self.terrain.cubemap:
			self.sceneManager.setSkyBox(True, self.terrain.cubemap, 0.6)

		# Place rigs
		for beam in self.terrain.beamobjs:
			try:
				self.addTruckToTerrain(data=beam)
			except Exception as e:
				log().error("Loading terrain: Failed to add truck {0} to terrain, message: {1}"
						.format(beam.fileWithExt, str(e)))

		# Place objects
		for obj in self.terrain.objects:
			try:
				self.addObjectToTerrain(data=obj)
			except Exception as e:
				log().error("Loading terrain: Failed to add object {0} to terrain, message: {1}"
					.format(obj.fileWithExt, str(e)))

		# Creating cameramesh
		if self.terrain.CameraStartPosition:
			cam = self.newEntryEx("cam.mesh", "mysimple/terrainselect", False, True, True)
			cam.OnSelecting.append(self.entryChanged) #only update interfaz
			cam.OnPositionChanged.append(self.specialEntryChanged) #update terrain and camera bookmark
			cam.data.scale = 0.1, 0.1, 0.1
			cam.data.name = RORCAMERA
			cam.allowRotation = False
			cam.position = self.terrain.CameraStartPosition.asTuple
			cam.rotation = 0, 90, 0
			cam.heightFromGround = 0.1
			cam.informPositionChanged() #create/modify a camera bookmark entry
		
		# Creating charactermesh
		if self.terrain.CharacterStartPosition:
			character = self.newEntryEx("character.mesh", "mysimple/terrainselect", False, True, True)
			character.OnSelecting.append(self.entryChanged)
			character.OnPositionChanged.append(self.specialEntryChanged)
			character.data.scale = 0.02, 0.02, 0.02
			character.data.name = RORCHARACTER
			character.allowRotation = False
			character.position = self.terrain.CharacterStartPosition.asTuple
			character.rotation = 90, 0, 0
			character.heightFromGround = 0.1
			character.informPositionChanged()

		# Creating Truckmesh
		if self.terrain.TruckStartPosition:
			truck = self.newEntryEx("truckstart.mesh", "mysimple/terrainselect", False, True, True)
			truck.OnSelecting.append(self.entryChanged)
			truck.OnPositionChanged.append(self.specialEntryChanged)
			truck.data.scale = 0.8, 0.8, 0.8
			truck.data.name = RORTRUCK
			truck.allowRotation = False
			truck.position = self.terrain.TruckStartPosition.asTuple
			truck.rotation = 0, 0, 0
			truck.heightFromGround = 0.1
			truck.informPositionChanged()

		self.camera.setPosition(self.terrain.CharacterStartPosition.asTuple)
		self.camera.moveRelative(ogre.Vector3(0, 2, 0))
		
		self.MapOptions.updateData(self.terrain)

	def load_terrain_from_terrn_file(self, filename, progress_window):
		progress_window.set_text("Resetting editor...")
		if not self.terrain is None:
			self.cameraBookmark.saveCamera()
			self.clear()
			self._resetVariables()

		self.roadSystem = RoadSystemClass(self.road, self)

		progress_window.set_text("Creating editor context...")
		import rortoolkit.terrain
		self.terrain = rortoolkit.terrain.TerrainEditorContext.create_from_terrn_file(filename, progress_window)
		if self.terrain.errorSaving != "":
			showInfo("info", "terrain loaded with the following error:\n" + self.terrain.errorSaving)
		
		self.cameraBookmark.load_from_pickle(filename)
		
		progress_window.set_text("Creating terrain...")
		cfgfile = os.path.join(os.path.dirname(filename), self.terrain.TerrainConfig)
		self.sceneManager.setWorldGeometry(cfgfile)
		self.createWaterPlane()
		if self.terrain.cubemap:
			self.sceneManager.setSkyBox(True, self.terrain.cubemap, 0.6)
		#ok let's go fix camera / Truck / character StartPosition if posible!!
		defaultx = ifNone(self.terrain.worldX, 0) / 2
		defaulty = 0
		defaultz = ifNone(self.terrain.worldZ, 0) / 2
		defaulty = ifNone(self.getTerrainHeight(ogre.Vector3(defaultx, defaulty, defaultz)), 0) + 2
		if self.terrain.WaterHeight:
			self.updateWaterPlane(self.terrain.WaterHeight)
			if defaulty < self.terrain.WaterHeight:
				defaulty = self.terrain.WaterHeight
		l = [defaultx, defaulty, defaultz]
		try:
			if self.terrain.CameraStartPosition.isZero():
				self.terrain.CameraStartPosition.asList = l
				l[0] = l[0] + 5
			if self.terrain.CharacterStartPosition.isZero():
				l[1] = self.getTerrainHeight(ogre.Vector3(l[0], l[1], l[2])) + 2
				self.terrain.CharacterStartPosition.asList = l
				l[0] = l[0] + 5
			if self.terrain.TruckStartPosition.isZero():				
				l[1] = self.getTerrainHeight(ogre.Vector3(l[0], l[1], l[2])) + 2
				self.terrain.TruckStartPosition.asList = l

		except Exception, err:
			log().error("Error while setting initial camera:")
			log().error(str(err))
			if rorSettings().stopOnExceptions:
				raise
		
		total = len(self.terrain.beamobjs)
		count = 0
		for beam in self.terrain.beamobjs:
			count += 1
			progress_window.set_text("Placing rig objects\n({0}/{1})\n{2}".format(count, total, beam.fileWithExt))
			progress_window.set_progress(count, total)
			try:
				self.addTruckToTerrain(data=beam)
			except Exception, err:
				log().error("Error while adding a Beam Construction to the terrain. Name: %s" % beam.name)
				log().error(str(err))

		total = len(self.terrain.objects)
		count = 0
		report_every = 25 # The reporting has quite an overhead
		for obj in self.terrain.objects:
			count += 1
			if count % report_every == 0:
				progress_window.set_text("Placing static objects\n({0}/{1})".format(count, total))
				progress_window.set_progress(count, total)
			try:
				newE = self.addObjectToTerrain(data=obj)
			except Exception, err:
				log().error("Error while adding an object to the terrain: Name: %s " % obj.name)
				log().error(str(err))
				if rorSettings().stopOnExceptions:
					raise 
		
		self.currentStatusMsg = "Terrain loaded"
		progress_window.set_text("Creating meshes...")
		progress_window.pulse_mode()

		# Creating cameramesh
		if self.terrain.CameraStartPosition:
			cam = self.newEntryEx("cam.mesh", "mysimple/terrainselect", False, True, True)
			cam.OnSelecting.append(self.entryChanged) #only update interfaz
			cam.OnPositionChanged.append(self.specialEntryChanged) #update terrain and camera bookmark
			cam.data.scale = 0.1, 0.1, 0.1
			cam.data.name = RORCAMERA
			cam.allowRotation = False
			cam.position = self.terrain.CameraStartPosition.asTuple
			cam.rotation = 0, 90, 0
			cam.heightFromGround = 0.1
			cam.informPositionChanged() #create/modify a camera bookmark entry
		
		# Creating charactermesh
		if self.terrain.CharacterStartPosition:
			character = self.newEntryEx("character.mesh", "mysimple/terrainselect", False, True, True)
			character.OnSelecting.append(self.entryChanged)
			character.OnPositionChanged.append(self.specialEntryChanged)
			character.data.scale = 0.02, 0.02, 0.02
			character.data.name = RORCHARACTER
			character.allowRotation = False
			character.position = self.terrain.CharacterStartPosition.asTuple
			character.rotation = 90, 0, 0
			character.heightFromGround = 0.1
			character.informPositionChanged()


		# Creating Truckmesh
		if self.terrain.TruckStartPosition:
			truck = self.newEntryEx("truckstart.mesh", "mysimple/terrainselect", False, True, True)
			truck.OnSelecting.append(self.entryChanged)
			truck.OnPositionChanged.append(self.specialEntryChanged)
			truck.data.scale = 0.8, 0.8, 0.8
			truck.data.name = RORTRUCK
			truck.allowRotation = False
			truck.position = self.terrain.TruckStartPosition.asTuple
			truck.rotation = 0, 0, 0
			truck.heightFromGround = 0.1
			truck.informPositionChanged()
		self.camera.setPosition(self.terrain.CharacterStartPosition.asTuple)
		self.camera.moveRelative(ogre.Vector3(0, 2, 0))
		
		self.MapOptions.updateData(self.terrain)
		self.checkSplineLine()

		self.lua = luaClass(filename, self)
		self.race = self.parent.race
		self.race.luaParser = self.lua
		
	
	def checkSplineLine(self):
		userNames = []
		uuid = []
		for k in self.roadSystem.splines.keys():
			name = self.roadSystem.splines[k]['name']
			if name is not None and name != '':
				userNames.append(name)
			else :
				userNames.append(k)
			uuid.append(k)
		self.road.splines = [uuid, userNames]
		
	def replaceSelectionWith(self, newOdefFilename):
		
		if self.selected.entry and self.selected.entry.data:
			if self.selected.entry.data.name in FIXEDENTRIES:
				rorSettings().mainApp.MessageBox("info", "good try !!, but you didn't success :-P ")
				return
		struid = str(self.selected.entry.uuid)
		newE = self.addGeneralObject(newOdefFilename, coords=(0, 0, 0), rot=(0, 0, 0))
		self.selected.entry.copyDetailsTo(newE)
		self.selected.entry = newE
		self.entries[struid].removeFromScene()
		self.entries.pop(struid)

	def addGeneralObject(self, filename, coords=None, rot=None):
		""" main routine to add any object / truck / load ... to the terrain
		filename - string with extension
		coords = None - Tuple
		rot = None  - Tuple
		
		return entry
		"""
		
		entry = None
		reason = ""
		if filename is None:
			reason = '- Select an object in Object Tree window.\n'
		if coords is None:
			if self.selected.coords.isNone():
				reason += '- Select an empty point of the terrain or an object on the terrain.' 
			else:
				coords = self.selected.coords.asTuple
		
		if reason != "":
			raise showedWarning("Object couldn't be added to the terrain:\n\n" + reason) 
			
		onlyfilename, extension = os.path.splitext(os.path.basename(filename))
		if extension.lower() in VALIDSTRUCKS:
				entry = self.addTruckToTerrain(truckFilename=filename, coords=coords, rot=rot)
		elif extension.lower() == '.odef':
				entry = self.addObjectToTerrain(odefFilename=filename, coords=coords, rot=rot)
		
		if entry is None:
			msg = " Unknown object to add to the terrain.\nPlease note you can only add an object from 'Objects' and\n 'Beam Objects' categories to the terrain.\n"
			raise showedWarning(msg)
		
		return entry

	def addObjectToTerrain(self, data=None, odefFilename=None, coords=None, rot=None,
						   doc=""" - if data != None, data is a pointer to the Object readed from .terrn file
									 - if data is None ror Editor is adding a new object to terrain from Object Tree
									 self.terrain.XXXXX.append(data) will tell RorTerrain class that it should 
									 save this new object.
									 
									 XXXXX may be: objects, beamobjs"""):
		if coords is None:
			coords = self.selected.coords.asTuple
		if rot is None:
			rot = 0, 0, 0
		
		if data is not None:
			coords = data.position
			rot = data.rotation
			 
		if coords is None and data is None:
			log().warning('Can not add an object to the terrain, coords and data is None')
			return None
		
		if data is None:
			import rortoolkit.terrain
			data = rortoolkit.terrain.EditorObject()
			data.fileWithExt = os.path.basename(odefFilename)
			if not self.raceMode:
				self.terrain.objects.append(data)
		else:
			odefFilename = data.fileWithExt

		if data.name in self.knownObjects.keys():
			odefDef = self.knownObjects[data.name]['odefDefinition']
			data.scale = odefDef.scale
		else:
			try:
				odefDef = None
				odefDef = odefClass(odefFilename)
				data.scale = odefDef.scale
			except Exception:
				data.error = True
				log().error("error while processing odef file %s" % odefFilename)
				log().error(Exception.message)
				if rorSettings().stopOnExceptions:
					raise 
				return None

		entry = self.newEntryEx(odefDef.meshName, None, True, True, False)
		entry.data = data
		self.checkKnownDimension(entry, odefDef)
		if len(odefDef.meshMaterial) > 0:
			entry.entity.setMaterialName(odefDef.meshMaterial[0])
		entry.position = coords
		self.applyMisplacement(entry)
		entry.rotation = rot
		if self.raceMode and not self.lua.showingcheckpoints:
			self.lua.races[self.lua.raceIndex].addCheckpoint(entry.data.name, coords, rot, entry)
			self.race.updateCheckpoints()
		return entry 

#===============================================================================
# we need to know object size, so, the first time is added to the terrain
# we calc BoundingBox corners and save in knownObjects for future use
#
# If we have 2.000 roads objects, all of them share the same KnownObjects definition 
#===============================================================================
	def checkKnownDimension(self, entry, odefDef=None): 
		""" Load on the fly object dimension.
		if user was modding or changing anything in files
		always get syncrhonise. So, we won't never save 
		KnownDimension to disk"""
		
		if entry:
			if not entry.data.name in self.knownObjects.keys():
				backupP = entry.position
				backupR = entry.rotation
				entry.node.showBoundingBox(True)
				if odefDef is None and entry.data.type == hardcoded['terrain']['objecttype']['.odef']: #it is an .odef file
					try:
						odefDef = odefClass(entry.data.fileWithExt)
					except Exception:
						entry.data.error = True
						log().error("error while processing odef file %s" % odefFilename)
						log().error(Exception.message)
						odefDef = None
						if rorSettings().stopOnExceptions:
							raise
				entry.position = 0, 0, 0
				entry.rotation = 90, 0, 0 #needed for AABB
				entry.node._updateBounds()
				misPlace = None
				self.knownObjects[entry.data.name] = { 
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
										 },
								 "instanceCount"	: 1,
								 "odefDefinition"   : odefDef,
								 "misPlace"		 : misPlace,
								 }
				self.knownObjects[entry.data.name]["aabb"]["centerUp"] = self.knownObjects[entry.data.name]["aabb"]["nearLeftTop"].midPoint(self.knownObjects[entry.data.name]["aabb"]["farRightTop"]) 
				self.knownObjects[entry.data.name]["long"] = self.knownObjects[entry.data.name]["aabb"]["nearLeftTop"].distance(self.knownObjects[entry.data.name]["aabb"]["farLeftTop"]) 
				self.knownObjects[entry.data.name]["wide"] = self.knownObjects[entry.data.name]["aabb"]["nearLeftTop"].distance(self.knownObjects[entry.data.name]["aabb"]["nearRightTop"]) 
				self.knownObjects[entry.data.name]["height"] = self.knownObjects[entry.data.name]["aabb"]["nearLeftTop"].distance(self.knownObjects[entry.data.name]["aabb"]["nearLeftBottom"])  
				entry.position = backupP
				entry.rotation = backupR
				entry.node.showBoundingBox(False)
				entry.node._updateBounds()
			else:
				self.knownObjects[entry.data.name]["instanceCount"] += 1
			
			k = self.knownObjects[entry.data.name]
			# fixed standard events for spawning boats, trucks, airplanes and repair shops
			# or whatever object who spawn objects
			if k["odefDefinition"] and k["odefDefinition"].isSpawnZone:
				if (len(entry.data.additionalOptions) == 0): 
					h = hardcoded['odef']['event'] 
					event = k["odefDefinition"].event 
					if event != "":
							if h.has_key(event):
								entry.data.additionalOptions.append(h[event])
								entry.data.additionalOptions.append("spawnZone_%s_%d" % (entry.data.name, k["instanceCount"]))

	def deleteObjectFromFile(self, entry):
		if entry:
			if entry.data.name in FIXEDENTRIES:
				raise showedError("This object is always needed. You can not delete it") 
			return True
		return False

	def addTruckToTerrain(self, data=None, truckFilename=None, coords=None, rot=None):
		if coords is None:
			coords = self.selected.coords.asTuple
		if rot is None:
			rot = 0, 0, 0
		
		if data is not None:
			coords = data.position
			rot = data.rotation

		if coords is None and data is None:
			return None

		if data is None:
			import rortoolkit.terrain
			data = rortoolkit.terrain.EditorObject()
			# insert load/truck/machine
			data.fileWithExt = os.path.basename(truckFilename)
		else:
			truckFilename = data.fileWithExt

		theuid = randomID()
		thenode = None
		theentity = None
		themanualobject = None
		try:
			thenode, theentity, themanualobject = createTruckMesh(self.sceneManager, truckFilename, theuid)
		except Exception, err:
			log().error("Error adding a Beam construction to the terrain")
			log().error(str(err))
			raise 

		entry = self.newEntry(True, False)
		entry.uuid = theuid		
		entry.manualobject = themanualobject
		entry.node = thenode
		entry.entity = theentity
		entry.data = data
		entry.position = coords
		entry.allowRotation = False
		# RORBUGFIX: RoR trucks and trailers can not be rotated or rear are reversed (reverse gear are fordward movement and main gears goes backwards
		entry.rotation = 0, 0, 0
#		print "rotation data of truck "  + str(entry.data.rotation)
		self.checkKnownDimension(entry)
		self.entries[entry.uuid] = entry
		if not entry.data in self.terrain.beamobjs:
			self.terrain.beamobjs.append(entry.data)
		return entry

	def getPointedPosition(self, event,
						doc=""" return Vector3 """):
		x, y = event.GetPosition() 
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()
		mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
		myRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
		myRaySceneQuery.setRay(mouseRay)
		result = myRaySceneQuery.execute()
		final = None
		if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
			final = result[0].worldFragment.singleIntersection
		if not self.terrain.isInWorld(self.camera.getPosition()):
			rorSettings().mainApp.MessageBox("info", "Your camera position is out of terrain dimensions, so you can select nothing. \n\n Please 'return to our World dimension' ;-)")
		self.sceneManager.destroyQuery(myRaySceneQuery)
		return final

	def populateScene(self):
		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7)

		fadeColour = (0.8, 0.8, 0.8)
#		self.sceneManager.setFog(ogre.FOG_LINEAR, fadeColour, 0.001, 5000.0, 10000.0)
		self.renderWindow.getViewport(0).BackgroundColour = fadeColour

		#create ray template
		# to know active selection
		self.selectionRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
		#to stick to ground
		self.terrainRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
		
		# setup the sky plane
		plane = ogre.Plane()
		plane.d = 5000
		plane.normal = -ogre.Vector3(0, 1, 0)

	def stickVectorToGround(self, nPos):
		nRay = ogre.Ray(ogre.Vector3(nPos.x, 5000, nPos.z), ogre.Vector3(0, -1, 0))
		self.terrainRaySceneQuery.setRay(nRay)
		#Perform the scene query
		result = self.terrainRaySceneQuery.execute()
		if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
			terrainHeight = result[0].worldFragment.singleIntersection.y
			return ogre.Vector3(nPos.x, terrainHeight, nPos.z)
		return nPos

	def ObjectResetRotation(self, rotx=False, roty=False, rotz=False):
		if self.selected.entry:
			rx, ry, rz = self.selected.entry.rotation
			if rotx:	rx = 0
			if roty:	ry = 0
			if rotz:	rz = 0
			self.selected.entry.node.resetOrientation()
			self.selected.entry.rotation = rx, ry, rz
			self.RotateNode.resetOrientation()
			self.RotateNode.setOrientation(self.selected.entry.node.getOrientation())

	def selectTerrain(self):
		self.selected.type = "terrain"
		self.selected.entry = None
		

	def _getCameraToViewportRay(self, screen_x, screen_y):
		width  = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()
		return self.camera.getCameraToViewportRay((screen_x / float(width)), (screen_y / float(height)))	

	def _updateMapSelection(self, event):
		x, y = event.GetPosition() 

		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()

		self.renderWindow.update()
		mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
		self.selectionRaySceneQuery.setRay(mouseRay)
		self.selectionRaySceneQuery.setSortByDistance(True)
		result = self.selectionRaySceneQuery.execute()

		#ensure that arrows are selected first, always!
		for r in result:
			if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
				if r.movable.getName() in self.axis.arrowNames:
					self.axis.arrow = r.movable
					return
					
		selectedSomething = False
		if len(self.ignorearray) > 20:
			self.ignorearray = []
		self.ignorearray.append("circlepointer")
		if not self.terrain.WaterHeight is None:
			self.ignorearray.append(self.waterentity.getName())
		menu = wx.Menu()
		self.popupSelection = {}
		try:
			for r in result:
				try:
					if r is not None and r.movable is not None and r.movable.getMovableType() == "Entity":
							name = r.movable.getName()
							if name in self.ignorearray:
								# you cannot select these objects
								continue
							realname = name[:-len('entity')]
							if self.entries.has_key(realname): 
								# invisible or deleted object not selectables
								if not self.entries[realname].visible:
									continue	
								if not self.entries[realname].canBeSelected:
									continue
								if self.entries[realname].data:
									if self.entries[realname].deleted:
										continue
							if not self.selected.entry is None and self.selected.entry.entity.getName() == name:
								continue
							rorname = self.getRoRName(r.movable)
							if rorname != '':
								item = menu.Append(wx.ID_ANY, rorname)
								self.Bind(wx.EVT_MENU, self.go, item)
								self.popupSelection[str(item.GetId())] = self.getEntry(r.movable)
							if not self.usePopup:
								break 
				except:
					if rorSettings().rorDebug:
						raise
				# when deleting an object from OgreScene, the object persist on there, eventhough after renderwindow.update()
				# if you click at the position the entity was, you get an access violation :-(
		finally:
			# breaking jump here
			pass
		self.axis.arrow = None
		if menu.GetMenuItemCount() == 1 :
			if self.selected.entry is None or not self.addtomultiselect: self.selected.entry = self.popupSelection[str(item.GetId())]
			elif self.addtomultiselect: self.selected.add(self.popupSelection[str(item.GetId())])
		elif menu.GetMenuItemCount() == 0 :
			self.selectTerrain()
		if self.usePopup and menu.GetMenuItemCount() > 1:			
			item = menu.Append(wx.ID_ANY, "Ground")
			self.Bind(wx.EVT_MENU, self.go, item)
			self.popupSelection[str(item.GetId())] = None
			self.PopupMenu(menu)

		menu.Destroy()
		return

	def go(self, event):
		selkey = str(event.GetId())
		if self.popupSelection[selkey] is None:
			self.selectTerrain()
		else:
			if self.selected.entry is None or not self.addtomultiselect: self.selected.entry = self.popupSelection[selkey]
			elif self.addtomultiselect: self.selected.add(self.popupSelection[selkey])

	def controlSelectedObject(self, action, value):
		pass

	def addObjectToHistory(self, entry):
		if len(self.commandhistory) > 0:
			if self.historypointer < len(self.commandhistory):
				del self.commandhistory[self.historypointer:]

		pos = entry.node.getPosition()
		rot = entry.node.getOrientation()
					
		if len(self.commandhistory) > 0:
			# check if double
			hentry = self.commandhistory[ -1]
			if hentry.position == pos and hentry.rotation == rot:
				return
		
		hentry = HistoryEntryClass()
		hentry.uuid = entry.uuid
		hentry.position = pos
		hentry.rotation = rot
		self.commandhistory.append(hentry)
		self.historypointer = len(self.commandhistory)

	def undoHistory(self):
		if self.historypointer == 0:
			self.currentStatusMsg = "nothing to undo"
			return
		self.axis.arrow = None
		
		
		self.historypointer -= 1
		hentry = self.commandhistory[self.historypointer]
		self.entries[hentry.uuid].node.setPosition(hentry.position)
		self.entries[hentry.uuid].node.setOrientation(hentry.rotation)
		self.selected.entry = self.entries[hentry.uuid]
		# update node positions
		self.currentStatusMsg = "undo step %d of %d" % (self.historypointer + 1, len(self.commandhistory))
		
	def redoHistory(self):
		if self.historypointer + 1 >= len(self.commandhistory):
			self.currentStatusMsg = "nothing to redo"
			return
		self.axis.arrow = None		
		
		self.historypointer += 1
		hentry = self.commandhistory[self.historypointer]
		self.entries[hentry.uuid].node.setPosition(hentry.position)
		self.entries[hentry.uuid].node.setOrientation(hentry.rotation)
		self.selected.type = 'object'
		self.selected.entry = self.entries[hentry.uuid]
		self.currentStatusMsg = "redo step %d of %d" % (self.historypointer + 1, len(self.commandhistory))

	def _translateSelected(self, axis_ogre, mouse_x1, mouse_y1, mouse_x2, mouse_y2):
		"""
		Translates selected object based on mouse input.
		:param string axis_str: X/Y/Z - OGRE world space (Y = up)
		"""
		
		if not self.selected.entry:
			return
		
		pivot = self.selected.entry.node._getDerivedPosition()
		was_success, offset = self._mouse_world_transforms.mouse_translate_along_axis(
			pivot, axis_ogre, mouse_x1, mouse_y1, mouse_x2, mouse_y2)
		if not was_success:
			return
		newpos = pivot + offset			
		self.selected.entry.position = newpos.x, newpos.y, newpos.z
		
		# Post-process
		self.selected.entry.data.modified = True
		self.selected.axis.attachTo(self.selected.entry.node)
		self.addObjectToHistory(self.selected.entry)

	def rotateSelected(self, axis, amount, steps=True):
		if not self.selected.entry:
			return
		if len(self.selected.entries) > 0 : 
			self.selected.multiselectNode.rotate(axis, amount, relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
			self.selected.axis.rotateNode.rotate(axis, amount, relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
			return
		else:
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
		
			newrot = self.selected.entry.node.getOrientation()
		
		self.addObjectToHistory(self.selected.entry)
		self.selected.entry.data.modified = True
		self.selected.entry.ogreRotation = newrot
		self.selected.axis.rotateNode.setOrientation(newrot)

	def addSelectedFromTO(self):
		if self.parent.ObjectTree is None:
			NoObjecTreeCreated = 'No Object tree created yet!!'
			raise logTerrainEditorError(NoObjecTreeCreated)
		if self.parent.ObjectTree.selectedfn is None:
			raise showedError("Please, select an object in Object Tree before pressing Space")

		if self.selected.entry is None:
			raise showedError("Please select an object in 3D window before pressing Space")
		oFilename = self.parent.ObjectTree.selectedfn
		# allow to use block mode with beam objects and statics objects
		# we do creating a child node so rotation and position will match with the selected one.
		entry = self.addGeneralObject(oFilename)
		if entry is None: return

		entry.changeParentTo(self.selected.entry.node)
		entry.ogrePosition = 0, 0, 0
		entry.node.resetOrientation()

		baseentry = self.selected.entry
		theY = baseentry.details["aabb"]["farMiddle"].y + baseentry.y
		entry.node.showBoundingBox(True)
		entry.node._updateBounds()
		entry.node.translate(self.selected.entry.details["aabb"]["farMiddle"] - entry.details["aabb"]["nearMiddle"])
		self.applyMisplacement(entry) #applied on addGeneralObject but reseted here !!!
#		entry.logPosRot("before parent")
		p = entry.node._getDerivedPosition()
		o = entry.node._getDerivedOrientation()
		entry.changeParentTo(None)
#		self.selected.entry.node.removeChild(entry.node)
#		self.sceneManager.getRootSceneNode().addChild(entry.node)
		entry.position = p.x, theY, p.z 
		entry.ogreRotation = o
#		self.zoomCamera(self.selected.entry.node.getPosition(), p)
		entry.node._updateBounds()
		self.selected.entry = entry
		return True

	def applyMisplacement(self, entry):
		if entry.details["misPlace"]:
			if not entry.details["misPlace"].isZero():
				mx = 0.0
				my = 0.0
				mz = 0.0
				if abs(entry.details["misPlace"].x) > 0.001: mx = entry.details["misPlace"].x
				if abs(entry.details["misPlace"].y) > 0.001: my = entry.details["misPlace"].y
				if abs(entry.details["misPlace"].z) > 0.001: mz = entry.details["misPlace"].z
				entry.node.translate((mx, my, mz), ogre.Node.TransformSpace.TS_LOCAL)
				log().debug("Applying misPlace %s to %s" % (", ".join(entry.details["misPlace"].asStrList), entry.data.name))

	def createDots(self, entry):
		""" create dots mesh on each aabb corner of an entry just for debugging
			return a dictionary with entries of Upper face"""
		toReturn = {}	
		pos = entry.node._getDerivedPosition()
		entry.node._updateBounds()
		main = entry.node.createChildSceneNode()
		for v in entry.details["aabb"].keys():
			p = self.newEntryEx("ellipsoid.mesh", "TruckEditor/NodeExhaustReference", True, True , True, main)
			p.data.scale = 0.12, 0.32, 0.12
			p.data.name = "point_%s" % v
			p.allowRotation = False
			pos = entry.details["aabb"][v]
			p.node.setPosition(pos.x, pos.y, pos.z)
			p.logPosRot(p.data.name)
			if v in ["farMiddle", "nearLeftTop", "nearRightTop", "farLeftTop", "farRightTop"]:
				toReturn[v] = p
		return toReturn

	def createDotAt(self, x, y, z, color=CLBLUE, sufix='', parentNode=None):
		p = self.newEntryEx("ellipsoid.mesh", color, True, True , True, parentNode, sufix)
		p.data.scale = 1, 1, 1
		p.allowRotation = False
		if sufix == '':
			p.data.name = "dot_%s" % (str(p.uuid)[:5])
		else:
			p.data.name = "%s_dot" % sufix
		p.node.setPosition(x, y, z)
		p.autoRemoveFromScene = True
		return p

	def createDot(self, entry, corner="", color=CLBLUE):
		""" create a dot on the corner of entry"""
		p = self.newEntryEx("ellipsoid.mesh", "TruckEditor/NodeExhaustReference", True, True , True, entry.node)
		p.data.scale = 0.12, 0.32, 0.12
		p.data.name = "point_%s" % str(p.uuid)
		p.allowRotation = False
		if not entry.details["aabb"].has_key(corner):
			log().error("%s is not a valid corner, please see KnownObjects aabb" % corner)

		pos = entry.details["aabb"][corner]
		p.node.setPosition(pos.x, pos.y, pos.z)
		p.logPosRot(p.data.name)
		return p

	def maxTerrainHeightOf(self, mydict):
		""" return the max of terrainHeight from 
			upper face of AABB node""" 
		if mydict:
			cp = [] # control points to get max terrain height
			for v in mydict.keys():
				cp.append(self.getTerrainHeight(mydict[v].node._getDerivedPosition()))
			cp.sort(reverse=True)
			return cp[0]
		else:
			log().info("I can not get control points terrain height from a empty dictionary")
			return 0

	def _onSelectionControlArrowsMouseEvent(self, event):

		if not (event.Dragging() and event.LeftIsDown()):
			return
			
		screen_x, screen_y = event.GetPosition()
		# TODO: Code something better
		# Currently, mouse X movement translates to object world-axis movement,
		#    regardless on the screen orientation of the axis.
		forcex = float(self._mouse_drag_start_screen_x - screen_x)
		forcex /= 2
		if event.ShiftDown():
			forcex /= 10
	
		LockSteps = event.AltDown()
		forceDegree = ogre.Degree(forcex).valueRadians()
		
		self.movingEntry = True
		arrow_name = self.selected.axis.arrow.getName()
		translate_axis = None
		if arrow_name == self.selected.axis.arrowNames[0]:
			 translate_axis = "X"
		elif arrow_name == self.selected.axis.arrowNames[1]:
			translate_axis = "Y"
		elif arrow_name == self.selected.axis.arrowNames[2]:
			translate_axis = "Z"
		elif arrow_name == self.selected.axis.arrowNames[3]:
			self.rotateSelected(ogre.Vector3(0, 1, 0), forceDegree, LockSteps)
		elif arrow_name == self.selected.axis.arrowNames[4]:
			self.rotateSelected(ogre.Vector3(1, 0, 0), forceDegree, LockSteps)
		elif arrow_name == self.selected.axis.arrowNames[5]:
			self.rotateSelected(ogre.Vector3(0, 0, 1), forceDegree, LockSteps)
			
		if translate_axis is not None:
			# Fix axis -> OGRE world space
			if translate_axis == "Z":
				translate_axis = "Y"
			elif translate_axis == "Y":
				translate_axis = "Z"
		
			self._translateSelected(translate_axis, 
				self._mouse_drag_start_screen_x, 
				self._mouse_drag_start_screen_y,
				screen_x, screen_y)
			
		self._mouse_drag_start_screen_x, self._mouse_drag_start_screen_y = event.GetPosition()

	def getTerrainHeight(self, pos):
		""" pos is a Vector3 by node.getPosition()"""
		if pos is not None:
			tmp = pos.y
			pos.y = 5000
			ray = ogre.Ray(pos, ogre.Vector3(0, -1, 0))
			self.terrainRaySceneQuery.setRay(ray)
			#Perform the scene query
			self.terrainRaySceneQuery.setQueryTypeMask(0)
			result = self.terrainRaySceneQuery.execute()
			pos.y = tmp
			if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
				return result[0].worldFragment.singleIntersection.y

		return None

	def onMouseEvent(self, event):
		if self.terrain is None:
			return
		if event.ButtonDown(wx.MOUSE_BTN_RIGHT):
			self._RMBHere = True
		if event.ButtonUp(wx.MOUSE_BTN_RIGHT):
			self._RMBHere = False
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()

		if event.MiddleDown() and self._placeWithMouse:
			self.selected.coords.asVector3 = self.getPointedPosition(event) + ogre.Vector3(0, 0.1, 0)
			self.addGeneralObject(self._object_tree_window.selectedfn)

		if self.selected.axis.arrow is None and event.GetWheelRotation() != 0:
			dir = 5
			if event.ShiftDown():
				dir *= self.cameraShiftVel   # speed is increased by a factor of 16
						
			if event.GetWheelRotation() > 0:
				dir *= -1   # move backwards
			
			self.moveVector += ogre.Vector3(0, 0, dir)
		if event.RightDown() or event.LeftDown():
			self.SetFocus()
		# ignore selected arrow if control key is pressed
		if not event.ControlDown() and 	self.selected.axis.arrow is not None:
			self._onSelectionControlArrowsMouseEvent(event)
		
		#here was spline
	
		if event.RightDown() and self._RMBHere: #Precedes dragging 
			self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click 
			self.autoTracking = False
		if event.Dragging() and event.RightIsDown() and event.ControlDown() and self._RMBHere:
			x, y = event.GetPosition() 
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y 
			if event.ShiftDown():
				dx = float(dx) / 10
				dy = float(dy) / 10
			self.camera.moveRelative(ogre.Vector3(dx, -dy, 0))
		elif event.Dragging() and event.RightIsDown() and self._RMBHere: #Dragging with RMB 
			x, y = event.GetPosition() 
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y 

			self.camera.yaw(ogre.Degree(dx / 3.0)) 
			self.camera.pitch(ogre.Degree(dy / 3.0)) 
		
		if event.LeftDown() and not event.ControlDown():
			if event.ShiftDown(): #get distance from previous entry to the new
				oldPos = self.selected.coords.asVector3
			self.selected.coords.asVector3 = self.getPointedPosition(event)	
			self.addtomultiselect = event.ShiftDown()
			self._updateMapSelection(event)
			self._mouse_drag_start_screen_x, self._mouse_drag_start_screen_y = event.GetPosition() #saves position of initial click 
			if event.ShiftDown():
				log().info('distance : %.3f' % (oldPos.distance(self.selected.coords.asVector3)))
		if (event.LeftDown()) and self.splineMode:
# if a big object represent a city /sky etc, every click in splineMode will make splineline to stick to 
# this object... not good
#			if self.selected.entry is not None:
#				frompoint = self.selected.entry.node.getPosition()
#			else:
			frompoint = self.getPointedPosition(event)
																
			self.roadSystem.createSplineLine(startAt=frompoint)
			
		if not event.Dragging() and event.LeftIsDown() and (not self.selected.entry is None) and event.ControlDown():
			self.selected.mouseOffset = self.getPointedPosition(event) - self.selected.entry.node.getPosition()
		#freedom movement
		if event.Dragging() and event.LeftIsDown() and (not self.selected.entry is None) and event.ControlDown(): 
			mousepos = self.getPointedPosition(event)
			if not mousepos is None:
				self.movingEntry = True
				self.autoTracking = False
				self.addObjectToHistory(self.selected.entry)
				objpos = self.selected.entry.ogrePosition
				oldHG = self.selected.entry.heightFromGround
				# mouse is not pointing to (0,0,0) object coordenate, so an offset is required
				offset = self.selected.mouseOffset
				final = (mousepos - offset)
				self.selected.entry.position = final.x, final.y, final.z
				self.selected.entry.data.modified = True
				self.selected.entry.heightFromGround = oldHG 
#				self.axis.attachTo(self.selected.entry.node)
		if event.LeftUp() and self.movingEntry:
			if self.selected.entry is not None:
				self.selected.entry.informPositionChanged()
			self.movingEntry = False
		elif event.Dragging() and event.LeftIsDown() and not event.ControlDown() and self.axis.arrow is None and event.ShiftDown():
			""" a selectionbox is created and it is the selected entry
			the rest of objects are child of self.selected.multiselectNode.
			
			the problem is that selectionBox is UNselectable and it changes its position while selecting others objects
			
			selecting with SHIFT key works properly
			selecting with sphere doesn't work properly
			"""
			if self.sphere is None:
				p = self.selected.coords.asVector3
				self.selectionBox = self.createDotAt(p.x, p.y, p.z, CLBLUE, "multiselectDot")
				self.selectionBox.allowRotation = True
				self.selectionBox.entity.setMaterialName('mysimple/translucientred')
				self.selectionBox.OnPositionChanged.append(self.moveSelection)
#				self.selectionBox.OnDeselecting.append(self.hideSelectionBox)
				self.sphere = ogre.Sphere()
				self.sphereQuery = self.sceneManager.createSphereQuery(self.sphere)
			
			if self.selected.entry <> self.selectionBox : 
				self.selectionBox.ogrePosition = self.selected.coords.asVector3
				self.selected.entry = self.selectionBox

			self.selectionBox.visible = True
			
			s = self.getPointedPosition(event).distance(self.selected.coords.asVector3) / 2	
			center = self.getPointedPosition(event).midPoint(self.selected.coords.asVector3)
			self.ignorearray = []
			self.ignorearray.append('circlepointer')
			self.ignorearray.append('waterPlane')
			self.ignorearray.extend(self.axis.arrowNames)
			self.ignorearray.append(str(self.selectionBox.uuid))
			self.selectionBox.node.setScale(s, s, s)
			self.selectionBox.node.setPosition(center)
			self.selectionBox.node._updateBounds()
			self.sphere.setCenter(center)
			self.sphere.setRadius(s)
			self.sphereQuery.setSphere(self.sphere)
#			self.selected.add(self.selectionBox)
#			self.log(' radius at, point at', [s, center.x, center.y, center.z])
			result = None
#			self.selected.remove(None) #remove actual selection
#			self.hideBoundingBox()
			try:
				result = self.sphereQuery.execute()
#				log().debug('sphere query')
				for r in result.movables:
					if not r is None and r.getMovableType() == "Entity":
						name = r.getName()
						name = name[:-len("entity")]
						if name.find("multiselectDot") == -1 :
							if self.entries.has_key(name):
								self.selected.add(self.entries[name])
#								if r.isAttached():
#									r.getParentSceneNode().showBoundingBox(True)
			except Exception, err:
				log().error(str(err))
				raise

	def moveSelection(self, entry):
		"selectionBox had been moved with freedom movement"
		pass

	def hideBoundingBox(self):
			for e in self.entries:
				self.entries[e].node.showBoundingBox(False)

	def onKeyDown(self, event):
		if self.terrain is None:
			return

		d = self.cameraVel 
		if self.cameraQuick:
			d *= (self.cameraShiftVel / 2)
		forceDegree = ogre.Degree(1).valueRadians()
		LockSteps = False
		
		if event.ShiftDown():
			d *= self.cameraShiftVel
		elif event.m_keyCode == wx.WXK_CAPITAL:
			self.cameraQuick = not self.cameraQuick
			self.showOverlay('POCore/run', self.cameraQuick)

		elif event.m_keyCode == WXK_B: # B
			e = self.addGeneralObject('road.odef', self.selected.coords.asTuple, (0, 0, 0))
			e.y += 0.1
			ry = 0.0
			y = 0.0
			for i in range (0, 25):
				p = e.node.getPosition()
				self.boundBox.dockTo(e)
				p = self.boundBox.realPos((5, 0, 0))
				angle = -25
				px, py, pz, rx, ry, rz = e.roadLookAt(p, angle)
				if ry + angle < -179:
					p.y -= 0.11
#					ry += 10
				else:
					ry += angle
					p.y += 0.11
				e = self.addGeneralObject('road.odef', (p.x, p.y, p.z), (rx, ry, rz))
				log().debug('ry %.3f' % ry) 
				

# works too
#			e.y += 0.2
#			ry = 0.0
#			for i in range (0,25):
#				p = e.node.getPosition()
#				self.boundBox.dockTo(e)
#				p = self.boundBox.realPos((3,0,0))
#				rx, ry, rz = e.roadLookAt(p, -10)
#				ry -= 10
#				e = self.addGeneralObject('road.odef',(p.x, p.y,p.z), (rx, ry, rz)) 
#				
#			next = ogre.Vector3(x, 0, x)
			# works
#			for i in range(0, 25):
#				rx, ry, rz = e.rotation
#
#				p = self.boundBox.realPos((3, 0, 0))
#				ry += 10
#				e = self.addGeneralObject('road.odef', (p.x, p.y, p.z), (rx, ry, rz))
#				self.boundBox.dockTo(e)
				
#			self.showOverlay('POCore/workingSpline', True)
#			self.roadSystem.walkOnRoads = not self.roadSystem.walkOnRoads
#			pass
		if event.m_keyCode == WXK_A: #  A, wx.WXK_LEFT:
			self.keyPress.x = -d
		elif event.m_keyCode == wx.WXK_INSERT:
			if self.selected:
				e = self.addGeneralObject(self._object_tree_window.selectedfn)
		
		elif event.m_keyCode == wx.WXK_DELETE:
			# delete key
			if self.deleteObjectFromFile(self.selected.entry):
				uid = str(self.selected.entry.uuid)
				if self.selected.entry.data.name.find('splinePoint_') > -1:
					pos = int (self.selected.entry.data.name.split('_')[1])
					self.selected.entry.visible = False
					self.selected.entry = None
					self.roadSystem.insertPoint(pos, None)
				else:
					self.selected.entry = None
					e = self.entries.pop(uid)
					e.visible = False
					e.autoRemoveFromScene = True
					e.deleted = True #inform on deleting
					del e
				
			
		elif event.m_keyCode == WXK_D: # D, wx.WXK_RIGHT:
			self.keyPress.x = d
		elif event.m_keyCode == WXK_W: # W ,wx.WXK_UP:
			self.keyPress.z = -d
		elif event.m_keyCode == WXK_S: # S, wx.WXK_DOWN:
			self.keyPress.z = d
		elif event.m_keyCode == WXK_F: # F
			self.keyPress.y = d
		elif event.m_keyCode == WXK_V: # V
			self.keyPress.y = -d
		elif event.m_keyCode == wx.WXK_PAGEUP: 
			self.undoHistory()
		elif event.m_keyCode == wx.WXK_PAGEDOWN: 
			self.redoHistory()
			
		elif event.m_keyCode == WXK_Q: 
			self.autoTracking = not self.autoTracking
			self.showOverlay('POCore/autotrack', self.autoTracking)
		elif event.m_keyCode == WXK_T: # 84 = T
			self.setFiltering()
		elif event.m_keyCode == WXK_R: # 82 = R
			self.setWireframe()
		elif event.m_keyCode == WXK_P: # 80 = P
			if self.selected.entry is None:
				print self.selected.coords.format("0.0,0.0,0.0, terrain")
			else:
				self.selected.entry.logPosRot(self.selected.entry.data.name)
				
		elif event.m_keyCode == WXK_X:
			if self.selected.entry is not None:
				self.selected.entry.node.rotate(ogre.Vector3(1, 0, 0), ogre.Degree(90))
		elif event.m_keyCode == WXK_Y: # Y ogre is Z on RoR
			if self.selected.entry is not None:
				self.selected.entry.node.rotate(ogre.Vector3(0, 0, 1), ogre.Degree(90))
			
		elif event.m_keyCode == WXK_Z:					
			if self.selected.entry is not None:
				self.selected.entry.node.rotate(ogre.Vector3(0, 1, 0), ogre.Degree(90))
			  
		elif event.m_keyCode == WXK_C:
			self.cameraCollision = not self.cameraCollision
		elif event.m_keyCode == wx.WXK_SPACE:
			self.addSelectedFromTO()
			sleep(PAUSE_PER_SECOND / 10)
		# rotating with keyboard
		elif event.m_keyCode == WXK_U:
			self.rotateSelected(ogre.Vector3(0, 1, 0), -forceDegree, LockSteps)
		elif event.m_keyCode == WXK_I:
			self.ObjectResetRotation(rotz=True)
		elif event.m_keyCode == WXK_O:
			self.rotateSelected(ogre.Vector3(0, 1, 0), forceDegree, LockSteps)

		elif event.m_keyCode == WXK_J:
			self.rotateSelected(ogre.Vector3(0, 0, 1), forceDegree, LockSteps)
		elif event.m_keyCode == WXK_K:
			self.ObjectResetRotation(roty=True)
		elif event.m_keyCode == WXK_L:
			self.rotateSelected(ogre.Vector3(0, 0, 1), -forceDegree, LockSteps)
		
		elif event.m_keyCode == WXK_DOT:
			self.rotateSelected(ogre.Vector3(1, 0, 0), forceDegree, LockSteps)
		elif event.m_keyCode == WXK_COMMA:
			self.ObjectResetRotation(rotx=True)			
		elif event.m_keyCode == WXK_M:
			self.rotateSelected(ogre.Vector3(1, 0, 0), -forceDegree, LockSteps)

		elif event.m_keyCode == wx.WXK_F4:  # print all info of the object 
			if self.selected.entry:
				self.ObjectDetails()
	
		if event.m_keyCode == wx.WXK_F5:
			self.statisticsOn = not self.statisticsOn
			self.showOverlay('POCore/DebugOverlay', self.statisticsOn)
			self.updateStatistics()
		# adding to preLoad
		if event.m_keyCode == wx.WXK_F1:
			if self.selected.entry is None:
				rorSettings().mainApp.MessageBox('info', 'Select an object before pressing F1\n to enter on Preload system mode.')
				
			if self.selected.entry:
				help = """ 
	Welcome to Preload System !!
This allow to correct the position and rotation of some objects 
each time you add it to the terrain.

How it works?
- Add the object you want to the terrain.
- Press F1 key to grab its position and rotation (you have already done)
- move and/or rotate the object.
- Press F2 key to finish.

Add new objects of the same type to the terrain pressing SPACE key, if 
you see it is misplace or misrotated unproperly, 
press F3 key to reset Preload system for the object and start again.


If you pressed F1 by mistake, don't press F1 nor F2 nor F3 keys.
\n"""								
				rorSettings().mainApp.MessageBox('info', help)
				log().debug("enter at Preload System")

				self.preLoadPosition = self.selected.entry.node._getDerivedPosition()
				self.selected.entry.rotation = 0, 0, 0
				self.preLoadRotation = 0.0, 0.0, 0.0
#				self.preLoadRotation = self.selected.entry.node._getDerivedOrientation()
				self.selected.entry.logPosRot("preload ")
		elif event.m_keyCode == wx.WXK_F2:
			if self.selected.entry:
				theName = self.selected.entry.data.name
				if not theName in self.preLoad.keys():
					self.preLoad[theName] = {"position": positionClass(), "rotation":rotationClass()}
				self.preLoad[theName]["position"].asVector3 = self.selected.entry.node._getDerivedPosition() - self.preLoadPosition
				self.selected.entry.logPosRot("after move/rotate")
				x, y, z = self.preLoad[theName]["position"].asTuple
				self.log("Missplace to apply ", [x, y, z])
				if self.knownObjects.has_key(theName):
					self.knownObjects[theName]["misPlace"] = self.preLoad[theName]["position"]
		elif event.m_keyCode == wx.WXK_F3:
			if self.selected.entry:
				theName = self.selected.entry.data.name
				if theName in self.preLoad.keys():
					self.preLoad[theName]["position"].asTuple = 0, 0, 0
					log().info(theName + " preLoad reseted")
				if self.knownObjects.has_key(theName):
					if self.knownObjects[theName]["misPlace"] is not None:
						self.knownObjects[theName]["misPlace"].asTuple = 0, 0, 0
		event.Skip()

	def onKeyUp(self, event):
		if self.terrain is None:
			return
		if event.m_keyCode == WXK_A: # A, wx.WXK_LEFT:
			self.keyPress.x = 0
		elif event.m_keyCode == WXK_D: # D, wx.WXK_RIGHT:
			self.keyPress.x = 0
		elif event.m_keyCode == WXK_W: # W ,wx.WXK_UP:
			self.keyPress.z = 0
		elif event.m_keyCode == WXK_S: # S, wx.WXK_DOWN:
			self.keyPress.z = 0
		elif event.m_keyCode == WXK_F:
			self.keyPress.y = 0
		elif event.m_keyCode == WXK_V:
			self.keyPress.y = 0
			
		event.Skip()

	def setFiltering(self):
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

	def setWireframe(self):
		detailsLevel = [ogre.PM_SOLID, ogre.PM_WIREFRAME, ogre.PM_POINTS]
		self.sceneDetailIndex = (self.sceneDetailIndex + 1) % len(detailsLevel)
		self.camera.polygonMode = detailsLevel[self.sceneDetailIndex]
	
	def givePoints(self, first, last, points):
		middle = first.midPoint(last)
		if first.distance(last) > 40:
			self.givePoints(first, middle, points)
			self.givePoints(middle, last, points)
		else:
			points.append(last)

	def getterrainWaterHeight(self, pos):
		y = self.getTerrainHeight(pos)
		if (y is not None) and (self.terrain.WaterHeight is not None):
			if self.terrain.WaterHeight > y :
				return self.terrain.WaterHeight + 1
		return y

	def maxTerrainHeightOf(self, mydict):
		""" return the max of terrainHeight from 
			upper face of AABB node""" 
		if mydict:
			cp = [] # control points to get max terrain height
			for v in mydict.keys():
				cp.append(self.getTerrainHeight(mydict[v].node._getDerivedPosition()))
			cp.sort(reverse=True)
			return cp[0]
		else:
			log().info("I can not get control points terrain height from a empty dictionary")
			return 0

	def maxterrainWaterHeight(self, atPos):
		""" atPos is a vector3 
		
		return a list
		Vector 3 at level of terrain/water, isWaterHeight 
		"""
		ht = self.getTerrainHeight(atPos)
		if ht is None : ht = 0.0
		w = self.terrain.WaterHeight
		if w is None : w = 0.0 
		if w > ht:
			return [ogre.Vector3(atPos.x, w , atPos.z), True]
		return [ogre.Vector3(atPos.x, ht, atPos.z), False]

	def log(self, text, param=[]):
		""" easy log any floating values, for example: 
			self.log(' data position is: ', [data.x, data.y, data.z]) 
			self.log(' vector3 ', vector)
		"""
		
		if isinstance(param, ogre.Vector3):
			param = [param.x, param.y, param.z]
			
		log().info(text.ljust(17) + " " + " ".join(["%.6f" % x for x in param]))
	

	def updateStatistics(self):
		statistics = self.renderWindow
		self._setGuiCaption('POCore/AverageFps', 'Avg FPS: %u' % statistics.getAverageFPS())
		self._setGuiCaption('POCore/CurrFps', 'FPS: %u' % statistics.getLastFPS())
		self._setGuiCaption('POCore/NumTris', 'Trianges: %u' % statistics.getTriangleCount())
		self._setGuiCaption('POCore/NumBatches', 'Batches: %u' % statistics.batchCount)
		
#		self._setGuiCaption('POCore/DebugText', Application.debugText)

	def _setGuiCaption(self, elementName, text):
		element = ogre.OverlayManager.getSingleton().getOverlayElement(elementName, False)
		element.setCaption(text) # ogre.UTFString(text))
	def MapStatistics(self):
		totalObjects = 0
		totalMeters = 0
		tmp = ""
		for k in self.knownObjects.keys():
			tmp += " %10d %s \n" % (self.knownObjects[k]["instanceCount"], k)
			totalObjects += self.knownObjects[k]["instanceCount"]
			if k in ['road', 'roadborderleft', 'roadborderright', 'roadborderboth', 'roadbridge']:
				totalMeters += 10 * self.knownObjects[k]["instanceCount"]
		msg = "Map Statistics for  %s (%s): \n" % (self.terrain.TerrainName, self.terrain.project_title)
		msg += "\n\n %9.2f Km of roads\n" % (float(totalMeters / 1000.0))
		msg += "%10d objects (without roads)\n" % (totalObjects - int(totalMeters / 10))
		msg += "%10d different objects\n" % len(self.knownObjects.keys())
		msg += 'Details: \n'
		msg += tmp		
		showInfo("Map Statistics", msg)

	def ObjectDetails(self):
		if self.selected.entry.data.name in self.knownObjects.keys():
			n = positionClass()
			msg = ""
			msg += "\n" + "Long (red X): %12.6f \nWide (green Z): %12.6f \nHeight(blue Y): %12.6f \n" % (self.knownObjects[self.selected.entry.data.name]["long"], \
																  self.knownObjects[self.selected.entry.data.name]["wide"], \
																  self.knownObjects[self.selected.entry.data.name]["height"])
			msg += "\n" + " You should be behind blue, red and green axis to interpret this values properly"
			msg += "\n" + "Vertices and dimension of the Bounding Box for object: %s" % self.selected.entry.data.name
			msg += "\n" + "%20s %12.6s,%12.6s,%12.6s" % ("Vertice:", "X", "Y", "Z")
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["nearLeftTop"]
			msg += "\n" + n.leftAlign("Near Left Top") 
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["nearMiddle"]
			msg += "\n" + n.leftAlign("near Middle")

			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["nearRightTop"]
			msg += "\n" + n.leftAlign("near Right Top")
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["farLeftTop"]
			msg += "\n" + n.leftAlign("far Left Top")
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["farMiddle"]
			msg += "\n" + n.leftAlign("far Middle")

			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["farRightTop"]
			msg += "\n" + n.leftAlign("far Righ tTop")

			msg += "\n" + n.leftAlign("Near Left Bottom")
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["nearRightBottom"]
			msg += "\n" + n.leftAlign("near Right Bottom")
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["farLeftBottom"]
			msg += "\n" + n.leftAlign("far Left Bottom")
			n.asVector3 = self.knownObjects[self.selected.entry.data.name]["aabb"]["farRightBottom"]
			msg += "\n" + n.leftAlign("far Right Bottom")

			msg += "\n" + "There are %d %s in %s terrain" % (self.knownObjects[self.selected.entry.data.name]["instanceCount"],
											 self.selected.entry.data.name,
											 self.terrain.TerrainName)
			showInfo("Details", msg)

