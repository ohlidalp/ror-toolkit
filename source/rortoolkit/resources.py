
import ror.rorcommon
import ogre.renderer.OGRE as OGRE

_resource_manager_singleton = None

def init():
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
			self._available_resources = {} # Key = group, Val = dict {path, type(FileSystem/Zip)}
			self._initialized_groups = [] # List of OGRE resource group names
			self._installdir_dirnames = ["materials", "meshes", "textures"]

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
			import os
			import os.path

			homedir_scan_dirnames = ["packs", "terrains", "vehicles"]
			
			# Scan directories under RoR home directory
			ror_homedir = config_mgr.rorHomeFolder
			for dirname in homedir_scan_dirnames:
				dir_path = config_mgr.getConcatPath(ror_homedir, [dirname])
				dir_path = os.path.normpath(dir_path)
				filenames = os.listdir(dir_path);
				for filename in filenames:
					filepath = os.path.normpath(os.path.join(dir_path, filename))
					res_grp_name = "homedir_" + dirname
					self._check_and_add_resource_location(res_grp_name, filepath)

			# Add zips under installation dir
			resources_dir = os.path.normpath( os.path.join(config_mgr.rorFolder, "resources") )
			for dirname in self._installdir_dirnames:
				dir_path = os.path.join(resources_dir, dirname)
				res_grp_name = "installdir_" + dirname
				self._check_and_add_resource_location(res_grp_name, dir_path)
				self._check_and_add_resource_location(res_grp_name, dir_path + ".zip")

		def _check_and_add_resource_location(self, group_name, filepath):
			"""
			Adds res. location to internal list, doesn't touch OGRE
			:returns: True if added
			"""
			import os.path

			if os.path.isdir(filepath):
				self._add_resource(group_name, filepath, "FileSystem")
				return True
			elif os.path.isfile(filepath) and (filepath[-4:] == ".zip"):
				self._add_resource(group_name, filepath, "Zip")
			else:
				return False
		
		def _add_resource(self, group_name, path, type):
			"""
			Adds res. location to internal list, doesn't touch OGRE
			"""
			entry = {
				"type": type,
				"path": path
			}

			if group_name not in self._available_resources:
				self._available_resources[group_name] = []
			self._available_resources[group_name].append(entry)

		def _add_ogre_resource_group(self, groupname, itemlist):
			ogre_res_mgr = OGRE.ResourceGroupManager.getSingleton()
			for item in itemlist:
				ogre_res_mgr.addResourceLocation(item["path"], item["type"], groupname)
			ogre_res_mgr.initialiseResourceGroup(groupname)
			self._initialized_groups.append(groupname)

		def init_all_known_resources(self):
			for group_key in self._available_resources:
				group_entries = self._available_resources[group_key]
				self._add_ogre_resource_group(group_key, group_entries)
			self._available_resources = {}

		def init_all_installdir_resources(self):
			for dirname in self._installdir_dirnames:
				grp_name = "installdir_" + dirname
				if grp_name in self._available_resources:
					grp_itemlist = self._available_resources[grp_name]
					self._add_ogre_resource_group(grp_name, grp_itemlist)
					del self._available_resources[grp_name]

		def search_importable_terrains(self):
			"""
			:returns: List of filenames
			"""
			# Search
			all_fileinfos = []
			ogre_res_mgr = OGRE.ResourceGroupManager.getSingleton()
			for group_name in self._initialized_groups:
				terrn_files = ogre_res_mgr.findResourceFileInfo(group_name, "*.terrn")
				terrn2_files = ogre_res_mgr.findResourceFileInfo(group_name, "*.terrn2")
				all_fileinfos.extend(terrn_files)
				all_fileinfos.extend(terrn2_files)
			# Return list of filenames
			all_filenames = []
			for fileinfo in all_fileinfos:
				all_filenames.append(fileinfo.filename)
			return all_filenames

	_resource_manager_singleton = ResourceManager()

def _get_singleton(fn_name):
	if _resource_manager_singleton is None:
		raise Exception("rortoolkit.resources.{}(): Resource manager was not initialized!".format(fn_name))
	return _resource_manager_singleton

def open_ogre_resource(filename):
	return OGRE.ResourceGroupManager.getSingleton().openResource(resourceName=filename, searchGroupsIfNotFound=True)

def get_resource_zip_path(filename):
	"""
	Returns full path of ZIPfile containing the resource, or None if the resource doesn't exist/isn't zipped.
	"""
	try:
		groupname = ror.rorcommon.ogreGroupFor(filename)
		fileinfo = OGRE.ResourceGroupManager.getSingleton().findResourceFileInfo(groupname, filename, False)
		return fileinfo[0].archive.Name
	except:
		return None

def setup_terrain_project_resources(project):
	import rortoolkit.terrain

	ogre_mgr = OGRE.ResourceGroupManager.getSingleton()
	# Project root
	grp_name = rortoolkit.terrain.OGRE_RESOURCEGROUP_ROOT
	ogre_mgr.addResourceLocation(project.get_project_directory(), "FileSystem", grp_name, False)
	ogre_mgr.initialiseResourceGroup(grp_name)
	# Project temp dir
	grp_name = rortoolkit.terrain.OGRE_RESOURCEGROUP_TEMP
	ogre_mgr.addResourceLocation(project.get_temp_directory(), "FileSystem", grp_name, False)
	ogre_mgr.initialiseResourceGroup(grp_name)
	# Project resource dir - recursive!
	grp_name = rortoolkit.terrain.OGRE_RESOURCEGROUP_RESOURCES
	ogre_mgr.addResourceLocation(project.get_resources_directory(), "FileSystem", grp_name, True) # Recursive!
	ogre_mgr.initialiseResourceGroup(grp_name)

def load_builtin_resources():
	_get_singleton("load_builtin_resources").load_builtin_resources()

def init_all_installdir_resources():
	_get_singleton("init_all_installdir_resources").init_all_installdir_resources()

def scan_for_available_resources():
	_get_singleton("scan_for_available_resources").scan_for_available_resources()

def init_all_known_resources():
	_get_singleton("init_all_known_resources").init_all_known_resources()

def search_importable_terrains():
	return _get_singleton("search_importable_terrains").search_importable_terrains()

