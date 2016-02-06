
import ror.rorcommon
import ogre.renderer.OGRE as OGRE

_resource_manager_singleton = None

def resource_manager_init_singleton():
	"""
	Inits resource manager singleton. Returns nothing.
	"""
	global _resource_manager_singleton
	if _resource_manager_singleton is not None:
		return
	
	class ResourceManager:
		"""
		Philosophy: RoRToolkit manages resources on per-project basis.
		Only built-in resources are loaded on startup.
		ResourceManager scans all available resources and lets the user
		pick which ones to import to current project.
		"""
		def __init__(self):
			self._available_resources = {} # Key = group, Val = filepath

		def load_builtin_resources(self):
			# aabb offset setup to zero
			OGRE.MeshManager.getSingleton().setBoundsPaddingFactor(0.0)

			config_mgr = ror.rorcommon.rorSettings()
			toolkit_dir = config_mgr.toolkitMainFolder
			
			materials_dir = config_mgr.getConcatPath(toolkit_dir, ["media", "materials"])
			models_dir    = config_mgr.getConcatPath(toolkit_dir, ["media", "models"])
			overlays_dir  = config_mgr.getConcatPath(toolkit_dir, ["media", "overlays"])

			ogre_res_mgr = OGRE.ResourceGroupManager.getSingleton()
			ogre_res_mgr.addResourceLocation(materials_dir, "FileSystem", "ToolkitBase")
			ogre_res_mgr.addResourceLocation(models_dir,    "FileSystem", "ToolkitBase")
			ogre_res_mgr.addResourceLocation(overlays_dir,  "FileSystem", "ToolkitBase")
			ogre_res_mgr.initialiseResourceGroup("ToolkitBase")

		def scan_for_available_resources(self):
			"""
			Adds found res. locations to internal list, doesn't touch OGRE
			"""
			config_mgr = ror.rorcommon.rorSettings()
			import os.path

			homedir_scan_dirnames = ["packs", "terrains", "vehicles"]
			
			# Scan directories under RoR home directory
			ror_homedir = config_mgr.rorHomeFolder
			for dirname in homedir_scan_dirnames:
				dir_path = config_mgr.getConcatPath(ror_homedir, [dirname])
				dir_path = os.path.normpath(dir_path)
				filenames = os.listdir(dir_path);
				for filename in filenames:
					filepath = os.path.normpath(path.join(dir_path, filename))
					self._check_and_add_resource_location(dirname, filepath)

		def _check_and_add_resource_location(self, group_name, filepath):
			"""
			Adds res. location to internal list, doesn't touch OGRE
			:returns: True if added
			"""
			if (os.path.isdir(filepath)):
				self._add_resource(group_name, filepath)
				return True
			elif (os.path.isfile(filepath)):
				# TODO: Check zipfile validity
				is_zipfile = filename[-4:] == ".zip"
				if is_zipfile:
					self._add_resource(group_name, filepath)
					return True
			else:
				return False
		
		def _add_resource(self, group_name, path):
			"""
			Adds res. location to internal list, doesn't touch OGRE
			"""
			if group_name not in self._available_resources:
				self._available_resources[group_name] = []
			self._available_resources[group_name].append(path)

	_resource_manager_singleton = ResourceManager()

def resource_manager_get_singleton():
	global _resource_manager_singleton
	if _resource_manager_singleton is None:
		raise Exception("Programmer error: ResourceManager was not initialized")
	return _resource_manager_singleton
