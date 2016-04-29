
# Tracktool - Spline-based track creation system for roads, railoads, dirt tracks etc...
# Created by only_a_ptr, 2016
# Designed to replace all previous road/track systems

SPLINE_POINT_MESH_NAME   = "roadsys_spline_point.mesh"
SPLINE_POINT_ENTITY_NAME = "RoadSplinePointEntity"

GROUND_POINT_MESH_NAME   = "roadtool_ground_point.mesh"
GROUND_POINT_ENTITY_NAME = "RoadGroundPointEntity"

TIP_POINT_MESH_NAME      = "roadtool_tip_point.mesh"
TIP_POINT_ENTITY_NAME    = "RoadTipPointEntity"

import ogre.renderer.OGRE as OGRE

class TrackPoint:
	def __init__(self):
		self.position = OGRE.Vector3()
		self.elevation = float(0)

class TrackSection:
	def __init__(self):
		self._ogre_spline = OGRE.SimpleSpline()
		self._points = []

	

# SNIPPETS:
#       self.line.append(self.ogreWindow.sceneManager.createManualObject("lineobj" + str(i)))

#		if ogre.MaterialManager.getSingleton().getByName("matline_ideal") is None:
#			mat = ogre.MaterialManager.getSingleton().create("matline_ideal", "ToolkitBase")
#			mat.setReceiveShadows(False)
#			mat.getTechnique(0).setLightingEnabled(True)
#			mat.getTechnique(0).getPass(0).setDiffuse(0, 1, 0, 0)
#			mat.getTechnique(0).getPass(0).setAmbient(0, 1, 0)
#			mat.getTechnique(0).getPass(0).setSelfIllumination(0, 1, 0)

class TrackSystem:

	def __init__(self, ogre_scene_mgr):
		self._ogre_scene_mgr = ogre_scene_mgr

		# Visualization
		self._spline_point_mesh = ogre_scene_mgr.createEntity(SPLINE_POINT_ENTITY_NAME, SPLINE_POINT_MESH_NAME)

		# Construction
		self._cursor_ground_mesh = ogre_scene_mgr.createEntity(GROUND_POINT_ENTITY_NAME, GROUND_POINT_MESH_NAME)
		self._cursor_ground_scenenode = ogre_scene_mgr.createSceneNode()
		self._cursor_ground_scenenode.attachObject(self._cursor_ground_mesh)
		self._cursor_tip_mesh = ogre_scene_mgr.createEntity(TIP_POINT_ENTITY_NAME, TIP_POINT_MESH_NAME)
		self._cursor_tip_scenenode = ogre_scene_mgr.createSceneNode()
		self._cursor_tip_scenenode.attachObject(self._cursor_tip_mesh)
		self._active_section = None
		self._dragged_point_indexes = []
		self._cursor_elevation = 0
		self._cursor_ground_pos = (0,0,0)
		self._is_active = False
		self._is_cursor_visible = False

	def set_active(self, val):
		if self._is_active != val:
			self._is_active = val

	def set_cursor_visible(self, val):
		if val != self._is_cursor_visible:
			self._is_cursor_visible = val
			root_sn = self._ogre_scene_mgr.getRootSceneNode()
			if val:
				root_sn.addChild(self._cursor_ground_scenenode)
				root_sn.addChild(self._cursor_tip_scenenode)
			else:
				root_sn.removeChild(self._cursor_ground_scenenode)
				root_sn.removeChild(self._cursor_tip_scenenode)

	def set_cursor_world_pos(self, x, y, z):
		self._cursor_ground_pos = (x,y,z)
		self._cursor_ground_scenenode.setPosition(x, y, z)
		self._cursor_tip_scenenode.setPosition(x, (y + self._cursor_elevation), z)
