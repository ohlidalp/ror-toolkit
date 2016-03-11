
"""
RoRToolkit terrain project live in TOOLKIT_HOME/map-projects/
Each project has it's subdirectory with following contents:
 * terrain-project.json - main project file, Always present.
 * terrain-heightmap-uint[8|16].raw - Heightmap. Optional.
 * temp [dir] - Temporary files
"""

# File names
PROJECT_JSON_FILENAME        = "terrain-project.json"
STATIC_OBJECTS_JSON_FILENAME = "terrain-static-objects.json"
RIG_OBJECTS_JSON_FILENAME    = "terrain-rig-objects.json"
OGRE_TSM_CONFIG_FILENAME     = "ogre-terrain-scene-mgr.cfg"
HEIGHTMAP_UINT8_FILENAME     = "heightmap-uint8.raw"
HEIGHTMAP_UINT16_FILENAME    = "heightmap-uint16.raw"

# Directory names
PROJECT_TEMP_SUBDIR          = "temp"
PROJECT_RESOURCES_SUBDIR     = "resources"

# OGRE resource-group names
OGRE_RESOURCEGROUP_ROOT      = "current-terrain-project-root"
OGRE_RESOURCEGROUP_RESOURCES = "current-terrain-project-resources"
OGRE_RESOURCEGROUP_TEMP      = "current-terrain-project-temp"

class TerrainObjectBase:
	"""
	A terrn-style terrain object.

	:attribute tuple  position_xyz      :
	:attribute object rotation_quaternion:
	:attribute tuple  rotation_rx_ry_rz : legacy RoR positioning
	:attribute str    qualifier_str     : Terrn feature
	:attribute str    location_name_str : Terrn feature
	"""
	
	def __init__(self):
		self.position_xyz        = None
		self.rotation_quaternion = None
		self.rotation_rx_ry_rz   = None # tuple(rx,ry,rz) --- legacy RoR positioning
		self.type                = None # Str
		self.extra_options       = None # list[str] | None
		self.filename            = None
		self.editor_settings     = {}

	@staticmethod
	def _json_import(this, json_dict):
		this.position_xyz        = json_dict["position_xyz"]
		this.rotation_quaternion = json_dict["rotation_quaternion"]
		this.rotation_rx_ry_rz   = json_dict["rotation_rx_ry_rz"]
		this.type                = json_dict["type"]
		this.extra_options       = json_dict["extra_options"]
		this.filename            = json_dict["filename"]
		this.editor_settings     = json_dict["editor_settings"]

	def json_export(self):
		return {
			"position_xyz"        : self.position_xyz,
			"rotation_quaternion" : self.rotation_quaternion,
			"rotation_rx_ry_rz"   : self.rotation_rx_ry_rz,
			"type"                : self.type,
			"extra_options"       : self.extra_options,
			"filename"            : self.filename,
			"editor_settings"     : self.editor_settings
		}

class TerrainStaticObject(TerrainObjectBase):

	def __init__(self):
		TerrainObjectBase.__init__(self)

	@staticmethod
	def create_from_json(json_dict):
		this = TerrainStaticObject()
		TerrainObjectBase._json_import(this, json_dict)
		return this

	def json_export(self):
		return TerrainObjectBase.json_export(self)

class TerrainRigObject(TerrainObjectBase):

	def __init__(self):
		TerrainObjectBase.__init__(self)

	@staticmethod
	def create_from_json(json_dict):
		this = TerrainRigObject()
		TerrainObjectBase._json_import(this, json_dict)
		return this

	def json_export(self):
		return TerrainObjectBase.json_export(self)

