
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
		self.position_xyz      = None
		self.rotation_matrix   = None # Primary method
		self.rotation_xyz      = None # Compatibility method
		self.qualifier_str     = None # Terrn feature
		self.location_name_str = None # Terrn feature

class TerrainProject:
	"""
	A rortoolkit terrain project.
	Not linked to any specific format (terrn, terrn2, future...)

	:attribute str name:
	:attribute dict authors: dict {author:str => credits:str}
	"""

	def __init__(self):
		self.name                    = None
		self.authors                 = {}
		self.use_caelum              = None # Bool
		self.use_heightmap           = None # Bool
		self.global_water_height     = None # Number|None
		self.sky_color_rgb           = None
		self.spawn_pos_truck_xyz     = None
		self.spawn_pos_camera_xyz    = None
		self.spawn_pos_character_xyz = None
		self.cube_map_name           = None # Str|None
		self.objects                 = []
