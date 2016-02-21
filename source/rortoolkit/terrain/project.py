
"""
RoRToolkit terrain project live in TOOLKIT_HOME/map-projects/
Each project has it's subdirectory with following contents:
 * terrain-project.json - main project file, Always present.
 * terrain-heightmap-uint[8|16].raw - Heightmap. Optional.
"""

class TerrainObject:
	"""
	A terrn-style terrain object.

	:attribute tuple  position_xyz      :
	:attribute object rotation_matrix   :
	:attribute tuple  rotation_xyz      : Compatibility method
	:attribute str    qualifier_str     : Terrn feature
	:attribute str    location_name_str : Terrn feature
	"""
	
	def __init__(self):
		self.position_xyz        = None
		self.rotation_quaternion = None # Primary method
		self.type                = None # Str
		self.extra_options       = None # list[str] | None

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
			"use_caelum"          : False,
			"sky_color_rgb"       : (0,0,0), # Tuple RGB
			"cubemap_name"        : None, # Str
			"full_map_diffuse_texture" : None, # Str | None
			"full_map_detail_texture" : None, # Str | None
			"detail_texture_num_tiles" : None, # Number | None
		}
		self.physics = {
			"global_gravity"      : None, # Number
			"global_water_height" : None, # Number | None
			"use_heightmap"       : False,
			"heightmap_size" : None,
			"heightmap_bpp" : 2,
			"heightmap_flip" : False,
			"heightmap_vertical_scale" : None,
		}
		self.gameplay = {
			"spawn_pos_truck_xyz"     : None, # Tuple XYZ
			"spawn_pos_camera_xyz"    : None, # Tuple XYZ
			"spawn_pos_character_xyz" : None, # Tuple XYZ
		}
		self.objects                 = []
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

	def save_as_json(self):
		import os.path
		import json

		# Prepare project dir
		project_dir = self.get_project_directory()
		if not os.path.isdir(project_dir):
			raise Exception("Failed to create map project dir: " + str(project_dir))

		# Save project file
		json_project = {
			"header"   : self.header,
			"visuals"  : self.visuals,
			"physics"  : self.physics,
			"gameplay" : self.gameplay,

			"ogre_legacy_terrain_scene_manager" : self.ogre_legacy_tsm
		}
		json_filename = os.path.join(project_dir, "terrain-project.json")
		json_f = open(name=json_filename, mode="w")
		json.dump(obj=json_project, fp=json_f, indent=4) # project file
		json_f.close()
	
	def get_project_directory(self):
		from ror.settingsManager import rorSettings
		import os.path

		subdirs = ["map-projects", self.header["technical_name"]]
		return os.path.normpath(rorSettings().concatToToolkitHomeFolder(subdirs))

	def get_heightmap_filename(self):
		if "heightmap_bpp" not in self.physics:
			return None
		if self.physics["heightmap_bpp"] == 2:
			return "heightmap-uint16.raw"
		else:
			return "heightmap-uint8.raw"