class TerrainProject:
	"""
	A rortoolkit terrain project.
	Not linked to any specific format (terrn, terrn2, future...)

	"""

	def __init__(self):
		self.header = {
			"format_version" : 1,
			"name"           : "Unititled terrain",
			"technical_name" : "Untitled_terrain",
			"authors"        : {},
		}
		self.visuals = {
			"use_caelum"               : False,
			"sky_color_rgb"            : (0,0,0), # Tuple RGB
			"cubemap_name"             : None, # Str
			"full_map_diffuse_texture" : None, # Str | None
			"full_map_detail_texture"  : None, # Str | None
			"detail_texture_num_tiles" : None, # Number | None
		}
		self.physics = {
			"global_gravity"           : None, # Number
			"global_water_height"      : None, # Number | None
			"use_heightmap"            : False,
			"heightmap_size"           : None,
			"heightmap_bpp"            : 2,
			"heightmap_flip"           : False,
			"heightmap_vertical_scale" : None,
		}
		self.gameplay = {
			"spawn_pos_truck_xyz"     : None, # Tuple XYZ
			"spawn_pos_camera_xyz"    : None, # Tuple XYZ
			"spawn_pos_character_xyz" : None, # Tuple XYZ
		}
		self.ogre_legacy_tsm = {
			"page_size_vertices"   : None,
			"tile_size_vertices"   : None,
			"max_pixel_error"      : None,
			"page_size_world_x"    : None,
			"page_size_world_z"    : None,
			"max_mipmap_level"     : None,
			"use_vertex_normals"   : True,
			"vertex_program_morph" : False,
			"lod_morph_start"      : None,
		}
		self.editor_settings = {}
		self.static_objects = []
		self.rig_objects    = []

	def save_as_json(self):
		import os.path
		import json
		import codecs

		# Prepare project dir
		project_dir = self.get_project_directory()
		if not os.path.isdir(project_dir):
			raise Exception("Failed to create map project dir: " + str(project_dir))

		# Save project file
		json_project = {
			"header"          : self.header,
			"visuals"         : self.visuals,
			"physics"         : self.physics,
			"gameplay"        : self.gameplay,
			"editor_settings" : self.editor_settings,
			"ogre_tsm_config" : self.ogre_legacy_tsm
		}
		json_filename = os.path.join(project_dir, PROJECT_JSON_FILENAME)
		json_f = codecs.open(json_filename, mode="w", encoding="utf-8")
		json.dump(obj=json_project, fp=json_f, indent=4)
		json_f.close()

		# Save static objects
		json_obj_list = []
		for obj in self.static_objects:
			json_obj_list.append(obj.json_export())
		json_filename = os.path.join(project_dir, STATIC_OBJECTS_JSON_FILENAME)
		json_f = codecs.open(json_filename, mode="w", encoding="utf-8")
		json.dump(obj=json_obj_list, fp=json_f, indent=4)
		json_f.close()

		# Save rig objects
		json_rig_list = []
		for obj in self.rig_objects:
			json_rig_list.append(obj.json_export())
		json_filename = os.path.join(project_dir, RIG_OBJECTS_JSON_FILENAME)
		json_f = codecs.open(json_filename, mode="w", encoding="utf-8")
		json.dump(obj=json_rig_list, fp=json_f, indent=4)
		json_f.close()
	
	def get_project_directory(self):
		from ror.settingsManager import rorSettings
		import os.path

		subdirs = ["map-projects", self.header["technical_name"]]
		return os.path.normpath(rorSettings().concatToToolkitHomeFolder(subdirs))

	def get_temp_directory(self):
		import os.path
		return os.path.join(self.get_project_directory(), PROJECT_TEMP_SUBDIR)

	def get_resources_directory(self):
		import os.path
		return os.path.join(self.get_project_directory(), PROJECT_RESOURCES_SUBDIR)

	def get_heightmap_filename(self):
		if "heightmap_bpp" not in self.physics:
			return None
		if self.physics["heightmap_bpp"] == 2:
			return HEIGHTMAP_UINT16_FILENAME
		else:
			return HEIGHTMAP_UINT8_FILENAME

	def export_ogre_tsm_config(self):
		import os
		import os.path

		# Mkdir
		tmp_dir_path = self.get_temp_directory()
		if not os.path.isdir(tmp_dir_path):
			os.mkdir(tmp_dir_path)
		
		# Export the file
		tsm_cfg_path = os.path.join(tmp_dir_path, OGRE_TSM_CONFIG_FILENAME)
		f = open(tsm_cfg_path, mode = "w")
		def add_line(text = ""):
			f.write(text + "\n")

		add_line("# Terrain configuration file for legacy OGRE TerrainSceneManager (deprecated in OGRE 1.7)")
		add_line("# ---------------------------------------------------------------------------------------")
		add_line()
		add_line("# The main world texture (if you wish the terrain manager to create a material for you)")
		add_line("WorldTexture={0}".format(self.visuals["full_map_diffuse_texture"]))
		add_line()
		add_line("# The detail texture (if you wish the terrain manager to create a material for you)")
		add_line("DetailTexture={0}".format(self.visuals["full_map_detail_texture"]))
		add_line()
		add_line("#number of times the detail texture will tile in a terrain tile")
		add_line("DetailTile={0}".format(self.visuals["detail_texture_num_tiles"]))
		add_line()
		add_line("# Heightmap source")
		add_line("PageSource=Heightmap")
		add_line()
		add_line("# Heightmap-source specific settings")
		add_line("Heightmap.image={0}".format(self.get_heightmap_filename()))
		add_line()
		add_line("# If you use RAW, fill in the below too")
		add_line("# RAW-specific setting - size (horizontal/vertical)")
		add_line("Heightmap.raw.size={0}".format(self.physics["heightmap_size"]))
		add_line("# RAW-specific setting - bytes per pixel (1 = 8bit, 2=16bit)")
		add_line("Heightmap.raw.bpp={0}".format(self.physics["heightmap_bpp"]))
		add_line("# Use this if you want to flip the terrain (eg Terragen exports raw upside down)")
		add_line("Heightmap.flip={0}".format(self.physics["heightmap_flip"]))
		add_line()
		add_line("# How large is a page of tiles (in vertices)? Must be (2^n)+1")
		add_line("PageSize={0}".format(self.ogre_legacy_tsm["page_size_vertices"]))
		add_line()
		add_line("# How large is each tile? Must be (2^n)+1 and be smaller than PageSize")
		add_line("TileSize={0}".format(self.ogre_legacy_tsm["tile_size_vertices"]))
		add_line()
		add_line("# The maximum error allowed when determining which LOD to use")
		add_line("MaxPixelError={0}".format(self.ogre_legacy_tsm["max_pixel_error"]))
		add_line()
		add_line("# The size of a terrain page, in world units")
		add_line("PageWorldX={0}".format(self.ogre_legacy_tsm["page_size_world_x"]))
		add_line("PageWorldZ={0}".format(self.ogre_legacy_tsm["page_size_world_z"]))
		add_line("# Maximum height of the terrain ")
		add_line("MaxHeight={0}".format(self.physics["heightmap_vertical_scale"]))
		add_line()
		add_line("# Upper LOD limit")
		add_line("MaxMipMapLevel={0}".format(self.ogre_legacy_tsm["max_mipmap_level"]))
		add_line()
		add_line("VertexNormals={0}".format(self.ogre_legacy_tsm["use_vertex_normals"]))
		add_line("#VertexColors=yes")
		add_line("#UseTriStrips=yes")
		add_line()
		add_line("# Use vertex program to morph LODs, if available")
		add_line("VertexProgramMorph={0}".format(self.ogre_legacy_tsm["vertex_program_morph"]))
		add_line()
		add_line("# The proportional distance range at which the LOD morph starts to take effect")
		add_line("# This is as a proportion of the distance between the current LODs effective range,")
		add_line("# and the effective range of the next lower LOD")
		add_line("LODMorphStart={0}".format(self.ogre_legacy_tsm["lod_morph_start"]))
		add_line()
		add_line("# This following section is for if you want to provide your own terrain shading routine")
		add_line("# Note that since you define your textures within the material this makes the ")
		add_line("# WorldTexture and DetailTexture settings redundant")
		add_line()
		add_line("# The name of the vertex program parameter you wish to bind the morph LOD factor to")
		add_line("# this is 0 when there is no adjustment (highest) to 1 when the morph takes it completely")
		add_line("# to the same position as the next lower LOD")
		add_line("# USE THIS IF YOU USE HIGH-LEVEL VERTEX PROGRAMS WITH LOD MORPHING")
		add_line("#MorphLODFactorParamName=morphFactor")
		add_line()
		add_line("# The index of the vertex program parameter you wish to bind the morph LOD factor to")
		add_line("# this is 0 when there is no adjustment (highest) to 1 when the morph takes it completely")
		add_line("# to the same position as the next lower LOD")
		add_line("# USE THIS IF YOU USE ASSEMBLER VERTEX PROGRAMS WITH LOD MORPHING")
		add_line("#MorphLODFactorParamIndex=4")
		add_line()
		add_line("# The name of the material you will define to shade the terrain")
		add_line("#CustomMaterialName=TestTerrainMaterial")

		f.close()

def load_project_from_directory(project_dir_name):
	import os.path
	import json
	import codecs

	project = TerrainProject()

	# Check project directory
	project.header["technical_name"] = project_dir_name
	project_dir_path = project.get_project_directory()
	if not os.path.isdir(project_dir_path):
		raise Exception("Error loading terrain project from directory [{}] - path doesn't exist".format(project_dir_path))

	# Load project JSON
	project_json_path = os.path.join(project_dir_path, PROJECT_JSON_FILENAME)
	if not os.path.isfile(project_json_path):
		raise Exception("Error loading terrain project, missing JSON file {}".format(project_json_path))
	f = codecs.open(project_json_path, mode="r", encoding="utf-8")
	json_project = json.load(f, encoding="utf-8")
	f.close()

	# Process project JSON
	project.header          = json_project["header"]
	project.visuals         = json_project["visuals"]
	project.physics         = json_project["physics"]
	project.gameplay        = json_project["gameplay"]
	project.ogre_legacy_tsm = json_project["ogre_tsm_config"]
	project.editor_settings = json_project["editor_settings"]

	# Load objects JSON
	objlist_json_path = os.path.join(project_dir_path, STATIC_OBJECTS_JSON_FILENAME)
	if os.path.isfile(objlist_json_path):
		f = codecs.open(objlist_json_path, mode="r", encoding="utf-8")
		json_objlist = json.load(f, encoding="utf-8")
		f.close()
		for json_obj in json_objlist:
			obj = TerrainStaticObject.create_from_json(json_obj)
			project.static_objects.append(obj)

	# Load rigs JSON
	riglist_json_path = os.path.join(project_dir_path, RIG_OBJECTS_JSON_FILENAME)
	if os.path.isfile(riglist_json_path):
		f = codecs.open(riglist_json_path, mode="r", encoding="utf-8")
		json_riglist = json.load(f, encoding="utf-8")
		f.close()
		for json_obj in json_riglist:
			obj = TerrainRigObject.create_from_json(json_obj)
			project.rig_objects.append(obj)

	return project

